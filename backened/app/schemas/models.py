"""
SIH26082 Backend - API Schemas
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This file defines all Pydantic models for request/response validation.
These schemas define the API contract between frontend and backend.

Pydantic automatically:
- Validates input data (rejects invalid requests)
- Generates OpenAPI/Swagger documentation
- Serializes responses to JSON
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ============================================
# ENUMS - Allowed values
# ============================================

class RiskLevel(str, Enum):
    """Risk level classification"""
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class PollutantType(str, Enum):
    """Pollutant types"""
    PM25 = "PM2.5"
    PM10 = "PM10"
    NO2 = "NO2"
    SO2 = "SO2"
    O3 = "O3"
    CO = "CO"


class AlertType(str, Enum):
    """Alert types"""
    PM25_THRESHOLD = "PM2.5_THRESHOLD"
    WBGT_THRESHOLD = "WBGT_THRESHOLD"
    COMPOUND_RISK = "COMPOUND_RISK"
    DATA_MISSING = "DATA_MISSING"


# ============================================
# REQUEST SCHEMAS - What frontend sends
# ============================================

class ForecastRequest(BaseModel):
    """
    Request body for POST /api/v1/forecast
    
    Frontend sends this to request predictions.
    
    Example:
        {
            "location": "Anand Lok",
            "date": "2026-09-06",
            "hours_ahead": 24
        }
    """
    
    location: str = Field(
        ...,
        description="Name of monitoring station (must be in configured locations)",
        example="Anand Lok"
    )
    
    date: Optional[str] = Field(
        default=None,
        description="Date for forecast (YYYY-MM-DD). If None, uses today.",
        example="2026-09-06"
    )
    
    hours_ahead: int = Field(
        default=24,
        ge=1,
        le=72,
        description="Number of hours to forecast (1-72)",
        example=24
    )
    
    include_uncertainty: bool = Field(
        default=True,
        description="Include confidence intervals in response"
    )
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v: str) -> str:
        """Validate location is non-empty"""
        if not v or len(v.strip()) == 0:
            raise ValueError("location cannot be empty")
        return v.strip()


class DataRequest(BaseModel):
    """
    Query parameters for GET /api/v1/data/{location}
    """
    
    location: str = Field(
        ...,
        description="Monitoring station name"
    )
    
    days_back: int = Field(
        default=7,
        ge=1,
        le=365,
        description="Number of past days of data to return"
    )
    
    resolution: str = Field(
        default="hourly",
        description="Data resolution: 'hourly', 'daily', 'weekly'"
    )


# ============================================
# RESPONSE SCHEMAS - What backend returns
# ============================================

class ForecastPoint(BaseModel):
    """
    Single forecast prediction point (one hour/timeframe)
    
    This is returned as part of ForecastResponse.
    Each point represents one hour's forecast.
    """
    
    timestamp: datetime = Field(
        ...,
        description="Prediction timestamp (ISO 8601)",
        example="2026-09-06T10:00:00Z"
    )
    
    hour: int = Field(
        ...,
        description="Hour of day (0-23)",
        example=10
    )
    
    # PM2.5 Predictions
    pm25: float = Field(
        ...,
        description="Predicted PM2.5 concentration (µg/m³)",
        example=62.5
    )
    
    pm25_lower: Optional[float] = Field(
        default=None,
        description="PM2.5 lower confidence bound (µg/m³)",
        example=52.7
    )
    
    pm25_upper: Optional[float] = Field(
        default=None,
        description="PM2.5 upper confidence bound (µg/m³)",
        example=72.3
    )
    
    pm25_risk_level: RiskLevel = Field(
        default=RiskLevel.NORMAL,
        description="PM2.5 risk classification"
    )
    
    # WBGT (Wet Bulb Globe Temperature)
    wbgt: Optional[float] = Field(
        default=None,
        description="Wet Bulb Globe Temperature (°C) - calculated from temp+humidity",
        example=35.2
    )
    
    wbgt_lower: Optional[float] = Field(
        default=None,
        description="WBGT lower confidence bound (°C)"
    )
    
    wbgt_upper: Optional[float] = Field(
        default=None,
        description="WBGT upper confidence bound (°C)"
    )
    
    wbgt_risk_level: RiskLevel = Field(
        default=RiskLevel.NORMAL,
        description="WBGT risk classification"
    )
    
    # Compound Risk
    compound_risk_level: RiskLevel = Field(
        default=RiskLevel.NORMAL,
        description="Combined PM2.5 + WBGT risk level (worst of the two)"
    )
    
    # Weather data (if available)
    temperature: Optional[float] = Field(
        default=None,
        description="Ambient temperature (°C)",
        example=40.5
    )
    
    humidity: Optional[float] = Field(
        default=None,
        description="Relative humidity (%)",
        example=35
    )
    
    wind_speed: Optional[float] = Field(
        default=None,
        description="Wind speed (km/h)",
        example=8.5
    )


class ForecastResponse(BaseModel):
    """
    Response body for POST /api/v1/forecast
    
    Contains complete forecast for next N hours.
    
    Example:
        {
            "location": "Anand Lok",
            "latitude": 28.623056,
            "longitude": 77.234167,
            "generated_at": "2026-09-06T10:00:00Z",
            "forecast_horizon_hours": 24,
            "points": [
                {
                    "timestamp": "2026-09-06T10:00:00Z",
                    "pm25": 62.5,
                    "pm25_lower": 52.7,
                    "pm25_upper": 72.3,
                    "wbgt": 35.2,
                    "compound_risk_level": "MODERATE"
                },
                ...
            ]
        }
    """
    
    location: str = Field(
        ...,
        description="Monitoring station name"
    )
    
    latitude: Optional[float] = Field(
        default=None,
        description="Station latitude"
    )
    
    longitude: Optional[float] = Field(
        default=None,
        description="Station longitude"
    )
    
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this forecast was generated (ISO 8601)"
    )
    
    forecast_horizon_hours: int = Field(
        ...,
        description="Number of hours forecasted"
    )
    
    model_name: str = Field(
        default="xgboost",
        description="Name of ML model used for prediction"
    )
    
    confidence_level: float = Field(
        default=0.95,
        description="Confidence level for uncertainty intervals (0.0-1.0)"
    )
    
    points: List[ForecastPoint] = Field(
        default=[],
        description="Array of hourly forecast points"
    )

    

    model_config = ConfigDict(
    json_schema_extra={
        "example": {
            "location": "Anand Lok",
            "generated_at": "2026-09-06T10:00:00Z",
            "forecast_horizon_hours": 24,
            "points": []
        }
    }
    )
    
 
    


class HistoricalDataPoint(BaseModel):
    """
    Single historical data point
    """
    
    timestamp: datetime = Field(..., description="Data timestamp")
    pm25: float = Field(..., description="PM2.5 value (µg/m³)")
    temperature: Optional[float] = Field(default=None)
    humidity: Optional[float] = Field(default=None)


class DataResponse(BaseModel):
    """
    Response body for GET /api/v1/data/{location}
    
    Returns historical data for a location.
    """
    
    location: str = Field(..., description="Monitoring station name")
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    data_points: List[HistoricalDataPoint] = Field(
        default=[],
        description="Array of historical data points"
    )
    count: int = Field(default=0, description="Number of data points")
    time_range_start: Optional[datetime] = Field(default=None)
    time_range_end: Optional[datetime] = Field(default=None)


# ============================================
# ALERT SCHEMAS
# ============================================

class Alert(BaseModel):
    """
    Single alert object
    """
    
    alert_id: str = Field(
        ...,
        description="Unique alert identifier",
        example="alert-20260906-001"
    )
    
    alert_type: AlertType = Field(
        ...,
        description="Type of alert"
    )
    
    location: str = Field(
        ...,
        description="Affected monitoring station"
    )
    
    severity: RiskLevel = Field(
        ...,
        description="Alert severity level"
    )
    
    value: float = Field(
        ...,
        description="The value that triggered the alert"
    )
    
    threshold: float = Field(
        ...,
        description="The threshold that was crossed"
    )
    
    message: str = Field(
        ...,
        description="Human-readable alert message"
    )
    
    triggered_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the alert was triggered"
    )
    
    resolved: bool = Field(
        default=False,
        description="Whether the alert has been resolved"
    )


class AlertResponse(BaseModel):
    """
    Response body for GET /api/v1/alerts
    
    Returns list of active alerts.
    
    Example:
        {
            "active_alerts": [
                {
                    "alert_id": "alert-001",
                    "alert_type": "PM2.5_THRESHOLD",
                    "location": "Anand Lok",
                    "severity": "SEVERE",
                    "value": 410,
                    "threshold": 350,
                    "message": "Severe air quality alert for Anand Lok"
                }
            ],
            "count": 1,
            "timestamp": "2026-09-06T10:00:00Z"
        }
    """
    
    active_alerts: List[Alert] = Field(
        default=[],
        description="List of currently active alerts"
    )
    
    count: int = Field(
        default=0,
        description="Number of active alerts"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this alert list was generated"
    )


# ============================================
# HEALTH CHECK SCHEMAS
# ============================================

class ServiceStatus(BaseModel):
    """
    Status of a backend service
    """
    
    name: str = Field(..., description="Service name")
    status: str = Field(..., description="Status: 'ok' or 'error'")
    message: Optional[str] = Field(default=None, description="Status message")
    last_check: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """
    Response body for GET /health
    
    Returns overall backend health status.
    
    Example:
        {
            "status": "ok",
            "backend_online": true,
            "timestamp": "2026-09-06T10:00:00Z",
            "services": [
                {
                    "name": "model",
                    "status": "ok",
                    "message": "Model loaded successfully"
                },
                {
                    "name": "data",
                    "status": "ok",
                    "message": "Data pipeline operational"
                }
            ]
        }
    """
    
    status: str = Field(
        default="ok",
        description="Overall status: 'ok' or 'error'"
    )
    
    backend_online: bool = Field(
        default=True,
        description="Is backend running?"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    
    version: str = Field(
        default="1.0.0",
        description="API version"
    )
    
    services: List[ServiceStatus] = Field(
        default=[],
        description="Status of individual services"
    )
    
    last_forecast_update: Optional[datetime] = Field(
        default=None,
        description="When forecasts were last calculated"
    )


# ============================================
# ERROR SCHEMAS
# ============================================

class ErrorDetail(BaseModel):
    """
    Detailed error information
    """
    
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """
    Validation error response
    """
    
    error: str = Field(default="validation_error")
    message: str = Field(default="Request validation failed")
    fields: dict = Field(default={}, description="Field-specific errors")


# ============================================
# UTILITY MODELS
# ============================================

class LocationInfo(BaseModel):
    """
    Information about a monitoring station
    """
    
    name: str = Field(..., description="Station name")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    region: Optional[str] = Field(default=None, description="Administrative region")
    authority: Optional[str] = Field(default=None, description="Operating authority")


class RiskAdvice(BaseModel):
    """
    Health advice for a risk level
    """
    
    risk_level: RiskLevel = Field(...)
    advice: str = Field(...)
    icon: str = Field(...)  # Emoji or icon name
    color: str = Field()  # Hex color for UI


# ============================================
# PAGINATION (for future use)
# ============================================

class PaginatedResponse(BaseModel):
    """
    Base model for paginated responses
    """
    
    total: int = Field(..., description="Total items")
    limit: int = Field(default=50, description="Items per page")
    offset: int = Field(default=0, description="Offset for pagination")
    has_more: bool = Field(default=False, description="Are there more results?")


# ============================================
# MODEL CONFIGURATION
# ============================================

# Configure JSON schema for all models
# BaseModel.model_config = {
#     "json_schema_extra": {
#         "examples": {}
#     }
# }