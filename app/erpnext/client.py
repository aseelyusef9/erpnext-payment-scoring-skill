"""
ERPNext API client for fetching customer, invoice, and payment data.
"""
import requests
from typing import List, Dict, Optional, Any
from app.config import settings


class ERPNextClient:
    """Client for interacting with ERPNext API."""
    
    def __init__(self):
        self.base_url = settings.ERPNEXT_URL
        self.api_key = settings.ERPNEXT_API_KEY
        self.api_secret = settings.ERPNEXT_API_SECRET
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to ERPNext API."""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Fetch customer details from ERPNext."""
        endpoint = f"/api/resource/Customer/{customer_id}"
        return self._make_request("GET", endpoint)
    
    def get_customer_invoices(self, customer_id: str) -> List[Dict[str, Any]]:
        """Fetch all invoices for a customer."""
        endpoint = "/api/resource/Sales Invoice"
        params = {
            "filters": f'[["customer", "=", "{customer_id}"]]',
            "fields": '["name", "customer", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"]'
        }
        result = self._make_request("GET", endpoint, params=params)
        return result.get("data", [])
    
    def get_customer_payments(self, customer_id: str) -> List[Dict[str, Any]]:
        """Fetch all payments for a customer."""
        endpoint = "/api/resource/Payment Entry"
        params = {
            "filters": f'[["party", "=", "{customer_id}"]]',
            "fields": '["name", "party", "posting_date", "paid_amount", "payment_type", "reference_no"]'
        }
        result = self._make_request("GET", endpoint, params=params)
        return result.get("data", [])
    
    def list_customers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all customers."""
        endpoint = "/api/resource/Customer"
        params = {
            "limit_page_length": limit,
            "fields": '["name", "customer_name", "customer_type"]'
        }
        result = self._make_request("GET", endpoint, params=params)
        return result.get("data", [])
