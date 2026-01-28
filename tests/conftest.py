"""
Pytest configuration and fixtures.
"""
import pytest
import os
from unittest.mock import Mock, MagicMock
from datetime import date, timedelta


# Mock Claude client BEFORE any imports
class MockClaudeClient:
    """Mock Claude AI client for testing."""
    
    class Messages:
        class Content:
            def __init__(self, text):
                self.text = text
        
        class Message:
            def __init__(self, content_text):
                self.content = [MockClaudeClient.Messages.Content(content_text)]
        
        def create(self, **kwargs):
            """Return a mock Claude response."""
            return self.Message('''{
                "payment_score": 75,
                "risk_level": "Medium",
                "key_factors": [
                    "Test factor 1",
                    "Test factor 2"
                ],
                "recommended_action": "Monitor account",
                "confidence_level": "High"
            }''')
    
    def __init__(self, api_key=None):
        self.messages = self.Messages()


def mock_get_claude_client():
    """Return mocked Claude client."""
    return MockClaudeClient()


# Patch the get_claude_client function at module level
import sys
from unittest.mock import patch

# Apply the mock globally
original_import = __builtins__.__import__

def mock_import(name, *args, **kwargs):
    module = original_import(name, *args, **kwargs)
    if name == 'app.services.claude_client':
        module.get_claude_client = mock_get_claude_client
    return module

__builtins__.__import__ = mock_import


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
