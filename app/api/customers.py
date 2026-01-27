"""
Customer API endpoints for payment scoring.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Tuple
import requests
import random
import traceback
from datetime import date, timedelta
from app.models import CustomerScore, Customer, Invoice, Payment
from app.erpnext import ERPNextClient
from app.services import ScoringService, InsightsService
from app.config import settings


router = APIRouter()

erpnext_client = ERPNextClient()
scoring_service = ScoringService()
insights_service = InsightsService()


def generate_mock_data(customer: Customer) -> Tuple[List[Invoice], List[Payment]]:
    """Generate mock invoices and payments with varied risk profiles."""
    
    # Determine risk profile based on customer name hash for consistency
    customer_hash = hash(customer.id) % 100
    
    if customer_hash < 30:  # 30% low risk
        risk_profile = "low"
        num_invoices = random.randint(5, 10)
        payment_rate = 0.95  # 95% payment rate
        avg_delay = random.randint(-5, 3)  # Early to slightly late
    elif customer_hash < 70:  # 40% medium risk
        risk_profile = "medium"
        num_invoices = random.randint(4, 8)
        payment_rate = 0.65  # 65% payment rate
        avg_delay = random.randint(0, 15)  # On time to moderately late
    else:  # 30% high risk
        risk_profile = "high"
        num_invoices = random.randint(3, 7)
        payment_rate = 0.35  # 35% payment rate
        avg_delay = random.randint(10, 45)  # Very late
    
    invoices = []
    payments = []
    today = date.today()
    
    for i in range(num_invoices):
        # Create invoices from the past 90 days
        days_ago = random.randint(15, 90)
        posting_date = today - timedelta(days=days_ago)
        due_date = posting_date + timedelta(days=30)
        
        amount = round(random.uniform(500, 5000), 2)
        invoice_id = f"MOCK-INV-{customer.id}-{i+1}"
        
        # Decide if this invoice should be paid
        should_pay = random.random() < payment_rate
        
        if should_pay:
            # Calculate payment date with typical delay for this risk profile
            payment_delay = random.randint(avg_delay - 5, avg_delay + 10)
            payment_date = due_date + timedelta(days=payment_delay)
            
            # Don't create future payments
            if payment_date <= today:
                invoice = Invoice(
                    id=invoice_id,
                    name=invoice_id,
                    customer=customer.id,
                    posting_date=posting_date,
                    due_date=due_date,
                    grand_total=amount,
                    outstanding_amount=0.0,
                    status="Paid"
                )
                
                payment = Payment(
                    id=f"MOCK-PAY-{customer.id}-{i+1}",
                    name=f"MOCK-PAY-{customer.id}-{i+1}",
                    party=customer.id,
                    posting_date=payment_date,
                    paid_amount=amount,
                    payment_type="Receive"
                )
                payments.append(payment)
            else:
                # Invoice not yet paid (future payment date)
                invoice = Invoice(
                    id=invoice_id,
                    name=invoice_id,
                    customer=customer.id,
                    posting_date=posting_date,
                    due_date=due_date,
                    grand_total=amount,
                    outstanding_amount=amount,
                    status="Overdue" if due_date < today else "Unpaid"
                )
        else:
            # Unpaid invoice
            invoice = Invoice(
                id=invoice_id,
                name=invoice_id,
                customer=customer.id,
                posting_date=posting_date,
                due_date=due_date,
                grand_total=amount,
                outstanding_amount=amount,
                status="Overdue" if due_date < today else "Unpaid"
            )
        
        invoices.append(invoice)
    
    return invoices, payments


@router.get("/customers")
async def list_customers(limit: int = Query(default=100, le=500)):
    """
    Get list of all customers.
    
    Returns list of customers from ERPNext.
    """
    try:
        customers = erpnext_client.list_customers(limit=limit)
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")


@router.get("/customers/payment-scores", response_model=List[CustomerScore])
async def get_payment_scores(limit: int = Query(default=100, le=500)):
    """
    Get payment scores for all customers.
    
    Returns list of customer payment scores sorted by risk level.
    """
    try:
        customers_data = erpnext_client.list_customers(limit=limit)
        scores = []
        
        from app.models import Customer, Invoice, Payment
        import traceback
        
        # Consider invoices from the past year
        from datetime import date
        cutoff_date = date.today() - timedelta(days=365)
        
        for customer_data in customers_data:
            try:
                customer = Customer(**customer_data)
                
                if settings.USE_MOCK_DATA:
                    invoices, payments = generate_mock_data(customer)
                else:
                    invoices_data = erpnext_client.get_customer_invoices(customer.id)
                    payments_data = erpnext_client.get_customer_payments(customer.id)
                    
                    # Filter to only recent invoices (past 30 days) and exclude canceled (docstatus=2)
                    recent_invoices_data = [
                        inv for inv in invoices_data 
                        if inv.get('posting_date') and inv.get('posting_date') >= cutoff_date.strftime("%Y-%m-%d")
                        and inv.get('docstatus') != 2  # Exclude canceled invoices
                    ]
                    
                    invoices = [Invoice(**inv) for inv in recent_invoices_data]
                    payments = [Payment(**pay) for pay in payments_data]
                
                score = scoring_service.calculate_customer_score(customer, invoices, payments)
                insights = insights_service.generate_insights(score, invoices)
                score.insights = insights
                scores.append(score)
            except Exception as e:
                # Log error for debugging but continue processing
                print(f"Error processing customer {customer_data.get('name', 'unknown')}: {str(e)}")
                print(traceback.format_exc())
                continue
        
        # Sort by score (lowest first = highest risk)
        scores.sort(key=lambda x: x.score)
        return scores
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_payment_scores: {str(e)}")
        print(error_details)
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment scores: {str(e)}")


@router.get("/customers/high-risk", response_model=List[CustomerScore])
async def get_high_risk_customers(limit: int = Query(default=100, le=500)):
    """
    Get customers with high risk (score < 50).
    
    These customers require immediate follow-up.
    """
    try:
        customers_data = erpnext_client.list_customers(limit=limit)
        high_risk_scores = []
        
        from app.models import Customer, Invoice, Payment
        
        for customer_data in customers_data:
            try:
                customer = Customer(**customer_data)
                
                if settings.USE_MOCK_DATA:
                    invoices, payments = generate_mock_data(customer)
                else:
                    invoices_data = erpnext_client.get_customer_invoices(customer.id)
                    payments_data = erpnext_client.get_customer_payments(customer.id)
                    invoices = [Invoice(**inv) for inv in invoices_data]
                    payments = [Payment(**pay) for pay in payments_data]
                
                score = scoring_service.calculate_customer_score(customer, invoices, payments)
                
                # Only include high risk customers (score < 50)
                if score.score < 50:
                    insights = insights_service.generate_insights(score, invoices)
                    score.insights = insights
                    high_risk_scores.append(score)
            except Exception as e:
                continue
        
        # Sort by score (lowest first = highest risk)
        high_risk_scores.sort(key=lambda x: x.score)
        return high_risk_scores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch high-risk customers: {str(e)}")


@router.get("/customers/followups")
async def get_customer_followups(limit: int = Query(default=100, le=500)):
    """
    Get list of customers requiring follow-up actions.
    
    Returns customers grouped by action type:
    - Immediate follow-up (score < 50)
    - Friendly reminder (50-79)
    """
    try:
        customers_data = erpnext_client.list_customers(limit=limit)
        followups = {
            "immediate_followup": [],
            "friendly_reminder": [],
            "no_action": []
        }
        
        from app.models import Customer, Invoice, Payment
        from datetime import date
        cutoff_date = date.today() - timedelta(days=120)
        
        for customer_data in customers_data:
            try:
                customer = Customer(**customer_data)
                
                if settings.USE_MOCK_DATA:
                    invoices, payments = generate_mock_data(customer)
                else:
                    invoices_data = erpnext_client.get_customer_invoices(customer.id)
                    payments_data = erpnext_client.get_customer_payments(customer.id)
                    recent_invoices_data = [
                        inv for inv in invoices_data 
                        if inv.get('posting_date') and inv.get('posting_date') >= cutoff_date.strftime("%Y-%m-%d")
                    ]
                    invoices = [Invoice(**inv) for inv in recent_invoices_data]
                    payments = [Payment(**pay) for pay in payments_data]
                
                score = scoring_service.calculate_customer_score(customer, invoices, payments)
                insights = insights_service.generate_insights(score, invoices)
                
                customer_info = {
                    "customer_id": score.customer_id,
                    "customer_name": score.customer_name,
                    "score": score.score,
                    "risk_level": score.risk_level,
                    "action": score.action,
                    "overdue_count": score.overdue_count,
                    "total_outstanding": score.total_outstanding,
                    "insights": insights
                }
                
                if score.action == "Immediate follow-up":
                    followups["immediate_followup"].append(customer_info)
                elif score.action == "Friendly reminder":
                    followups["friendly_reminder"].append(customer_info)
                else:
                    followups["no_action"].append(customer_info)
            except Exception as e:
                continue
        
        # Sort each group by score
        for key in followups:
            followups[key].sort(key=lambda x: x["score"])
        
        return followups
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch followups: {str(e)}")


@router.get("/customers/{customer_id}/score", response_model=CustomerScore)
async def get_customer_score(customer_id: str):
    """
    Calculate and return payment score for a specific customer.
    
    Args:
        customer_id: ERPNext customer ID
        
    Returns:
        CustomerScore with payment behavior analysis
    """
    try:
        # Fetch customer data
        customer_data = erpnext_client.get_customer(customer_id)
        from app.models import Customer
        customer = Customer(**customer_data.get("data", {}))
        
        # Fetch invoices and payments
        from app.models import Invoice, Payment
        from datetime import date
        if settings.USE_MOCK_DATA:
            invoices, payments = generate_mock_data(customer)
        else:
            invoices_data = erpnext_client.get_customer_invoices(customer_id)
            payments_data = erpnext_client.get_customer_payments(customer_id)
            invoices = [Invoice(**inv) for inv in invoices_data]
            payments = [Payment(**pay) for pay in payments_data]
            
            # Debug logging for leen
            if customer_id == "leen":
                today = date.today()
                due_invoices = [inv for inv in invoices if inv.due_date and inv.due_date <= today]
                paid_invoices = [inv for inv in due_invoices if inv.is_paid()]
                print(f"DEBUG leen: Total={len(invoices)}, Due={len(due_invoices)}, Paid={len(paid_invoices)}")
                if due_invoices:
                    print(f"Sample due invoice: status={due_invoices[0].status}, outstanding={due_invoices[0].outstanding_amount}")
        
        # Calculate score
        score = scoring_service.calculate_customer_score(customer, invoices, payments)
        
        # Generate insights
        insights = insights_service.generate_insights(score, invoices)
        score.insights = insights
        
        return score
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        raise HTTPException(status_code=500, detail=f"ERPNext API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate score: {str(e)}")


@router.get("/customers/{customer_id}/insights")
async def get_customer_insights(customer_id: str):
    """Get detailed payment insights for a customer."""
    try:
        # Fetch customer data
        customer_data = erpnext_client.get_customer(customer_id)
        from app.models import Customer
        customer = Customer(**customer_data.get("data", {}))
        
        # Fetch invoices
        from app.models import Invoice
        if settings.USE_MOCK_DATA:
            invoices, _ = generate_mock_data(customer)
            invoices_data = [inv.dict() for inv in invoices]
        else:
            invoices_data = erpnext_client.get_customer_invoices(customer_id)
            invoices = [Invoice(**inv) for inv in invoices_data]
        
        # Generate insights
        trend_analysis = insights_service.generate_trend_analysis(invoices)
        
        return {
            "customer_id": customer_id,
            "customer_name": customer.customer_name,
            "trend_analysis": trend_analysis,
            "total_invoices": len(invoices),
            "invoices": invoices_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")
