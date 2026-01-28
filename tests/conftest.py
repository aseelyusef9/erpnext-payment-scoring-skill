"""
Pytest configuration and fixtures.
"""
import pytest
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
