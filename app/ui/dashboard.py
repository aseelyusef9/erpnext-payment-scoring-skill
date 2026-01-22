"""
Dashboard UI component for Payment Scoring Skill.
Serves an ERPNext-styled interface for payment analysis.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter()

# Get the directory paths
UI_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(UI_DIR, "templates")
STATIC_DIR = os.path.join(UI_DIR, "static")


@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard page."""
    dashboard_path = os.path.join(TEMPLATE_DIR, "dashboard.html")
    
    with open(dashboard_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard_alt():
    """Alternative route for dashboard."""
    return await get_dashboard()

