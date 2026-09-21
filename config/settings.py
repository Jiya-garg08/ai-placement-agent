import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    """Application configuration settings."""
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Cost & Mock Guardrails
    AZURE_MOCK_MODE: bool = os.getenv("AZURE_MOCK_MODE", "True").lower() in ("true", "1", "t")
    AZURE_DAILY_BUDGET_LIMIT: float = float(os.getenv("AZURE_DAILY_BUDGET_LIMIT", "3.00"))
    AZURE_TOTAL_BUDGET_CAP: float = float(os.getenv("AZURE_TOTAL_BUDGET_CAP", "200.00"))
    
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'placement.db'}")
    
    # Microsoft Foundry / Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    
    # Azure AI Search
    AZURE_SEARCH_SERVICE_ENDPOINT: str = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT", "")
    AZURE_SEARCH_API_KEY: str = os.getenv("AZURE_SEARCH_API_KEY", "")
    AZURE_SEARCH_INDEX_NAME: str = os.getenv("AZURE_SEARCH_INDEX_NAME", "placement-kb-index")
    
    # GitHub Integration
    GITHUB_PERSONAL_ACCESS_TOKEN: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")

settings = Settings()
