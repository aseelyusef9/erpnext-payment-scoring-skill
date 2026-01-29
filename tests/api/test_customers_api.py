"""
API tests for customer endpoints using unittest framework.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path when running as standalone script
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

import requests
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app


class TestCustomerAPI(unittest.TestCase):
    """Test cases for customer API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)
    
    def test_list_customers(self):
        """Test listing customers endpoint."""
        with patch("app.api.customers.erpnext_client") as mock_client:
            mock_client.list_customers.return_value = [
                {"name": "CUST-001", "customer_name": "Test Customer 1"},
                {"name": "CUST-002", "customer_name": "Test Customer 2"}
            ]
            
            response = self.client.get("/api/v1/customers")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 2)
    
    def test_get_customer_score(self):
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
            
            response = self.client.get("/api/v1/customers/CUST-001/score")
            
            # With no invoices, should return default score
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["customer_id"], "CUST-001")
            self.assertIn("score", data)
            self.assertIn("risk_level", data)
    
    def test_get_customer_score_not_found(self):
        """Test get customer score for non-existent customer."""
        with patch("app.api.customers.erpnext_client") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.get_customer.side_effect = requests.exceptions.HTTPError(response=mock_response)
            
            response = self.client.get("/api/v1/customers/INVALID-ID/score")
            self.assertEqual(response.status_code, 404)
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")


class TestCustomerAPIBadInputs(unittest.TestCase):
    """Test cases for customer API bad input validation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = TestClient(app)
    
    def test_list_customers_with_negative_limit(self):
        """Test list customers with negative limit value."""
        response = self.client.get("/api/v1/customers?limit=-5")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_list_customers_with_zero_limit(self):
        """Test list customers with zero limit value."""
        response = self.client.get("/api/v1/customers?limit=0")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_list_customers_with_exceeding_limit(self):
        """Test list customers with limit exceeding maximum (500)."""
        response = self.client.get("/api/v1/customers?limit=501")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_list_customers_with_invalid_type(self):
        """Test list customers with non-integer limit value."""
        response = self.client.get("/api/v1/customers?limit=abc")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_payment_scores_with_negative_limit(self):
        """Test payment scores with negative limit value."""
        response = self.client.get("/api/v1/customers/payment-scores?limit=-10")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_payment_scores_with_zero_limit(self):
        """Test payment scores with zero limit value."""
        response = self.client.get("/api/v1/customers/payment-scores?limit=0")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_payment_scores_with_exceeding_limit(self):
        """Test payment scores with limit exceeding maximum."""
        response = self.client.get("/api/v1/customers/payment-scores?limit=1000")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_high_risk_customers_with_negative_limit(self):
        """Test high risk customers with negative limit value."""
        response = self.client.get("/api/v1/customers/high-risk?limit=-5")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_high_risk_customers_with_zero_limit(self):
        """Test high risk customers with zero limit value."""
        response = self.client.get("/api/v1/customers/high-risk?limit=0")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_followups_with_negative_limit(self):
        """Test customer followups with negative limit value."""
        response = self.client.get("/api/v1/customers/followups?limit=-1")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_followups_with_zero_limit(self):
        """Test customer followups with zero limit value."""
        response = self.client.get("/api/v1/customers/followups?limit=0")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
    
    def test_followups_with_exceeding_limit(self):
        """Test customer followups with limit exceeding maximum."""
        response = self.client.get("/api/v1/customers/followups?limit=600")
        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())


if __name__ == '__main__':
    unittest.main()
