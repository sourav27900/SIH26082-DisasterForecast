"""
SIH26082 Backend - Data Route
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

Endpoint: GET /api/v1/data/{location}
Purpose: Return historical PM2.5 data for locations
"""

import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from datetime import datetime

from app.schemas.models import DataResponse, HistoricalDataPoint
from app.services.data_service import DataService, get_data_service
from config import get_settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["data"])


@router.get(
    "/data/{location}",
    response_model=DataResponse,
    summary="Get historical data",
    description="Returns historical PM2.5 data for a location"
)
async def get_location_data(
    location: str,
    days_back: int = Query(7, ge=1, le=365, description="Number of past days to return"),
    resolution: str = Query("hourly", description="Data resolution: 'hourly', 'daily'"),
    data_service: Optional[DataService] = None
) -> DataResponse:
    """
    Get historical PM2.5 data for a location.
    
    Args:
        location: Monitoring station name
        days_back: Number of past days (default 7)
        resolution: Data resolution (default 'hourly')
        data_service: Data service
    
    Returns:
        DataResponse with historical data points
    
    Example Requests:
        GET /api/v1/data/Anand%20Lok
        GET /api/v1/data/Anand%20Lok?days_back=30
        GET /api/v1/data/Anand%20Lok?days_back=7&resolution=daily
    
    Example Response:
        {
            "location": "Anand Lok",
            "latitude": 28.623056,
            "longitude": 77.234167,
            "data_points": [
                {
                    "timestamp": "2026-08-30T00:00:00Z",
                    "pm25": 62.5,
                    "temperature": 38.5,
                    "humidity": 45.0
                },
                ...
            ],
            "count": 168,
            "time_range_start": "2026-08-30T00:00:00Z",
            "time_range_end": "2026-09-06T10:00:00Z"
        }
    """
    logger.info(f"📊 Data request: {location}, {days_back} days, resolution={resolution}")
    
    try:
        settings = get_settings()
        
        # 1. VALIDATE LOCATION
        
        if location not in settings.locations:
            logger.warning(f"❌ Invalid location: {location}")
            raise HTTPException(
                status_code=400,
                detail=f"Location '{location}' not found"
            )
        
        # 2. MOCK DATA (would use data_service in production)
        
        logger.debug(f"📂 Loading data for {location}")
        
        # Generate mock historical data
        data_points = []
        from datetime import timedelta
        
        for i in range(days_back * 24):  # Hourly data
            timestamp = datetime.utcnow() - timedelta(hours=i)
            
            # Simple pattern
            pm25 = 50 + (30 * ((timestamp.hour - 12) / 24))
            temperature = 35 + (10 * ((timestamp.hour - 12) / 24))
            humidity = 40 + (20 * ((timestamp.hour - 12) / 24))
            
            # Ensure values are in realistic range
            pm25 = max(20, min(150, pm25))
            temperature = max(20, min(45, temperature))
            humidity = max(20, min(70, humidity))
            
            point = HistoricalDataPoint(
                timestamp=timestamp,
                pm25=float(pm25),
                temperature=float(temperature),
                humidity=float(humidity)
            )
            
            data_points.append(point)
        
        # 3. AGGREGATE BY RESOLUTION
        
        if resolution == "daily":
            # Aggregate to daily (simple mean)
            logger.debug("📈 Aggregating to daily resolution")
            daily_data = {}
            
            for point in data_points:
                date_key = point.timestamp.date()
                
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        "count": 0,
                        "pm25_sum": 0,
                        "temp_sum": 0,
                        "humidity_sum": 0,
                        "timestamp": point.timestamp
                    }
                
                daily_data[date_key]["count"] += 1
                daily_data[date_key]["pm25_sum"] += point.pm25
                daily_data[date_key]["temp_sum"] += point.temperature or 0
                daily_data[date_key]["humidity_sum"] += point.humidity or 0
            
            # Calculate daily means
            data_points = [
                HistoricalDataPoint(
                    timestamp=data["timestamp"],
                    pm25=data["pm25_sum"] / data["count"],
                    temperature=data["temp_sum"] / data["count"] if data["count"] > 0 else None,
                    humidity=data["humidity_sum"] / data["count"] if data["count"] > 0 else None
                )
                for data in daily_data.values()
            ]
        
        # 4. BUILD RESPONSE
        
        if not data_points:
            logger.warning(f"⚠️  No data available for {location}")
            data_points = []
        
        # Get time range
        time_range_start = data_points[-1].timestamp if data_points else None
        time_range_end = data_points[0].timestamp if data_points else None
        
        response = DataResponse(
            location=location,
            latitude=28.623056,  # Mock coordinates
            longitude=77.234167,
            data_points=data_points,
            count=len(data_points),
            time_range_start=time_range_start,
            time_range_end=time_range_end
        )
        
        logger.info(f"✅ Returned {len(data_points)} data points for {location}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving data: {str(e)}"
        )


@router.get(
    "/data/{location}/stats",
    summary="Get data statistics",
    description="Get statistical summary of PM2.5 data for a location"
)
async def get_location_stats(
    location: str,
    days_back: int = Query(7, ge=1, le=365)
):
    """
    Get statistical summary of PM2.5 data.
    
    Args:
        location: Monitoring station name
        days_back: Number of past days to analyze
    
    Returns:
        Statistics dict with min, max, mean, median, etc.
    
    Example:
        GET /api/v1/data/Anand%20Lok/stats?days_back=30
    
    Example Response:
        {
            "location": "Anand Lok",
            "total_records": 720,
            "min_pm25": 28.5,
            "max_pm25": 145.3,
            "mean_pm25": 62.1,
            "median_pm25": 58.5,
            "std_pm25": 28.3,
            "timestamp": "2026-09-06T10:00:00Z"
        }
    """
    logger.info(f"📈 Stats request: {location}, {days_back} days")
    
    try:
        settings = get_settings()
        
        # Validate location
        if location not in settings.locations:
            raise HTTPException(
                status_code=400,
                detail=f"Location '{location}' not found"
            )
        
        # Mock statistics
        stats = {
            "location": location,
            "total_records": days_back * 24,
            "min_pm25": 25.5,
            "max_pm25": 145.3,
            "mean_pm25": 62.1,
            "median_pm25": 58.5,
            "std_pm25": 28.3,
            "p10": 38.2,
            "p25": 45.3,
            "p75": 78.9,
            "p90": 95.6,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Stats calculated for {location}")
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return {"error": str(e)}, 500


@router.get(
    "/locations",
    summary="List all locations",
    description="Get list of all available monitoring locations"
)
async def get_locations():
    """
    Get list of all available monitoring locations.
    
    Returns:
        List of location names
    
    Example Response:
        {
            "locations": [
                "Air Check",
                "Anand Lok",
                "Ashok Vihar, Delhi - DPCC",
                ...
            ],
            "count": 24,
            "timestamp": "2026-09-06T10:00:00Z"
        }
    """
    logger.debug("📍 Getting available locations")
    
    try:
        settings = get_settings()
        
        return {
            "locations": settings.locations,
            "count": len(settings.locations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting locations: {e}")
        return {"error": str(e)}, 500