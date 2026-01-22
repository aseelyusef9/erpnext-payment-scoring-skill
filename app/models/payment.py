"""
Payment data models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class Payment(BaseModel):
    """Payment model representing an ERPNext Payment Entry."""
    
    id: str = Field(..., alias="name")
    party: Optional[str] = Field(default=None, description="Customer ID")
    posting_date: date
    paid_amount: float = Field(default=0.0, ge=0)
    payment_type: str = "Receive"
    reference_no: Optional[str] = None
    mode_of_payment: Optional[str] = None
    reference_date: Optional[date] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "PAY-00001",
                "party": "CUST-00001",
                "posting_date": "2026-01-15",
                "paid_amount": 10000.00,
                "payment_type": "Receive",
                "reference_no": "CHQ123456",
                "mode_of_payment": "Bank Transfer"
            }
        }
