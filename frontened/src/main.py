# import streamlit as st
# import pandas as pd
# import numpy as np
# import pydeck as pdk

# # 1. Page Configuration
# st.set_page_config(
#     page_title="Delhi NCR Heat & Air Early Warning System",
#     page_icon="🌍",
#     layout="wide",
# )

# # 2. App Header
# st.title("🌡️ Air Pollution-Weather Coupled Forecasting System")
# st.markdown("**Ministry of Earth Sciences (MoES) | SIH26082 — Delhi NCR Region**")
# st.markdown("---")

# # 3. Sidebar Configuration Controls
# st.sidebar.header("⚙️ Simulation Controls")
# forecast_horizon = st.sidebar.slider("Forecast Window (Hours Ahead)", 1, 48, 24)
# alert_threshold = st.sidebar.selectbox(
#     "Filter Alert Level",
#     ["All Levels", "Severe Heatwave", "Moderate Heatwave", "Normal"],
# )
# simulate_cpp_boost = st.sidebar.checkbox(
#     "Enable C++ High-Performance Grid Engine", value=True
# )

# # 4. Mock Delhi NCR Spatial Data (Coordinates around Delhi)
# data = pd.DataFrame(
i
#             "Anand Vihar",
#             "Connaught Place",
#             "Gurugram Cyber City",
#             "Noida Sector 62",
#             "Okhla Phase 3",
#             "Punjabi Bagh",
#         ],
#         "latitude": [28.6508, 28.6280, 28.4947, 28.6200, 28.5300, 28.6630],
#         "longitude": [77.3152, 77.2090, 77.0880, 77.3640, 77.2800, 77.1250],
#         "temperature": [43.5, 41.2, 42.0, 40.8, 44.1, 42.5],
#         "aqi": [385, 290, 310, 275, 410, 350],
#         "thermal_stress": [
#             "Severe Heatwave",
#             "Moderate Heatwave",
#             "Severe Heatwave",
#             "Moderate Heatwave",
#             "Severe Heatwave",
#             "Severe Heatwave",
#         ],
#     }
# )

# # Filter data based on sidebar selection
# if alert_threshold != "All Levels":
#     data = data[data["thermal_stress"] == alert_threshold]

# # 5. Dashboard Layout Tabs
# tab1, tab2, tab3 = st.tabs(
#     [
#         "🗺️ Delhi NCR Geospatial Map",
#         "📊 Detailed Zone Metrics",
#         "💡 Actionable Advisories",
#     ]
# )

# with tab1:
#     st.subheader("Live Thermal Stress & Pollution Hotspot Map")
#     st.caption("Hover or click nodes to check station-specific micro-climate data.")

#     # PyDeck Map Configuration for Delhi NCR
#     layer = pdk.Layer(
#         "ScatterplotLayer",
#         data=data,
#         get_position="[longitude, latitude]",
#         get_color="[255, 60, 60, 200]",
#         get_radius="temperature * 35",
#         pickable=True,
#         auto_highlight=True,
#     )

#     view_state = pdk.ViewState(
#         latitude=28.6139,
#         longitude=77.2090,
#         zoom=10.5,
#         pitch=40,
#     )

#     r = pdk.Deck(
#         layers=[layer],
#         initial_view_state=view_state,
#         tooltip={"text": "Station: {name}\nTemp: {temperature}°C\nAQI: {aqi}"},
#     )
#     st.pydeck_chart(r)

# with tab2:
#     st.subheader("Station-Wise Analytical Breakdown")

#     # Metrics Row
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Average NCR Temp", f"{data['temperature'].mean():.1f} °C", "+1.8°C")
#     col2.metric("Peak AQI Recorded", f"{data['aqi'].max()}", "Severe")
#     col3.metric(
#         "Processing Backend",
#         "C++ / Pybind11" if simulate_cpp_boost else "Pure Python",
#         "Optimized",
#     )

