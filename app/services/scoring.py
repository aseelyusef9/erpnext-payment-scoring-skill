"""
Payment scoring service for calculating customer payment scores.
"""
from typing import List
from app.models import Customer, Invoice, Payment, CustomerScore
from app.config import settings


class ScoringService:
    """Service for calculating customer payment behavior scores."""
    
    def calculate_customer_score(
        self,
        customer: Customer,
        invoices: List[Invoice],
        payments: List[Payment]
    ) -> CustomerScore:
        """Calculate payment score using business rules."""
        if len(invoices) < settings.MIN_TRANSACTIONS_FOR_SCORING:
            return self._default_score(customer, invoices)
        
        avg_delay = self._calculate_avg_payment_delay(invoices)
        reliability = self._calculate_payment_reliability(invoices)
        overdue_ratio = self._calculate_overdue_ratio(invoices)
        score = self._calculate_final_score(reliability, avg_delay, overdue_ratio, invoices)
        risk_level = self._determine_risk_level(score)
        action = self._determine_action(score)
        
        total_invoices = len(invoices)
        total_paid = sum(1 for inv in invoices if inv.is_paid())
        total_outstanding = sum(inv.outstanding_amount for inv in invoices)
        overdue_count = sum(1 for inv in invoices if inv.calculate_days_overdue() > 0 and not inv.is_paid())
        
        return CustomerScore(
            customer_id=customer.id,
            customer_name=customer.customer_name,
            score=round(score, 2),
            risk_level=risk_level,
            action=action,
            avg_payment_delay=round(avg_delay, 2),
            payment_reliability=round(reliability, 2),
            total_invoices=total_invoices,
            total_paid=total_paid,
            total_outstanding=round(total_outstanding, 2),
            overdue_count=overdue_count
        )
    
    def _calculate_avg_payment_delay(self, invoices: List[Invoice]) -> float:
        if not invoices:
            return 0.0
        total_delay = sum(inv.calculate_days_overdue() for inv in invoices)
        return total_delay / len(invoices)
    
    def _calculate_payment_reliability(self, invoices: List[Invoice]) -> float:
        if not invoices:
            return 0.0
        on_time = sum(1 for inv in invoices if inv.is_paid() and inv.calculate_days_overdue() <= 0)
        return (on_time / len(invoices)) * 100
    
    def _calculate_overdue_ratio(self, invoices: List[Invoice]) -> float:
        if not invoices:
            return 0.0
        overdue = sum(1 for inv in invoices if inv.calculate_days_overdue() > 0 and not inv.is_paid())
        return overdue / len(invoices)
    
    def _calculate_final_score(self, reliability: float, avg_delay: float, overdue_ratio: float, invoices: List[Invoice]) -> float:
        """
        Calculate final score using business rule:
        Score = 100 - (Overdue_Invoices × 10) - (Average_Delay_Days × 1)
        """
        overdue_count = sum(1 for inv in invoices if inv.calculate_days_overdue() > 0 and not inv.is_paid())
        total_delay = sum(inv.calculate_days_overdue() for inv in invoices)
        avg_delay_days = total_delay / len(invoices) if invoices else 0
        
        score = 100 - (overdue_count * 10) - (avg_delay_days * 1)
        return max(0, min(100, score))
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on score."""
        if score >= 80:
            return "low"
        elif score >= 50:
            return "medium"
        else:
            return "high"
    
    def _determine_action(self, score: float) -> str:
        """Determine recommended action based on score."""
        if score >= 80:
            return "None"
        elif score >= 50:
            return "Friendly reminder"
        else:
            return "Immediate follow-up"
    
    def _default_score(self, customer: Customer, invoices: List[Invoice]) -> CustomerScore:
        """Return default score for customers with insufficient transactions."""
        return CustomerScore(
            customer_id=customer.id,
            customer_name=customer.customer_name,
            score=50.0,
            risk_level="medium",
            action="Friendly reminder",
            avg_payment_delay=0.0,
            payment_reliability=0.0,
            total_invoices=len(invoices),
            total_paid=0,
            total_outstanding=sum(inv.outstanding_amount for inv in invoices),
            overdue_count=0,
            insights="Insufficient transaction history"
        )
