"""
Health check API endpoints.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.config import settings
from app.erpnext import ERPNextClient

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


@router.get("/health/erpnext")
async def erpnext_health_check():
    """Check ERPNext connectivity."""
    try:
        client = ERPNextClient()
        # Try to make a simple API call
        client.list_customers(limit=1)
        
        return {
            "status": "connected",
            "erpnext_url": settings.ERPNEXT_URL,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"ERPNext connection failed: {str(e)}"
        )
