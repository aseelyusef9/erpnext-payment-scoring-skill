"""
API tests for customer endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)


def test_list_customers():
    """Test listing customers endpoint."""
    with patch("app.api.customers.erpnext_client") as mock_client:
        mock_client.list_customers.return_value = [
            {"name": "CUST-001", "customer_name": "Test Customer 1"},
            {"name": "CUST-002", "customer_name": "Test Customer 2"}
        ]
        
        response = client.get("/api/v1/customers")
        assert response.status_code == 200
        assert len(response.json()) == 2


def test_get_customer_score():
    """Test get customer score endpoint."""
    with patch("app.api.customers.erpnext_client") as mock_client:
        # Mock customer data
        mock_client.get_customer.return_value = {
            "data": {
                "name": "CUST-001",
                "customer_name": "Test Customer"
            }
        }
        
        # Mock invoices
        mock_client.get_customer_invoices.return_value = []
        
        # Mock payments
        mock_client.get_customer_payments.return_value = []
        
        response = client.get("/api/v1/customers/CUST-001/score")
        
        # With no invoices, should return default score
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST-001"
        assert "score" in data
        assert "risk_level" in data


def test_get_customer_score_not_found():
    """Test get customer score for non-existent customer."""
    with patch("app.api.customers.erpnext_client") as mock_client:
        import requests
        mock_response = Mock()
        mock_response.status_code = 404
        mock_client.get_customer.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        response = client.get("/api/v1/customers/INVALID-ID/score")
        assert response.status_code == 404


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
