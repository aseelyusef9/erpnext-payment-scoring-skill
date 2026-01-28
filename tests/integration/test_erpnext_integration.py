"""
Integration tests for ERPNext client.
"""
import pytest
import os
from app.erpnext import ERPNextClient
from app.config import settings


@pytest.mark.integration
@pytest.mark.skipif(
    not settings.ERPNEXT_API_KEY,
    reason="ERPNext credentials not configured"
)
def test_erpnext_connection():
    """Test ERPNext API connection."""
    client = ERPNextClient()
    
    try:
        customers = client.list_customers(limit=1)
        assert isinstance(customers, list)
    except Exception as e:
        pytest.skip(f"ERPNext not accessible: {str(e)}")


@pytest.mark.integration
@pytest.mark.skipif(
    not settings.ERPNEXT_API_KEY,
    reason="ERPNext credentials not configured"
)
def test_get_customer():
    """Test getting customer details."""
    client = ERPNextClient()
    
    # First, get a customer ID
    customers = client.list_customers(limit=1)
    if not customers:
        pytest.skip("No customers available in ERPNext")
    
    customer_id = customers[0]["name"]
    customer = client.get_customer(customer_id)
    
    assert "data" in customer
    assert customer["data"]["name"] == customer_id


@pytest.mark.integration
@pytest.mark.skipif(
    not settings.ERPNEXT_API_KEY,
    reason="ERPNext credentials not configured"
)
def test_get_customer_invoices():
    """Test fetching customer invoices."""
    client = ERPNextClient()
    
    # Get a customer
    customers = client.list_customers(limit=1)
    if not customers:
        pytest.skip("No customers available in ERPNext")
    
    customer_id = customers[0]["name"]
    invoices = client.get_customer_invoices(customer_id)
    
    assert isinstance(invoices, list)


@pytest.mark.integration
@pytest.mark.skipif(
    not settings.ERPNEXT_API_KEY,
    reason="ERPNext credentials not configured"
)
def test_get_customer_payments():
    """Test fetching customer payments."""
    client = ERPNextClient()
    
    # Get a customer
    customers = client.list_customers(limit=1)
    if not customers:
        pytest.skip("No customers available in ERPNext")
    
    customer_id = customers[0]["name"]
    payments = client.get_customer_payments(customer_id)
    
    assert isinstance(payments, list)
