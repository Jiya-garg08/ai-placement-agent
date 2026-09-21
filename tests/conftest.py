import os
import pytest

# Enforce mock mode and test environment for all automated test runs
os.environ["APP_ENV"] = "testing"
os.environ["AZURE_MOCK_MODE"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
