"""
Unit tests for AI-powered payment risk analysis.

Tests the PaymentAIAnalyzer which uses Claude AI for scoring.
Since we can't mock Claude API in unit tests, we test:
1. Data preparation logic
2. Response parsing
3. Fallback behavior
4. Error handling
"""
import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.payment_ai_analyzer import PaymentAIAnalyzer
from app.models import Customer, Invoice, CustomerScore


@pytest.fixture
def sample_customer():
    """Create sample customer."""
    return Customer(
        id="CUST-00001",
        name="CUST-00001",
        customer_name="Test Customer Corp",
        customer_type="Company"
    )


@pytest.fixture
def high_risk_invoices():
    """Create invoices for a high-risk customer (many overdue)."""
    today = date.today()
    return [
        Invoice(
            id="INV-001",
            name="INV-001",
            customer="CUST-00001",
            posting_date=today - timedelta(days=45),
            due_date=today - timedelta(days=30),
            grand_total=5000.0,
            outstanding_amount=5000.0,
            status="Overdue"
        ),
        Invoice(
            id="INV-002",
            name="INV-002",
            customer="CUST-00001",
            posting_date=today - timedelta(days=35),
            due_date=today - timedelta(days=20),
            grand_total=3000.0,
            outstanding_amount=3000.0,
            status="Overdue"
        ),
        Invoice(
            id="INV-003",
            name="INV-003",
            customer="CUST-00001",
            posting_date=today - timedelta(days=25),
            due_date=today - timedelta(days=10),
            grand_total=2000.0,
            outstanding_amount=2000.0,
            status="Overdue"
        ),
    ]


@pytest.fixture
def low_risk_invoices():
    """Create invoices for a low-risk customer (all paid on time)."""
    today = date.today()
    return [
        Invoice(
            id="INV-001",
            name="INV-001",
            customer="CUST-00001",
            posting_date=today - timedelta(days=30),
            due_date=today - timedelta(days=20),
            grand_total=1000.0,
            outstanding_amount=0.0,
            status="Paid"
        ),
        Invoice(
            id="INV-002",
            name="INV-002",
            customer="CUST-00001",
            posting_date=today - timedelta(days=20),
            due_date=today - timedelta(days=10),
            grand_total=2000.0,
            outstanding_amount=0.0,
            status="Paid"
        ),
    ]


@pytest.fixture
def mock_claude_response_high_risk():
    """Mock Claude API response for high-risk customer."""
    return {
        "customer_name": "Test Customer Corp",
        "payment_score": 25,
        "risk_level": "High",
        "recommended_action": "Immediate follow-up",
        "insights": "Customer has significant payment issues with multiple overdue invoices."
    }


@pytest.fixture
def mock_claude_response_low_risk():
    """Mock Claude API response for low-risk customer."""
    return {
        "customer_name": "Test Customer Corp",
        "payment_score": 90,
        "risk_level": "Low",
        "recommended_action": "None",
        "insights": "Excellent payment history with all invoices paid on time."
    }


