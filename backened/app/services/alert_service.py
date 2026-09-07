"""
SIH26082 Backend - Alert Service
Air Pollution-Weather Coupled Forecasting System
Ministry of Earth Sciences, India

This service handles:
1. Alert triggering based on thresholds
2. Active alert tracking
3. Alert generation and storage
4. Alert resolution
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================
# ALERT DEFINITIONS
# ============================================

class AlertType(str, Enum):
    """Types of alerts"""
    PM25_THRESHOLD = "PM2.5_THRESHOLD"
    WBGT_THRESHOLD = "WBGT_THRESHOLD"
    COMPOUND_RISK = "COMPOUND_RISK"
    DATA_MISSING = "DATA_MISSING"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


# ============================================
# ALERT OBJECT
# ============================================

class Alert:
    """
    Single alert object
    """
    
    def __init__(
        self,
        alert_id: str,
        alert_type: AlertType,
        location: str,
        severity: AlertSeverity,
        value: float,
        threshold: float,
        message: str,
        triggered_at: Optional[datetime] = None,
        resolved: bool = False
    ):
        self.alert_id = alert_id
        self.alert_type = alert_type
        self.location = location
        self.severity = severity
        self.value = value
        self.threshold = threshold
        self.message = message
        self.triggered_at = triggered_at or datetime.utcnow()
        self.resolved = resolved
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON response"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "location": self.location,
            "severity": self.severity.value,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved": self.resolved
        }


# ============================================
# ALERT SERVICE
# ============================================

class AlertService:
    """
    Service for alert management.
    
    Tracks active alerts and generates new ones based on thresholds.
    """
    
    def __init__(self):
        """Initialize alert service"""
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_counter = 0
        logger.info("🔔 Alert service initialized")
    
    
    # ============================================
    # THRESHOLD CHECKING
    # ============================================
    
    def check_pm25_threshold(
        self,
        location: str,
        pm25_value: float,
        thresholds: Dict[str, float]
    ) -> Optional[Alert]:
        """
        Check if PM2.5 crossed a threshold and generate alert if needed.
        
        Args:
            location: Station name
            pm25_value: PM2.5 concentration (µg/m³)
            thresholds: Dict with threshold values
                {"normal": 50, "moderate": 100, "high": 250, "severe": 350}
        
        Returns:
            Alert object if threshold crossed, None otherwise
        """
        try:
            severity = None
            threshold_value = None
            
            if pm25_value >= thresholds.get("severe", 350):
                severity = AlertSeverity.SEVERE
                threshold_value = thresholds.get("severe", 350)
            elif pm25_value >= thresholds.get("high", 250):
                severity = AlertSeverity.HIGH
                threshold_value = thresholds.get("high", 250)
            elif pm25_value >= thresholds.get("moderate", 100):
                severity = AlertSeverity.MODERATE
                threshold_value = thresholds.get("moderate", 100)
            
            if severity is None:
                return None
            
            # Generate alert
            alert_id = self._generate_alert_id()
            message = f"PM2.5 alert: {pm25_value:.1f} µg/m³ at {location} ({severity.value})"
            
            alert = Alert(
                alert_id=alert_id,
                alert_type=AlertType.PM25_THRESHOLD,
                location=location,
                severity=severity,
                value=pm25_value,
                threshold=threshold_value,
                message=message
            )
            
            logger.warning(f"🚨 PM2.5 Alert triggered: {message}")
            return alert
        
        except Exception as e:
            logger.error(f"❌ Error checking PM2.5 threshold: {e}")
            return None
    
    
    def check_wbgt_threshold(
        self,
        location: str,
        wbgt_value: float,
        thresholds: Dict[str, float]
    ) -> Optional[Alert]:
        """
        Check if WBGT crossed a threshold and generate alert if needed.
        
        Args:
            location: Station name
            wbgt_value: WBGT value (°C)
            thresholds: Dict with threshold values
                {"normal": 28, "moderate": 32, "high": 35, "severe": 38}
        
        Returns:
            Alert object if threshold crossed, None otherwise
        """
        try:
            severity = None
            threshold_value = None
            
            if wbgt_value >= thresholds.get("severe", 38):
                severity = AlertSeverity.SEVERE
                threshold_value = thresholds.get("severe", 38)
            elif wbgt_value >= thresholds.get("high", 35):
                severity = AlertSeverity.HIGH
                threshold_value = thresholds.get("high", 35)
            elif wbgt_value >= thresholds.get("moderate", 32):
                severity = AlertSeverity.MODERATE
                threshold_value = thresholds.get("moderate", 32)
            
            if severity is None:
                return None
            
            # Generate alert
            alert_id = self._generate_alert_id()
            message = f"Heatwave alert: WBGT {wbgt_value:.1f}°C at {location} ({severity.value})"
            
            alert = Alert(
                alert_id=alert_id,
                alert_type=AlertType.WBGT_THRESHOLD,
                location=location,
                severity=severity,
                value=wbgt_value,
                threshold=threshold_value,
                message=message
            )
            
            logger.warning(f"🚨 WBGT Alert triggered: {message}")
            return alert
        
        except Exception as e:
            logger.error(f"❌ Error checking WBGT threshold: {e}")
            return None
    
    
    def check_compound_risk(
        self,
        location: str,
        pm25_risk: str,
        wbgt_risk: str
    ) -> Optional[Alert]:
        """
        Check for compound (heat + air quality) risk.
        
        If both PM2.5 and WBGT are high, compound risk is higher.
        
        Args:
            location: Station name
            pm25_risk: PM2.5 risk level ("NORMAL", "MODERATE", "HIGH", "SEVERE")
            wbgt_risk: WBGT risk level ("NORMAL", "MODERATE", "HIGH", "SEVERE")
        
        Returns:
            Alert if compound risk is HIGH or SEVERE, None otherwise
        """
        try:
            risk_scores = {
                "NORMAL": 1,
                "MODERATE": 2,
                "HIGH": 3,
                "SEVERE": 4
            }
            
            pm25_score = risk_scores.get(pm25_risk, 1)
            wbgt_score = risk_scores.get(wbgt_risk, 1)
            
            # Compound risk if both are moderate or worse
            if pm25_score >= 2 and wbgt_score >= 2:
                compound_score = max(pm25_score, wbgt_score)
                
                if compound_score >= 3:  # HIGH or SEVERE
                    severity = AlertSeverity.HIGH if compound_score == 3 else AlertSeverity.SEVERE
                    
                    alert_id = self._generate_alert_id()
                    message = f"Compound risk alert: Heat ({wbgt_risk}) + Air Quality ({pm25_risk}) at {location}"
                    
                    alert = Alert(
                        alert_id=alert_id,
                        alert_type=AlertType.COMPOUND_RISK,
                        location=location,
                        severity=severity,
                        value=float(compound_score),
                        threshold=3.0,
                        message=message
                    )
                    
                    logger.warning(f"🚨 Compound Risk Alert: {message}")
                    return alert
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error checking compound risk: {e}")
            return None
    
    
    # ============================================
    # ALERT TRACKING
    # ============================================
    
    def add_alert(self, alert: Alert) -> None:
        """
        Add alert to active alerts.
        
        Args:
            alert: Alert object to add
        """
        self.active_alerts[alert.alert_id] = alert
        logger.info(f"📌 Alert added: {alert.alert_id}")
    
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Mark alert as resolved.
        
        Args:
            alert_id: ID of alert to resolve
        
        Returns:
            True if resolved, False if not found
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            logger.info(f"✅ Alert resolved: {alert_id}")
            return True
        
        logger.warning(f"⚠️  Alert not found: {alert_id}")
        return False
    
    
    def get_active_alerts(self, location: Optional[str] = None) -> List[Alert]:
        """
        Get all active (unresolved) alerts.
        
        Args:
            location: Optional filter by location
        
        Returns:
            List of active Alert objects
        """
        alerts = [
            alert for alert in self.active_alerts.values()
            if not alert.resolved
        ]
        
        if location:
            alerts = [a for a in alerts if a.location == location]
        
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)
    
    
    def get_all_alerts(self, location: Optional[str] = None) -> List[Alert]:
        """
        Get all alerts (including resolved).
        
        Args:
            location: Optional filter by location
        
        Returns:
            List of all Alert objects
        """
        alerts = list(self.active_alerts.values())
        
        if location:
            alerts = [a for a in alerts if a.location == location]
        
        return sorted(alerts, key=lambda a: a.triggered_at, reverse=True)
    
    
    def clear_old_alerts(self, hours: int = 24) -> int:
        """
        Remove resolved alerts older than specified hours.
        
        Args:
            hours: Age threshold in hours
        
        Returns:
            Number of alerts removed
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        alerts_to_remove = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.resolved and alert.triggered_at < cutoff_time
        ]
        
        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]
        
        if alerts_to_remove:
            logger.info(f"🗑️  Removed {len(alerts_to_remove)} old alerts")
        
        return len(alerts_to_remove)
    
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        self.alert_counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        return f"alert-{timestamp}-{self.alert_counter:04d}"
    
    
    def get_summary(self) -> Dict:
        """
        Get summary of current alerts.
        
        Returns:
            Dict with alert counts by severity
        """
        active = self.get_active_alerts()
        
        summary = {
            "total_active": len(active),
            "severe": len([a for a in active if a.severity == AlertSeverity.SEVERE]),
            "high": len([a for a in active if a.severity == AlertSeverity.HIGH]),
            "moderate": len([a for a in active if a.severity == AlertSeverity.MODERATE]),
            "normal": len([a for a in active if a.severity == AlertSeverity.NORMAL]),
        }
        
        return summary


