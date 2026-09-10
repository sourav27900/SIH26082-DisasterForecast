"""
SIH26082 Backend - Configuration Management
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This file loads environment variables from .env file and defines all configuration
needed by the backend. Single source of truth for all settings.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import logging

logger = logging.getLogger(__name__)


# ENVIRONMENT SETTINGS CLASS

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables (.env file)
    
    Usage:
        settings = Settings()  # Loads from .env automatically
        print(settings.app_name)
    """
    
    # APP BASIC SETTINGS
    
    app_name: str = Field(
        default="SIH26082 Backend",
        description="Application name"
    )
    
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    debug: bool = Field(
        default=True,
        description="Debug mode - enables hot reload and detailed errors"
    )
    
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    
    
    # SERVER SETTINGS
    
    host: str = Field(
        default="0.0.0.0",
        description="Server host to bind to"
    )
    
    port: int = Field(
        default=8000,
        description="Server port"
    )
    
    reload: bool = Field(
        default=True,
        description="Auto-reload on code change (dev only)"
    )
    
    
    # FILE PATHS
    
    model_path: Path = Field(
        default=Path("ml/model/xgb_model.joblib"),
        description="Path to trained XGBoost model file. ML team provides this."
    )
    
    data_path: Path = Field(
        default=Path("ml/data/delhi_pm25_features.csv"),
        description="Path to PM2.5 features CSV data"
    )
    
    feature_metadata_path: Path = Field(
        default=Path("ml/model/metadata.json"),
        description="Path to feature column names and imputation values"
    )
    
    
    # ML MODEL SETTINGS
    
    model_name: str = Field(
        default="xgboost",
        description="Name of the model to use for predictions"
    )
    
    forecast_horizon_hours: int = Field(
        default=24,
        description="Number of hours ahead to predict (1-72)"
    )
    
    model_device: str = Field(
        default="cpu",
        description="Device to run model on: 'cpu' or 'cuda'"
    )
    
    model_confidence_level: float = Field(
        default=0.95,
        description="Confidence level for uncertainty intervals (0.68, 0.95, etc.)"
    )
    
    
    # PM2.5 ALERT THRESHOLDS (µg/m³)
    
    pm25_threshold_normal: float = Field(
        default=50.0,
        description="PM2.5 normal (Good) threshold"
    )
    
    pm25_threshold_moderate: float = Field(
        default=100.0,
        description="PM2.5 moderate (Moderate) threshold"
    )
    
    pm25_threshold_high: float = Field(
        default=250.0,
        description="PM2.5 high (Poor) threshold"
    )
    
    pm25_threshold_severe: float = Field(
        default=350.0,
        description="PM2.5 severe (Very Poor) threshold"
    )
    
    
    # WBGT (Wet Bulb Globe Temperature) THRESHOLDS (°C)
    
    wbgt_threshold_normal: float = Field(
        default=28.0,
        description="WBGT normal (safe) threshold"
    )
    
    wbgt_threshold_moderate: float = Field(
        default=32.0,
        description="WBGT moderate (caution) threshold"
    )
    
    wbgt_threshold_high: float = Field(
        default=35.0,
        description="WBGT high (extreme caution) threshold"
    )
    
    wbgt_threshold_severe: float = Field(
        default=38.0,
        description="WBGT severe (heat emergency) threshold"
    )
    
    
    # DELHI NCR MONITORING STATIONS
    
    locations: list[str] = Field(
        default=[
            "Air Check",
            "Anand Lok",
            "Ashok Vihar, Delhi - DPCC",
            "CRRI Mathura Road, New Delhi - IMD",
            "Cantonment Area, Delhi - DPCC",
            "Commonwealth Sports Complex, Delhi - DPCC",
            "DTU, New Delhi - CPCB",
            "IGNOU_Maidan Garhi, Delhi - DPCC",
            "IHBAS, Dilshad Garden, New Delhi - CPCB",
            "IIT Delhi, Delhi - IITM",
            "JNU, Delhi - DPCC",
            "Knowledge Park - V, Greater Noida - UPPCB",
            "New Delhi",
            "Pusa, Delhi - DPCC",
            "Santushti Apartments, Vasant Kunj",
            "Sector - 62, Noida, UP - IMD",
            "Sector 1, Noida extension",
            "Sector-116, Noida - UPPCB",
            "Shadipur, Delhi - CPCB",
            "Sirifort, Delhi - CPCB",
            "Sonia Vihar, Delhi - DPCC",
            "Talkatora Garden, Delhi - DPCC",
            "Teri Gram, Gurugram - HSPCB",
            "Ved Vihar-Loni, Ghaziabad - UPPCB"
        ],
        description="List of monitoring station names in Delhi NCR"
    )
    
    
    # DATA PIPELINE SETTINGS
    
    data_update_interval_minutes: int = Field(
        default=15,
        description="How often to recalculate forecasts (15 min batch cycles)"
    )
    
    data_lookback_hours: int = Field(
        default=72,
        description="How many past hours of data to use as features (for lags)"
    )
    
    missing_value_strategy: str = Field(
        default="median",
        description="How to handle missing values: 'median', 'ffill', 'drop'"
    )
    
    
    # FRONTEND CORS SETTINGS
    
    frontend_origins: list[str] = Field(
        default=[
            "http://localhost",
            "http://localhost:3000",       # React dev
            "http://localhost:5173",       # Vite dev
            "http://localhost:8501",       # Streamlit
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8501",
        ],
        description="Allowed frontend origins for CORS (add production URLs here)"
    )
    
    
    # LOGGING SETTINGS
    
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    
    # API RESPONSE SETTINGS
    
    response_timeout_seconds: int = Field(
        default=30,
        description="Timeout for API requests to external services"
    )
    
    max_forecast_points: int = Field(
        default=72,
        description="Maximum forecast hours to return (safety limit)"
    )
    
    
    # PYDANTIC CONFIG
    
    class Config:
        """Pydantic configuration"""
        
        # Load from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        # Use environment variable if .env not found
        case_sensitive = False
        
        # Ignore extra fields
        extra = "ignore"


