"""
SIH26082 Backend - Forecast Route
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

Endpoint: POST /api/v1/forecast
Purpose: Generate PM2.5 and thermal stress forecasts
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Optional

from app.schemas.models import (
    ForecastRequest, ForecastResponse, ForecastPoint, RiskLevel
)
from app.services.model_service import XGBoostModelService, get_model_service
from app.services.wbgt_service import WBGTService, get_wbgt_service
from app.services.alert_service import AlertService, get_alert_service
from app.services.data_service import DataService, get_data_service
from config import get_settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["forecast"])


@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate 24-hour forecast",
    description="Generates PM2.5 and thermal stress forecasts for specified location"
)
async def create_forecast(
    request: ForecastRequest,
    model_service: XGBoostModelService = Depends(get_model_service),
    wbgt_service: WBGTService = Depends(get_wbgt_service),
    alert_service: AlertService = Depends(get_alert_service),
    # data_service: Optional[DataService] = None
    data_service: DataService = Depends(get_data_service)
) -> ForecastResponse:
    """
    Generate forecast for a location.
    
    Takes location and forecast horizon, returns hourly predictions for:
    - PM2.5 (air quality)
    - WBGT (thermal stress)
    - Risk levels and advisories
    
    Args:
        request: ForecastRequest with location and hours_ahead
        model_service: XGBoost model for predictions
        wbgt_service: WBGT calculator
        alert_service: Alert generator
        data_service: Data loader
    
    Returns:
        ForecastResponse with hourly forecast points
    
    Example Request:
        POST /api/v1/forecast
        {
            "location": "Anand Lok",
            "date": "2026-09-06",
            "hours_ahead": 24
        }
    
    Example Response:
        {
            "location": "Anand Lok",
            "generated_at": "2026-09-06T10:00:00Z",
            "forecast_horizon_hours": 24,
            "points": [
                {
                    "timestamp": "2026-09-06T10:00:00Z",
                    "pm25": 62.5,
                    "pm25_lower": 52.7,
                    "pm25_upper": 72.3,
                    "pm25_risk_level": "MODERATE",
                    "wbgt": 35.2,
                    "wbgt_risk_level": "HIGH",
                    "compound_risk_level": "HIGH"
                },
                ...
            ]
        }
    """
    logger.info(f"🔮 Forecast request: {request.location}, {request.hours_ahead} hours")
    
    try:
        settings = get_settings()
        
        # 1. VALIDATE REQUEST
        
        if not settings.locations or request.location not in settings.locations:
            logger.warning(f"❌ Invalid location: {request.location}")
            raise HTTPException(
                status_code=400,
                detail=f"Location '{request.location}' not found. Valid locations: {', '.join(settings.locations[:5])}..."
            )
        
        if not (1 <= request.hours_ahead <= settings.max_forecast_points):
            logger.warning(f"❌ Invalid forecast horizon: {request.hours_ahead}")
            raise HTTPException(
                status_code=400,
                detail=f"hours_ahead must be between 1 and {settings.max_forecast_points}"
            )
        
        # 2. GET LATEST DATA & FEATURES
        
        # Mock feature vector (would come from data_service)
        logger.debug(f"📊 Getting features for {request.location}")
        
        features = {
            "latitude": 28.623056,
            "longitude": 77.234167,
            "pm25": 62.5,
            "pm25_lag_1h": 56.8,
            "pm25_lag_3h": 62.7,
            "pm25_lag_6h": 33.6,
            "pm25_lag_12h": 33.7,
            "pm25_lag_24h": 33.7,
            "pm25_rolling_mean_3h": 62.7,
            "pm25_rolling_mean_6h": 62.7,
            "pm25_rolling_mean_24h": 33.95,
            "pm25_rolling_std_6h": 5.9,
            "hour_sin": 0.5,
            "hour_cos": -0.866,
            "dow_sin": 0.975,
            "dow_cos": -0.222,
        }
        
        # 3. GENERATE FORECASTS
        
        logger.debug(f"🤖 Running ML predictions...")
        
        # Get 24-hour forecast from model
        pm25_forecast = model_service.predict_24h_forecast(
            features,
            hours_ahead=request.hours_ahead
        )
        
        # 4. BUILD FORECAST POINTS
        
        logger.debug(f"🏗️  Building forecast points...")
        
        points = []
        now = datetime.utcnow()
        
        for i, pm25_pred in enumerate(pm25_forecast):
            forecast_time = now + timedelta(hours=i + 1)
            hour = forecast_time.hour
            
            # PM2.5 values
            pm25_value = pm25_pred.get("pm25", 62.5)
            pm25_lower = pm25_pred.get("pm25_lower", pm25_value - 10)
            pm25_upper = pm25_pred.get("pm25_upper", pm25_value + 10)
            
            # Classify PM2.5 risk
            if pm25_value <= settings.pm25_threshold_normal:
                pm25_risk = RiskLevel.NORMAL
            elif pm25_value <= settings.pm25_threshold_moderate:
                pm25_risk = RiskLevel.MODERATE
            elif pm25_value <= settings.pm25_threshold_high:
                pm25_risk = RiskLevel.HIGH
            else:
                pm25_risk = RiskLevel.SEVERE
            
            # Mock temperature and humidity (would come from actual data)
            temperature = 40 + (10 * (hour - 6) / 12)  # Simple diurnal pattern
            humidity = 35 - (5 * (hour - 6) / 12)      # Inverse pattern
            
            # Calculate WBGT
            wbgt_value = wbgt_service.calculate_wbgt(
                temperature=temperature,
                humidity=humidity,
                wind_speed=2.0,
                solar_radiation=500.0 if 6 <= hour <= 18 else 0.0
            )
            
            wbgt_risk = wbgt_service.classify_wbgt_risk(wbgt_value)
            
            # Compound risk (worst of both)
            compound_risk_scores = {
                "NORMAL": 1,
                "MODERATE": 2,
                "HIGH": 3,
                "SEVERE": 4
            }
            
            pm25_score = compound_risk_scores[pm25_risk.value]
            wbgt_score = compound_risk_scores[wbgt_risk.value]
            compound_score = max(pm25_score, wbgt_score)
            
            compound_risk_map = {
                1: RiskLevel.NORMAL,
                2: RiskLevel.MODERATE,
                3: RiskLevel.HIGH,
                4: RiskLevel.SEVERE
            }
            compound_risk = compound_risk_map[compound_score]
            
            # Build forecast point
            point = ForecastPoint(
                timestamp=forecast_time,
                hour=hour,
                pm25=pm25_value,
                pm25_lower=pm25_lower if request.include_uncertainty else None,
                pm25_upper=pm25_upper if request.include_uncertainty else None,
                pm25_risk_level=pm25_risk,
                wbgt=wbgt_value,
                wbgt_lower=wbgt_value - 2 if request.include_uncertainty else None,
                wbgt_upper=wbgt_value + 2 if request.include_uncertainty else None,
                wbgt_risk_level=wbgt_risk,
                compound_risk_level=compound_risk,
                temperature=temperature,
                humidity=humidity,
                wind_speed=2.0
            )
            
            points.append(point)
            
            # Check for alerts
            pm25_alert = alert_service.check_pm25_threshold(
                location=request.location,
                pm25_value=pm25_value,
                thresholds={
                    "normal": settings.pm25_threshold_normal,
                    "moderate": settings.pm25_threshold_moderate,
                    "high": settings.pm25_threshold_high,
                    "severe": settings.pm25_threshold_severe
                }
            )
            
            if pm25_alert:
                alert_service.add_alert(pm25_alert)
            
            wbgt_alert = alert_service.check_wbgt_threshold(
                location=request.location,
                wbgt_value=wbgt_value,
                thresholds={
                    "normal": settings.wbgt_threshold_normal,
                    "moderate": settings.wbgt_threshold_moderate,
                    "high": settings.wbgt_threshold_high,
                    "severe": settings.wbgt_threshold_severe
                }
            )
            
            if wbgt_alert:
                alert_service.add_alert(wbgt_alert)
        
        # 5. BUILD RESPONSE
        
        response = ForecastResponse(
            location=request.location,
            latitude=features.get("latitude"),
            longitude=features.get("longitude"),
            generated_at=now,
            forecast_horizon_hours=request.hours_ahead,
            model_name=settings.model_name,
            confidence_level=settings.model_confidence_level,
            points=points[:request.hours_ahead]
        )
        
        logger.info(f"✅ Forecast generated: {len(points)} points for {request.location}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Forecast generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating forecast: {str(e)}"
        )


@router.get(
    "/forecast/{location}",
    response_model=ForecastResponse,
    summary="Get forecast for location",
    description="Get latest forecast for a specific location"
)
async def get_forecast(
    location: str,
    hours_ahead: int = 24,
    model_service: XGBoostModelService = Depends(get_model_service),
    wbgt_service: WBGTService = Depends(get_wbgt_service),
    alert_service: AlertService = Depends(get_alert_service)
) -> ForecastResponse:
    """
    GET endpoint for forecast (alternative to POST).
    
    Args:
        location: Monitoring station name
        hours_ahead: Number of hours to forecast (default 24)
    
    Returns:
        ForecastResponse
    
    Example:
        GET /api/v1/forecast/Anand%20Lok?hours_ahead=24
    """
    request = ForecastRequest(
        location=location,
        hours_ahead=hours_ahead
    )
    
    return await create_forecast(
        request=request,
        model_service=model_service,
        wbgt_service=wbgt_service,
        alert_service=alert_service
    )