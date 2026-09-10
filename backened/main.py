"""
SIH26082 Backend - Main Entry Point
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This file creates and configures the FastAPI application instance.
All routes are registered here.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
from config import get_settings

# Import route modules (these will be created in routes/ folder)
# Uncomment as each route file is created
from app.routes import health , forecast , alerts, data

# STARTUP & SHUTDOWN EVENTS

async def lifespan(app: FastAPI):
    """
    Manage app lifecycle:
    - Startup: Load model, data, initialize services
    - Shutdown: Clean up resources
    """
    # STARTUP
    logger.info("🚀 Backend starting up...")
    logger.info("📊 Loading configuration...")
    settings = get_settings()
    logger.info(f"   App: {settings.app_name}")
    logger.info(f"   Debug: {settings.debug}")
    logger.info(f"   Model path: {settings.model_path}")
    logger.info(f"   Data path: {settings.data_path}")
    
    logger.info("✅ Backend startup complete")
    
    yield  # App is now running
    
    # SHUTDOWN
    logger.info("🛑 Backend shutting down...")
    logger.info("✅ Cleanup complete")


# CREATE FASTAPI APP

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Real-time forecasting system for air pollution and thermal stress in Delhi NCR",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json",  # OpenAPI schema
    lifespan=lifespan
)


# MIDDLEWARE SETUP

# CORS - Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://localhost:8501",      # Streamlit
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all headers
)


# ROUTE REGISTRATION

"""
Register route routers here as they're created.
Uncomment each one after the corresponding route file is created.

Structure:
- routes/health.py  → Health check endpoints
- routes/forecast.py → Forecast prediction endpoints  
- routes/alerts.py  → Alert endpoints
- routes/data.py    → Historical data endpoints
"""

# TODO: Uncomment these once route files are created
app.include_router(health.router, tags=["health"])
app.include_router(forecast.router, tags=["forecast"])
app.include_router(alerts.router, tags=["alerts"])
app.include_router(data.router, tags=["data"])


# FALLBACK ROOT ENDPOINT

@app.get("/")
async def root():
    """
    Root endpoint - returns API info
    Use this to verify backend is running
    """
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "forecast": "/api/v1/forecast",
            "alerts": "/api/v1/alerts",
            "data": "/api/v1/data/{location}"
        }
    }


# ERROR HANDLERS (Optional, add as needed)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch any unhandled exceptions and return error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An error occurred"
    }


# RUN (for development)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )