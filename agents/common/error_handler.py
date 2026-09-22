import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, Any, Optional, Dict, Tuple
from collections import deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """Sliding-window request and token rate limiter to enforce strict Azure grant budget caps

    and prevent HTTP 429 overage throttling.
    """

    def __init__(self, max_requests_per_minute: int = 30, max_tokens_per_minute: int = 40000):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self._request_timestamps = deque()
        self._token_records = deque()  # stores (timestamp, token_count)

    def can_proceed(self) -> Tuple[bool, str]:
        """Check if a new invocation is permitted under current sliding-window rates."""
        now = time.time()
        window_start = now - 60.0

        # Purge timestamps older than 60s
        while self._request_timestamps and self._request_timestamps[0] < window_start:
            self._request_timestamps.popleft()

        while self._token_records and self._token_records[0][0] < window_start:
            self._token_records.popleft()

        if len(self._request_timestamps) >= self.max_requests_per_minute:
            return False, f"Request rate limit exceeded ({self.max_requests_per_minute}/min). Please wait a moment."

        current_tokens = sum(t[1] for t in self._token_records)
        if current_tokens >= self.max_tokens_per_minute:
            return False, f"Token rate limit cap reached ({self.max_tokens_per_minute} TPM). Please wait a moment."

        return True, ""

    def record_request(self, token_estimate: int = 500) -> None:
        """Log consumption upon API execution."""
        now = time.time()
        self._request_timestamps.append(now)
        self._token_records.append((now, token_estimate))

    def reset(self) -> None:
        """Clear all active records."""
        self._request_timestamps.clear()
        self._token_records.clear()


class ResponseCache:
    """In-memory resilient response cache providing fallback outputs when external APIs fail."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached output if present and not expired."""
        if key not in self._cache:
            return None
        timestamp, value = self._cache[key]
        if time.time() - timestamp > self.default_ttl:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store item in response cache."""
        ttl = ttl_seconds or self.default_ttl
        self._cache[key] = (time.time(), value)

    def clear(self) -> None:
        """Flush cache."""
        self._cache.clear()


# Global Singleton Instances
global_rate_limiter = RateLimiter(max_requests_per_minute=45, max_tokens_per_minute=50000)
global_response_cache = ResponseCache(default_ttl_seconds=3600)


def safe_agent_call(
    func: Callable[..., Any],
    *args,
    fallback_func: Optional[Callable[..., Any]] = None,
    cache_key: Optional[str] = None,
    timeout_seconds: float = 12.0,
    rate_limiter: Optional[RateLimiter] = None,
    cache: Optional[ResponseCache] = None,
    **kwargs
) -> Tuple[Any, bool, Optional[str]]:
    """Execute subagent or external API call with comprehensive safety boundaries:

    - Rate limit verification
    - Execution timeout protection
    - Automatic response caching
    - Graceful degradation to cached or heuristic fallback upon failure

    Returns:
        Tuple of (result, is_fallback, error_or_notice_message)
    """
    limiter = rate_limiter or global_rate_limiter
    res_cache = cache or global_response_cache

    # 1. Rate Limiting Check
    allowed, limit_msg = limiter.can_proceed()
    if not allowed:
        logger.warning(f"Rate limiter tripped: {limit_msg}")
        if cache_key:
            cached_val = res_cache.get(cache_key)
            if cached_val is not None:
                return cached_val, True, f"{limit_msg} Served resilient cached output."

        if fallback_func:
            try:
                fallback_res = fallback_func(*args, **kwargs)
                return fallback_res, True, f"{limit_msg} Served offline fallback."
            except Exception as fe:
                return None, True, f"{limit_msg} Fallback also failed: {str(fe)}"

        return None, True, limit_msg

    # 2. Timeout and Exception Guarded Execution
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            result = future.result(timeout=timeout_seconds)

        # Successful call - record rate limit usage & update cache
        limiter.record_request()
        if cache_key and result is not None:
            res_cache.set(cache_key, result)

        return result, False, None

    except TimeoutError:
        error_msg = f"Agent call timed out after {timeout_seconds} seconds."
        logger.error(error_msg)

        if cache_key:
            cached_val = res_cache.get(cache_key)
            if cached_val is not None:
                return cached_val, True, f"{error_msg} Served cached output."

        if fallback_func:
            try:
                return fallback_func(*args, **kwargs), True, f"{error_msg} Served offline fallback."
            except Exception as fe:
                return None, True, f"{error_msg} Fallback failed: {str(fe)}"

        return None, True, error_msg

    except Exception as e:
        error_msg = f"Agent execution failed with error: {str(e)}"
        logger.error(error_msg)

        if cache_key:
            cached_val = res_cache.get(cache_key)
            if cached_val is not None:
                return cached_val, True, f"{error_msg} Served cached output."

        if fallback_func:
            try:
                return fallback_func(*args, **kwargs), True, f"{error_msg} Served offline fallback."
            except Exception as fe:
                return None, True, f"{error_msg} Fallback failed: {str(fe)}"

        return None, True, error_msg