#     st.markdown("### Raw Parameter Table")
#     st.dataframe(data, use_container_width=True)

#     st.markdown("### 24-Hour Temperature & Pollution Trend Simulation")
#     chart_data = pd.DataFrame(
#         np.random.randn(24, 2) * [2, 20] + [40, 300],
#         columns=["Temperature (°C)", "AQI Level"],
#     )
#     st.line_chart(chart_data)

# with tab3:
#     st.subheader("Emergency Response & Mitigation Protocol (MoES Guidelines)")
#     st.error(
#         "🚨 **RED ALERT ACTIVE:** Severe thermal stress detected in East and South Delhi industrial belts."
#     )
#     st.markdown("""
#     * **For Construction Workers:** Mandatory halting of heavy outdoor labor between 1:00 PM and 4:30 PM.
#     * **For Municipal Bodies:** Initiate water-sprinkling routines across identified high-density traffic corridors to control particulate resuspension.
#     * **Vulnerable Groups:** Citizens with respiratory conditions are advised to keep emergency inhalers accessible and stay indoors.
#     """)
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ============================================
# 1. PAGE CONFIGURATION & THEME SETUP
# ============================================
st.set_page_config(
    page_title="Delhi NCR Heat & Air Early Warning System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Dark/Light Mode Toggle
st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ============================================
# 2. SIDEBAR - THEME & CONTROLS
# ============================================
st.sidebar.markdown("### 🎨 **Theme Settings**")
theme_mode = st.sidebar.radio(
    "Select Theme", ["🌙 Dark Mode", "☀️ Light Mode"], index=0, horizontal=True
)

# Apply theme to Plotly
plotly_template = "plotly_dark" if theme_mode == "🌙 Dark Mode" else "plotly"

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Simulation Controls")
forecast_horizon = st.sidebar.slider("Forecast Window (Hours Ahead)", 1, 48, 24)
alert_threshold = st.sidebar.selectbox(
    "Filter Alert Level",
    ["All Levels", "Severe Heatwave", "Moderate Heatwave", "Normal"],
)
simulate_cpp_boost = st.sidebar.checkbox(
    "Enable C++ High-Performance Grid Engine", value=True
)
show_synthetic_data = st.sidebar.checkbox("Show Synthetic Forecast Data", value=True)

# ============================================
# 3. SYNTHETIC DATA GENERATORS
# ============================================


def generate_delhi_ncr_stations():
    """Generate Delhi NCR monitoring stations with realistic data"""
    np.random.seed(42)
    stations = {
        "name": [
            "Anand Vihar",
            "Connaught Place",
            "Gurugram Cyber City",
            "Noida Sector 62",
            "Okhla Phase 3",
            "Punjabi Bagh",
            "IIT Delhi",
            "Dwarka",
            "Rohini",
            "Ghaziabad",
        ],
        "latitude": [
            28.6508,
            28.6280,
            28.4947,
            28.6200,
            28.5300,
            28.6630,
            28.5921,
            28.5921,
            28.7041,
            28.8694,
        ],
        "longitude": [
            77.3152,
            77.2090,
            77.0880,
            77.3640,
            77.2800,
            77.1250,
            77.1925,
            77.0452,
            77.0852,
            77.5580,
        ],
        "temperature": np.random.uniform(38.5, 45.2, 10),
        "humidity": np.random.uniform(25, 55, 10),
        "wind_speed": np.random.uniform(2, 12, 10),
        "aqi": np.random.randint(180, 450, 10),
        "pm25": np.random.uniform(80, 350, 10),
        "pm10": np.random.uniform(150, 500, 10),
    }

    # Assign thermal stress based on temperature
    thermal_stress = []
    for temp in stations["temperature"]:
        if temp > 42:
            thermal_stress.append("Severe Heatwave")
        elif temp > 40:
            thermal_stress.append("Moderate Heatwave")
        else:
            thermal_stress.append("Normal")
    stations["thermal_stress"] = thermal_stress

    return pd.DataFrame(stations)


def generate_24h_forecast():
    """Generate 24-hour temperature, AQI, and pollution forecast"""
    hours = np.arange(0, 24)
    base_temp = 40
    base_aqi = 320
    base_pm25 = 200

    # Realistic diurnal cycle
    temp_cycle = base_temp + 3 * np.sin(2 * np.pi * (hours - 6) / 24)
    temp_noise = np.random.normal(0, 0.5, 24)
    temperature = temp_cycle + temp_noise

    # AQI typically inversely correlates with temperature (higher in cooler hours)
    aqi_cycle = base_aqi - 2 * np.sin(2 * np.pi * (hours - 6) / 24)
    aqi_noise = np.random.normal(0, 15, 24)
    aqi = np.clip(aqi_cycle + aqi_noise, 50, 500)

    # PM2.5 similar trend to AQI
    pm25_cycle = base_pm25 - 1.5 * np.sin(2 * np.pi * (hours - 6) / 24)
    pm25_noise = np.random.normal(0, 10, 24)
    pm25 = np.clip(pm25_cycle + pm25_noise, 30, 400)

    timestamps = [datetime.now() + timedelta(hours=int(h)) for h in hours]

    return pd.DataFrame(
        {
            "Time": timestamps,
            "Hour": hours,
            "Temperature (°C)": temperature,
            "AQI": aqi,
            "PM2.5 (µg/m³)": pm25,
            "PM10 (µg/m³)": pm25 * 1.8,
            "NO₂ (µg/m³)": np.random.uniform(40, 120, 24),
            "O₃ (µg/m³)": np.random.uniform(30, 90, 24),
        }
    )


def generate_thermal_stress_index():
    """Generate Thermal Stress Index based on temperature and humidity"""
    data = generate_delhi_ncr_stations()

    # Simple UTCI-like calculation: TSI = Temp + 0.5 * Humidity
    data["Thermal_Stress_Index"] = data["temperature"] + 0.5 * (
        data["humidity"] / 100 * data["temperature"]
    )

    return data


def generate_weekly_forecast():
    """Generate 7-day forecast"""
    days = pd.date_range(start=datetime.now(), periods=7, freq="D")

    data = {
        "Date": days,
        "Avg_Temp": np.random.uniform(39, 44, 7),
        "Max_Temp": np.random.uniform(43, 46, 7),
        "Min_Temp": np.random.uniform(32, 38, 7),
        "Avg_AQI": np.random.uniform(280, 400, 7),
        "Heatwave_Risk": np.random.choice(["Low", "Moderate", "High", "Severe"], 7),
    }

    return pd.DataFrame(data)


def generate_pollution_heatmap():
    """Generate hourly pollution heatmap data"""
    stations = generate_delhi_ncr_stations()["name"].tolist()
    hours = np.arange(0, 24)

    # PM2.5 heatmap (higher values = worse)
    heatmap_data = np.random.uniform(100, 350, size=(len(stations), 24))

    return pd.DataFrame(
        heatmap_data, index=stations, columns=[f"{h:02d}:00" for h in hours]
    )


# ============================================
# 4. LOAD DATA
# ============================================
data = generate_delhi_ncr_stations()
forecast_24h = generate_24h_forecast()
thermal_index_data = generate_thermal_stress_index()
weekly_data = generate_weekly_forecast()
pollution_heatmap = generate_pollution_heatmap()

# Filter data based on sidebar selection
if alert_threshold != "All Levels":
    data = data[data["thermal_stress"] == alert_threshold]

# ============================================
# 5. APP HEADER
# ============================================
st.title("🌡️ Air Pollution-Weather Coupled Forecasting System")
st.markdown("**Ministry of Earth Sciences (MoES) | SIH26082 — Delhi NCR Region**")

# Display theme indicator
theme_indicator = (
    "🌙 Dark Mode Active" if theme_mode == "🌙 Dark Mode" else "☀️ Light Mode Active"
)
st.caption(
    f"{theme_indicator} | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
st.markdown("---")

# ============================================
# 6. KEY METRICS - TOP ROW
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_temp = data["temperature"].mean()
    st.metric(
        "🌡️ Average NCR Temp",
        f"{avg_temp:.1f}°C",
        f"+{avg_temp - 38:.1f}°C",
        delta_color="inverse",
    )

with col2:
    peak_aqi = data["aqi"].max()
    st.metric("🌫️ Peak AQI", f"{int(peak_aqi)}", "Severe ⚠️", delta_color="inverse")

with col3:
    avg_pm25 = data["pm25"].mean()
    st.metric(
        "💨 Avg PM2.5", f"{avg_pm25:.0f} µg/m³", "Hazardous", delta_color="inverse"
    )

with col4:
    backend_status = "C++ Optimized ⚡" if simulate_cpp_boost else "Python 🐍"
    st.metric("⚙️ Backend", backend_status, "Active")

st.markdown("---")

# ============================================
# 7. DASHBOARD TABS
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🗺️ Geospatial Map",
        "📊 24H Forecast",
        "📈 Detailed Analytics",
        "🔥 Thermal Stress",
        "💡 Advisories",
    ]
)

