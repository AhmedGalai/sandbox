import time
from datetime import datetime
import requests
import streamlit as st
import plotly.graph_objects as go
from collections import deque

# ============================================================================
# CONFIGURATION
# ============================================================================
DEFAULT_SENSOR_IP = "192.168.178.189"
MAX_HISTORY_POINTS = 50

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="DHT Sensor Monitor",
    page_icon="*",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "sensor_ip" not in st.session_state:
    st.session_state.sensor_ip = DEFAULT_SENSOR_IP

if "sensor_history" not in st.session_state:
    st.session_state.sensor_history = {
        "timestamps": deque(maxlen=MAX_HISTORY_POINTS),
        "temperatures": deque(maxlen=MAX_HISTORY_POINTS),
        "humidities": deque(maxlen=MAX_HISTORY_POINTS)
    }

if "last_update" not in st.session_state:
    st.session_state.last_update = None

# ============================================================================
# DHT SENSOR API FUNCTIONS
# ============================================================================
def get_dht_data(ip: str, timeout: int = 3):
    """Get temperature and humidity data from DHT sensor"""
    try:
        url = f"http://{ip}/api/dht"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        # Check if response is ok
        if not data.get("ok", False):
            return {"success": False, "error": data.get("error", "Unknown error from sensor")}

        # ESP sends temperature_c and humidity_percent
        return {
            "success": True,
            "temperature": data.get("temperature_c", 0.0),
            "humidity": data.get("humidity_percent", 0.0),
            "timestamp": datetime.now()
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Connection timeout after {timeout}s"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": f"Cannot connect to device at {ip}"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except ValueError:
        return {"success": False, "error": "Invalid JSON response from device"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def store_sensor_data(temperature: float, humidity: float, timestamp: datetime):
    """Store sensor data in history"""
    st.session_state.sensor_history["timestamps"].append(timestamp)
    st.session_state.sensor_history["temperatures"].append(temperature)
    st.session_state.sensor_history["humidities"].append(humidity)

def create_temperature_chart():
    """Create temperature chart"""
    history = st.session_state.sensor_history

    if len(history["timestamps"]) == 0:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(history["timestamps"]),
        y=list(history["temperatures"]),
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        title="Temperature History",
        xaxis_title="Time",
        yaxis_title="Temperature (C)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_humidity_chart():
    """Create humidity chart"""
    history = st.session_state.sensor_history

    if len(history["timestamps"]) == 0:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(history["timestamps"]),
        y=list(history["humidities"]),
        mode='lines+markers',
        name='Humidity',
        line=dict(color='#4ECDC4', width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        title="Humidity History",
        xaxis_title="Time",
        yaxis_title="Humidity (%)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Custom CSS
st.markdown("""
    <style>
    .sensor-card {
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
    .status-ok {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-error {
        color: #f44336;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("DHT Sensor Monitor")
st.caption(f"Last updated: {st.session_state.last_update or 'Never'}")

st.divider()

# Sidebar
with st.sidebar:
    st.header("Settings")

    st.subheader("Sensor Configuration")
    sensor_ip = st.text_input(
        "Sensor IP Address",
        value=st.session_state.sensor_ip,
        help="Enter the IP address of your DHT sensor"
    )

    if sensor_ip != st.session_state.sensor_ip:
        st.session_state.sensor_ip = sensor_ip

    st.divider()

    st.subheader("Refresh Settings")
    auto_refresh = st.toggle("Auto Refresh", value=False)
    refresh_interval = st.slider("Refresh Interval (seconds)", 2, 30, 5)

    st.divider()

    st.subheader("API Timeout")
    api_timeout = st.slider("Request Timeout (seconds)", 1, 10, 3)

    st.divider()

    if st.button("Refresh Now", use_container_width=True):
        st.rerun()

    if st.button("Clear History", use_container_width=True):
        st.session_state.sensor_history = {
            "timestamps": deque(maxlen=MAX_HISTORY_POINTS),
            "temperatures": deque(maxlen=MAX_HISTORY_POINTS),
            "humidities": deque(maxlen=MAX_HISTORY_POINTS)
        }
        st.success("History cleared!")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    st.subheader("About")
    st.info("""
    DHT Sensor Monitor

    Features:
    - Real-time temperature monitoring
    - Real-time humidity monitoring
    - Historical data plotting
    - Configurable refresh rate
    """)

# Main content
st.header("Sensor Data")

# Fetch sensor data
with st.spinner("Reading sensor data..."):
    sensor_data = get_dht_data(st.session_state.sensor_ip, timeout=api_timeout)

if sensor_data['success']:
    # Store data in history
    store_sensor_data(
        sensor_data['temperature'],
        sensor_data['humidity'],
        sensor_data['timestamp']
    )

    # Update last update time
    st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display current readings
    st.markdown("<div class='sensor-card'>", unsafe_allow_html=True)

    st.subheader("Current Readings")
    st.markdown("<span class='status-ok'>Connected</span>", unsafe_allow_html=True)

    # Metrics in columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Temperature",
            value=f"{sensor_data['temperature']:.1f} C",
            delta=None
        )
    with col2:
        st.metric(
            label="Humidity",
            value=f"{sensor_data['humidity']:.1f} %",
            delta=None
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Display charts
    st.header("Historical Data")

    col1, col2 = st.columns(2)

    with col1:
        temp_chart = create_temperature_chart()
        if temp_chart:
            st.plotly_chart(temp_chart, use_container_width=True)
        else:
            st.info("No temperature data available yet")

    with col2:
        humidity_chart = create_humidity_chart()
        if humidity_chart:
            st.plotly_chart(humidity_chart, use_container_width=True)
        else:
            st.info("No humidity data available yet")

    # Display data table
    if len(st.session_state.sensor_history["timestamps"]) > 0:
        st.divider()
        st.subheader("Recent Readings")

        # Create dataframe from history
        import pandas as pd
        df = pd.DataFrame({
            "Time": list(st.session_state.sensor_history["timestamps"]),
            "Temperature (C)": [f"{t:.1f}" for t in st.session_state.sensor_history["temperatures"]],
            "Humidity (%)": [f"{h:.1f}" for h in st.session_state.sensor_history["humidities"]]
        })
        # Reverse to show most recent first
        df = df.iloc[::-1].reset_index(drop=True)
        st.dataframe(df, use_container_width=True, height=300)

else:
    # Display error
    st.markdown("<div class='sensor-card'>", unsafe_allow_html=True)
    st.subheader("Sensor Status")
    st.markdown("<span class='status-error'>Connection Error</span>", unsafe_allow_html=True)
    st.error(f"Error: {sensor_data['error']}")
    st.info(f"Trying to connect to: {st.session_state.sensor_ip}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.warning("""
    **Troubleshooting:**
    - Check if the sensor device is powered on
    - Verify the IP address is correct
    - Ensure the device is on the same network
    - Check if the /api/dht endpoint is available
    """)

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.divider()
st.caption("DHT Sensor Monitor v1.0")
