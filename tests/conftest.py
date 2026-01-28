"""
Pytest configuration and fixtures for all tests.
"""
import os
import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture(autouse=True)
def mock_claude_for_tests():
    """
    Automatically mock Claude AI client for all tests.
    Tests run without real API calls or API key.
    """
    # Mock the get_claude_client function
    with patch("app.services.claude_client.get_claude_client") as mock_get_client:
        # Create a mock Claude client
        mock_client = MagicMock()
        
        # Mock the messages.create method to return a fake response
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
        mock_get_client.return_value = mock_client
        
        yield mock_client
