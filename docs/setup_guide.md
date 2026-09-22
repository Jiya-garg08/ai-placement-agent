# 🛠️ Comprehensive Developer Setup & Installation Guide

Welcome to the **AI Placement Preparation Agent** installation and configuration guide. This document details how to set up, run, and test the application across local environments, Docker containers, and live Azure cloud configurations.

---

## 📋 System Requirements

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS 12+, or Ubuntu 20.04+ | Any modern 64-bit OS |
| **Python** | Python 3.10+ | Python 3.12 |
| **Memory (RAM)** | 4 GB | 8 GB+ |
| **Storage** | 1 GB free space | 2 GB free space |
| **Docker (Optional)**| Docker 24.0+ & Docker Compose 2.20+ | Docker Desktop with Buildx |

---

## 🚀 Fast Track Launch: One-Click Shell Scripts

We provide turnkey scripts that automate virtual environment creation, dependency installation, database initialization, test question seeding, and Streamlit execution.

### On Windows
Run from Command Prompt or PowerShell:
```cmd
scripts\run_local.bat
```

### On Linux or macOS
Grant execution permissions and run:
```bash
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

The application will be live at: **[http://localhost:8501](http://localhost:8501)**.

---

## ⚙️ Manual Local Installation (Step-by-Step)

If you prefer to configure your environment manually, follow these standard steps:

### 1. Clone the Repository
```bash
git clone https://github.com/Jiya-garg08/ai-placement-agent.git
cd ai-placement-agent
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the pre-configured sample file:
```bash
# Windows (CMD)
copy .env.example .env

# Windows (PowerShell) / Linux / macOS
cp .env.example .env
```

> [!IMPORTANT]
> By default, `.env.example` has `AZURE_MOCK_MODE=True` enabled. This guarantees **100% free offline execution ($0.00 spent)** using high-fidelity local mocks for Azure OpenAI and Azure AI Search.

### 5. Initialize Database & Seed Sample Candidate
```bash
# Initialize SQLite database schema
python -c "from database.database import init_db; init_db()"

# Seed 20+ curated placement questions across 10 CS domains
python -m scripts.seed_data

# Seed complete demo candidate (Jiya Garg) with resumes, roadmap & quiz history
python -c "from app.utils.seed_demo_student import seed_demo_student; seed_demo_student()"
```

### 6. Run the Streamlit Application
```bash
streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🐳 Docker & Docker Compose Deployment

The application is fully containerized with a production multi-stage build, minimal Debian Bookworm footprint, non-root user execution, and persistent volume mounting.

### Quick Launch via Docker Compose
```bash
# Build and run in background
docker compose up --build -d

# Inspect running container logs
docker compose logs -f

# Stop container
docker compose down
```

### One-Click Docker Helper Scripts
- **Windows**: `scripts\docker_run.bat`
- **Linux/macOS**: `chmod +x scripts/docker_run.sh && ./scripts/docker_run.sh`

### Docker Architecture Highlights
- **Base**: `python:3.12-slim-bookworm`
- **Security**: Runs under dedicated unprivileged user `appuser` (UID: 10001).
- **Health Check**: Automated periodic probe hitting `http://localhost:8501/_stcore/health`.
- **Persistence**: Host volume `./data` mapped to `/app/data` ensures your SQLite database and uploaded resumes persist across container rebuilds.

---

## 🔑 Environment Configuration Reference

All settings are strongly typed and validated via Pydantic in [`config/settings.py`](file:///e:/placement_preparation_agent/config/settings.py):

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `AZURE_MOCK_MODE` | `True` | When `True`, utilizes local heuristics & mock models without incurring cloud costs. |
| `DATABASE_URL` | `sqlite:///data/placement_prep.db` | SQLAlchemy connection string (SQLite locally, PostgreSQL in prod). |
| `AZURE_OPENAI_ENDPOINT` | `https://mock.openai.azure.com/` | Azure OpenAI resource URL. |
| `AZURE_OPENAI_API_KEY` | `mock-key` | Azure OpenAI authentication key. |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4o-mini` | Chat completion model deployment name. |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | `text-embedding-3-small` | Vector embedding model deployment name. |
| `AZURE_SEARCH_ENDPOINT` | `https://mock.search.windows.net/` | Azure AI Search service URL. |
| `AZURE_SEARCH_API_KEY` | `mock-search-key` | Azure AI Search admin API key. |
| `AZURE_SEARCH_INDEX_NAME` | `placement-prep-kb` | RAG vector search index name. |
| `GITHUB_TOKEN` | *(Optional)* | Personal access token for MCP live repository analysis. |

---

## 🧪 Running the Automated Test Suite

We maintain an exhaustive automated test suite with **113+ tests** spanning unit, integration, and security verification.

```bash
# Run entire test suite
python -m pytest tests/ -v

# Run with test coverage report
python -m pytest --cov=. --cov-report=term-missing

# Run specific domain test suites
python -m pytest tests/unit/test_security.py -v         # PII redaction & prompt injection defense
python -m pytest tests/integration/test_streamlit_journey.py -v # 10-page end-to-end journey
python -m pytest tests/unit/test_docker_setup.py -v      # Docker & Compose validation
```

---

## 🩺 Troubleshooting & FAQ

### 1. Port 8501 is already in use
If another Streamlit instance or service is occupying port 8501, specify an alternative port:
```bash
streamlit run app/streamlit_app.py --server.port=8502
```

### 2. Database Locked Error (SQLite)
SQLite can report a lock if multiple processes hold write locks simultaneously. We configured `expire_on_commit=False` and session scoped transactions. If an old process was aborted, delete or rename `data/placement_prep.db` and run:
```bash
python -c "from database.database import init_db; init_db()"
python -m scripts.seed_data
```

### 3. Missing Dependencies
If new modules were added to `requirements.txt`:
```bash
pip install -r requirements.txt --upgrade
```

---

## 🛡️ Security & Zero-Leak Guarantee

- Sensitive tokens matching GitHub, OpenAI, or Azure signatures are proactively blocked by `config/security.py`.
- Candidate emails, phone numbers, SSNs, Aadhaar numbers, and credit cards are automatically redacted before LLM ingestion.
- Never commit `.env` or personal access tokens to GitHub. The `.gitignore` and `.dockerignore` files are strictly configured to prevent credential leaks.
