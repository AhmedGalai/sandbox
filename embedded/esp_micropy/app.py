import time
from datetime import datetime
import requests
import streamlit as st

# ============================================================================
# CONFIGURATION
# ============================================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Shelly Pro Plug API endpoints configuration
# Add your Shelly devices here
SHELLY_DEVICES = {
    "Device 1": {
        "ip": "192.168.1.100",
        "name": "Living Room Plug",
        "enabled": False  # Set to True when you have actual device
    },
    "Device 2": {
        "ip": "192.168.1.101",
        "name": "Bedroom Plug",
        "enabled": False
    },
    "Device 3": {
        "ip": "192.168.1.102",
        "name": "Kitchen Plug",
        "enabled": False
    },
    "Device 4": {
        "ip": "192.168.1.103",
        "name": "Office Plug",
        "enabled": False
    },
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Smart Home Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "device_states" not in st.session_state:
    st.session_state.device_states = {k: {"on": False, "power": 0.0, "energy": 0.0}
                                       for k in SHELLY_DEVICES.keys()}

if "last_update" not in st.session_state:
    st.session_state.last_update = None

if "devices_config" not in st.session_state:
    st.session_state.devices_config = SHELLY_DEVICES.copy()

# ============================================================================
# SHELLY API FUNCTIONS
# ============================================================================
def shelly_get_status(ip: str, timeout: int = 3):
    """Get status from Shelly Pro Plug"""
    try:
        url = f"http://{ip}/rpc/Switch.GetStatus?id=0"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "on": data.get("output", False),
            "power": data.get("apower", 0.0),
            "energy": data.get("aenergy", {}).get("total", 0.0) / 1000.0,  # Convert to kWh
            "temperature": data.get("temperature", {}).get("tC", None)
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Connection timeout after {timeout}s"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": f"Cannot connect to device at {ip}"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except ValueError as e:
        return {"success": False, "error": "Invalid JSON response from device"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def shelly_toggle(ip: str, turn_on: bool, timeout: int = 3):
    """Toggle Shelly Pro Plug on/off"""
    try:
        state = "on" if turn_on else "off"
        url = f"http://{ip}/rpc/Switch.Set?id=0&on={str(turn_on).lower()}"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return {"success": True, "state": state}
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Connection timeout after {timeout}s"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": f"Cannot connect to device at {ip}"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

# ============================================================================
# LOGIN MODAL
# ============================================================================
def show_login():
    """Display blocking login modal"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background-color: #f0f2f6;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    st.title("🔐 Login Required")
    st.write("Please enter your credentials to access the dashboard")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful! Redirecting...")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid username or password")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================================
# AUTHENTICATION CHECK
# ============================================================================
if not st.session_state.authenticated:
    show_login()

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Custom CSS
st.markdown("""
    <style>
    .device-card {
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
    }
    .status-on {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-off {
        color: #f44336;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([6, 1])
with col1:
    st.title("🏠 Smart Home Dashboard")
    st.caption(f"Last updated: {st.session_state.last_update or 'Never'}")
with col2:
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("Refresh Settings")
    auto_refresh = st.toggle("Auto Refresh", value=False)
    refresh_interval = st.slider("Refresh Interval (seconds)", 2, 30, 5)

    st.divider()

    st.subheader("API Timeout")
    api_timeout = st.slider("Request Timeout (seconds)", 1, 10, 3)

    st.divider()

    if st.button("🔄 Refresh All Devices", use_container_width=True):
        st.rerun()

    st.divider()

    st.subheader("About")
    st.info("""
    This dashboard controls multiple Shelly Pro Plug devices.

    **Features:**
    - Real-time device status
    - Power monitoring
    - Energy consumption tracking
    - Remote control
    """)

# Main content with tabs
tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Settings"])

# ============================================================================
# DASHBOARD TAB
# ============================================================================
with tab1:
    st.header("Device Controls")

    # Create grid for devices
    devices_list = list(st.session_state.devices_config.items())
    num_devices = len(devices_list)

    # Display devices in rows of 2
    for i in range(0, num_devices, 2):
        cols = st.columns(2)

        for j, col in enumerate(cols):
            idx = i + j
            if idx >= num_devices:
                break

            device_key, device_config = devices_list[idx]

            with col:
                with st.container():
                    st.markdown(f"<div class='device-card'>", unsafe_allow_html=True)

                    # Device header
                    device_col1, device_col2 = st.columns([3, 1])
                    with device_col1:
                        st.subheader(f"🔌 {device_config['name']}")
                    with device_col2:
                        if not device_config['enabled']:
                            st.markdown("**`Placeholder`**")

                    if device_config['enabled']:
                        try:
                            # Fetch status
                            status = shelly_get_status(device_config['ip'], timeout=api_timeout)

                            if status['success']:
                                # Update session state
                                st.session_state.device_states[device_key] = {
                                    "on": status['on'],
                                    "power": status['power'],
                                    "energy": status['energy']
                                }

                                # Display status
                                state_text = "ON" if status['on'] else "OFF"
                                state_class = "status-on" if status['on'] else "status-off"
                                st.markdown(f"Status: <span class='{state_class}'>{state_text}</span>",
                                          unsafe_allow_html=True)

                                # Metrics
                                metric_col1, metric_col2 = st.columns(2)
                                with metric_col1:
                                    st.metric("Power", f"{status['power']:.1f} W")
                                with metric_col2:
                                    st.metric("Energy", f"{status['energy']:.2f} kWh")

                                if status.get('temperature'):
                                    st.metric("Temperature", f"{status['temperature']:.1f} °C")

                                # Control buttons
                                btn_col1, btn_col2 = st.columns(2)
                                with btn_col1:
                                    if st.button("Turn ON", key=f"on_{device_key}",
                                               disabled=status['on'], use_container_width=True):
                                        try:
                                            result = shelly_toggle(device_config['ip'], True, timeout=api_timeout)
                                            if result['success']:
                                                st.success("Turned ON")
                                                time.sleep(0.5)
                                                st.rerun()
                                            else:
                                                st.error(f"Error: {result['error']}")
                                        except Exception as e:
                                            st.error(f"Failed to turn on: {str(e)}")

                                with btn_col2:
                                    if st.button("Turn OFF", key=f"off_{device_key}",
                                               disabled=not status['on'], use_container_width=True):
                                        try:
                                            result = shelly_toggle(device_config['ip'], False, timeout=api_timeout)
                                            if result['success']:
                                                st.success("Turned OFF")
                                                time.sleep(0.5)
                                                st.rerun()
                                            else:
                                                st.error(f"Error: {result['error']}")
                                        except Exception as e:
                                            st.error(f"Failed to turn off: {str(e)}")
                            else:
                                st.error(f"Connection Error: {status['error']}")
                                st.info(f"IP: {device_config['ip']}")
                        except Exception as e:
                            st.error(f"Unexpected error: {str(e)}")
                            st.info(f"IP: {device_config['ip']}")
                    else:
                        # Placeholder device
                        st.info(f"""
                        **Configuration Needed**

                        IP Address: `{device_config['ip']}`

                        Enable this device in the Settings tab.
                        """)

                    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# SETTINGS TAB
# ============================================================================
with tab2:
    st.header("API Endpoint Configuration")
    st.write("Configure your Shelly devices below. Changes are saved in session state.")

    st.divider()

    for device_key, device_config in st.session_state.devices_config.items():
        with st.expander(f"🔌 {device_key} - {device_config['name']}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                new_name = st.text_input(
                    "Device Name",
                    value=device_config['name'],
                    key=f"name_{device_key}"
                )

                new_ip = st.text_input(
                    "IP Address",
                    value=device_config['ip'],
                    key=f"ip_{device_key}",
                    help="Enter the IP address of your Shelly device (e.g., 192.168.1.100)"
                )

            with col2:
                new_enabled = st.toggle(
                    "Enable Device",
                    value=device_config['enabled'],
                    key=f"enabled_{device_key}"
                )

                st.write("")
                st.write("")

                if st.button("Test Connection", key=f"test_{device_key}", use_container_width=True):
                    with st.spinner("Testing connection..."):
                        try:
                            test_result = shelly_get_status(new_ip, timeout=3)
                            if test_result['success']:
                                st.success(f"Connected successfully! Device is {'ON' if test_result['on'] else 'OFF'}")
                            else:
                                st.error(f"Connection failed: {test_result['error']}")
                        except Exception as e:
                            st.error(f"Connection test failed: {str(e)}")

            if st.button("Save Changes", key=f"save_{device_key}", use_container_width=True):
                st.session_state.devices_config[device_key] = {
                    'name': new_name,
                    'ip': new_ip,
                    'enabled': new_enabled
                }
                st.success(f"Settings saved for {device_key}")
                time.sleep(0.5)
                st.rerun()

            st.divider()

    st.divider()

    # Bulk actions
    st.subheader("Bulk Actions")
    bulk_col1, bulk_col2 = st.columns(2)

    with bulk_col1:
        if st.button("Enable All Devices", use_container_width=True):
            for key in st.session_state.devices_config:
                st.session_state.devices_config[key]['enabled'] = True
            st.success("All devices enabled")
            time.sleep(0.5)
            st.rerun()

    with bulk_col2:
        if st.button("Disable All Devices", use_container_width=True):
            for key in st.session_state.devices_config:
                st.session_state.devices_config[key]['enabled'] = False
            st.success("All devices disabled")
            time.sleep(0.5)
            st.rerun()

# Auto refresh
if auto_refresh:
    st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(refresh_interval)
    st.rerun()
else:
    st.session_state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Footer
st.divider()
st.caption("Smart Home Dashboard v1.0 | Shelly Pro Plug Controller")
