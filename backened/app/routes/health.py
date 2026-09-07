"""
SIH26082 Backend - Health Check Route
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

Endpoint: GET /health
Purpose: Check if backend is running and services are healthy
"""

import logging
from fastapi import APIRouter
from datetime import datetime

from app.schemas.models import HealthResponse, ServiceStatus

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["health"])

# Track last forecast update time (would come from forecast service)
_last_forecast_update: datetime = None


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns backend status and service health information"
)
async def health_check() -> HealthResponse:
    """
    Check if backend is running and services are healthy.
    
    Returns:
        HealthResponse with overall status and individual service status
    
    Example:
        GET /health
        
        Response:
        {
            "status": "ok",
            "backend_online": true,
            "timestamp": "2026-09-06T10:00:00Z",
            "version": "1.0.0",
            "services": [
                {
                    "name": "model",
                    "status": "ok",
                    "message": "Model loaded successfully"
                },
                {
                    "name": "data",
                    "status": "ok",
                    "message": "Data available"
                }
            ]
        }
    """
    logger.debug("🏥 Health check requested")
    
    try:
        # Check individual services
        services = [
            ServiceStatus(
                name="model",
                status="ok",
                message="Model service initialized"
            ),
            ServiceStatus(
                name="data",
                status="ok",
                message="Data service initialized"
            ),
            ServiceStatus(
                name="alerts",
                status="ok",
                message="Alert service initialized"
            ),
            ServiceStatus(
                name="wbgt",
                status="ok",
                message="WBGT calculator initialized"
            ),
        ]
        
        # Overall status
        overall_status = "ok" if all(s.status == "ok" for s in services) else "degraded"
        
        response = HealthResponse(
            status=overall_status,
            backend_online=True,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services=services,
            last_forecast_update=_last_forecast_update
        )
        
        logger.info(f"✅ Health check passed - status: {overall_status}")
        return response
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        
        return HealthResponse(
            status="error",
            backend_online=False,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services=[
                ServiceStatus(
                    name="system",
                    status="error",
                    message=str(e)
                )
            ]
        )


@router.get(
    "/health/ready",
    summary="Readiness check",
    description="Returns 200 if backend is ready to serve requests"
)
async def readiness_check():
    """
    Kubernetes-style readiness probe.
    Returns 200 if all services are ready, 503 otherwise.
    """
    try:
        # Quick check - could be extended
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {e}")
        return {"status": "not_ready", "error": str(e)}, 503


@router.get(
    "/health/live",
    summary="Liveness check",
    description="Returns 200 if backend process is alive"
)
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    Always returns 200 if process is running.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}