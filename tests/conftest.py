"""
Pytest configuration and fixtures.
"""
import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import date, timedelta


# Mock Claude client globally before any imports
@pytest.fixture(scope="session", autouse=True)
def mock_claude_client():
    """Mock Claude client for all tests."""
    
    class MockContent:
        def __init__(self, text):
            self.text = text
    
    class MockMessage:
        def __init__(self):
            self.content = [MockContent('''{
                "payment_score": 75,
                "risk_level": "Medium",
                "key_factors": ["Factor 1", "Factor 2"],
                "recommended_action": "Monitor account",
                "confidence_level": "High"
            }''')]
    
    class MockMessages:
        def create(self, **kwargs):
            return MockMessage()
    
    class MockClaudeClient:
        def __init__(self, api_key=None):
            self.messages = MockMessages()
    
    with patch('app.services.claude_client.get_claude_client', return_value=MockClaudeClient()):
        yield


# Mock ERPNext client ONLY for unit and API tests (NOT integration tests)
@pytest.fixture(scope="function", autouse=True)
def mock_erpnext_for_unit_tests(request):
    """Mock ERPNext client for non-integration tests only."""
    
    # Skip mocking if this is an integration test
    if "integration" in request.keywords:
        yield
        return
    
    # Also check file path as fallback
    test_file = str(request.fspath)
    if "integration" in test_file:
        yield
        return
    
    class MockERPNextClient:
        def __init__(self):
            pass
        
        def list_customers(self, limit=None):
            """Return mock customer list."""
            return [
                {
                    "name": "CUST-00001",
                    "customer_name": "Test Customer Corp",
                    "customer_type": "Company",
                    "territory": "United States"
                },
                {
                    "name": "CUST-00002",
                    "customer_name": "Another Corp",
                    "customer_type": "Company",
                    "territory": "Canada"
                }
            ]
        
        def get_customer(self, customer_id):
            """Return mock customer data."""
            return {
                "data": {
                    "name": customer_id,
                    "customer_name": f"Customer {customer_id}",
                    "customer_type": "Company",
                    "territory": "United States"
                }
            }
        
        def get_customer_invoices(self, customer_id):
            """Return mock invoices."""
            today = date.today()
            return [
                {
                    "name": "INV-001",
                    "customer": customer_id,
                    "posting_date": str(today - timedelta(days=60)),
                    "due_date": str(today - timedelta(days=30)),
                    "grand_total": 5000.00,
                    "outstanding_amount": 2000.00,
                    "status": "Overdue"
                },
                {
                    "name": "INV-002",
                    "customer": customer_id,
                    "posting_date": str(today - timedelta(days=30)),
                    "due_date": str(today),
                    "grand_total": 3000.00,
                    "outstanding_amount": 0.00,
                    "status": "Paid",
                    "payment_date": str(today - timedelta(days=2))
                }
            ]
        
        def get_customer_payments(self, customer_id):
            """Return mock payments."""
            today = date.today()
            return [
                {
                    "name": "PAY-001",
                    "party": customer_id,
                    "posting_date": str(today - timedelta(days=2)),
                    "paid_amount": 3000.00,
                    "references": [{"allocated_amount": 3000.00}]
                }
            ]
    
    # Apply mock only for non-integration tests
    with patch('app.erpnext.client.ERPNextClient', MockERPNextClient):
        yield


@pytest.fixture
def sample_customer():
    """Create a sample customer for testing."""
    from app.models import Customer
    return Customer(
        id="CUST-00001",
        customer_name="Test Customer Corp",
        customer_type="Company",
        territory="United States"
    )


@pytest.fixture
def high_risk_invoices():
    """Create sample invoices for high-risk customer."""
    from app.models import Invoice
    today = date.today()
    
    return [
        Invoice(
            id="INV-001",
            customer_id="CUST-00001",
            posting_date=today - timedelta(days=90),
            due_date=today - timedelta(days=30),
            grand_total=5000.00,
            outstanding_amount=5000.00,
            status="Overdue"
        ),
        Invoice(
            id="INV-002",
            customer_id="CUST-00001",
            posting_date=today - timedelta(days=60),
            due_date=today - timedelta(days=20),
            grand_total=3000.00,
            outstanding_amount=3000.00,
            status="Overdue"
        ),
        Invoice(
            id="INV-003",
            customer_id="CUST-00001",
            posting_date=today - timedelta(days=40),
            due_date=today - timedelta(days=10),
            grand_total=2000.00,
            outstanding_amount=2000.00,
            status="Overdue"
        )
    ]


@pytest.fixture
def low_risk_invoices():
    """Create sample invoices for low-risk customer."""
    from app.models import Invoice
    today = date.today()
    
    return [
        Invoice(
            id="INV-004",
            customer_id="CUST-00002",
            posting_date=today - timedelta(days=60),
            due_date=today - timedelta(days=30),
            grand_total=4000.00,
            outstanding_amount=0.00,
            status="Paid",
            payment_date=today - timedelta(days=28)
        ),
        Invoice(
            id="INV-005",
            customer_id="CUST-00002",
            posting_date=today - timedelta(days=30),
            due_date=today,
            grand_total=3000.00,
            outstanding_amount=0.00,
            status="Paid",
            payment_date=today - timedelta(days=2)
        )
    ]
