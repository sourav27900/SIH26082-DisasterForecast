import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# 1. Page Configuration
st.set_page_config(
    page_title="Delhi NCR Heat & Air Early Warning System",
    page_icon="🌍",
    layout="wide",
)

# 2. App Header
st.title("🌡️ Air Pollution-Weather Coupled Forecasting System")
st.markdown("**Ministry of Earth Sciences (MoES) | SIH26082 — Delhi NCR Region**")
st.markdown("---")

# 3. Sidebar Configuration Controls
st.sidebar.header("⚙️ Simulation Controls")
forecast_horizon = st.sidebar.slider("Forecast Window (Hours Ahead)", 1, 48, 24)
alert_threshold = st.sidebar.selectbox(
    "Filter Alert Level",
    ["All Levels", "Severe Heatwave", "Moderate Heatwave", "Normal"],
)
simulate_cpp_boost = st.sidebar.checkbox(
    "Enable C++ High-Performance Grid Engine", value=True
)

# 4. Mock Delhi NCR Spatial Data (Coordinates around Delhi)
data = pd.DataFrame(
    {
        "name": [
            "Anand Vihar",
            "Connaught Place",
            "Gurugram Cyber City",
            "Noida Sector 62",
            "Okhla Phase 3",
            "Punjabi Bagh",
        ],
        "latitude": [28.6508, 28.6280, 28.4947, 28.6200, 28.5300, 28.6630],
        "longitude": [77.3152, 77.2090, 77.0880, 77.3640, 77.2800, 77.1250],
        "temperature": [43.5, 41.2, 42.0, 40.8, 44.1, 42.5],
        "aqi": [385, 290, 310, 275, 410, 350],
        "thermal_stress": [
            "Severe Heatwave",
            "Moderate Heatwave",
            "Severe Heatwave",
            "Moderate Heatwave",
            "Severe Heatwave",
            "Severe Heatwave",
        ],
    }
)

# Filter data based on sidebar selection
if alert_threshold != "All Levels":
    data = data[data["thermal_stress"] == alert_threshold]

# 5. Dashboard Layout Tabs
tab1, tab2, tab3 = st.tabs(
    [
        "🗺️ Delhi NCR Geospatial Map",
        "📊 Detailed Zone Metrics",
        "💡 Actionable Advisories",
    ]
)

with tab1:
    st.subheader("Live Thermal Stress & Pollution Hotspot Map")
    st.caption("Hover or click nodes to check station-specific micro-climate data.")

    # PyDeck Map Configuration for Delhi NCR
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position="[longitude, latitude]",
        get_color="[255, 60, 60, 200]",
        get_radius="temperature * 35",
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=28.6139,
        longitude=77.2090,
        zoom=10.5,
        pitch=40,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Station: {name}\nTemp: {temperature}°C\nAQI: {aqi}"},
    )
    st.pydeck_chart(r)

with tab2:
    st.subheader("Station-Wise Analytical Breakdown")

    # Metrics Row
    col1, col2, col3 = st.columns(3)
    col1.metric("Average NCR Temp", f"{data['temperature'].mean():.1f} °C", "+1.8°C")
    col2.metric("Peak AQI Recorded", f"{data['aqi'].max()}", "Severe")
    col3.metric(
        "Processing Backend",
        "C++ / Pybind11" if simulate_cpp_boost else "Pure Python",
        "Optimized",
    )

    st.markdown("### Raw Parameter Table")
    st.dataframe(data, use_container_width=True)

    st.markdown("### 24-Hour Temperature & Pollution Trend Simulation")
    chart_data = pd.DataFrame(
        np.random.randn(24, 2) * [2, 20] + [40, 300],
        columns=["Temperature (°C)", "AQI Level"],
    )
    st.line_chart(chart_data)

with tab3:
    st.subheader("Emergency Response & Mitigation Protocol (MoES Guidelines)")
    st.error(
        "🚨 **RED ALERT ACTIVE:** Severe thermal stress detected in East and South Delhi industrial belts."
    )
    st.markdown("""
    * **For Construction Workers:** Mandatory halting of heavy outdoor labor between 1:00 PM and 4:30 PM.
    * **For Municipal Bodies:** Initiate water-sprinkling routines across identified high-density traffic corridors to control particulate resuspension.
    * **Vulnerable Groups:** Citizens with respiratory conditions are advised to keep emergency inhalers accessible and stay indoors.
    """)
