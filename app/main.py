"""
Main application entry point for the Payment Scoring Skill service.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api import customers, health
import os

app = FastAPI(
    title="ERPNext Payment Scoring Skill",
    description="AI-powered payment behavior analysis for ERPNext",
    version="1.0.0"
)

# Mount static files for UI
STATIC_DIR = os.path.join(os.path.dirname(__file__), "ui", "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(customers.router, prefix="/api/v1", tags=["customers"])


@app.get("/")
async def root():
    return {
        "message": "ERPNext Payment Scoring Skill API",
        "version": "1.0.0",
        "endpoints": {
            "api_docs": "/docs",
            "dashboard": "/dashboard",
            "health": "/health"
        }
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the payment scoring dashboard."""
    template_path = os.path.join(os.path.dirname(__file__), "ui", "templates", "dashboard.html")
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, media_type="text/html")
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
