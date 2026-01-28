"""
Pytest configuration and fixtures for all tests.
"""
import os
import pytest
from unittest.mock import Mock, MagicMock, patch


# Patch get_claude_client at module level before any imports
@pytest.fixture(scope="session", autouse=True)
def mock_claude_globally():
    """Mock Claude client globally for all tests."""
    with patch("app.services.claude_client.get_claude_client") as mock_get:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = '''{
            "payment_score": 75,
            "risk_level": "Medium",
            "confidence_level": "High",
            "key_factors": [
                "Customer has consistent payment history",
                "Average payment delay of 5 days"
            ],
            "recommended_action": "Standard credit terms",
            "predicted_next_payment_date": "2026-02-15",
            "insights": "Customer shows medium risk profile with moderate payment reliability."
        }'''
        mock_client.messages.create.return_value = mock_response
        mock_get.return_value = mock_client
        yield


@pytest.fixture(autouse=True)
def mock_anthropic_key(monkeypatch):
    """Set a fake Anthropic API key for tests."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-for-testing")
