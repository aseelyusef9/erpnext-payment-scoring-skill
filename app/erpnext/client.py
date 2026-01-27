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
            "Content-Type": "application/json",
            # Be explicit to avoid proxy issues and 417 responses
            "Accept": "application/json",
            "User-Agent": "ERPNextClient/1.0",
            # Suppress potential Expect: 100-continue behavior
            "Expect": ""
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to ERPNext API."""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Include server error details to aid troubleshooting
            try:
                details = response.json()
            except Exception:
                details = response.text
            raise requests.exceptions.HTTPError(f"{e} | Details: {details}", response=response)
        return response.json()
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Fetch customer details from ERPNext."""
        endpoint = f"/api/resource/Customer/{customer_id}"
        return self._make_request("GET", endpoint)

    def find_customer_by_name(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """Find a customer by exact customer_name."""
        endpoint = "/api/resource/Customer"
        params = {
            "filters": f'[["customer_name", "=", "{customer_name}"]] ',
            "fields": '["name", "customer_name", "customer_type"]'
        }
        result = self._make_request("GET", endpoint, params=params)
        data = result.get("data", [])
        return data[0] if data else None

    def create_customer(
        self,
        customer_name: str,
        customer_type: str = "Company",
        customer_group: str = "All Customer Groups",
        territory: str = "All Territories",
    ) -> Dict[str, Any]:
        """Create a customer with minimal required fields."""
        payload = {
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": customer_type,
            "customer_group": customer_group,
            "territory": territory,
        }
        endpoint = "/api/resource/Customer"
        result = self._make_request("POST", endpoint, json=payload)
        return result.get("data", {})

    def get_sales_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Fetch Sales Invoice details."""
        endpoint = f"/api/resource/Sales Invoice/{invoice_id}"
        return self._make_request("GET", endpoint).get("data", {})

    def get_active_fiscal_year(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the first active Fiscal Year.
        Returns dict with fields including year_start_date and year_end_date.
        """
        endpoint = "/api/resource/Fiscal Year"
        params = {
            "filters": '[ ["is_active", "=", 1] ]',
            "fields": '["name", "year_start_date", "year_end_date", "is_active"]',
            "limit_page_length": 1,
            "order_by": "year_start_date desc"
        }
        result = self._make_request("GET", endpoint, params=params)
        data = result.get("data", [])
        return data[0] if data else None

    def get_item(self, item_code: str) -> Dict[str, Any]:
        """Fetch item details."""
        endpoint = f"/api/resource/Item/{item_code}"
        return self._make_request("GET", endpoint)

    def create_item(
        self,
        item_code: str,
        item_name: Optional[str] = None,
        stock_uom: str = "Nos",
        item_group: str = "All Item Groups",
        is_stock_item: int = 0,
    ) -> Dict[str, Any]:
        """
        Create a basic Item in ERPNext so it can be invoiced.
        Uses minimal required fields.
        """
        item_doc = {
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_name or item_code,
            "stock_uom": stock_uom,
            "item_group": item_group,
            "is_stock_item": is_stock_item,
            "disabled": 0,
        }
        endpoint = "/api/resource/Item"
        result = self._make_request("POST", endpoint, json=item_doc)
        return result.get("data", {})
    
    def get_customer_invoices(self, customer_id: str) -> List[Dict[str, Any]]:
        """Fetch all invoices for a customer."""
        endpoint = "/api/resource/Sales Invoice"
        params = {
            "filters": f'[["customer", "=", "{customer_id}"]]',
            "fields": '["name", "customer", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "docstatus"]',
            "limit_page_length": 500  # Increase from default 20 to get all invoices
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
    
    def create_sales_invoice(self, customer_id: str, items: List[Dict[str, Any]], 
                           posting_date: str = None, due_date: str = None) -> Dict[str, Any]:
        """
        Create a Sales Invoice in ERPNext.
        
        Args:
            customer_id: ERPNext customer ID
            items: List of items [{"item_code": "Camera", "qty": 1, "rate": 1000}]
            posting_date: Invoice date (YYYY-MM-DD)
            due_date: Payment due date (YYYY-MM-DD)
        """
        # Ensure child table items include correct doctype for ERPNext
        normalized_items = []
        for itm in items:
            ni = {
                "doctype": "Sales Invoice Item",
                "item_code": itm.get("item_code"),
                "qty": itm.get("qty", 1),
                "rate": itm.get("rate")
            }
            normalized_items.append(ni)

        invoice_data = {
            "doctype": "Sales Invoice",
            "customer": customer_id,
            "posting_date": posting_date,
            "due_date": due_date,
            "set_posting_time": 1,
            "items": normalized_items
        }
        
        endpoint = "/api/resource/Sales Invoice"
        result = self._make_request("POST", endpoint, json=invoice_data)
        return result.get("data", {})
    
    def create_payment_entry(self, customer_id: str, invoice_id: str, 
                           amount: float, posting_date: str = None) -> Dict[str, Any]:
        """
        Create a Payment Entry for an invoice in ERPNext.
        
        Args:
            customer_id: Customer ID
            invoice_id: Sales Invoice ID
            amount: Payment amount
            posting_date: Payment date (YYYY-MM-DD)
        """
        # Use ERPNext's helper to build a valid Payment Entry with accounts & exchange rates
        build_endpoint = "/api/method/erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry"
        build_payload = {
            "party_type": "Customer",
            "party": customer_id,
            "posting_date": posting_date,
            "payment_type": "Receive",
            # ERPNext expects dt/dn (doctype/name) for helper
            "dt": "Sales Invoice",
            "dn": invoice_id,
        }
        built = self._make_request("POST", build_endpoint, json=build_payload)
        pe_doc = built.get("message") or built.get("data")
        if not pe_doc:
            raise requests.exceptions.HTTPError("Failed to build Payment Entry via ERPNext helper")

        # Adjust amounts if explicitly provided
        if amount is not None:
            pe_doc["paid_amount"] = amount
            pe_doc["received_amount"] = amount
            # Ensure references allocation aligns
            for ref in pe_doc.get("references", []):
                if ref.get("reference_doctype") == "Sales Invoice" and ref.get("reference_name") == invoice_id:
                    ref["allocated_amount"] = amount

        # Finally create the Payment Entry
        create_endpoint = "/api/resource/Payment Entry"
        result = self._make_request("POST", create_endpoint, json=pe_doc)
        return result.get("data", {})
    
    def submit_document(self, doctype: str, docname: str) -> Dict[str, Any]:
        """
        Submit a document in ERPNext (make it permanent).
        
        Args:
            doctype: Document type (e.g., "Sales Invoice", "Payment Entry")
            docname: Document name/ID
        """
        # Use the frappe.client.submit method instead of direct resource update
        endpoint = "/api/method/frappe.client.submit"
        params = {
            "doctype": doctype,
            "name": docname
        }
        result = self._make_request("POST", endpoint, json=params)
        return result.get("message", {})
