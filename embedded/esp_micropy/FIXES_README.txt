DHT SENSOR DASHBOARD - FIXES AND TROUBLESHOOTING
================================================

PROBLEMS FIXED:
--------------

1. JSON Key Mismatch
   - ESP was sending: temperature_c, humidity_percent
   - Dashboard was expecting: temperature, humidity
   - FIXED: Updated both app.py and app_simple.py to use correct keys

2. Socket Exhaustion on ESP32
   - Sockets were not being closed properly
   - No timeout on client connections
   - Memory leaks due to no garbage collection
   - FIXED: Added proper socket handling, timeouts, and garbage collection

3. Missing Error Handling
   - No validation of ESP response
   - No proper timeout handling
   - FIXED: Added comprehensive error handling and validation


CHANGES MADE TO main.py (ESP32):
--------------------------------

1. Added garbage collection (gc module)
2. Added socket timeout (2 seconds) to prevent hanging connections
3. Changed send() to sendall() for reliable data transmission
4. Added error handling in serve_forever()
5. Reduced listen backlog from 5 to 3
6. Added request counter and periodic garbage collection (every 10 requests)
7. Added memory monitoring and logging
8. Added exception handling for accept() failures


CHANGES MADE TO app.py and app_simple.py:
-----------------------------------------

1. Fixed JSON key mapping:
   - temperature_c -> temperature
   - humidity_percent -> humidity
2. Added validation of "ok" field in response
3. Better error messages for sensor failures


HOW TO FIX YOUR ESP32:
---------------------

1. Re-upload the fixed main.py to your ESP32:

   ampy --port /dev/ttyUSB0 put main.py

   OR use your preferred upload method (Thonny, mpremote, etc.)

2. Reboot the ESP32 (unplug and plug back in)

3. Check the serial monitor to see:
   - WiFi connection status
   - IP address (should be 192.168.178.189)
   - "HTTP server listening on port 80" message


TESTING YOUR ESP32:
-------------------

Use the diagnostic script to test your ESP32:

   python test_esp.py

Or specify a different IP:

   python test_esp.py 192.168.178.189

The script will:
- Test the /health endpoint
- Test the /api/dht endpoint
- Send 10 rapid requests to check stability
- Show detailed error messages


NETWORK TROUBLESHOOTING:
-----------------------

If ping fails (like you experienced):

1. Check ESP32 WiFi connection:
   - Connect via serial monitor
   - Look for "WiFi connected. IP: x.x.x.x" message
   - If not connected, check SSID and password in main.py

2. Network issues:
   - Make sure ESP32 and computer are on same network
   - Check router settings (some routers isolate WiFi clients)
   - Try disabling firewall temporarily
   - Check if router assigned different IP (check DHCP table)

3. ESP32 crashed:
   - Serial monitor will show errors or reset messages
   - Reboot ESP32
   - Check power supply (needs stable 3.3V or 5V)

4. Socket exhaustion (before fix):
   - ESP stops responding after several requests
   - Needs reboot to work again
   - FIXED by the changes in main.py


RUNNING THE DASHBOARD:
----------------------

After fixing the ESP32:

1. Install dependencies:
   pip install streamlit requests plotly pandas

2. Run the simple dashboard:
   streamlit run app_simple.py

3. Or run the full dashboard:
   streamlit run app.py

4. Dashboard settings:
   - Default IP: 192.168.178.189
   - Change IP in sidebar if needed
   - Enable auto-refresh for real-time monitoring
   - Adjust timeout if your network is slow


COMMON ERRORS AND SOLUTIONS:
----------------------------

Error: "Connection timeout after 3s"
Solution:
  - ESP32 is not responding
  - Check if ESP32 is on and connected to WiFi
  - Try increasing timeout in sidebar

Error: "Cannot connect to device"
Solution:
  - Wrong IP address
  - ESP32 not on same network
  - Firewall blocking connection

Error: "Invalid JSON response"
Solution:
  - ESP32 crashed or sent incomplete response
  - Reboot ESP32
  - Check serial monitor for errors

Error: "HTTP error: 503"
Solution:
  - DHT sensor read error
  - Sensor might be disconnected
  - Check DHT sensor wiring (GPIO 14)

Dashboard shows 0.0 for temperature/humidity:
Solution:
  - JSON keys were wrong (now fixed)
  - Check if test_esp.py shows correct values
  - Clear browser cache and refresh


EXPECTED BEHAVIOR:
-----------------

ESP32:
- Responds to ping within 10-50ms
- /health returns: {"ok": true, "uptime_ms": ...}
- /api/dht returns:
  {
    "ok": true,
    "temperature_c": 25.0,
    "humidity_percent": 60.0,
    "sample_age_ms": 100,
    "uptime_ms": 123456
  }

Dashboard:
- Connects within 1-3 seconds
- Shows current temperature and humidity
- Plots update with each refresh
- Charts show historical data (up to 50 points)


MONITORING ESP32 HEALTH:
------------------------

Connect to serial monitor to see:
- WiFi connection status
- Client connection messages
- Request handling logs
- Memory usage every 10 requests
- Any error messages

Example healthy output:
  WiFi connected. IP: 192.168.178.189
  HTTP server listening on port 80
  Client connected from ('192.168.178.68', 54321)
  Client connected from ('192.168.178.68', 54322)
  Handled 10 requests. Free mem: 25600 bytes
  ...


PERFORMANCE NOTES:
------------------

DHT11 sensor:
- Minimum read interval: 2 seconds
- Reading more frequently will return cached values
- This is normal behavior to protect the sensor

ESP32 socket handling:
- Can handle ~3 concurrent connections
- Closes connections immediately after response
- Garbage collection runs every 10 requests
- Should handle continuous requests without crashing


CONTACT AND SUPPORT:
--------------------

If issues persist after applying these fixes:
1. Check serial monitor output from ESP32
2. Run test_esp.py and share the output
3. Verify all files are updated (main.py, app.py, app_simple.py)
4. Try a different computer or network
