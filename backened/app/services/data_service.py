"""
SIH26082 Backend - Data Service
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This service handles:
1. Loading CSV data
2. Filtering by location/date
3. Creating feature vectors
4. Handling missing data
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ============================================
# DATA SERVICE
# ============================================

class DataService:
    """
    Service for data loading and preprocessing.
    
    Loads PM2.5 features CSV and provides data access.
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize data service.
        
        Args:
            data_path: Path to delhi_pm25_features.csv
        """
        self.data_path = Path(data_path)
        self.df = None
        self.locations = None
        
        self._load_data()
    
    
    def _load_data(self) -> None:
        """
        Load CSV data into memory.
        """
        logger.info(f"📂 Loading data from: {self.data_path}")
        
        try:
            if not self.data_path.exists():
                logger.warning(f"⚠️  Data file not found: {self.data_path}")
                logger.info("   Using mock data for development")
                self._create_mock_data()
                return
            
            # Load CSV
            self.df = pd.read_csv(self.data_path)
            
            # Convert datetime column
            if "datetime" in self.df.columns:
                self.df["datetime"] = pd.to_datetime(self.df["datetime"])
            
            # Sort by location and datetime
            if "location" in self.df.columns:
                self.df = self.df.sort_values(["location", "datetime"])
            
            self.locations = self.df["location"].unique().tolist() if "location" in self.df.columns else []
            
            logger.info(f"✅ Data loaded: {len(self.df)} rows, {len(self.locations)} locations")
            logger.info(f"   Columns: {', '.join(self.df.columns.tolist())}")
            logger.info(f"   Locations: {', '.join(self.locations[:3])}..." if len(self.locations) > 3 else f"   Locations: {', '.join(self.locations)}")
        
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            logger.info("   Using mock data for development")
            self._create_mock_data()
    
    
    def _create_mock_data(self) -> None:
        """
        Create mock data for development/testing.
        """
        logger.info("📊 Creating mock data for development")
        
        # Mock data structure
        dates = pd.date_range("2026-08-05", "2026-09-02", freq="1H")
        locations_list = [
            "Air Check",
            "Anand Lok",
            "Ashok Vihar, Delhi - DPCC",
            "IIT Delhi, Delhi - IITM",
            "Pusa, Delhi - DPCC"
        ]
        
        data = []
        for location in locations_list:
            for date in dates:
                data.append({
                    "datetime": date,
                    "location": location,
                    "latitude": 28.6 + (hash(location) % 100) / 1000,
                    "longitude": 77.2 + (hash(location) % 100) / 1000,
                    "pm25": 50 + (hash(date.timestamp() + hash(location)) % 150),
                    "hour": date.hour,
                    "dow": date.weekday(),
                    "hour_sin": 0.5,
                    "hour_cos": -0.866,
                    "dow_sin": 0.975,
                    "dow_cos": -0.222,
                    "pm25_lag_1h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_lag_3h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_lag_6h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_lag_12h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_lag_24h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_rolling_mean_3h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_rolling_mean_6h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_rolling_mean_24h": 50 + (hash(date.timestamp()) % 100),
                    "pm25_rolling_std_6h": 5,
                })
        
        self.df = pd.DataFrame(data)
        self.locations = self.df["location"].unique().tolist()
        
        logger.info(f"✅ Mock data created: {len(self.df)} rows, {len(self.locations)} locations")
    
    
    # ============================================
    # DATA ACCESS
    # ============================================
    
    def get_location_data(
        self,
        location: str,
        days_back: int = 7
    ) -> pd.DataFrame:
        """
        Get historical data for a location.
        
        Args:
            location: Station name
            days_back: Number of past days to return
        
        Returns:
            DataFrame with historical data
        """
        try:
            if self.df is None or len(self.df) == 0:
                logger.warning("⚠️  No data available")
                return pd.DataFrame()
            
            # Filter by location
            location_data = self.df[self.df["location"] == location].copy()
            
            if len(location_data) == 0:
                logger.warning(f"⚠️  No data for location: {location}")
                return pd.DataFrame()
            
            # Filter by date range
            if "datetime" in location_data.columns:
                cutoff_date = datetime.utcnow() - timedelta(days=days_back)
                location_data = location_data[location_data["datetime"] >= cutoff_date]
            
            logger.debug(f"📊 Loaded {len(location_data)} rows for {location}")
            return location_data
        
        except Exception as e:
            logger.error(f"❌ Error getting location data: {e}")
            return pd.DataFrame()
    
    
    def get_latest_reading(self, location: str) -> Optional[Dict]:
        """
        Get most recent data point for a location.
        
        Args:
            location: Station name
        
        Returns:
            Dict with latest reading or None
        """
        try:
            location_data = self.df[self.df["location"] == location]
            
            if len(location_data) == 0:
                logger.warning(f"⚠️  No data for location: {location}")
                return None
            
            latest = location_data.iloc[-1]
            
            return {
                "location": location,
                "timestamp": latest.get("datetime"),
                "pm25": float(latest.get("pm25", 0)),
                "latitude": float(latest.get("latitude", 0)),
                "longitude": float(latest.get("longitude", 0)),
            }
        
        except Exception as e:
            logger.error(f"❌ Error getting latest reading: {e}")
            return None
    
    
    def get_feature_vector(self, location: str) -> Optional[Dict]:
        """
        Get feature vector for ML model inference.
        
        Returns all features needed for prediction.
        
        Args:
            location: Station name
        
        Returns:
            Dict with feature values or None
        """
        try:
            location_data = self.df[self.df["location"] == location]
            
            if len(location_data) == 0:
                logger.warning(f"⚠️  No data for location: {location}")
                return None
            
            latest = location_data.iloc[-1]
            
            # Extract all feature columns
            feature_columns = [
                "latitude", "longitude", "pm25",
                "pm25_lag_1h", "pm25_lag_3h", "pm25_lag_6h", "pm25_lag_12h", "pm25_lag_24h",
                "pm25_rolling_mean_3h", "pm25_rolling_mean_6h", "pm25_rolling_mean_24h",
                "pm25_rolling_std_6h",
                "hour_sin", "hour_cos", "dow_sin", "dow_cos",
            ]
            
            features = {}
            for col in feature_columns:
                if col in latest.index:
                    features[col] = float(latest[col])
                else:
                    logger.warning(f"⚠️  Missing feature: {col}")
                    features[col] = 0.0
            
            logger.debug(f"✅ Feature vector ready for {location}")
            return features
        
        except Exception as e:
            logger.error(f"❌ Error getting feature vector: {e}")
            return None
    
    
    def get_all_locations(self) -> List[str]:
        """
        Get list of all available locations.
        
        Returns:
            List of location names
        """
        return self.locations or []
    
    
    def is_location_valid(self, location: str) -> bool:
        """
        Check if location is valid.
        
        Args:
            location: Station name
        
        Returns:
            True if location exists in data
        """
        return location in self.get_all_locations()
    
    
    def get_data_stats(self, location: str) -> Optional[Dict]:
        """
        Get statistics for a location's PM2.5 data.
        
        Args:
            location: Station name
        
        Returns:
            Dict with statistics or None
        """
        try:
            location_data = self.df[self.df["location"] == location]
            
            if len(location_data) == 0:
                return None
            
            pm25_data = location_data["pm25"].dropna()
            
            if len(pm25_data) == 0:
                return None
            
            return {
                "location": location,
                "total_records": len(location_data),
                "non_null_records": len(pm25_data),
                "min_pm25": float(pm25_data.min()),
                "max_pm25": float(pm25_data.max()),
                "mean_pm25": float(pm25_data.mean()),
                "median_pm25": float(pm25_data.median()),
                "std_pm25": float(pm25_data.std()),
            }
        
        except Exception as e:
            logger.error(f"❌ Error calculating stats: {e}")
            return None
    
    
    def get_data_info(self) -> Dict:
        """
        Get overall data information.
        
        Returns:
            Dict with data stats
        """
        if self.df is None or len(self.df) == 0:
            return {
                "status": "No data loaded",
                "total_rows": 0,
                "locations_count": 0,
                "date_range": None
            }
        
        date_range = None
        if "datetime" in self.df.columns:
            min_date = self.df["datetime"].min()
            max_date = self.df["datetime"].max()
            date_range = f"{min_date} to {max_date}"
        
        return {
            "status": "Data loaded",
            "total_rows": len(self.df),
            "locations_count": len(self.locations or []),
            "date_range": date_range,
            "columns": self.df.columns.tolist() if self.df is not None else []
        }


# ============================================
# DEPENDENCY INJECTION
# ============================================

_data_service: Optional[DataService] = None


def get_data_service(data_path: Path) -> DataService:
    """
    Get or create data service (singleton).
    
    Usage in routes:
        @app.get("/data/{location}")
        def get_data(location: str, service: DataService = Depends(get_data_service)):
            data = service.get_location_data(location)
    """
    global _data_service
    
    if _data_service is None:
        logger.info("🔧 Initializing data service...")
        _data_service = DataService(data_path)
    
    return _data_service


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    """
    Test data service by running:
        python data_service.py
    """
    print("\n" + "="*60)
    print("DATA SERVICE TEST")
    print("="*60 + "\n")
    
    service = DataService(Path("data_pipelines/delhi_pm25_features.csv"))
    
    print("📊 DATA INFO:")
    info = service.get_data_info()
    for key, val in info.items():
        print(f"   {key}: {val}")
    
    print("\n📍 AVAILABLE LOCATIONS:")
    locations = service.get_all_locations()
    for i, loc in enumerate(locations[:5], 1):
        print(f"   {i}. {loc}")
    if len(locations) > 5:
        print(f"   ... and {len(locations) - 5} more")
    
    if locations:
        location = locations[0]
        
        print(f"\n📈 DATA FOR: {location}")
        
        # Latest reading
        latest = service.get_latest_reading(location)
        if latest:
            print(f"\n   Latest Reading:")
            print(f"      PM2.5: {latest['pm25']:.1f} µg/m³")
            print(f"      Time: {latest['timestamp']}")
        
        # Feature vector
        features = service.get_feature_vector(location)
        if features:
            print(f"\n   Feature Vector (sample):")
            for key in list(features.keys())[:5]:
                print(f"      {key}: {features[key]}")
        
        # Statistics
        stats = service.get_data_stats(location)
        if stats:
            print(f"\n   Statistics:")
            print(f"      Min PM2.5: {stats['min_pm25']:.1f}")
            print(f"      Mean PM2.5: {stats['mean_pm25']:.1f}")
            print(f"      Max PM2.5: {stats['max_pm25']:.1f}")
    
    print("\n" + "="*60 + "\n")