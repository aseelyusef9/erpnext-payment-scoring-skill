"""
AI-powered payment risk analyzer using Claude AI.
Replaces formula-based scoring with intelligent reasoning.
"""
import json
import os
from typing import List
from app.services.claude_client import get_claude_client
from app.models import Customer, Invoice, CustomerScore


MODEL_NAME = "claude-sonnet-4-20250514"


class PaymentAIAnalyzer:
    """AI-driven payment risk analysis using Claude."""
    
    def __init__(self):
        """Initialize the AI analyzer."""
        self.client = get_claude_client()
        self.model = MODEL_NAME
        
        # Load analysis prompt from file
        prompt_file = os.path.join(
            os.path.dirname(__file__), 
            "analysis_prompt"
        )
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.base_prompt = f.read()
    
    def analyze_customer(
        self,
        customer: Customer,
        invoices: List[Invoice]
    ) -> CustomerScore:
        """
        Analyze customer payment behavior using Claude AI.
        
        Args:
            customer: Customer object
            invoices: List of customer invoices
            
        Returns:
            CustomerScore with AI-generated insights
        """
        # Prepare aggregated data for Claude
        customer_data = self._prepare_customer_data(customer, invoices)
        
        try:
            # Get AI analysis
            ai_result = self._call_claude_api(customer_data)
            
            # Convert AI result to CustomerScore
            return self._build_customer_score(customer, invoices, ai_result)
            
        except Exception as e:
            # Fallback to safe default if AI fails
            return self._fallback_score(customer, invoices, str(e))
    
    def _prepare_customer_data(
        self, 
        customer: Customer, 
        invoices: List[Invoice]
    ) -> dict:
        """Prepare aggregated customer data for AI analysis."""
        total_invoices = len(invoices)
        invoices_paid = sum(1 for inv in invoices if inv.is_paid())
        overdue_invoices = sum(
            1 for inv in invoices 
            if inv.calculate_days_overdue() > 0 and not inv.is_paid()
        )
        
        # Calculate average payment delay
        if invoices:
            total_delay = sum(inv.calculate_days_overdue() for inv in invoices)
            avg_delay = total_delay / total_invoices
        else:
            avg_delay = 0.0
        
        # Calculate payment reliability
        payment_reliability = (
            (invoices_paid / total_invoices * 100) if total_invoices > 0 else 0.0
        )
        
        # Calculate outstanding amount
        total_outstanding = sum(inv.outstanding_amount for inv in invoices)
        
        return {
            "customer_name": customer.customer_name,
            "total_invoices": total_invoices,
            "invoices_paid_count": invoices_paid,
            "overdue_invoices": overdue_invoices,
            "avg_payment_delay_days": round(avg_delay, 2),
            "payment_reliability_percent": round(payment_reliability, 2),
            "total_outstanding_amount": round(total_outstanding, 2)
        }
    
    def _call_claude_api(self, customer_data: dict) -> dict:
        """Call Claude API with customer data."""
        prompt = f"""{self.base_prompt}

━━━━━━━━━━━━━━━━━━
CUSTOMER DATA
━━━━━━━━━━━━━━━━━━
{json.dumps(customer_data, indent=2)}

━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (JSON ONLY)
━━━━━━━━━━━━━━━━━━
{{
  "customer_name": "<string>",
  "payment_score": <integer 0-100>,
  "risk_level": "Low | Medium | High",
  "recommended_action": "None | Friendly reminder | Immediate follow-up",
  "insights": "<2-3 sentence business explanation>"
}}

⚠️ RETURN JSON ONLY. NO MARKDOWN. NO EXTRA TEXT.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.2,  # Low temperature for consistent results
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_text = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()
        
        return json.loads(raw_text)
    
    def _build_customer_score(
        self,
        customer: Customer,
        invoices: List[Invoice],
        ai_result: dict
    ) -> CustomerScore:
        """Build CustomerScore from AI result."""
        total_invoices = len(invoices)
        total_paid = sum(1 for inv in invoices if inv.is_paid())
        total_outstanding = sum(inv.outstanding_amount for inv in invoices)
        overdue_count = sum(
            1 for inv in invoices 
            if inv.calculate_days_overdue() > 0 and not inv.is_paid()
        )
        
        # Calculate metrics for display
        if invoices:
            total_delay = sum(inv.calculate_days_overdue() for inv in invoices)
            avg_delay = total_delay / total_invoices
            reliability = (total_paid / total_invoices) * 100
        else:
            avg_delay = 0.0
            reliability = 0.0
        
        # Get score from AI
        score = ai_result.get("payment_score", 50)
        
        # Override risk level based on score thresholds (75+: low, 40-74: medium, 0-39: high)
        if score >= 75:
            risk_level = "low"
            action = "None"
        elif score >= 40:
            risk_level = "medium"
            action = "Friendly reminder"
        else:
            risk_level = "high"
            action = "Immediate follow-up"
        
        return CustomerScore(
            customer_id=customer.id,
            customer_name=customer.customer_name,
            score=score,
            risk_level=risk_level,
            action=action,
            avg_payment_delay=round(avg_delay, 2),
            payment_reliability=round(reliability, 2),
            total_invoices=total_invoices,
            total_paid=total_paid,
            total_outstanding=round(total_outstanding, 2),
            overdue_count=overdue_count,
            insights=ai_result.get("insights", "AI analysis completed.")
        )
    
    def _fallback_score(
        self,
        customer: Customer,
        invoices: List[Invoice],
        error_msg: str
    ) -> CustomerScore:
        """Fallback score when AI analysis fails."""
        total_invoices = len(invoices)
        total_paid = sum(1 for inv in invoices if inv.is_paid())
        total_outstanding = sum(inv.outstanding_amount for inv in invoices)
        overdue_count = sum(
            1 for inv in invoices 
            if inv.calculate_days_overdue() > 0 and not inv.is_paid()
        )
        
        return CustomerScore(
            customer_id=customer.id,
            customer_name=customer.customer_name,
            score=50,
            risk_level="medium",
            action="Friendly reminder",
            avg_payment_delay=0.0,
            payment_reliability=0.0,
            total_invoices=total_invoices,
            total_paid=total_paid,
            total_outstanding=round(total_outstanding, 2),
            overdue_count=overdue_count,
            insights=f"AI analysis unavailable. Using fallback assessment. Error: {error_msg}"
        )
