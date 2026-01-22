"""
Insights generation service for payment behavior analysis.
"""
from typing import List
from app.models import CustomerScore, Invoice


class InsightsService:
    """Service for generating insights about customer payment behavior."""
    
    def generate_insights(
        self,
        score: CustomerScore,
        invoices: List[Invoice]
    ) -> str:
        """
        Generate human-readable insights about customer payment behavior.
        
        Args:
            score: Customer payment score
            invoices: List of customer invoices
            
        Returns:
            String with generated insights
        """
        insights = []
        
        # Risk level insight
        if score.risk_level == "low":
            insights.append(f"✓ {score.customer_name} is a low-risk customer with excellent payment behavior.")
        elif score.risk_level == "medium":
            insights.append(f"⚠ {score.customer_name} shows moderate risk. Monitor payment patterns closely.")
        else:
            insights.append(f"⚠ {score.customer_name} is high-risk. Consider credit limits or payment terms.")
        
        # Payment reliability
        if score.payment_reliability >= 90:
            insights.append(f"✓ Highly reliable with {score.payment_reliability:.1f}% on-time payment rate.")
        elif score.payment_reliability >= 70:
            insights.append(f"→ Moderate reliability at {score.payment_reliability:.1f}% on-time payments.")
        else:
            insights.append(f"✗ Low reliability with only {score.payment_reliability:.1f}% payments on time.")
        
        # Payment delay
        if score.avg_payment_delay == 0:
            insights.append("✓ Always pays on or before due date.")
        elif score.avg_payment_delay < 7:
            insights.append(f"→ Typically pays within {score.avg_payment_delay:.1f} days of due date.")
        else:
            insights.append(f"⚠ Average delay of {score.avg_payment_delay:.1f} days indicates payment challenges.")
        
        # Outstanding amounts
        if score.total_outstanding > 0:
            insights.append(f"→ Current outstanding balance: ${score.total_outstanding:,.2f}")
        
        # Transaction volume
        insights.append(f"→ Transaction history: {score.total_paid}/{score.total_invoices} invoices paid.")
        
        # Recommendations
        if score.score >= 80:
            insights.append("✓ Recommended: Consider extended payment terms or credit increase.")
        elif score.score <= 40:
            insights.append("⚠ Recommended: Require advance payment or reduce credit limits.")
        
        return " ".join(insights)
    
    def generate_trend_analysis(self, recent_invoices: List[Invoice]) -> str:
        """Generate trend analysis from recent invoice data."""
        if not recent_invoices:
            return "No recent transaction data available."
        
        # Sort by date
        sorted_invoices = sorted(recent_invoices, key=lambda x: x.posting_date)
        
        # Analyze recent vs older behavior
        mid_point = len(sorted_invoices) // 2
        recent = sorted_invoices[mid_point:]
        older = sorted_invoices[:mid_point]
        
        recent_delays = sum(inv.calculate_days_overdue() for inv in recent) / len(recent)
        older_delays = sum(inv.calculate_days_overdue() for inv in older) / len(older) if older else recent_delays
        
        if recent_delays < older_delays * 0.8:
            return "📈 Trend: Payment behavior is improving over time."
        elif recent_delays > older_delays * 1.2:
            return "📉 Trend: Payment delays are increasing. Early intervention recommended."
        else:
            return "→ Trend: Payment behavior remains stable."