class TestPaymentAIAnalyzer:
    """Test AI-powered payment risk analyzer."""
    
    def test_data_preparation_high_risk(self, sample_customer, high_risk_invoices):
        """Test that customer data is prepared correctly for high-risk scenario."""
        analyzer = PaymentAIAnalyzer()
        data = analyzer._prepare_customer_data(sample_customer, high_risk_invoices)
        
        assert data["customer_name"] == "Test Customer Corp"
        assert data["total_invoices"] == 3
        assert data["invoices_paid_count"] == 0
        assert data["overdue_invoices"] == 3
        assert data["avg_payment_delay_days"] > 0
        assert data["payment_reliability_percent"] == 0.0
        assert data["total_outstanding_amount"] == 10000.0
    
    def test_data_preparation_low_risk(self, sample_customer, low_risk_invoices):
        """Test that customer data is prepared correctly for low-risk scenario."""
        analyzer = PaymentAIAnalyzer()
        data = analyzer._prepare_customer_data(sample_customer, low_risk_invoices)
        
        assert data["customer_name"] == "Test Customer Corp"
        assert data["total_invoices"] == 2
        assert data["invoices_paid_count"] == 2
        assert data["overdue_invoices"] == 0
        assert data["payment_reliability_percent"] == 100.0
        assert data["total_outstanding_amount"] == 0.0
    
    @patch('app.services.payment_ai_analyzer.get_claude_client')
    def test_analyze_customer_with_mock_ai(
        self, 
        mock_get_client, 
        sample_customer, 
        high_risk_invoices,
        mock_claude_response_high_risk
    ):
        """Test customer analysis with mocked Claude API."""
        # Mock Claude client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = '{"customer_name": "Test Customer Corp", "payment_score": 25, "risk_level": "High", "recommended_action": "Immediate follow-up", "insights": "Customer has significant payment issues."}'
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        analyzer = PaymentAIAnalyzer()
        score = analyzer.analyze_customer(sample_customer, high_risk_invoices)
        
        # Verify results
        assert isinstance(score, CustomerScore)
        assert score.customer_name == "Test Customer Corp"
        assert score.score == 25
        assert score.risk_level == "high"  # Normalized to lowercase
        assert score.action == "Immediate follow-up"
        assert "payment issues" in score.insights.lower()
    
    def test_fallback_on_ai_error(self, sample_customer, high_risk_invoices):
        """Test fallback behavior when AI fails."""
        # Create analyzer with invalid API key to trigger error
        with patch('app.services.payment_ai_analyzer.get_claude_client') as mock_client:
            mock_client.side_effect = ValueError("API key not found")
            
            # Should raise error during initialization
            with pytest.raises(ValueError):
                analyzer = PaymentAIAnalyzer()
    
    def test_fallback_score_structure(self, sample_customer, high_risk_invoices):
        """Test that fallback score has correct structure."""
        analyzer = PaymentAIAnalyzer()
        score = analyzer._fallback_score(
            sample_customer, 
            high_risk_invoices, 
            "Test error"
        )
        
        assert isinstance(score, CustomerScore)
        assert score.score == 50  # Default fallback score
        assert score.risk_level == "medium"
        assert score.action == "Friendly reminder"
        assert "AI analysis unavailable" in score.insights
        assert "Test error" in score.insights
    
    def test_score_response_parsing(self, sample_customer, high_risk_invoices):
        """Test building CustomerScore from AI response."""
        analyzer = PaymentAIAnalyzer()
        ai_result = {
            "customer_name": "Test Customer Corp",
            "payment_score": 35,
            "risk_level": "High",
            "recommended_action": "Immediate follow-up",
            "insights": "Test insights"
        }
        
        score = analyzer._build_customer_score(
            sample_customer,
            high_risk_invoices,
            ai_result
        )
        
        assert score.score == 35
        assert score.risk_level == "high"  # Normalized
        assert score.action == "Immediate follow-up"
        assert score.insights == "Test insights"
        assert score.total_invoices == 3
        assert score.overdue_count == 3


@pytest.mark.integration
class TestPaymentAIAnalyzerIntegration:
    """
    Integration tests that call the real Claude API.
    
    These tests are marked as 'integration' and should be:
    - Skipped in CI/CD (no API key available)
    - Run manually during development
    - Run with caution (costs money)
    
    Run with: pytest -m integration
    Skip with: pytest -m "not integration"
    """
    
    @pytest.mark.skip(reason="Requires real API key and costs money")
    def test_real_api_high_risk(self, sample_customer, high_risk_invoices):
        """Test with real Claude API for high-risk customer."""
        analyzer = PaymentAIAnalyzer()
        score = analyzer.analyze_customer(sample_customer, high_risk_invoices)
        
        # Verify AI gave appropriate risk assessment
        assert score.score < 50  # Should be high risk
        assert score.risk_level == "high"
        assert "overdue" in score.insights.lower() or "risk" in score.insights.lower()
    
    @pytest.mark.skip(reason="Requires real API key and costs money")
    def test_real_api_low_risk(self, sample_customer, low_risk_invoices):
        """Test with real Claude API for low-risk customer."""
        analyzer = PaymentAIAnalyzer()
        score = analyzer.analyze_customer(sample_customer, low_risk_invoices)
        
        # Verify AI gave appropriate risk assessment
        assert score.score > 70  # Should be low risk
        assert score.risk_level == "low"
        assert len(score.insights) > 0