# ============================================
# DEPENDENCY INJECTION
# ============================================

_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """
    Get or create alert service (singleton).
    
    Usage in routes:
        @app.post("/forecast")
        def forecast(alert_service: AlertService = Depends(get_alert_service)):
            alert = alert_service.check_pm25_threshold(...)
    """
    global _alert_service
    
    if _alert_service is None:
        logger.info("🔧 Initializing alert service...")
        _alert_service = AlertService()
    
    return _alert_service


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    """
    Test alert service by running:
        python alert_service.py
    """
    print("\n" + "="*60)
    print("ALERT SERVICE TEST")
    print("="*60 + "\n")
    
    service = AlertService()
    
    # Test PM2.5 alert
    print("TEST 1: PM2.5 Threshold Alert")
    thresholds_pm25 = {
        "normal": 50,
        "moderate": 100,
        "high": 250,
        "severe": 350
    }
    
    alert = service.check_pm25_threshold(
        location="Anand Lok",
        pm25_value=410,
        thresholds=thresholds_pm25
    )
    
    if alert:
        service.add_alert(alert)
        print(f"   Alert ID: {alert.alert_id}")
        print(f"   Severity: {alert.severity.value}")
        print(f"   Message: {alert.message}")
    
    # Test WBGT alert
    print("\nTEST 2: WBGT Threshold Alert")
    thresholds_wbgt = {
        "normal": 28,
        "moderate": 32,
        "high": 35,
        "severe": 38
    }
    
    alert = service.check_wbgt_threshold(
        location="Anand Lok",
        wbgt_value=36.5,
        thresholds=thresholds_wbgt
    )
    
    if alert:
        service.add_alert(alert)
        print(f"   Alert ID: {alert.alert_id}")
        print(f"   Severity: {alert.severity.value}")
    
    # Test compound risk
    print("\nTEST 3: Compound Risk Alert")
    alert = service.check_compound_risk(
        location="Anand Lok",
        pm25_risk="SEVERE",
        wbgt_risk="HIGH"
    )
    
    if alert:
        service.add_alert(alert)
        print(f"   Alert ID: {alert.alert_id}")
        print(f"   Message: {alert.message}")
    
    # Test summary
    print("\nTEST 4: Alert Summary")
    summary = service.get_summary()
    print(f"   Total Active: {summary['total_active']}")
    print(f"   Severe: {summary['severe']}")
    print(f"   High: {summary['high']}")
    print(f"   Moderate: {summary['moderate']}")
    
    # Test active alerts
    print("\nTEST 5: Active Alerts")
    active = service.get_active_alerts()
    for alert in active:
        print(f"   - {alert.alert_id}: {alert.message}")
    
    print("\n" + "="*60 + "\n")