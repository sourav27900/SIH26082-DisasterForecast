import streamlit as st
import requests
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Test backend connection
try:
    health = requests.get(f"{BACKEND_URL}/health", timeout=3)
    if health.status_code == 200:
        st.success("✅ Backend connected successfully!")
    else:
        st.warning(f"⚠️ Backend returned status: {health.status_code}")
except requests.exceptions.ConnectionError:
    st.error("🚨 Cannot connect to backend. Run `python main.py` in the backend folder.")

    

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Delhi NCR Heat & Air Early Warning System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. THEME / UI
# ============================================================
st.markdown(
    """
    <style>
        .stApp {
            background:
                linear-gradient(rgba(5, 14, 24, .72), rgba(5, 14, 24, .84)),
                linear-gradient(180deg, #6c8290 0%, #b5c5c7 42%, #354f52 100%);
            overflow-x: hidden;
        }

        /* Full-screen illustrated weather atmosphere, inspired by the supplied
           AQI.in recording: soft sky, drifting clouds, distant hills and mist. */
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            opacity: .30;
            background:
                radial-gradient(ellipse at 18% 38%, rgba(255,255,255,.55) 0 8%, transparent 22%),
                radial-gradient(ellipse at 82% 28%, rgba(255,255,255,.45) 0 7%, transparent 20%),
                linear-gradient(180deg, transparent 52%, rgba(190,210,201,.25) 53%, transparent 75%);
            animation: skyDrift 22s ease-in-out infinite alternate;
        }

        .stApp::after {
            content: "";
            position: fixed;
            left: -10%;
            right: -10%;
            bottom: -5%;
            height: 38%;
            z-index: 0;
            pointer-events: none;
            opacity: .28;
            background:
                radial-gradient(ellipse at 18% 90%, #1d4a42 0 14%, transparent 15%),
                radial-gradient(ellipse at 38% 100%, #28584d 0 20%, transparent 21%),
                radial-gradient(ellipse at 65% 92%, #214d43 0 17%, transparent 18%),
                radial-gradient(ellipse at 88% 100%, #315f4e 0 18%, transparent 19%);
            filter: blur(2px);
            animation: landscapeMove 26s ease-in-out infinite alternate;
        }

        @keyframes skyDrift {
            0% { transform: translate3d(-2%, 0, 0) scale(1.02); }
            50% { transform: translate3d(2%, 1%, 0) scale(1.05); }
            100% { transform: translate3d(-1%, -1%, 0) scale(1.02); }
        }

        @keyframes landscapeMove {
            0% { transform: translateX(-2%) scale(1.02); }
            100% { transform: translateX(2%) scale(1.06); }
        }

        @keyframes cloudFloat {
            0% { transform: translateX(-8vw); }
            100% { transform: translateX(108vw); }
        }

        @keyframes mistFloat {
            0%, 100% { transform: translateX(-2%) scaleX(1); opacity: .16; }
            50% { transform: translateX(3%) scaleX(1.05); opacity: .28; }
        }

        .weather-scene {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
        }

        .weather-cloud {
            position: absolute;
            width: 180px;
            height: 55px;
            border-radius: 60px;
            background: rgba(245, 248, 246, .18);
            filter: blur(9px);
            box-shadow:
                45px -18px 0 8px rgba(245,248,246,.15),
                88px 0 0 4px rgba(245,248,246,.13),
                120px -13px 0 10px rgba(245,248,246,.12);
            animation: cloudFloat linear infinite;
        }

        .cloud-a { top: 16%; left: -240px; animation-duration: 48s; }
        .cloud-b { top: 31%; left: -420px; transform: scale(.72); animation-duration: 62s; animation-delay: -22s; }
        .cloud-c { top: 9%; left: -360px; transform: scale(1.2); animation-duration: 74s; animation-delay: -41s; }

        .weather-mist {
            position: absolute;
            left: -5%;
            bottom: 18%;
            width: 110%;
            height: 120px;
            border-radius: 50%;
            background: rgba(230, 241, 235, .20);
            filter: blur(28px);
            animation: mistFloat 14s ease-in-out infinite;
        }

        .weather-sun {
            position: absolute;
            width: 150px;
            height: 150px;
            right: 10%;
            top: 15%;
            border-radius: 50%;
            background: rgba(255, 219, 118, .18);
            box-shadow: 0 0 70px 35px rgba(255, 215, 105, .10);
            animation: sunPulse 7s ease-in-out infinite;
        }

        @keyframes sunPulse {
            0%, 100% { opacity: .65; transform: scale(.96); }
            50% { opacity: 1; transform: scale(1.05); }
        }

        /* Keep Streamlit content above the animated scene. */
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stHeader"],
        [data-testid="stSidebar"] {
            position: relative;
            z-index: 1;
        }

        @keyframes glowPulse {
            0%, 100% { box-shadow: 0 0 0 rgba(0, 200, 255, 0); }
            50% { box-shadow: 0 0 28px rgba(0, 200, 255, .18); }
        }

        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
            letter-spacing: .2px;
            animation: titleIn .8s ease-out both;
        }

        @keyframes titleIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .subtitle {
            color: #9bb0c6;
            margin-bottom: 1rem;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(100,190,255,.18);
            border-radius: 14px;
            padding: 12px;
            background: rgba(22, 33, 46, 0.85);
            backdrop-filter: blur(10px);
            animation: glowPulse 4s ease-in-out infinite;
        }

        .status-card {
            padding: 14px 18px;
            border-radius: 14px;
            border: 1px solid rgba(100,190,255,.20);
            margin-bottom: 10px;
            background: rgba(22, 33, 46, 0.85);
            backdrop-filter: blur(10px);
        }

        .map-caption {
            color: #a9bfd4;
            margin-bottom: .6rem;
        }

        .small-muted {
            color: #8b949e;
            font-size: .85rem;
        }
        
        .forecast-container {
            background: rgba(22, 33, 46, 0.85);
            border: 1px solid rgba(100, 190, 255, 0.2);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            margin-bottom: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }
        
        .forecast-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .forecast-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0;
        }
        
        .see-hourly {
            color: #64beff;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }
        
        .cal-header {
            text-align: center;
            color: #8b949e;
            font-size: 0.85rem;
            font-weight: 500;
            padding-bottom: 8px;
        }
        
        .cal-cell {
            background: rgba(10, 15, 25, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 10px;
            text-align: left;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .cal-cell:hover {
            background: rgba(10, 15, 25, 0.6);
            border-color: rgba(100, 190, 255, 0.3);
            transform: translateY(-2px);
        }
        
        .cal-cell.today {
            background: #3b82f6;
            border: 1px solid #60a5fa;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
        }
        
        .cal-day {
            font-size: 0.9rem;
            color: #a9bfd4;
            font-weight: 500;
            margin-bottom: 8px;
            align-self: flex-start;
        }
        
        .cal-cell.today .cal-day {
            color: #ffffff;
            font-weight: 700;
        }
        
        .cal-icon {
            font-size: 1.5rem;
            margin-bottom: 8px;
        }
        
        .cal-temp {
            font-size: 0.85rem;
            color: #ffffff;
            font-weight: 500;
        }
        
        .cal-temp span {
            color: #8b949e;
        }
        
        .summary-chips {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 16px;
            justify-content: center;
        }
        
        .chip {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .chip-sunny { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
        .chip-cloudy { background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); }
        .chip-rainy { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
        .chip-snowy { background: rgba(6, 182, 212, 0.15); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.3); }
        
        .summary-text {
            text-align: center;
            color: #a9bfd4;
            font-size: 0.95rem;
            margin-top: 16px;
            line-height: 1.5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="weather-scene" aria-hidden="true">
        <div class="weather-sun"></div>
        <div class="weather-cloud cloud-a"></div>
        <div class="weather-cloud cloud-b"></div>
        <div class="weather-cloud cloud-c"></div>
        <div class="weather-mist"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 3. CONSTANTS
# ============================================================
STATIONS = [
    ("Anand Vihar", 28.6508, 77.3152),
    ("Connaught Place", 28.6280, 77.2090),
    ("Gurugram Cyber City", 28.4947, 77.0880),
    ("Noida Sector 62", 28.6200, 77.3640),
    ("Okhla Phase 3", 28.5300, 77.2800),
    ("Punjabi Bagh", 28.6630, 77.1250),
    ("IIT Delhi", 28.5921, 77.1925),
    ("Dwarka", 28.5921, 77.0452),
    ("Rohini", 28.7041, 77.0852),
    ("Ghaziabad", 28.6692, 77.4538),
]

SEVERITY_ORDER = ["Normal", "Moderate Heatwave", "Severe Heatwave"]

# ============================================================
# 4. SIDEBAR CONTROLS
# ============================================================
st.sidebar.title("⚙️ Control Center")

plotly_template = "plotly_dark"

forecast_horizon = st.sidebar.slider(
    "Forecast Window (hours)",
    min_value=6,
    max_value=48,
    value=24,
    step=6,
)

alert_threshold = st.sidebar.selectbox(
    "Thermal Alert Filter",
    ["All Levels", *SEVERITY_ORDER],
)

show_synthetic_data = st.sidebar.checkbox(
    "Show synthetic forecast data",
    value=True,
)

auto_refresh = st.sidebar.checkbox(
    "Simulate live refresh",
    value=True,
    help="Refreshes the demo every 2 seconds so the dashboard feels live.",
)

seed = st.sidebar.number_input(
    "Simulation Seed",
    min_value=1,
    max_value=9999,
    value=42,
    step=1,
    help="Use the same seed for repeatable demo data.",
)

# ============================================================
# 5. DATA GENERATION
# ============================================================

# 1. REAL BACKEND FORECAST FETCHER
@st.cache_data(ttl=60)  # Cache for 60 seconds to avoid spamming the backend
def fetch_backend_forecast(location: str, hours: int) -> pd.DataFrame:
    """Fetches real forecast data from the FastAPI backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/forecast",
            json={
                "location": location,
                "date": datetime.now().strftime("%Y-%m-%d"), 
                "hours_ahead": hours,
                "include_uncertainty": True
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        # Convert the nested "points" list into a flat Pandas DataFrame
        df = pd.DataFrame(data["points"])
        
        # Add a "Time" column to match what your existing frontend charts expect
        df["Time"] = pd.to_datetime(df["timestamp"]).dt.strftime("%H:%M")
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to fetch forecast from backend: {e}")
        return None


# 2. MOCK DATA GENERATORS (For parts of the dashboard without backend endpoints yet)
@st.cache_data(show_spinner=False)
def generate_stations(seed_value: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed_value)
    names = [x[0] for x in STATIONS]
    latitudes = [x[1] for x in STATIONS]
    longitudes = [x[2] for x in STATIONS]

    temperature = rng.uniform(38.5, 45.2, len(STATIONS))
    humidity = rng.uniform(25, 55, len(STATIONS))
    wind_speed = rng.uniform(2, 12, len(STATIONS))
    aqi = rng.integers(180, 451, len(STATIONS))
    pm25 = rng.uniform(80, 350, len(STATIONS))
    pm10 = rng.uniform(150, 500, len(STATIONS))

    thermal_stress = np.select(
        [temperature > 42, temperature > 40],
        ["Severe Heatwave", "Moderate Heatwave"],
        default="Normal",
    )

    df = pd.DataFrame({
        "name": names, "latitude": latitudes, "longitude": longitudes,
        "temperature": temperature, "humidity": humidity, "wind_speed": wind_speed,
        "aqi": aqi, "pm25": pm25, "pm10": pm10, "thermal_stress": thermal_stress,
    })
    df["Thermal_Stress_Index"] = df["temperature"] * (1 + df["humidity"] / 200) - df["wind_speed"] * 0.08
    return df

@st.cache_data(show_spinner=False)
def generate_forecast_fallback(seed_value: int, hours: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed_value + 100)
    hour_index = np.arange(hours)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    temp_base = 40.5
    temp_cycle = 3.2 * np.sin(2 * np.pi * (hour_index - 6) / 24)
    temperature = temp_base + temp_cycle + rng.normal(0, 0.45, hours)
    aqi_base = 315
    aqi_cycle = -18 * np.sin(2 * np.pi * (hour_index - 6) / 24)
    aqi = np.clip(aqi_base + aqi_cycle + rng.normal(0, 18, hours), 50, 500)
    pm25 = np.clip(195 - 20 * np.sin(2 * np.pi * (hour_index - 6) / 24) + rng.normal(0, 9, hours), 20, 500)
    pm10 = np.clip(pm25 * rng.uniform(1.65, 2.05, hours), 40, 700)
    timestamps = [now + timedelta(hours=int(h)) for h in hour_index]
    return pd.DataFrame({
        "Time": timestamps, "Temperature (°C)": temperature, "AQI": aqi,
        "PM2.5 (µg/m³)": pm25, "PM10 (µg/m³)": pm10,
        "NO₂ (µg/m³)": rng.uniform(40, 120, hours), "O₃ (µg/m³)": rng.uniform(30, 90, hours),
    })

@st.cache_data(show_spinner=False)
def generate_weekly(seed_value: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed_value + 200)
    dates = pd.date_range(start=datetime.now(), periods=7, freq="D")
    max_temp = rng.uniform(42, 46, 7)
    min_temp = rng.uniform(31, 37, 7)
    avg_temp = (max_temp + min_temp) / 2
    avg_aqi = rng.uniform(260, 420, 7)
    risk = np.select([max_temp >= 45, max_temp >= 43, avg_aqi >= 350], ["Severe", "High", "Moderate"], default="Low")
    return pd.DataFrame({"Date": dates, "Avg_Temp": avg_temp, "Max_Temp": max_temp, "Min_Temp": min_temp, "Avg_AQI": avg_aqi, "Heatwave_Risk": risk})

@st.cache_data(show_spinner=False)
def generate_heatmap(seed_value: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed_value + 300)
    names = [x[0] for x in STATIONS]
    hours = [f"{h:02d}:00" for h in range(24)]
    values = rng.uniform(90, 360, (len(names), 24))
    return pd.DataFrame(values, index=names, columns=hours)


# ============================================================
# 6. LOAD + FILTER DATA
# ============================================================
# 1. Try to get REAL forecast from backend first
forecast = fetch_backend_forecast(location="Anand Vihar", hours=forecast_horizon)

# 2. If backend is down, gracefully fall back to synthetic data so the app doesn't crash
if forecast is None:
    forecast = generate_forecast_fallback(seed, forecast_horizon)

# 3. Load the rest of the dashboard data (still using synthetic for now)
all_data = generate_stations(seed)
weekly = generate_weekly(seed)
heatmap = generate_heatmap(seed)

# 4. Apply sidebar filters
filtered_data = all_data.copy()
if alert_threshold != "All Levels":
    filtered_data = filtered_data[filtered_data["thermal_stress"] == alert_threshold]







#------------------------------code_break--------------------------
# @st.cache_data(show_spinner=False)
# def generate_stations(seed_value: int) -> pd.DataFrame:
#     rng = np.random.default_rng(seed_value)

#     names = [x[0] for x in STATIONS]
#     latitudes = [x[1] for x in STATIONS]
#     longitudes = [x[2] for x in STATIONS]

#     temperature = rng.uniform(38.5, 45.2, len(STATIONS))
#     humidity = rng.uniform(25, 55, len(STATIONS))
#     wind_speed = rng.uniform(2, 12, len(STATIONS))
#     aqi = rng.integers(180, 451, len(STATIONS))
#     pm25 = rng.uniform(80, 350, len(STATIONS))
#     pm10 = rng.uniform(150, 500, len(STATIONS))

#     thermal_stress = np.select(
#         [temperature > 42, temperature > 40],
#         ["Severe Heatwave", "Moderate Heatwave"],
#         default="Normal",
#     )

#     df = pd.DataFrame(
#         {
#             "name": names,
#             "latitude": latitudes,
#             "longitude": longitudes,
#             "temperature": temperature,
#             "humidity": humidity,
#             "wind_speed": wind_speed,
#             "aqi": aqi,
#             "pm25": pm25,
#             "pm10": pm10,
#             "thermal_stress": thermal_stress,
#         }
#     )

#     # A simple demo index. It is explicitly a simulation metric, not UTCI.
#     df["Thermal_Stress_Index"] = (
#         df["temperature"] * (1 + df["humidity"] / 200)
#         - df["wind_speed"] * 0.08
#     )

#     return df


# @st.cache_data(show_spinner=False)
# def generate_forecast(seed_value: int, hours: int) -> pd.DataFrame:
#     rng = np.random.default_rng(seed_value + 100)
#     hour_index = np.arange(hours)
#     now = datetime.now().replace(minute=0, second=0, microsecond=0)

#     # Diurnal temperature pattern.
#     temp_base = 40.5
#     temp_cycle = 3.2 * np.sin(2 * np.pi * (hour_index - 6) / 24)
#     temperature = temp_base + temp_cycle + rng.normal(0, 0.45, hours)

#     # Pollution is modeled independently with a mild inverse relationship
#     # to temperature plus random variation for demonstration purposes.
#     aqi_base = 315
#     aqi_cycle = -18 * np.sin(2 * np.pi * (hour_index - 6) / 24)
#     aqi = np.clip(aqi_base + aqi_cycle + rng.normal(0, 18, hours), 50, 500)

#     pm25 = np.clip(
#         195 - 20 * np.sin(2 * np.pi * (hour_index - 6) / 24)
#         + rng.normal(0, 9, hours),
#         20,
#         500,
#     )

#     pm10 = np.clip(pm25 * rng.uniform(1.65, 2.05, hours), 40, 700)

#     timestamps = [now + timedelta(hours=int(h)) for h in hour_index]

#     return pd.DataFrame(
#         {
#             "Time": timestamps,
#             "Temperature (°C)": temperature,
#             "AQI": aqi,
#             "PM2.5 (µg/m³)": pm25,
#             "PM10 (µg/m³)": pm10,
#             "NO₂ (µg/m³)": rng.uniform(40, 120, hours),
#             "O₃ (µg/m³)": rng.uniform(30, 90, hours),
#         }
#     )


# @st.cache_data(show_spinner=False)
# def generate_weekly(seed_value: int) -> pd.DataFrame:
#     rng = np.random.default_rng(seed_value + 200)
#     dates = pd.date_range(
#         start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
#         periods=7,
#         freq="D",
#     )

#     max_temp = rng.uniform(42, 46, 7)
#     min_temp = rng.uniform(31, 37, 7)
#     avg_temp = (max_temp + min_temp) / 2
#     avg_aqi = rng.uniform(260, 420, 7)

#     risk = np.select(
#         [max_temp >= 45, max_temp >= 43, avg_aqi >= 350],
#         ["Severe", "High", "Moderate"],
#         default="Low",
#     )

#     return pd.DataFrame(
#         {
#             "Date": dates,
#             "Avg_Temp": avg_temp,
#             "Max_Temp": max_temp,
#             "Min_Temp": min_temp,
#             "Avg_AQI": avg_aqi,
#             "Heatwave_Risk": risk,
#         }
#     )


# @st.cache_data(show_spinner=False)
# def generate_heatmap(seed_value: int) -> pd.DataFrame:
#     rng = np.random.default_rng(seed_value + 300)
#     names = [x[0] for x in STATIONS]
#     hours = [f"{h:02d}:00" for h in range(24)]

#     values = rng.uniform(90, 360, (len(names), 24))
#     return pd.DataFrame(values, index=names, columns=hours)


# ============================================================
# 6. LOAD + FILTER DATA
# ============================================================
# all_data = generate_stations(seed)
# forecast = generate_forecast(seed, forecast_horizon)
# weekly = generate_weekly(seed)
# heatmap = generate_heatmap(seed)

# filtered_data = all_data.copy()
# if alert_threshold != "All Levels":
#     filtered_data = filtered_data[
#         filtered_data["thermal_stress"] == alert_threshold
#     ]

# ============================================================
# 7. HEADER
# ============================================================
st.markdown(
    '<div class="main-title">🌡️ Air Pollution–Weather Coupled Forecasting System</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Ministry of Earth Sciences (MoES) | SIH26082 — Delhi NCR Region</div>',
    unsafe_allow_html=True,
)

status_col1, status_col2, status_col3 = st.columns([1.2, 1.2, 2])
with status_col1:
    st.success("● SYSTEM ONLINE")
with status_col2:
    st.info(f"● {len(filtered_data)} zones selected")
with status_col3:
    st.caption(
        f"Last simulated update: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}"
    )

st.markdown("---")

# ============================================================
# 8. KPI CARDS
# ============================================================
k1, k2, k3, k4, k5 = st.columns(5)

avg_temp = filtered_data["temperature"].mean() if not filtered_data.empty else np.nan
peak_aqi = filtered_data["aqi"].max() if not filtered_data.empty else np.nan
avg_pm25 = filtered_data["pm25"].mean() if not filtered_data.empty else np.nan
severe_count = int((all_data["thermal_stress"] == "Severe Heatwave").sum())
high_aqi_count = int((all_data["aqi"] >= 300).sum())

k1.metric("🌡️ Avg Temperature", f"{avg_temp:.1f} °C" if not np.isnan(avg_temp) else "—")
k2.metric("🌫️ Peak AQI", f"{peak_aqi:.0f}" if not np.isnan(peak_aqi) else "—")
k3.metric("💨 Avg PM2.5", f"{avg_pm25:.0f} µg/m³" if not np.isnan(avg_pm25) else "—")
k4.metric("🔥 Severe Heat Zones", severe_count)
k5.metric("⚠️ AQI ≥ 300", high_aqi_count)

# ============================================================
# 8.5 30-DAY FORECAST SECTION
# ============================================================
calendar_html = """<div class="forecast-container">
<div class="forecast-header">
<h3 class="forecast-title">Delhi 30-Days (September 2026) Weather Forecast</h3>
<a href="#" class="see-hourly">See Hourly ↗</a>
</div>
<div style="display: flex; gap: 32px; flex-wrap: wrap;">
<div style="flex: 2; min-width: 400px;">
<div class="calendar-grid">
<div class="cal-header">Sun</div>
<div class="cal-header">Mon</div>
<div class="cal-header">Tue</div>
<div class="cal-header">Wed</div>
<div class="cal-header">Thu</div>
<div class="cal-header">Fri</div>
<div class="cal-header">Sat</div>
"""

# Sept 1 2026 is Tuesday. Sun, Mon = 2 hidden cells.
calendar_html += '<div class="cal-cell" style="visibility: hidden;"></div>' * 2

import random
rng_cal = random.Random(42)

for day in range(1, 31):
    is_today = (day == 7)
    today_class = " today" if is_today else ""
    if day in [4, 8, 15, 22]: icon = "☀️"
    elif day in [2, 9, 16]: icon = "☁️"
    else: icon = "🌧️"
    
    high_temp = rng_cal.randint(34, 42)
    low_temp = high_temp - rng_cal.randint(6, 10)
    
    calendar_html += f"""<div class="cal-cell{today_class}">
<div class="cal-day">{day}{" Today" if is_today else ""}</div>
<div class="cal-icon">{icon}</div>
<div class="cal-temp">{high_temp}° <span>/ {low_temp}°</span></div>
</div>\n"""

calendar_html += """</div>
</div>
<div style="flex: 1; min-width: 250px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
<style>
.donut-chart {
width: 180px;
height: 180px;
border-radius: 50%;
background: conic-gradient(
#f59e0b 0% 17.4%, 
#a855f7 17.4% 30.4%, 
#3b82f6 30.4% 100%, 
#06b6d4 100% 100%
);
display: flex;
align-items: center;
justify-content: center;
margin: 0 auto 20px auto;
}
.donut-inner {
width: 130px;
height: 130px;
background: rgba(22, 33, 46, 0.95);
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
color: white;
font-size: 1.2rem;
font-weight: 600;
text-align: center;
line-height: 1.2;
}
</style>
<div class="donut-chart">
<div class="donut-inner">30<br>Days</div>
</div>
<div class="summary-chips">
<div class="chip chip-sunny">☀️ Sunny</div>
<div class="chip chip-cloudy">☁️ Cloudy</div>
<div class="chip chip-rainy">🌧️ Rainy</div>
<div class="chip chip-snowy">❄️ Snowy</div>
</div>
<p class="summary-text">The monthly weather averages in Delhi consist of 4 sunny days, 3 cloudy days, 16 rainy days, and 0 snowy days.</p>
</div>
</div>
</div>
"""
st.markdown(calendar_html, unsafe_allow_html=True)

# ============================================================
# 9. TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🗺️ Geospatial Map",
        "📊 Forecast",
        "📈 Analytics",
        "🔥 Thermal Stress",
        "🚨 Advisories",
    ]
)