# ============================================
# TAB 1: GEOSPATIAL MAP
# ============================================
with tab1:
    st.subheader("Live Thermal Stress & Pollution Hotspot Map")
    st.caption(
        "Hover over nodes to check station-specific micro-climate data. Node size represents temperature intensity."
    )

    # PyDeck Map
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position="[longitude, latitude]",
        get_color="[255, 60, 60, 200]",
        get_radius="temperature * 40",
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
        tooltip={
            "text": "Station: {name}\nTemp: {temperature:.1f}°C\nAQI: {aqi:.0f}\nPM2.5: {pm25:.1f}"
        },
    )
    st.pydeck_chart(r)

    # Station data table
    st.markdown("### Monitoring Stations Data")
    st.dataframe(
        data[["name", "temperature", "aqi", "pm25", "thermal_stress"]].sort_values(
            "aqi", ascending=False
        ),
        use_container_width=True,
        height=300,
    )

# ============================================
# TAB 2: 24-HOUR FORECAST
# ============================================
with tab2:
    st.subheader("24-Hour Weather & Pollution Forecast")

    col1, col2 = st.columns(2)

    # Temperature Forecast
    with col1:
        fig_temp = go.Figure()
        fig_temp.add_trace(
            go.Scatter(
                x=forecast_24h["Time"],
                y=forecast_24h["Temperature (°C)"],
                mode="lines+markers",
                name="Temperature",
                line=dict(color="#FF6B6B", width=3),
                marker=dict(size=8),
                fill="tozeroy",
                fillcolor="rgba(255, 107, 107, 0.2)",
            )
        )

        fig_temp.update_layout(
            title="🌡️ Temperature Trend (24H)",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            template=plotly_template,
            hovermode="x unified",
            height=400,
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    # AQI Forecast
    with col2:
        fig_aqi = go.Figure()
        fig_aqi.add_trace(
            go.Scatter(
                x=forecast_24h["Time"],
                y=forecast_24h["AQI"],
                mode="lines+markers",
                name="AQI",
                line=dict(color="#4ECDC4", width=3),
                marker=dict(size=8),
                fill="tozeroy",
                fillcolor="rgba(78, 205, 196, 0.2)",
            )
        )

        # Add AQI threshold lines
        fig_aqi.add_hline(
            y=200,
            line_dash="dash",
            line_color="orange",
            annotation_text="Moderate",
            annotation_position="right",
        )
        fig_aqi.add_hline(
            y=300,
            line_dash="dash",
            line_color="red",
            annotation_text="Poor",
            annotation_position="right",
        )

        fig_aqi.update_layout(
            title="🌫️ AQI Forecast (24H)",
            xaxis_title="Time",
            yaxis_title="AQI Index",
            template=plotly_template,
            hovermode="x unified",
            height=400,
        )
        st.plotly_chart(fig_aqi, use_container_width=True)

    # PM2.5 & PM10 Comparison
    fig_pm = go.Figure()
    fig_pm.add_trace(
        go.Scatter(
            x=forecast_24h["Time"],
            y=forecast_24h["PM2.5 (µg/m³)"],
            mode="lines",
            name="PM2.5",
            line=dict(color="#FF8C42", width=2.5),
        )
    )
    fig_pm.add_trace(
        go.Scatter(
            x=forecast_24h["Time"],
            y=forecast_24h["PM10 (µg/m³)"],
            mode="lines",
            name="PM10",
            line=dict(color="#A29BFE", width=2.5),
        )
    )

    fig_pm.update_layout(
        title="💨 Particulate Matter (PM2.5 & PM10) Forecast",
        xaxis_title="Time",
        yaxis_title="Concentration (µg/m³)",
        template=plotly_template,
        hovermode="x unified",
        height=400,
    )
    st.plotly_chart(fig_pm, use_container_width=True)

# ============================================
# TAB 3: DETAILED ANALYTICS
# ============================================
with tab3:
    st.subheader("Comprehensive Analytics Dashboard")

    # 7-Day Forecast
    st.markdown("### 📅 7-Day Temperature & AQI Forecast")
    col1, col2 = st.columns(2)

    with col1:
        fig_7day_temp = go.Figure()
        fig_7day_temp.add_trace(
            go.Bar(
                x=weekly_data["Date"].dt.strftime("%a"),
                y=weekly_data["Max_Temp"],
                name="Max Temp",
                marker_color="#FF6B6B",
            )
        )
        fig_7day_temp.add_trace(
            go.Bar(
                x=weekly_data["Date"].dt.strftime("%a"),
                y=weekly_data["Min_Temp"],
                name="Min Temp",
                marker_color="#4ECDC4",
            )
        )

        fig_7day_temp.update_layout(
            title="7-Day Temperature Trend",
            xaxis_title="Day",
            yaxis_title="Temperature (°C)",
            template=plotly_template,
            barmode="group",
            height=400,
        )
        st.plotly_chart(fig_7day_temp, use_container_width=True)

    with col2:
        fig_7day_aqi = px.bar(
            weekly_data,
            x=weekly_data["Date"].dt.strftime("%a"),
            y="Avg_AQI",
            color="Heatwave_Risk",
            color_discrete_map={
                "Low": "#6BCB77",
                "Moderate": "#FFD93D",
                "High": "#FF6B6B",
                "Severe": "#8B0000",
            },
            title="7-Day AQI & Heatwave Risk",
        )
        fig_7day_aqi.update_layout(
            template=plotly_template,
            height=400,
        )
        st.plotly_chart(fig_7day_aqi, use_container_width=True)

    # Pollution Heatmap
    st.markdown("### 🔥 Hourly Pollution Heatmap (PM2.5)")
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=pollution_heatmap.values,
            x=pollution_heatmap.columns,
            y=pollution_heatmap.index,
            colorscale="RdYlGn_r",
            text=pollution_heatmap.values,
            texttemplate="%{text:.0f}",
            textfont={"size": 9},
        )
    )
    fig_heatmap.update_layout(
        title="Hourly PM2.5 Distribution Across Stations",
        xaxis_title="Hour of Day",
        yaxis_title="Monitoring Station",
        template=plotly_template,
        height=400,
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Station Correlation
    st.markdown("### 📊 Parameter Correlation Matrix")
    correlation_data = data[["temperature", "humidity", "aqi", "pm25"]].corr()

    fig_corr = go.Figure(
        data=go.Heatmap(
            z=correlation_data.values,
            x=correlation_data.columns,
            y=correlation_data.columns,
            colorscale="Viridis",
            text=correlation_data.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 11},
        )
    )
    fig_corr.update_layout(
        title="Parameter Correlation Analysis",
        template=plotly_template,
        height=400,
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ============================================
# TAB 4: THERMAL STRESS INDEX
# ============================================
with tab4:
    st.subheader("🔥 Thermal Stress Index Analysis")

    thermal_index_sorted = thermal_index_data.sort_values(
        "Thermal_Stress_Index", ascending=False
    )

    # Gauge chart for overall thermal stress
    avg_tsi = thermal_index_sorted["Thermal_Stress_Index"].mean()

    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=avg_tsi,
            title={"text": "Average Thermal Stress Index"},
            delta={"reference": 45, "suffix": " vs Safe Threshold"},
            gauge={
                "axis": {"range": [30, 60]},
                "bar": {"color": "#FF6B6B"},
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
    fig_gauge.update_layout(template=plotly_template, height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Station-wise thermal stress
    col1, col2 = st.columns(2)

    with col1:
        fig_tsi_bar = px.bar(
            thermal_index_sorted,
            x="Thermal_Stress_Index",
            y="name",
            orientation="h",
            color="Thermal_Stress_Index",
            color_continuous_scale="RdYlGn_r",
            title="Station-wise Thermal Stress Index",
            labels={"name": "Station", "Thermal_Stress_Index": "TSI Value"},
        )
        fig_tsi_bar.update_layout(template=plotly_template, height=400)
        st.plotly_chart(fig_tsi_bar, use_container_width=True)

    with col2:
        fig_temp_humidity = px.scatter(
            thermal_index_data,
            x="temperature",
            y="humidity",
            size="Thermal_Stress_Index",
            color="thermal_stress",
            hover_name="name",
            color_discrete_map={
                "Normal": "#6BCB77",
                "Moderate Heatwave": "#FFD93D",
                "Severe Heatwave": "#FF6B6B",
            },
            title="Temperature vs Humidity (Size = TSI)",
        )
        fig_temp_humidity.update_layout(template=plotly_template, height=400)
        st.plotly_chart(fig_temp_humidity, use_container_width=True)

    # Thermal stress data table
    st.markdown("### Detailed Thermal Metrics")
    st.dataframe(
        thermal_index_sorted[
            [
                "name",
                "temperature",
                "humidity",
                "wind_speed",
                "Thermal_Stress_Index",
                "thermal_stress",
            ]
        ].reset_index(drop=True),
        use_container_width=True,
        height=250,
    )

# ============================================
# TAB 5: ACTIONABLE ADVISORIES
# ============================================
with tab5:
    st.subheader("Emergency Response & Mitigation Protocol")

    # Alert Level Indicator
    severe_count = len(
        thermal_index_data[thermal_index_data["thermal_stress"] == "Severe Heatwave"]
    )
    moderate_count = len(
        thermal_index_data[thermal_index_data["thermal_stress"] == "Moderate Heatwave"]
    )

    if severe_count >= 5:
        alert_level = "🔴 RED ALERT"
        alert_color = "#FF6B6B"
    elif severe_count >= 3 or moderate_count >= 6:
        alert_level = "🟠 ORANGE ALERT"
        alert_color = "#FFD93D"
    else:
        alert_level = "🟢 YELLOW ALERT"
        alert_color = "#90EE90"

    st.markdown(
        f"<h3 style='color:{alert_color}'>{alert_level} ACTIVE</h3>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.info(f"🔴 Severe Heatwave Zones: **{severe_count}** stations")
    col2.warning(f"🟠 Moderate Heatwave Zones: **{moderate_count}** stations")
    col3.success(f"🟢 Normal Zones: **{10 - severe_count - moderate_count}** stations")

    st.markdown("---")

    # Advisories by stakeholder
    st.markdown("### 👷 **Construction & Outdoor Workers**")
    st.error("""
    **MANDATORY RESTRICTIONS (1:00 PM - 4:30 PM):**
    - Halt all heavy outdoor labor during peak heat hours
    - Provide continuous access to cool water & shaded rest areas
    - Implement mandatory 2-hour rest breaks every 4 hours
    - Use heat-reflective PPE & cooling vests
    - Monitor workers for signs of heat stress (dizziness, fatigue, profuse sweating)
    """)

    st.markdown("### 🚗 **Traffic & Municipal Management**")
    st.warning("""
    **AIR QUALITY MITIGATION:**
    - Activate water-sprinkling routines on high-traffic corridors (4:00 AM & 7:00 PM)
    - Divert heavy vehicles from residential zones during peak hours
    - Increase frequency of street cleaning in industrial areas
    - Monitor real-time AQI at major intersections
    - Implement traffic signal optimization to reduce congestion
    """)

    st.markdown("### 👨‍⚕️ **Vulnerable Groups & Healthcare**")
    st.info("""
    **HEALTH ADVISORY:**
    - Individuals with asthma, COPD, cardiovascular disease: Keep inhalers & medications accessible
    - Elderly & children: Avoid outdoor activities during peak hours (1:00 PM - 5:00 PM)
    - Stay indoors with air purifiers running during Severe Air Quality alerts
    - Wear N95 masks when venturing outside (AQI > 300)
    - Hydrate adequately: Drink 3-4 liters of water daily
    - Watch for symptoms: Cough, shortness of breath, chest pain, heat exhaustion
    """)

    st.markdown("### 🏛️ **Government & Institutional Response**")
    st.success("""
    **COORDINATED ACTION PLAN:**
    - Activate Multi-Agency Crisis Response Coordination Centers
    - Deploy mobile medical units to high-risk industrial zones
    - Broadcast public service announcements every 2 hours
    - Distribute free masks & cooling kits to vulnerable populations
    - Open community cooling centers in schools & government buildings
    - Coordinate with hospitals for emergency capacity preparedness
    """)

    st.markdown("---")

    # Real-time alert feed
    st.markdown("### 🚨 Live Alert Feed")

    alerts_data = {
        "Time": [
            datetime.now() - timedelta(hours=0, minutes=15),
            datetime.now() - timedelta(hours=1, minutes=30),
            datetime.now() - timedelta(hours=3, minutes=45),
        ],
        "Location": ["Okhla Phase 3", "Anand Vihar", "Gurugram Cyber City"],
        "Severity": ["CRITICAL", "HIGH", "MODERATE"],
        "Message": [
            "AQI 410 - Severe Air Quality. All outdoor activities halted.",
            "Temperature 44.1°C - Extreme Heatwave. Emergency services on alert.",
            "Combined heat-pollution event. Worker evacuation recommended.",
        ],
    }

    alerts_df = pd.DataFrame(alerts_data)

    # Color-code by severity
    def highlight_severity(val):
        if val == "CRITICAL":
            return "background-color: #FF6B6B; color: white;"
        elif val == "HIGH":
            return "background-color: #FFD93D; color: black;"
        else:
            return "background-color: #FFE66D; color: black;"

    st.dataframe(
        alerts_df.style.applymap(highlight_severity, subset=["Severity"]),
        use_container_width=True,
        height=200,
    )

# ============================================
# 8. FOOTER
# ============================================
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>🌍 Smart India Hackathon 2026 | Problem ID: SIH26082</p>
    <p>Developed for Ministry of Earth Sciences (MoES), Government of India</p>
    <p>Powered by Streamlit • Plotly • PyDeck | Data Updates: Real-time forecasting engine</p>
</div>
""",
    unsafe_allow_html=True,
)
