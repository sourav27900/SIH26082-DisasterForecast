"""
SIH26082 Backend - WBGT Service
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This service handles:
1. WBGT (Wet Bulb Globe Temperature) calculation
2. Risk level classification
3. Health advisory generation
4. Thermal stress assessment

THIS IS WHERE THERMAL TEAM PLUGS IN THEIR FORMULA
"""

import logging
import math
from typing import Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================
# RISK CLASSIFICATIONS
# ============================================

class RiskLevel(str, Enum):
    """Thermal risk levels"""
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


# ============================================
# WBGT CALCULATION SERVICE
# ============================================

class WBGTService:
    """
    Service for WBGT calculation and thermal stress assessment.
    
    WBGT Formula (Simplified):
    WBGT = 0.7 × Tw + 0.2 × Tg + 0.1 × Ta
    
    Where:
    - Tw = wet-bulb temperature (function of T, RH)
    - Tg = black-globe temperature (T + effect of solar radiation)
    - Ta = ambient temperature
    
    THERMAL TEAM: Replace placeholder formula with actual WBGT calculation
    """
    
    # WBGT Thresholds (from config)
    # These come from config.py
    WBGT_THRESHOLDS = {
        "NORMAL": 28.0,      # Safe for all activities
        "MODERATE": 32.0,    # Caution, limit intense activity
        "HIGH": 35.0,        # Extreme caution, outdoor work stops
        "SEVERE": 38.0       # Heat emergency
    }
    
    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize WBGT service.
        
        Args:
            thresholds: Optional custom WBGT thresholds
        """
        if thresholds:
            self.WBGT_THRESHOLDS = thresholds
            logger.info(f"📊 Using custom WBGT thresholds: {thresholds}")
        else:
            logger.info(f"📊 Using default WBGT thresholds")
    
    
    # ============================================
    # CORE WBGT CALCULATIONS
    # ============================================
    
    def calculate_wet_bulb_temperature(
        self,
        temperature: float,
        humidity: float
    ) -> float:
        """
        Calculate wet-bulb temperature from dry-bulb temp and relative humidity.
        
        THERMAL TEAM: Replace this with accurate formula
        
        Current formula is approximation (Magnus formula):
        Tw ≈ T × atan(0.151977 × (RH + 8.313659)^0.5) + atan(T + RH) - atan(RH - 1.676331)
        
        Args:
            temperature: Ambient temperature (°C)
            humidity: Relative humidity (%)
        
        Returns:
            Wet-bulb temperature (°C)
        """
        try:
            # Simplified approximation (for development)
            # THERMAL TEAM: Replace with accurate calculation
            
            # Method 1: Simple linear approximation
            # Tw ≈ T × (0.151977 × sqrt(RH + 8.313659) + atan(T + RH) - atan(RH - 1.67633))
            
            # For now, use simpler approximation
            # Tw ≈ T - ((100 - RH) / 5)  (rough approximation)
            
            if humidity <= 0 or humidity > 100:
                logger.warning(f"⚠️  Invalid humidity: {humidity}%. Using default.")
                humidity = 50.0
            
            # Approximation valid for: T > 0°C, 0 < RH < 100
            wet_bulb = temperature - ((100 - humidity) / 5.0)
            
            # Ensure wet bulb <= dry bulb
            wet_bulb = min(wet_bulb, temperature)
            
            logger.debug(f"💧 Wet bulb: T={temperature}°C, RH={humidity}% → Tw={wet_bulb:.1f}°C")
            return wet_bulb
        
        except Exception as e:
            logger.error(f"❌ Error calculating wet bulb: {e}")
            # Fallback
            return temperature - 5.0
    
    
    def calculate_globe_temperature(
        self,
        temperature: float,
        wind_speed: float,
        solar_radiation: float = 0.0
    ) -> float:
        """
        Calculate black-globe temperature.
        
        THERMAL TEAM: Replace with accurate formula
        
        Globe temperature accounts for solar radiation and wind.
        Tg = Ta + (solar_effect - wind_cooling)
        
        Args:
            temperature: Ambient temperature (°C)
            wind_speed: Wind speed (m/s or km/h, must be consistent)
            solar_radiation: Solar radiation (W/m², default 0 = no direct sun)
        
        Returns:
            Globe temperature (°C)
        """
        try:
            # Simple approximation
            # Solar heating effect: ~0.05°C per W/m²
            # Wind cooling: reduces effect based on speed
            
            if wind_speed < 0:
                logger.warning(f"⚠️  Invalid wind speed: {wind_speed}. Using 0.")
                wind_speed = 0.0
            
            if solar_radiation < 0:
                logger.warning(f"⚠️  Invalid solar radiation: {solar_radiation}. Using 0.")
                solar_radiation = 0.0
            
            # Approximation
            solar_effect = solar_radiation * 0.05
            wind_factor = 1.0 - (wind_speed * 0.02)  # Wind reduces heating
            
            globe_temp = temperature + (solar_effect * wind_factor)
            
            logger.debug(
                f"🌍 Globe temp: T={temperature}°C, "
                f"Wind={wind_speed}, Solar={solar_radiation}W/m² → Tg={globe_temp:.1f}°C"
            )
            return globe_temp
        
        except Exception as e:
            logger.error(f"❌ Error calculating globe temperature: {e}")
            return temperature
    
    
    def calculate_wbgt(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float = 0.0,
        solar_radiation: float = 0.0
    ) -> float:
        """
        Calculate WBGT (Wet Bulb Globe Temperature).
        
        WBGT = 0.7 × Tw + 0.2 × Tg + 0.1 × Ta
        
        Where:
        - Tw = wet-bulb temperature
        - Tg = globe temperature
        - Ta = ambient temperature
        
        THERMAL TEAM: This is the main function to replace
        
        Args:
            temperature: Ambient temperature (°C) - REQUIRED
            humidity: Relative humidity (%) - REQUIRED
            wind_speed: Wind speed (m/s, default 0) - OPTIONAL
            solar_radiation: Solar radiation (W/m², default 0) - OPTIONAL
        
        Returns:
            WBGT value (°C)
        
        Example:
            wbgt = calculate_wbgt(
                temperature=40.5,
                humidity=35.0,
                wind_speed=2.5,
                solar_radiation=500.0
            )
            # Returns: ~35.2°C
        """
        try:
            logger.debug(
                f"🔥 Calculating WBGT: T={temperature}°C, RH={humidity}%, "
                f"Wind={wind_speed}, Solar={solar_radiation}W/m²"
            )
            
            # Calculate components
            tw = self.calculate_wet_bulb_temperature(temperature, humidity)
            tg = self.calculate_globe_temperature(temperature, wind_speed, solar_radiation)
            ta = temperature
            
            # Combine weighted average
            wbgt = (0.7 * tw) + (0.2 * tg) + (0.1 * ta)
            
            logger.debug(f"   Tw={tw:.1f}°C, Tg={tg:.1f}°C, Ta={ta:.1f}°C → WBGT={wbgt:.1f}°C")
            return round(wbgt, 1)
        
        except Exception as e:
            logger.error(f"❌ Error calculating WBGT: {e}")
            # Fallback: return ambient temp (conservative estimate)
            return round(temperature, 1)
    
    
    # ============================================
    # RISK CLASSIFICATION
    # ============================================
    
    def classify_wbgt_risk(self, wbgt_value: float) -> RiskLevel:
        """
        Classify WBGT into risk level.
        
        Args:
            wbgt_value: WBGT in °C
        
        Returns:
            RiskLevel enum
        """
        try:
            if wbgt_value <= self.WBGT_THRESHOLDS["NORMAL"]:
                return RiskLevel.NORMAL
            elif wbgt_value <= self.WBGT_THRESHOLDS["MODERATE"]:
                return RiskLevel.MODERATE
            elif wbgt_value <= self.WBGT_THRESHOLDS["HIGH"]:
                return RiskLevel.HIGH
            else:
                return RiskLevel.SEVERE
        
        except Exception as e:
            logger.error(f"❌ Error classifying WBGT: {e}")
            return RiskLevel.MODERATE
    
    
    # ============================================
    # HEALTH ADVISORIES
    # ============================================
    
    def get_advisories(self, wbgt_value: float, risk_level: RiskLevel) -> Dict[str, str]:
        """
        Generate health advisories for a WBGT level.
        
        Args:
            wbgt_value: WBGT value in °C
            risk_level: Classified risk level
        
        Returns:
            Dict with advisories for different groups
        """
        try:
            advisories = {
                "general": self._get_general_advice(risk_level),
                "workers": self._get_worker_advice(risk_level),
                "vulnerable": self._get_vulnerable_advice(risk_level),
                "outdoor": self._get_outdoor_advice(risk_level),
            }
            
            logger.debug(f"📋 Advisories generated for WBGT={wbgt_value:.1f}°C ({risk_level})")
            return advisories
        
        except Exception as e:
            logger.error(f"❌ Error generating advisories: {e}")
            return {
                "general": "Unable to generate advice",
                "error": str(e)
            }
    
    
    def _get_general_advice(self, risk_level: RiskLevel) -> str:
        """General public advice"""
        advice_map = {
            RiskLevel.NORMAL: "🟢 No heat precautions needed. Conditions are safe for outdoor activities.",
            RiskLevel.MODERATE: "🟡 Caution: Limit prolonged outdoor exertion. Stay hydrated. Take frequent breaks.",
            RiskLevel.HIGH: "🟠 Warning: Avoid outdoor activities during peak heat hours (11 AM - 4 PM). Limit exertion.",
            RiskLevel.SEVERE: "🔴 ALERT: Do NOT engage in outdoor activities. Heat emergency conditions. Stay indoors in air-conditioned spaces."
        }
        return advice_map.get(risk_level, "Conditions require caution.")
    
    
    def _get_worker_advice(self, risk_level: RiskLevel) -> str:
        """Advice for outdoor workers"""
        advice_map = {
            RiskLevel.NORMAL: "✅ Standard precautions. Provide water breaks every 2 hours.",
            RiskLevel.MODERATE: "⚠️  Mandatory water breaks every 1.5 hours. Provide shaded rest areas. Reduce workload by 25%.",
            RiskLevel.HIGH: "🔴 STOP work outdoors 1 PM - 5 PM. Mandatory cooling breaks every 30 minutes. Provide cooling vests.",
            RiskLevel.SEVERE: "🚫 HALT all outdoor work. Emergency protocols active. Worker evacuation required."
        }
        return advice_map.get(risk_level, "Monitor worker safety closely.")
    
    
    def _get_vulnerable_advice(self, risk_level: RiskLevel) -> str:
        """Advice for elderly, children, ill persons"""
        advice_map = {
            RiskLevel.NORMAL: "✅ Safe. Normal activity with standard hydration.",
            RiskLevel.MODERATE: "⚠️  Stay indoors during 11 AM - 4 PM. Keep medications accessible. Monitor health.",
            RiskLevel.HIGH: "🔴 Stay indoors in air-conditioned spaces. Avoid outdoor exposure. Keep emergency numbers ready.",
            RiskLevel.SEVERE: "🚫 EMERGENCY: Seek immediate shelter in cool environments. Contact healthcare provider if experiencing heat illness symptoms."
        }
        return advice_map.get(risk_level, "Avoid outdoor exposure.")
    
    
    def _get_outdoor_advice(self, risk_level: RiskLevel) -> str:
        """Advice for outdoor activities (sports, events)"""
        advice_map = {
            RiskLevel.NORMAL: "✅ Events can proceed normally with standard safety measures.",
            RiskLevel.MODERATE: "⚠️  Limit activity duration. Provide water stations every 15 minutes. Have medical staff present.",
            RiskLevel.HIGH: "🔴 CANCEL outdoor events during peak hours. If proceeding: Reduce duration, increase rest breaks, mandatory cooling.",
            RiskLevel.SEVERE: "🚫 CANCEL all outdoor events. Postpone to cooler times or indoor venues."
        }
        return advice_map.get(risk_level, "Monitor event conditions continuously.")
    
    
    # ============================================
    # COMPOUND RISK ASSESSMENT
    # ============================================
    
    def assess_compound_risk(
        self,
        wbgt_value: float,
        pm25_value: float,
        pm25_risk_level: str
    ) -> Dict[str, any]:
        """
        Assess combined thermal + air quality risk.
        
        High WBGT + High AQI = Higher risk (people breathe harder, inhale more pollutants)
        
        Args:
            wbgt_value: WBGT in °C
            pm25_value: PM2.5 in µg/m³
            pm25_risk_level: "NORMAL", "MODERATE", "HIGH", "SEVERE"
        
        Returns:
            Dict with compound risk assessment
        """
        try:
            wbgt_risk = self.classify_wbgt_risk(wbgt_value)
            
            # Simple compound risk logic
            risk_scores = {
                "NORMAL": 1,
                "MODERATE": 2,
                "HIGH": 3,
                "SEVERE": 4
            }
            
            wbgt_score = risk_scores.get(wbgt_risk.value, 2)
            pm25_score = risk_scores.get(pm25_risk_level, 2)
            
            compound_score = max(wbgt_score, pm25_score)  # Worst of the two
            
            # Map back to risk level
            compound_risk_map = {
                1: RiskLevel.NORMAL,
                2: RiskLevel.MODERATE,
                3: RiskLevel.HIGH,
                4: RiskLevel.SEVERE
            }
            
            compound_risk = compound_risk_map.get(compound_score, RiskLevel.MODERATE)
            
            return {
                "compound_risk_level": compound_risk.value,
                "wbgt_risk": wbgt_risk.value,
                "pm25_risk": pm25_risk_level,
                "compound_score": compound_score,
                "message": f"Combined heat ({wbgt_risk.value}) + air quality ({pm25_risk_level}) = {compound_risk.value} risk"
            }
        
        except Exception as e:
            logger.error(f"❌ Error assessing compound risk: {e}")
            return {
                "error": str(e),
                "compound_risk_level": RiskLevel.MODERATE.value
            }


# ============================================
# DEPENDENCY INJECTION
# ============================================

_wbgt_service: Optional[WBGTService] = None


def get_wbgt_service(thresholds: Optional[Dict[str, float]] = None) -> WBGTService:
    """
    Get or create WBGT service (singleton).
    
    Usage in routes:
        @app.post("/forecast")
        def forecast(wbgt_service: WBGTService = Depends(get_wbgt_service)):
            wbgt = wbgt_service.calculate_wbgt(temp, humidity)
    """
    global _wbgt_service
    
    if _wbgt_service is None:
        logger.info("🔧 Initializing WBGT service...")
        _wbgt_service = WBGTService(thresholds)
    
    return _wbgt_service


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    """
    Test WBGT service by running:
        python wbgt_service.py
    """
    print("\n" + "="*60)
    print("WBGT SERVICE TEST")
    print("="*60 + "\n")
    
    service = WBGTService()
    
    # Test 1: Normal conditions
    print("TEST 1: Normal Conditions")
    print("   Input: T=25°C, RH=50%")
    wbgt = service.calculate_wbgt(temperature=25, humidity=50)
    risk = service.classify_wbgt_risk(wbgt)
    print(f"   WBGT: {wbgt}°C → Risk: {risk.value}")
    
    # Test 2: Moderate heat
    print("\nTEST 2: Moderate Heat")
    print("   Input: T=35°C, RH=40%")
    wbgt = service.calculate_wbgt(temperature=35, humidity=40)
    risk = service.classify_wbgt_risk(wbgt)
    print(f"   WBGT: {wbgt}°C → Risk: {risk.value}")
    advisories = service.get_advisories(wbgt, risk)
    print(f"   General: {advisories['general']}")
    
    # Test 3: Severe heat
    print("\nTEST 3: Severe Heat")
    print("   Input: T=42°C, RH=30%, Wind=2 m/s, Solar=600 W/m²")
    wbgt = service.calculate_wbgt(
        temperature=42,
        humidity=30,
        wind_speed=2,
        solar_radiation=600
    )
    risk = service.classify_wbgt_risk(wbgt)
    print(f"   WBGT: {wbgt}°C → Risk: {risk.value}")
    advisories = service.get_advisories(wbgt, risk)
    print(f"   General: {advisories['general']}")
    print(f"   Workers: {advisories['workers']}")
    
    # Test 4: Compound risk
    print("\nTEST 4: Compound Risk Assessment")
    compound = service.assess_compound_risk(
        wbgt_value=36.0,
        pm25_value=350,
        pm25_risk_level="SEVERE"
    )
    print(f"   WBGT Risk: {compound['wbgt_risk']}")
    print(f"   PM2.5 Risk: {compound['pm25_risk']}")
    print(f"   Compound: {compound['compound_risk_level']}")
    print(f"   Message: {compound['message']}")
    
    print("\n" + "="*60 + "\n")