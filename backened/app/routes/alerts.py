"""
SIH26082 Backend - Alerts Route
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

Endpoint: GET /api/v1/alerts
Purpose: Return active alerts for locations
"""

import logging
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime

from app.schemas.models import AlertResponse, Alert as AlertSchema
from app.services.alert_service import AlertService, get_alert_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["alerts"])


@router.get(
    "/alerts",
    response_model=AlertResponse,
    summary="Get active alerts",
    description="Returns all active alerts across all locations or specific location"
)
async def get_alerts(
    location: Optional[str] = Query(None, description="Filter by location"),
    alert_service: AlertService = Depends(get_alert_service)
) -> AlertResponse:
    """
    Get active (unresolved) alerts.
    
    Can filter by location or return all alerts.
    
    Args:
        location: Optional location filter
        alert_service: Alert service
    
    Returns:
        AlertResponse with list of active alerts
    
    Example Requests:
        GET /api/v1/alerts                          # All active alerts
        GET /api/v1/alerts?location=Anand%20Lok    # Alerts for specific location
    
    Example Response:
        {
            "active_alerts": [
                {
                    "alert_id": "alert-20260906-001",
                    "alert_type": "PM2.5_THRESHOLD",
                    "location": "Anand Lok",
                    "severity": "SEVERE",
                    "value": 410,
                    "threshold": 350,
                    "message": "PM2.5 alert: 410.0 µg/m³ at Anand Lok (SEVERE)",
                    "triggered_at": "2026-09-06T10:00:00Z",
                    "resolved": false
                }
            ],
            "count": 1,
            "timestamp": "2026-09-06T10:00:00Z"
        }
    """
    logger.info(f"📢 Getting alerts" + (f" for {location}" if location else ""))
    
    try:
        # Get active alerts
        active_alerts = alert_service.get_active_alerts(location=location)
        
        logger.debug(f"   Found {len(active_alerts)} active alerts")
        
        # Convert to response schema
        alerts_data = [alert.to_dict() for alert in active_alerts]
        
        response = AlertResponse(
            active_alerts=alerts_data,
            count=len(alerts_data),
            timestamp=datetime.utcnow()
        )
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Error getting alerts: {e}")
        return AlertResponse(
            active_alerts=[],
            count=0,
            timestamp=datetime.utcnow()
        )


@router.get(
    "/alerts/{alert_id}",
    summary="Get specific alert",
    description="Get details of a specific alert by ID"
)
async def get_alert(
    alert_id: str,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get details of a specific alert.
    
    Args:
        alert_id: Alert ID to retrieve
        alert_service: Alert service
    
    Returns:
        Alert details or error if not found
    
    Example:
        GET /api/v1/alerts/alert-20260906-001
    """
    try:
        if alert_id in alert_service.active_alerts:
            alert = alert_service.active_alerts[alert_id]
            return alert.to_dict()
        else:
            return {"error": f"Alert {alert_id} not found"}, 404
    
    except Exception as e:
        logger.error(f"❌ Error getting alert {alert_id}: {e}")
        return {"error": str(e)}, 500


@router.post(
    "/alerts/{alert_id}/resolve",
    summary="Resolve an alert",
    description="Mark an alert as resolved"
)
async def resolve_alert(
    alert_id: str,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Mark an alert as resolved.
    
    Args:
        alert_id: ID of alert to resolve
        alert_service: Alert service
    
    Returns:
        Success or error response
    
    Example:
        POST /api/v1/alerts/alert-20260906-001/resolve
    """
    logger.info(f"🔧 Resolving alert: {alert_id}")
    
    try:
        success = alert_service.resolve_alert(alert_id)
        
        if success:
            return {"status": "success", "message": f"Alert {alert_id} resolved"}
        else:
            return {"status": "error", "message": f"Alert {alert_id} not found"}, 404
    
    except Exception as e:
        logger.error(f"❌ Error resolving alert: {e}")
        return {"status": "error", "message": str(e)}, 500


@router.get(
    "/alerts/summary",
    summary="Alert summary",
    description="Get summary of alert counts by severity"
)
async def get_alerts_summary(
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get summary of active alerts grouped by severity.
    
    Returns:
        Dict with counts by severity level
    
    Example Response:
        {
            "total_active": 5,
            "severe": 1,
            "high": 2,
            "moderate": 2,
            "normal": 0,
            "timestamp": "2026-09-06T10:00:00Z"
        }
    """
    logger.debug("📊 Getting alert summary")
    
    try:
        summary = alert_service.get_summary()
        summary["timestamp"] = datetime.utcnow().isoformat()
        return summary
    
    except Exception as e:
        logger.error(f"❌ Error getting alert summary: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }