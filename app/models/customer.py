"""
Customer data models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Customer(BaseModel):
    """Customer model representing an ERPNext customer."""
    
    id: str = Field(..., alias="name")
    customer_name: str
    customer_type: Optional[str] = None
    territory: Optional[str] = None
    customer_group: Optional[str] = None
    
    class Config:
        populate_by_name = True


class CustomerScore(BaseModel):
    """Customer payment score and risk assessment."""
    
    customer_id: str
    customer_name: str
    score: float = Field(..., ge=0, le=100, description="Payment score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high")
    action: str = Field(..., description="Recommended action: None, Friendly reminder, Immediate follow-up")
    avg_payment_delay: float = Field(..., description="Average payment delay in days")
    payment_reliability: float = Field(..., ge=0, le=100, description="Reliability percentage")
    total_invoices: int
    total_paid: int
    total_outstanding: float
    overdue_count: int = Field(default=0, description="Number of currently overdue invoices")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    insights: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-00001",
                "customer_name": "ABC Corporation",
                "score": 85.5,
                "risk_level": "low",
                "action": "None",
                "avg_payment_delay": 5.2,
                "payment_reliability": 95.0,
                "total_invoices": 50,
                "total_paid": 48,
                "total_outstanding": 15000.00,
                "insights": "Consistently pays on time with minimal delays"
            }
        }
