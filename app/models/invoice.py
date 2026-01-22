"""
Invoice data models.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class Invoice(BaseModel):
    """Invoice model representing an ERPNext Sales Invoice."""
    
    id: str = Field(..., alias="name")
    customer: str = ""
    posting_date: date
    due_date: Optional[date] = None
    grand_total: float = Field(default=0.0, ge=0)
    outstanding_amount: float = Field(default=0.0, ge=0)
    status: str = "Draft"
    payment_date: Optional[date] = None
    days_overdue: Optional[int] = None
    
    class Config:
        populate_by_name = True
    
    def calculate_days_overdue(self, current_date: Optional[date] = None) -> int:
        """Calculate days overdue for this invoice."""
        if not self.due_date or self.status == "Paid":
            return 0
        
        reference_date = self.payment_date or current_date or date.today()
        if reference_date > self.due_date:
            return (reference_date - self.due_date).days
        return 0
    
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.status == "Paid" or self.outstanding_amount == 0
