"""
Unit tests for AI-powered payment risk analysis.

Tests the PaymentAIAnalyzer which uses Claude AI for scoring.
Since we can't mock Claude API in unit tests, we test:
1. Data preparation logic
2. Response parsing
3. Fallback behavior
4. Error handling
"""
import unittest
import sys
from pathlib import Path

# Add project root to path when running as standalone script
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

from datetime import date, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.payment_ai_analyzer import PaymentAIAnalyzer
from app.models import Customer, Invoice, CustomerScore


class TestPaymentAIAnalyzer(unittest.TestCase):
    """Test AI-powered payment risk analyzer."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Sample customer
        self.sample_customer = Customer(
            id="CUST-00001",
            name="CUST-00001",
            customer_name="Test Customer Corp",
            customer_type="Company"
        )
        
        # High risk invoices (many overdue)
        today = date.today()
        self.high_risk_invoices = [
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
        
        # Low risk invoices (all paid on time)
        self.low_risk_invoices = [
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
    
    def test_data_preparation_high_risk(self):
        """Test that customer data is prepared correctly for high-risk scenario."""
        analyzer = PaymentAIAnalyzer()
        data = analyzer._prepare_customer_data(self.sample_customer, self.high_risk_invoices)
        
        self.assertEqual(data["customer_name"], "Test Customer Corp")
        self.assertEqual(data["total_invoices"], 3)
        self.assertEqual(data["invoices_paid_count"], 0)
        self.assertEqual(data["overdue_invoices"], 3)
        self.assertGreater(data["avg_payment_delay_days"], 0)
        self.assertEqual(data["payment_reliability_percent"], 0.0)
        self.assertEqual(data["total_outstanding_amount"], 10000.0)
    
    def test_data_preparation_low_risk(self):
        """Test that customer data is prepared correctly for low-risk scenario."""
        analyzer = PaymentAIAnalyzer()
        data = analyzer._prepare_customer_data(self.sample_customer, self.low_risk_invoices)
        
        self.assertEqual(data["customer_name"], "Test Customer Corp")
        self.assertEqual(data["total_invoices"], 2)
        self.assertEqual(data["invoices_paid_count"], 2)
        self.assertEqual(data["overdue_invoices"], 0)
        self.assertEqual(data["payment_reliability_percent"], 100.0)
        self.assertEqual(data["total_outstanding_amount"], 0.0)
    
    @patch('app.services.payment_ai_analyzer.get_claude_client')
    def test_analyze_customer_with_mock_ai(self, mock_get_client):
        """Test customer analysis with mocked Claude API."""
        # Mock Claude client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = '{"customer_name": "Test Customer Corp", "payment_score": 25, "risk_level": "High", "recommended_action": "Immediate follow-up", "insights": "Customer has significant payment issues."}'
        mock_client.messages.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        analyzer = PaymentAIAnalyzer()
        score = analyzer.analyze_customer(self.sample_customer, self.high_risk_invoices)
        
        # Verify results
        self.assertIsInstance(score, CustomerScore)
        self.assertEqual(score.customer_name, "Test Customer Corp")
        self.assertEqual(score.score, 25)
        self.assertEqual(score.risk_level, "high")  # Normalized to lowercase
        self.assertEqual(score.action, "Immediate follow-up")
        self.assertIn("payment issues", score.insights.lower())
    
    def test_fallback_on_ai_error(self):
        """Test fallback behavior when AI fails."""
        # Create analyzer with invalid API key to trigger error
        with patch('app.services.payment_ai_analyzer.get_claude_client') as mock_client:
            mock_client.side_effect = ValueError("API key not found")
            
            # Should raise error during initialization
            with self.assertRaises(ValueError):
                analyzer = PaymentAIAnalyzer()
    
    def test_fallback_score_structure(self):
        """Test that fallback score has correct structure."""
        analyzer = PaymentAIAnalyzer()
        score = analyzer._fallback_score(
            self.sample_customer, 
            self.high_risk_invoices, 
            "Test error"
        )
        
        self.assertIsInstance(score, CustomerScore)
        self.assertIsInstance(score.score, (int, float))  # Score is computed from invoices
        self.assertIn(score.risk_level, ["low", "medium", "high"])
        self.assertIsNotNone(score.action)
        self.assertIn("AI analysis unavailable", score.insights)
        self.assertIn("Test error", score.insights)
    
    def test_score_response_parsing(self):
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
            self.sample_customer,
            self.high_risk_invoices,
            ai_result
        )
        
        self.assertEqual(score.score, 35)
        self.assertEqual(score.risk_level, "high")  # Normalized
        self.assertEqual(score.action, "Immediate follow-up")
        self.assertEqual(score.insights, "Test insights")
        self.assertEqual(score.total_invoices, 3)
        self.assertEqual(score.overdue_count, 3)


@unittest.skip("Integration tests - require real API key and costs money")
class TestPaymentAIAnalyzerIntegration(unittest.TestCase):
    """
    Integration tests that call the real Claude API.
    
    These tests are skipped by default because they:
    - Require real API keys
    - Cost money to run
    - Should be run manually during development
    
    To run: Remove the @unittest.skip decorator
    """
    
    def setUp(self):
        """Set up test fixtures before each test."""
        today = date.today()
        
        self.sample_customer = Customer(
            id="CUST-00001",
            name="CUST-00001",
            customer_name="Test Customer Corp",
            customer_type="Company"
        )
        
        self.high_risk_invoices = [
            Invoice(
                id="INV-001",
                name="INV-001",
                customer="CUST-00001",
                posting_date=today - timedelta(days=45),
                due_date=today - timedelta(days=30),
                grand_total=5000.0,
                outstanding_amount=5000.0,
                status="Overdue"
            )
        ]
        
        self.low_risk_invoices = [
            Invoice(
                id="INV-001",
                name="INV-001",
                customer="CUST-00001",
                posting_date=today - timedelta(days=30),
                due_date=today - timedelta(days=20),
                grand_total=1000.0,
                outstanding_amount=0.0,
                status="Paid"
            )
        ]
    
    def test_real_api_high_risk(self):
        """Test with real Claude API for high-risk customer."""
        analyzer = PaymentAIAnalyzer()
        score = analyzer.analyze_customer(self.sample_customer, self.high_risk_invoices)
        
        # Verify AI gave appropriate risk assessment
        self.assertLess(score.score, 50)  # Should be high risk
        self.assertEqual(score.risk_level, "high")
        self.assertTrue(
            "overdue" in score.insights.lower() or "risk" in score.insights.lower()
        )
    
    def test_real_api_low_risk(self):
        """Test with real Claude API for low-risk customer."""
        analyzer = PaymentAIAnalyzer()
        score = analyzer.analyze_customer(self.sample_customer, self.low_risk_invoices)
        
        # Verify AI gave appropriate risk assessment
        self.assertGreater(score.score, 70)  # Should be low risk
        self.assertEqual(score.risk_level, "low")
        self.assertGreater(len(score.insights), 0)


if __name__ == '__main__':
    unittest.main()
