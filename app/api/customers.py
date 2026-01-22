"""
Customer API endpoints for payment scoring.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models import CustomerScore
from app.erpnext import ERPNextClient
from app.services import ScoringService, InsightsService

router = APIRouter()

erpnext_client = ERPNextClient()
scoring_service = ScoringService()
insights_service = InsightsService()


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
        
        for customer_data in customers_data:
            try:
                customer = Customer(**customer_data)
                invoices_data = erpnext_client.get_customer_invoices(customer.id)
                payments_data = erpnext_client.get_customer_payments(customer.id)
                
                invoices = [Invoice(**inv) for inv in invoices_data]
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
        
        for customer_data in customers_data:
            try:
                customer = Customer(**customer_data)
                invoices_data = erpnext_client.get_customer_invoices(customer.id)
                payments_data = erpnext_client.get_customer_payments(customer.id)
                
                invoices = [Invoice(**inv) for inv in invoices_data]
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
        invoices_data = erpnext_client.get_customer_invoices(customer_id)
        payments_data = erpnext_client.get_customer_payments(customer_id)
        
        # Convert to model objects
        from app.models import Invoice, Payment
        invoices = [Invoice(**inv) for inv in invoices_data]
        payments = [Payment(**pay) for pay in payments_data]
        
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
        invoices_data = erpnext_client.get_customer_invoices(customer_id)
        from app.models import Invoice
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
