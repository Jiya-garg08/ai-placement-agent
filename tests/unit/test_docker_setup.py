import re
from pathlib import Path
import yaml


def test_dockerfile_structure_and_security():
    """Verify Dockerfile uses multi-stage builds, non-root user, and healthchecks."""
    dockerfile_path = Path("Dockerfile")
    assert dockerfile_path.exists(), "Dockerfile must be present in repository root"
    content = dockerfile_path.read_text(encoding="utf-8")

    # Multi-stage check
    assert "FROM python:3.12" in content
    assert "AS builder" in content
    assert "AS runner" in content

    # Security: Non-root user
    assert "groupadd" in content
    assert "useradd" in content
    assert "USER appuser" in content

    # Port & Healthcheck
    assert "EXPOSE 8501" in content
    assert "HEALTHCHECK" in content
    assert "_stcore/health" in content

    # CMD
    assert "streamlit" in content
    assert "app/streamlit_app.py" in content


def test_docker_compose_validity():
    """Verify docker-compose.yml defines services, volumes, and mock environments."""
    compose_path = Path("docker-compose.yml")
    assert compose_path.exists(), "docker-compose.yml must be present in repository root"
    content = compose_path.read_text(encoding="utf-8")

    parsed = yaml.safe_load(content)
    assert "services" in parsed
    service_names = list(parsed["services"].keys())
    assert len(service_names) >= 1

    svc = parsed["services"][service_names[0]]
    assert "ports" in svc
    assert any("8501:8501" in str(p) for p in svc["ports"])
    assert "volumes" in svc
    assert any("./data:/app/data" in str(v) for v in svc["volumes"])

    # Verify AZURE_MOCK_MODE is true in container environment
    env = svc.get("environment", [])
    if isinstance(env, list):
        assert any("AZURE_MOCK_MODE=true" in item for item in env)
    elif isinstance(env, dict):
        assert env.get("AZURE_MOCK_MODE") in [True, "true"]


def test_dockerignore_entries():
    """Verify .dockerignore excludes virtualenvs, test caches, and sensitive files."""
    dockerignore_path = Path(".dockerignore")
    assert dockerignore_path.exists()
    content = dockerignore_path.read_text(encoding="utf-8")

    expected_ignores = [".git", "__pycache__", ".venv", ".pytest_cache", ".env"]
    for pattern in expected_ignores:
        assert pattern in content, f".dockerignore should exclude '{pattern}'"


def test_launch_scripts_exist():
    """Verify one-click development and container launch scripts are present."""
    scripts = [
        "scripts/run_local.sh",
        "scripts/run_local.bat",
        "scripts/docker_run.sh",
        "scripts/docker_run.bat"
    ]
    for s in scripts:
        p = Path(s)
        assert p.exists(), f"Script {s} must exist"
        assert p.stat().st_size > 50, f"Script {s} must not be empty"
