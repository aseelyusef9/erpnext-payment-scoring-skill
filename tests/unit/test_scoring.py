"""
Unit tests for the scoring service.
"""
import pytest
from datetime import date, timedelta
from app.services import ScoringService
from app.models import Customer, Invoice, Payment


@pytest.fixture
def scoring_service():
    """Create scoring service instance."""
    return ScoringService()


@pytest.fixture
def sample_customer():
    """Create sample customer."""
    return Customer(
        name="CUST-00001",
        customer_name="Test Customer",
        customer_type="Company"
    )


@pytest.fixture
def sample_invoices():
    """Create sample invoices."""
    today = date.today()
    return [
        Invoice(
            name="INV-001",
            customer="CUST-00001",
            posting_date=today - timedelta(days=30),
            due_date=today - timedelta(days=20),
            grand_total=1000.0,
            outstanding_amount=0.0,
            status="Paid",
            payment_date=today - timedelta(days=18)
        ),
        Invoice(
            name="INV-002",
            customer="CUST-00001",
            posting_date=today - timedelta(days=20),
            due_date=today - timedelta(days=10),
            grand_total=2000.0,
            outstanding_amount=0.0,
            status="Paid",
            payment_date=today - timedelta(days=9)
        ),
        Invoice(
            name="INV-003",
            customer="CUST-00001",
            posting_date=today - timedelta(days=10),
            due_date=today,
            grand_total=1500.0,
            outstanding_amount=0.0,
            status="Paid",
            payment_date=today - timedelta(days=1)
        )
    ]


def test_calculate_customer_score(scoring_service, sample_customer, sample_invoices):
    """Test customer score calculation."""
    score = scoring_service.calculate_customer_score(
        customer=sample_customer,
        invoices=sample_invoices,
        payments=[]
    )
    
    assert score.customer_id == "CUST-00001"
    assert 0 <= score.score <= 100
    assert score.risk_level in ["low", "medium", "high"]
    assert score.total_invoices == 3


def test_payment_reliability_calculation(scoring_service, sample_invoices):
    """Test payment reliability calculation."""
    reliability = scoring_service._calculate_payment_reliability(sample_invoices)
    assert 0 <= reliability <= 100


def test_avg_payment_delay_calculation(scoring_service, sample_invoices):
    """Test average payment delay calculation."""
    avg_delay = scoring_service._calculate_avg_payment_delay(sample_invoices)
    assert avg_delay >= 0


def test_risk_level_determination(scoring_service):
    """Test risk level determination."""
    assert scoring_service._determine_risk_level(85) == "low"
    assert scoring_service._determine_risk_level(55) == "medium"
    assert scoring_service._determine_risk_level(30) == "high"


def test_insufficient_data_scoring(scoring_service, sample_customer):
    """Test scoring with insufficient data."""
    score = scoring_service.calculate_customer_score(
        customer=sample_customer,
        invoices=[],
        payments=[]
    )
    
    assert score.score == 50.0
    assert score.risk_level == "medium"
    assert "Insufficient transaction history" in score.insights