# ============================================================
# TAB 1 — MAP
# ============================================================
with tab1:
    st.subheader("🌍 Delhi NCR — Google-Style Satellite Risk Map")
    st.markdown(
        '<div class="map-caption">High-resolution satellite imagery • Risk-zone pulse effect • '
        'Circle size = temperature intensity • Color = thermal-risk level</div>',
        unsafe_allow_html=True,
    )

    map_data = all_data.copy()

    color_map = {
        "Normal": [34, 197, 94, 210],
        "Moderate Heatwave": [245, 158, 11, 225],
        "Severe Heatwave": [239, 68, 68, 235],
    }

    map_data["color"] = map_data["thermal_stress"].map(color_map)

    # Google satellite imagery tile layer. This is the closest visual match
    # to the Google Earth screenshot you provided.
    #
    # NOTE: This endpoint is useful for a local/demo prototype. For a
    # production deployment, use an official Google Maps Platform tile/API
    # integration with the appropriate API key and licensing.
    satellite_layer = pdk.Layer(
        "TileLayer",
        data="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        min_zoom=0,
        max_zoom=20,
        tile_sijze=256,
        opacity=1.0,
        pickable=False,
    )

    # Main station markers.
    risk_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[longitude, latitude]",
        get_fill_color="color",
        get_radius="temperature * 42",
        radius_min_pixels=7,
        radius_max_pixels=45,
        pickable=True,
        auto_highlight=True,
        stroked=True,
        get_line_color="[255, 255, 255, 180]",
        line_width_min_pixels=1,
    )

    # Larger transparent rings give the stations a radar/pulse appearance.
    pulse_data = map_data.copy()
    pulse_data["pulse_color"] = pulse_data["color"].apply(
        lambda c: [c[0], c[1], c[2], 55]
    )

    pulse_layer = pdk.Layer(
        "ScatterplotLayer",
        data=pulse_data,
        get_position="[longitude, latitude]",
        get_fill_color="[0, 0, 0, 0]",
        get_line_color="pulse_color",
        get_radius="temperature * 70",
        radius_min_pixels=14,
        radius_max_pixels=62,
        stroked=True,
        filled=False,
        line_width_min_pixels=2,
    )
    
    view_state = pdk.ViewState(
        latitude=28.6139,
        longitude=77.2090,
        zoom=10.2,
        pitch=0,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=[satellite_layer, pulse_layer, risk_layer],
        initial_view_state=view_state,
        tooltip={
            "html": """
                <b>{name}</b><br/>
                🌡️ Temperature: {temperature}°C<br/>
                🌫️ AQI: {aqi}<br/>
                💨 PM2.5: {pm25} µg/m³<br/>
                💧 Humidity: {humidity}%<br/>
                🔥 Risk: {thermal_stress}
            """,
            "style": {
                "backgroundColor": "rgba(7,17,31,.94)",
                "color": "white",
            },
        },
    )

    st.pydeck_chart(deck, use_container_width=True)

    st.markdown(
        f"""
        <div style="
            margin-top:-8px;
            padding:10px 14px;
            border-radius:12px;
            background:linear-gradient(
                90deg,
                rgba(0,180,255,.08),
                rgba(255,120,40,.08),
                rgba(0,180,255,.08)
            );
            border:1px solid rgba(100,190,255,.15);
            overflow:hidden;
        ">
            <div style="
                white-space:nowrap;
                animation: radarMove 12s linear infinite;
                color:#b9d8ef;
                font-size:13px;
            ">
                ◉ SATELLITE FEED • ◉ {len(map_data)} MONITORED ZONES
                • ◉ THERMAL + AQI RISK SCAN ACTIVE • ◉ SYSTEM ONLINE
            </div>
        </div>
        <style>
            @keyframes radarMove {{
                0% {{ transform: translateX(0); }}
                100% {{ transform: translateX(-18%); }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Station Ranking")
    ranking = all_data[
        ["name", "temperature", "aqi", "pm25", "thermal_stress"]
    ].sort_values(["aqi", "temperature"], ascending=False)

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True,
        column_config={
            "temperature": st.column_config.NumberColumn("Temp °C", format="%.1f"),
            "aqi": st.column_config.NumberColumn("AQI", format="%.0f"),
            "pm25": st.column_config.NumberColumn("PM2.5", format="%.1f"),
        },
    )

# ============================================================
# TAB 2 — FORECAST
# ============================================================
with tab2:
    st.subheader(f"📊 Next {forecast_horizon}-Hour Forecast")

    if not show_synthetic_data:
        st.warning(
            "Synthetic forecast display is disabled. Enable it from the sidebar to view simulated forecast data."
        )
    else:
        left, right = st.columns(2)

        with left:
            fig_temp = go.Figure()
            fig_temp.add_trace(
                go.Scatter(
                    x=forecast["Time"],
                    y=forecast["Temperature (°C)"],
                    mode="lines+markers",
                    name="Temperature",
                    line=dict(width=3),
                    fill="tozeroy",
                    opacity=0.9,
                )
            )
            fig_temp.add_hline(
                y=42,
                line_dash="dash",
                annotation_text="Severe threshold",
            )
            fig_temp.update_layout(
                title="🌡️ Temperature Forecast",
                xaxis_title="Time",
                yaxis_title="°C",
                template=plotly_template,
                hovermode="x unified",
                height=380,
            )
            st.plotly_chart(fig_temp, use_container_width=True)

        with right:
            fig_aqi = go.Figure()
            fig_aqi.add_trace(
                go.Scatter(
                    x=forecast["Time"],
                    y=forecast["AQI"],
                    mode="lines+markers",
                    name="AQI",
                    line=dict(width=3),
                    fill="tozeroy",
                    opacity=0.9,
                )
            )
            fig_aqi.add_hline(y=300, line_dash="dash", annotation_text="High-risk zone")
            fig_aqi.update_layout(
                title="🌫️ AQI Forecast",
                xaxis_title="Time",
                yaxis_title="AQI",
                template=plotly_template,
                hovermode="x unified",
                height=380,
            )
            st.plotly_chart(fig_aqi, use_container_width=True)

        fig_pm = go.Figure()
        fig_pm.add_trace(
            go.Scatter(
                x=forecast["Time"],
                y=forecast["PM2.5 (µg/m³)"],
                mode="lines",
                name="PM2.5",
                line=dict(width=2.5),
            )
        )
        fig_pm.add_trace(
            go.Scatter(
                x=forecast["Time"],
                y=forecast["PM10 (µg/m³)"],
                mode="lines",
                name="PM10",
                line=dict(width=2.5),
            )
        )
        fig_pm.update_layout(
            title="💨 Particulate Matter Forecast",
            xaxis_title="Time",
            yaxis_title="µg/m³",
            template=plotly_template,
            hovermode="x unified",
            height=380,
        )
        st.plotly_chart(fig_pm, use_container_width=True)

        st.markdown("### Forecast Data")
        st.dataframe(
            forecast,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Time": st.column_config.DatetimeColumn(format="DD MMM HH:mm"),
                "Temperature (°C)": st.column_config.NumberColumn(format="%.1f"),
                "AQI": st.column_config.NumberColumn(format="%.0f"),
                "PM2.5 (µg/m³)": st.column_config.NumberColumn(format="%.1f"),
                "PM10 (µg/m³)": st.column_config.NumberColumn(format="%.1f"),
            },
        )

# ============================================================
# TAB 3 — ANALYTICS
# ============================================================
with tab3:
    st.subheader("📈 Advanced Analytics")

    c1, c2 = st.columns(2)

    with c1:
        fig_week_temp = go.Figure()
        days = weekly["Date"].dt.strftime("%a")

        fig_week_temp.add_trace(
            go.Bar(x=days, y=weekly["Max_Temp"], name="Max Temp")
        )
        fig_week_temp.add_trace(
            go.Bar(x=days, y=weekly["Min_Temp"], name="Min Temp")
        )
        fig_week_temp.update_layout(
            title="7-Day Temperature Outlook",
            barmode="group",
            template=plotly_template,
            height=380,
        )
        st.plotly_chart(fig_week_temp, use_container_width=True)

    with c2:
        fig_week_aqi = px.bar(
            weekly,
            x=days,
            y="Avg_AQI",
            color="Heatwave_Risk",
            title="7-Day AQI & Heat Risk",
        )
        fig_week_aqi.update_layout(
            template=plotly_template,
            height=380,
            xaxis_title="Day",
            yaxis_title="Average AQI",
        )
        st.plotly_chart(fig_week_aqi, use_container_width=True)

    st.markdown("### 🔥 Hourly PM2.5 Heatmap")

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap.values,
            x=heatmap.columns,
            y=heatmap.index,
            colorscale="RdYlGn_r",
            text=np.round(heatmap.values, 0),
            texttemplate="%{text}",
            colorbar_title="PM2.5",
        )
    )
    fig_heatmap.update_layout(
        title="Pollution Intensity by Station & Hour",
        template=plotly_template,
        height=480,
        xaxis_title="Hour",
        yaxis_title="Station",
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("### 🔗 Parameter Correlations")
    correlation = all_data[
        ["temperature", "humidity", "wind_speed", "aqi", "pm25", "pm10"]
    ].corr()

    fig_corr = go.Figure(
        data=go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.columns,
            colorscale="Viridis",
            zmin=-1,
            zmax=1,
            text=correlation.round(2).values,
            texttemplate="%{text}",
        )
    )
    fig_corr.update_layout(
        title="Correlation Matrix",
        template=plotly_template,
        height=430,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ============================================================
# TAB 4 — THERMAL STRESS
# ============================================================
with tab4:
    st.subheader("🔥 Thermal Stress Analysis")

    avg_tsi = all_data["Thermal_Stress_Index"].mean()

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=avg_tsi,
            title={"text": "Average Simulated Thermal Stress Index"},
            delta={"reference": 45},
            gauge={
                "axis": {"range": [30, 60]},
                "steps": [
                    {"range": [30, 40], "color": "#90EE90"},
                    {"range": [40, 50], "color": "#FFD93D"},
                    {"range": [50, 60], "color": "#FF6B6B"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 55,
                },
            },
        )
    )
    gauge.update_layout(template=plotly_template, height=360)
    st.plotly_chart(gauge, use_container_width=True)

    left, right = st.columns(2)

    with left:
        tsi_sorted = all_data.sort_values(
            "Thermal_Stress_Index", ascending=True
        )
        fig_tsi = px.bar(
            tsi_sorted,
            x="Thermal_Stress_Index",
            y="name",
            orientation='h',
            color="Thermal_Stress_Index",
            color_continuous_scale="RdYlGn_r",
            title="Station-wise Thermal Stress",
        )
        fig_tsi.update_layout(template=plotly_template, height=430)
        st.plotly_chart(fig_tsi, use_container_width=True)

    with right:
        fig_scatter = px.scatter(
            all_data,
            x="temperature",
            y="humidity",
            size="Thermal_Stress_Index",
            color="thermal_stress",
            hover_name="name",
            title="Temperature vs Humidity",
        )
        fig_scatter.update_layout(
            template=plotly_template,
            height=430,
            xaxis_title="Temperature °C",
            yaxis_title="Humidity %",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### Detailed Thermal Metrics")
    st.dataframe(
        all_data[
            [
                "name",
                "temperature",
                "humidity",
                "wind_speed",
                "Thermal_Stress_Index",
                "thermal_stress",
            ]
        ].sort_values("Thermal_Stress_Index", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "temperature": st.column_config.NumberColumn("Temp °C", format="%.1f"),
            "humidity": st.column_config.NumberColumn("Humidity %", format="%.1f"),
            "wind_speed": st.column_config.NumberColumn("Wind m/s", format="%.1f"),
            "Thermal_Stress_Index": st.column_config.NumberColumn("TSI", format="%.2f"),
        },
    )

# ============================================================
# TAB 5 — ADVISORIES
# ============================================================
with tab5:
    st.subheader("🚨 Emergency Response & Mitigation Center")

    severe_count = int(
        (all_data["thermal_stress"] == "Severe Heatwave").sum()
    )
    moderate_count = int(
        (all_data["thermal_stress"] == "Moderate Heatwave").sum()
    )
    normal_count = len(all_data) - severe_count - moderate_count

    if severe_count >= 5:
        alert_level = "🔴 RED ALERT"
        alert_text = "Multiple zones show severe thermal stress."
    elif severe_count >= 3 or moderate_count >= 6:
        alert_level = "🟠 ORANGE ALERT"
        alert_text = "Elevated heat stress requires coordinated mitigation."
    else:
        alert_level = "🟡 YELLOW ALERT"
        alert_text = "Conditions require monitoring and preparedness."

    st.markdown(
        f"""
        <div class="status-card">
            <h2>{alert_level}</h2>
            <p>{alert_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns(3)
    a1.error(f"🔴 Severe: {severe_count}")
    a2.warning(f"🟠 Moderate: {moderate_count}")
    a3.success(f"🟢 Normal: {normal_count}")

    st.markdown("### 👷 Construction & Outdoor Workers")
    st.error(
        """
        **Operational guidance for peak heat periods**
        - Schedule heavy outdoor work outside peak heat where possible.
        - Provide shaded recovery areas and frequent hydration breaks.
        - Use a buddy system for heat-stress monitoring.
        - Escalate workers showing signs of heat illness to appropriate medical care.
        """
    )

    st.markdown("### 🚗 Traffic & Municipal Management")
    st.warning(
        """
        **Pollution mitigation**
        - Prioritize high-AQI traffic corridors for monitoring.
        - Increase dust-control and road-cleaning activity where appropriate.
        - Optimize traffic flow around persistent congestion hotspots.
        - Use station-level AQI trends to prioritize interventions.
        """
    )

    st.markdown("### 👨‍⚕️ Public Health")
    st.info(
        """
        **Public advisory**
        - Reduce strenuous outdoor activity during severe heat or pollution episodes.
        - Keep indoor spaces well ventilated or filtered as appropriate.
        - Vulnerable people should follow advice from their healthcare professionals.
        - Seek urgent medical help for severe breathing difficulty, chest pain,
          confusion, fainting, or suspected heat illness.
        """
    )

    st.markdown("### 🏛️ Institutional Response")
    st.success(
        """
        **Coordination priorities**
        - Maintain a common operating picture across agencies.
        - Identify high-risk zones and prioritize resources.
        - Prepare cooling, medical, transport, and public-information capacity.
        - Review alert status as new observations arrive.
        """
    )

    st.markdown("---")
    st.markdown("### 🚨 Live Alert Feed")

    now = datetime.now()
    alerts = pd.DataFrame(
        {
            "Time": [
                now - timedelta(minutes=15),
                now - timedelta(hours=1, minutes=30),
                now - timedelta(hours=3, minutes=45),
            ],
            "Location": [
                "Okhla Phase 3",
                "Anand Vihar",
                "Gurugram Cyber City",
            ],
            "Severity": ["CRITICAL", "HIGH", "MODERATE"],
            "Message": [
                "AQI 410 — severe pollution event detected.",
                "Temperature 44.1°C — extreme heat condition detected.",
                "Combined heat-pollution event — enhanced monitoring recommended.",
            ],
        }
    )

    def highlight_severity(value):
        styles = {
            "CRITICAL": "background-color: #dc2626; color: white; font-weight: bold;",
            "HIGH": "background-color: #f59e0b; color: black; font-weight: bold;",
            "MODERATE": "background-color: #facc15; color: black;",
        }
        return styles.get(value, "")

    # pandas >= 2.x: Styler.map replaces the removed Styler.applymap API.
    st.dataframe(
        alerts.style.map(highlight_severity, subset=["Severity"]),
        use_container_width=True,
        hide_index=True,
        height=220,
    )

# ============================================================
# 10. FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#8b949e; font-size:12px;">
        <p>🌍 Smart India Hackathon 2026 | Problem ID: SIH26082</p>
        <p>Delhi NCR Heat & Air Early Warning System</p>
        <p>Streamlit • Plotly • PyDeck • Synthetic Demonstration Data</p>
        <p><b>Note:</b> Synthetic values are for demonstration and UI prototyping,
        not operational public-safety forecasting.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Optional lightweight refresh loop for demo presentations.
if auto_refresh:
    import time
    time.sleep(2)
    st.rerun()
