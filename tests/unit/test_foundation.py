import os
import pytest

def test_environment_loads():
    """Verify default testing environment flags."""
    assert os.getenv("APP_ENV", "testing") in ["testing", "development"]

def test_mock_mode_flag():
    """Verify that Azure mock mode is active by default for budget protection."""
    mock_mode = os.getenv("AZURE_MOCK_MODE", "True")
    assert mock_mode in ["True", "true", "1"]
