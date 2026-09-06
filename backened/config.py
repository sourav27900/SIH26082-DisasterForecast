import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SIH26082 Backend"
    debug: bool = True
    model_path: Path = Path("ml/artifacts/xgb_model.joblib")
    data_path: Path = Path("data_pipelines/delhi_pm25_features.csv")
    forecast_horizon_hours: int = 24
    alert_thresholds: dict = {"moderate": 100, "severe": 300}
    
    locations: list[str] = [
        "Anand Vihar", "Dwarka", "RK Puram", "Punjabi Bagh", "Rohini",
        "Nehru Nagar", "IGI Airport", "IIT Delhi", "Mandir Marg", "Pusa",
        "Shadipur", "Sirifort", "Vivek Vihar", "Wazirpur", "Ashok Vihar",
        "Bawana", "Mundka", "Najafgarh", "Narela", "Okhla Phase-2",
        "Patparganj", "Jahangirpuri", "Lodhi Road", "Major Dhyan Chand Stadium",
        "NSIT Dwarka", "DTU", "IHBAS", "CRRI Mathura Road", "Aya Nagar",
        "Alipur", "Sonia Vihar", "Preet Vihar"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()