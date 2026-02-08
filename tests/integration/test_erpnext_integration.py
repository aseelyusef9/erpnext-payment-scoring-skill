"""
Integration tests for ERPNext client.
"""
import unittest
import sys
from pathlib import Path

# Add project root to path when running as standalone script
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from app.erpnext import ERPNextClient
from app.config import settings


@unittest.skipIf(
    not settings.ERPNEXT_API_KEY,
    "ERPNext credentials not configured"
)
class TestERPNextIntegration(unittest.TestCase):
    """Integration tests for ERPNext API client."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests."""
        cls.client = ERPNextClient()
    
    def test_erpnext_connection(self):
        """Test ERPNext API connection."""
        try:
            customers = self.client.list_customers(limit=1)
            self.assertIsInstance(customers, list)
        except Exception as e:
            self.skipTest(f"ERPNext not accessible: {str(e)}")
    
    def test_get_customer(self):
        """Test getting customer details."""
        # First, get a customer ID
        customers = self.client.list_customers(limit=1)
        if not customers:
            self.skipTest("No customers available in ERPNext")
        
        customer_id = customers[0]["name"]
        customer = self.client.get_customer(customer_id)
        
        self.assertIn("data", customer)
        self.assertEqual(customer["data"]["name"], customer_id)
    
    def test_get_customer_invoices(self):
        """Test fetching customer invoices."""
        # Get a customer
        customers = self.client.list_customers(limit=1)
        if not customers:
            self.skipTest("No customers available in ERPNext")
        
        customer_id = customers[0]["name"]
        invoices = self.client.get_customer_invoices(customer_id)
        
        self.assertIsInstance(invoices, list)
    
    def test_get_customer_payments(self):
        """Test fetching customer payments."""
        # Get a customer
        customers = self.client.list_customers(limit=1)
        if not customers:
            self.skipTest("No customers available in ERPNext")
        
        customer_id = customers[0]["name"]
        payments = self.client.get_customer_payments(customer_id)
        
        self.assertIsInstance(payments, list)


if __name__ == '__main__':
    unittest.main()