# SETTINGS SINGLETON (Lazy Loading)

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings.
    
    This uses lazy loading - only creates Settings object once,
    then reuses it for all subsequent calls.
    
    Usage in routes (dependency injection):
        @app.get("/forecast")
        def forecast(settings: Settings = Depends(get_settings)):
            print(settings.model_path)
    
    Returns:
        Settings: Configuration object with all settings
    """
    global _settings
    
    if _settings is None:
        logger.info("📋 Loading configuration from .env file...")
        _settings = Settings()
        logger.info(f"   App: {_settings.app_name}")
        logger.info(f"   Debug: {_settings.debug}")
        logger.info(f"   Environment: {_settings.environment}")
        logger.info(f"   Model: {_settings.model_path}")
        logger.info(f"   Data: {_settings.data_path}")
        logger.info("✅ Configuration loaded successfully")
    
    return _settings


# VALIDATION & CHECKS

def validate_settings() -> bool:
    """
    Validate that all required settings are valid.
    
    Returns:
        bool: True if all valid, False otherwise
    """
    settings = get_settings()
    errors = []
    
    # Check paths exist (optional - may not exist yet)
    # if not settings.model_path.exists():
    #     errors.append(f"Model path does not exist: {settings.model_path}")
    
    # Check forecast horizon is valid
    if not (1 <= settings.forecast_horizon_hours <= 72):
        errors.append("forecast_horizon_hours must be between 1 and 72")
    
    # Check thresholds are in order
    if not (settings.pm25_threshold_normal < 
            settings.pm25_threshold_moderate < 
            settings.pm25_threshold_high < 
            settings.pm25_threshold_severe):
        errors.append("PM2.5 thresholds must be in ascending order")
    
    if not (settings.wbgt_threshold_normal < 
            settings.wbgt_threshold_moderate < 
            settings.wbgt_threshold_high < 
            settings.wbgt_threshold_severe):
        errors.append("WBGT thresholds must be in ascending order")
    
    # Check confidence level
    if not (0 < settings.model_confidence_level < 1):
        errors.append("model_confidence_level must be between 0 and 1")
    
    # Log any errors
    if errors:
        logger.error("❌ Configuration validation failed:")
        for error in errors:
            logger.error(f"   - {error}")
        return False
    
    logger.info("✅ Configuration validation passed")
    return True


# HELPER FUNCTIONS

def get_risk_level_pm25(pm25_value: float, settings: Settings = None) -> str:
    """
    Classify PM2.5 value into risk level based on thresholds.
    
    Args:
        pm25_value: PM2.5 concentration in µg/m³
        settings: Settings object (uses get_settings() if None)
    
    Returns:
        str: Risk level - "NORMAL", "MODERATE", "HIGH", or "SEVERE"
    """
    if settings is None:
        settings = get_settings()
    
    if pm25_value <= settings.pm25_threshold_normal:
        return "NORMAL"
    elif pm25_value <= settings.pm25_threshold_moderate:
        return "MODERATE"
    elif pm25_value <= settings.pm25_threshold_high:
        return "HIGH"
    else:
        return "SEVERE"


def get_risk_level_wbgt(wbgt_value: float, settings: Settings = None) -> str:
    """
    Classify WBGT value into risk level based on thresholds.
    
    Args:
        wbgt_value: WBGT in °C
        settings: Settings object (uses get_settings() if None)
    
    Returns:
        str: Risk level - "NORMAL", "MODERATE", "HIGH", or "SEVERE"
    """
    if settings is None:
        settings = get_settings()
    
    if wbgt_value <= settings.wbgt_threshold_normal:
        return "NORMAL"
    elif wbgt_value <= settings.wbgt_threshold_moderate:
        return "MODERATE"
    elif wbgt_value <= settings.wbgt_threshold_high:
        return "HIGH"
    else:
        return "SEVERE"


# MODULE INITIALIZATION

if __name__ == "__main__":
    """
    Test configuration loading by running:
        python config.py
    """
    print("\n" + "="*60)
    print("CONFIGURATION TEST")
    print("="*60 + "\n")
    
    settings = get_settings()
    
    print("📋 BASIC SETTINGS:")
    print(f"   App Name: {settings.app_name}")
    print(f"   Version: {settings.app_version}")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")
    
    print("\n🔧 PATHS:")
    print(f"   Model: {settings.model_path}")
    print(f"   Data: {settings.data_path}")
    
    print("\n📊 THRESHOLDS (PM2.5):")
    print(f"   Normal: {settings.pm25_threshold_normal}")
    print(f"   Moderate: {settings.pm25_threshold_moderate}")
    print(f"   High: {settings.pm25_threshold_high}")
    print(f"   Severe: {settings.pm25_threshold_severe}")
    
    print("\n🌡️  THRESHOLDS (WBGT):")
    print(f"   Normal: {settings.wbgt_threshold_normal}")
    print(f"   Moderate: {settings.wbgt_threshold_moderate}")
    print(f"   High: {settings.wbgt_threshold_high}")
    print(f"   Severe: {settings.wbgt_threshold_severe}")
    
    print("\n📍 LOCATIONS:")
    print(f"   Total: {len(settings.locations)}")
    for i, location in enumerate(settings.locations, 1):
        print(f"   {i}. {location}")
    
    print("\n✅ Validation:")
    is_valid = validate_settings()
    print(f"   Status: {'PASS ✓' if is_valid else 'FAIL ✗'}")
    
    print("\n" + "="*60 + "\n")