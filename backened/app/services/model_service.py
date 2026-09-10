"""
SIH26082 Backend - Model Service
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This service handles:
1. Loading trained ML model
2. Feature preprocessing
3. Making predictions
4. Uncertainty quantification

THIS IS WHERE ML TEAM PLUGS IN THE REAL MODEL
"""

import logging
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ============================================
# ABSTRACT BASE CLASS - Extensible for multiple models
# ============================================

class BasePredictorService(ABC):
    """
    Abstract base class for prediction services.
    Allows swapping different models (XGBoost, LSTM, etc.)
    """
    
    @abstractmethod
    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """Make prediction from features"""
        pass
    
    @abstractmethod
    def predict_multiple(self, features_list: List[Dict]) -> List[Dict]:
        """Make predictions for multiple samples"""
        pass


# ============================================
# XGBOOST MODEL SERVICE
# ============================================

class XGBoostModelService(BasePredictorService):
    """
    Service for XGBoost model inference.
    
    Handles:
    - Loading .joblib model file
    - Feature preprocessing
    - Predictions with uncertainty estimation
    
    ML TEAM: Replace placeholder with real model loading logic
    """
    
    def __init__(self, model_path: Path, feature_metadata_path: Optional[Path] = None):
        """
        Initialize model service.
        
        Args:
            model_path: Path to trained model (xgb_model.joblib)
            feature_metadata_path: Path to feature metadata JSON
        """
        self.model_path = Path(model_path)
        self.feature_metadata_path = Path(feature_metadata_path) if feature_metadata_path else None
        
        self.model = None
        self.feature_columns = None
        self.imputation_values = None
        self.model_metrics = None
        
        self._load_model()
        self._load_metadata()
    
    
    def _load_model(self) -> None:
        """
        Load trained XGBoost model from disk.
        
        ML TEAM: This is where your model.joblib gets loaded
        """
        logger.info(f"📦 Loading model from: {self.model_path}")
        
        try:
            if self.model_path.exists():
                # Load actual model
                self.model = joblib.load(self.model_path)
                logger.info("✅ Model loaded successfully")
                logger.info(f"   Model type: {type(self.model).__name__}")
            else:
                logger.warning(f"⚠️  Model file not found at {self.model_path}")
                logger.warning("   Using MOCK predictions for development")
                self.model = None
        
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            logger.warning("   Using MOCK predictions for development")
            self.model = None
    
    
    def _load_metadata(self) -> None:
        """
        Load feature metadata (column names, imputation values, etc.)
        
        Expected JSON structure:
        {
            "feature_columns": ["pm25", "temp", "humidity", ...],
            "imputation_medians": {"pm25_lag_1h": 33.5, ...},
            "model_metrics": {"r2": 0.778, "mae": 5.32, ...}
        }
        """
        if not self.feature_metadata_path or not self.feature_metadata_path.exists():
            logger.warning("⚠️  Feature metadata file not found")
            logger.info("   Using default feature columns")
            
            # Default columns (from training notebook)
            self.feature_columns = [
                "latitude", "longitude", "pm25",
                "pm25_lag_1h", "pm25_lag_3h", "pm25_lag_6h", "pm25_lag_12h", "pm25_lag_24h",
                "pm25_rolling_mean_3h", "pm25_rolling_mean_6h", "pm25_rolling_mean_24h",
                "pm25_rolling_std_6h",
                "hour_sin", "hour_cos", "dow_sin", "dow_cos",
                # + location one-hot encoded columns
            ]
            
            # Default imputation values
            self.imputation_values = {
                "pm25_lag_1h": 33.5,
                "pm25_lag_3h": 33.5,
                "pm25_lag_6h": 33.6,
                "pm25_lag_12h": 33.7,
                "pm25_lag_24h": 33.7,
            }
            
            return
        
        try:
            with open(self.feature_metadata_path, 'r') as f:
                metadata = json.load(f)
            
            self.feature_columns = metadata.get("feature_columns", [])
            self.imputation_values = metadata.get("imputation_medians", {})
            self.model_metrics = metadata.get("model_metrics", {})
            
            logger.info(f"✅ Metadata loaded: {len(self.feature_columns)} features")
            logger.info(f"   R²: {self.model_metrics.get('r2', 'N/A')}")
            logger.info(f"   MAE: {self.model_metrics.get('mae', 'N/A')}")
            logger.info(f"   RMSE: {self.model_metrics.get('rmse', 'N/A')}")
        
        except Exception as e:
            logger.error(f"❌ Error loading metadata: {e}")
            logger.warning("   Using default metadata")
    
    
    def preprocess_features(self, features: Dict[str, float]) -> np.ndarray:
        """
        Preprocess raw features into model input format.
        
        Handles:
        - Missing values (imputation)
        - Feature ordering
        - Type conversion
        
        Args:
            features: Dict with feature values
        
        Returns:
            numpy array ready for model.predict()
        """
        # Start with all expected columns
        feature_array = []
        
        for col in self.feature_columns:
            if col in features:
                value = features[col]
            elif col in self.imputation_values:
                # Use median imputation
                value = self.imputation_values[col]
            else:
                # Default to 0 (or could raise error)
                logger.warning(f"⚠️  Missing feature: {col}, using 0")
                value = 0.0
            
            feature_array.append(float(value))
        
        return np.array([feature_array])  # 2D array: (1, n_features)
    
    
    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Make single prediction.
        
        Args:
            features: Dict with feature values
                Example: {
                    "latitude": 28.623,
                    "longitude": 77.234,
                    "pm25": 62.5,
                    "pm25_lag_1h": 56.8,
                    ...
                }
        
        Returns:
            Dict with prediction and uncertainty:
            {
                "pm25": 62.5,
                "pm25_lower": 52.7,
                "pm25_upper": 72.3,
                "confidence": 0.95
            }
        """
        try:
            # Preprocess features
            X = self.preprocess_features(features)
            
            if self.model is None:
                # MOCK PREDICTION (for development)
                logger.debug("📊 Using mock prediction (model not loaded)")
                current_pm25 = features.get("pm25", 62.5)
                return {
                    "pm25": current_pm25,
                    "pm25_lower": current_pm25 - 9.8,  # Mock RMSE
                    "pm25_upper": current_pm25 + 9.8,
                    "confidence": 0.95,
                    "is_mock": True
                }
            
            else:
                # REAL PREDICTION
                logger.debug("🎯 Making real prediction with XGBoost model")
                prediction = self.model.predict(X)[0]
                
                # Get uncertainty (RMSE from metadata or estimate)
                rmse = self.model_metrics.get("rmse", 9.8) if self.model_metrics else 9.8
                
                return {
                    "pm25": float(prediction),
                    "pm25_lower": float(prediction - 1.96 * rmse),  # 95% CI
                    "pm25_upper": float(prediction + 1.96 * rmse),
                    "confidence": 0.95,
                    "is_mock": False
                }
        
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            logger.info("   Returning mock prediction")
            
            current_pm25 = features.get("pm25", 62.5)
            return {
                "pm25": current_pm25,
                "pm25_lower": current_pm25 - 10,
                "pm25_upper": current_pm25 + 10,
                "confidence": 0.95,
                "is_mock": True,
                "error": str(e)
            }
    
    
    def predict_multiple(self, features_list: List[Dict]) -> List[Dict]:
        """
        Make predictions for multiple samples.
        
        Args:
            features_list: List of feature dicts
        
        Returns:
            List of prediction dicts
        """
        logger.debug(f"📊 Making {len(features_list)} predictions")
        
        try:
            # Preprocess all features
            X = np.vstack([
                self.preprocess_features(f) for f in features_list
            ])
            
            if self.model is None:
                # Mock predictions
                return [
                    {
                        "pm25": f.get("pm25", 62.5),
                        "pm25_lower": f.get("pm25", 62.5) - 9.8,
                        "pm25_upper": f.get("pm25", 62.5) + 9.8,
                        "confidence": 0.95,
                        "is_mock": True
                    }
                    for f in features_list
                ]
            
            else:
                # Real predictions
                predictions = self.model.predict(X)
                rmse = self.model_metrics.get("rmse", 9.8) if self.model_metrics else 9.8
                
                return [
                    {
                        "pm25": float(pred),
                        "pm25_lower": float(pred - 1.96 * rmse),
                        "pm25_upper": float(pred + 1.96 * rmse),
                        "confidence": 0.95,
                        "is_mock": False
                    }
                    for pred in predictions
                ]
        
        except Exception as e:
            logger.error(f"❌ Batch prediction error: {e}")
            return [
                {
                    "pm25": f.get("pm25", 62.5),
                    "pm25_lower": f.get("pm25", 62.5) - 10,
                    "pm25_upper": f.get("pm25", 62.5) + 10,
                    "confidence": 0.95,
                    "is_mock": True,
                    "error": str(e)
                }
                for f in features_list
            ]
    
    
    def predict_24h_forecast(self, current_features: Dict, hours_ahead: int = 24) -> List[Dict]:
        """
        Generate 24-hour forecast by iterative prediction.
        
        For each future hour:
        1. Use current + past features
        2. Get prediction
        3. Use prediction as next hour's feature
        4. Repeat
        
        ML TEAM: This is iterative forecasting - will be called by route handlers
        
        Args:
            current_features: Current hour's features
            hours_ahead: How many hours to forecast (1-72)
        
        Returns:
            List of hourly forecasts
        """
        logger.debug(f"🔮 Generating {hours_ahead}-hour forecast")
        
        forecasts = []
        features_copy = current_features.copy()
        
        for hour in range(hours_ahead):
            try:
                # Predict next hour
                pred = self.predict(features_copy)
                
                # Store forecast
                forecast_point = {
                    "hour_offset": hour + 1,
                    "pm25": pred["pm25"],
                    "pm25_lower": pred["pm25_lower"],
                    "pm25_upper": pred["pm25_upper"],
                    "confidence": pred["confidence"],
                }
                forecasts.append(forecast_point)
                
                # Update features for next iteration
                # Shift lags and update with new prediction
                if "pm25_lag_24h" in features_copy:
                    features_copy["pm25_lag_24h"] = features_copy["pm25_lag_12h"]
                if "pm25_lag_12h" in features_copy:
                    features_copy["pm25_lag_12h"] = features_copy["pm25_lag_6h"]
                if "pm25_lag_6h" in features_copy:
                    features_copy["pm25_lag_6h"] = features_copy["pm25_lag_3h"]
                if "pm25_lag_3h" in features_copy:
                    features_copy["pm25_lag_3h"] = features_copy["pm25_lag_1h"]
                if "pm25_lag_1h" in features_copy:
                    features_copy["pm25_lag_1h"] = pred["pm25"]
                
                # Update rolling means
                if "pm25_rolling_mean_24h" in features_copy:
                    features_copy["pm25_rolling_mean_24h"] = np.mean([
                        features_copy.get("pm25", pred["pm25"]),
                        features_copy.get("pm25_lag_1h", pred["pm25"]),
                    ])
                
                # Update current PM2.5
                features_copy["pm25"] = pred["pm25"]
            
            except Exception as e:
                logger.error(f"❌ Forecast step {hour + 1} failed: {e}")
                forecasts.append({
                    "hour_offset": hour + 1,
                    "error": str(e)
                })
        
        return forecasts
    
    
    def get_model_info(self) -> Dict:
        """
        Get metadata about the loaded model.
        """
        return {
            "model_type": type(self.model).__name__ if self.model else "MOCK",
            "model_path": str(self.model_path),
            "feature_count": len(self.feature_columns) if self.feature_columns else 0,
            "metrics": self.model_metrics or {},
            "loaded": self.model is not None,
            "metadata_file": str(self.feature_metadata_path) if self.feature_metadata_path else None
        }


# ============================================
# DEPENDENCY INJECTION - For FastAPI
# ============================================

_model_service: Optional[XGBoostModelService] = None


def get_model_service() -> XGBoostModelService:
    """
    Get or create model service (singleton pattern).
    
    Usage in routes:
        @app.post("/forecast")
        def forecast(service: XGBoostModelService = Depends(get_model_service)):
            pred = service.predict(features)
    """
    global _model_service
    
    if _model_service is None:
        logger.info("🔧 Initializing model service...")
        from config import get_settings
        settings = get_settings()
                
        _model_service = XGBoostModelService(
            model_path=settings.model_path,
            feature_metadata_path=settings.feature_metadata_path
        )

        # _model_service = XGBoostModelService(model_path, metadata_path)
        _model_service = XGBoostModelService(
                model_path=settings.model_path,
                feature_metadata_path=settings.feature_metadata_path
            )
    
    return _model_service


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    """
    Test model service by running:
        python model_service.py
    """
    print("\n" + "="*60)
    print("MODEL SERVICE TEST")
    print("="*60 + "\n")
    
    # Initialize service with mock model
    service = XGBoostModelService(
        model_path=Path("ml/artifacts/xgb_model.joblib"),
        feature_metadata_path=Path("ml/artifacts/feature_metadata.json")
    )
    
    print("📊 MODEL INFO:")
    info = service.get_model_info()
    for key, val in info.items():
        print(f"   {key}: {val}")
    
    # Test prediction
    print("\n🎯 SINGLE PREDICTION TEST:")
    test_features = {
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
    
    pred = service.predict(test_features)
    print(f"   Prediction: {pred['pm25']:.1f} µg/m³")
    print(f"   Confidence: {pred['pm25_lower']:.1f} - {pred['pm25_upper']:.1f}")
    print(f"   Is Mock: {pred.get('is_mock', False)}")
    
    # Test 24h forecast
    print("\n🔮 24-HOUR FORECAST TEST:")
    forecast = service.predict_24h_forecast(test_features, hours_ahead=5)
    for point in forecast:
        if "error" not in point:
            print(f"   Hour +{point['hour_offset']}: {point['pm25']:.1f} µg/m³")
    
    print("\n" + "="*60 + "\n")