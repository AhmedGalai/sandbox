#!/usr/bin/env python3
"""
Simple test script to diagnose ESP32 DHT sensor connection issues
"""

import requests
import json
import time
import sys

ESP_IP = "192.168.178.189"
TIMEOUT = 5

def test_connection(ip):
    """Test basic connection to ESP32"""
    print(f"\n{'='*60}")
    print(f"Testing ESP32 at {ip}")
    print(f"{'='*60}\n")

    # Test 1: Health check
    print("Test 1: Health endpoint (/health)")
    try:
        url = f"http://{ip}/health"
        print(f"  URL: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text}")
        data = response.json()
        print(f"  Uptime: {data.get('uptime_ms', 0) / 1000:.1f} seconds")
        print("  Result: PASS\n")
    except requests.exceptions.Timeout:
        print(f"  Result: FAIL - Timeout after {TIMEOUT}s\n")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  Result: FAIL - Connection error: {e}\n")
        return False
    except Exception as e:
        print(f"  Result: FAIL - {e}\n")
        return False

    # Test 2: DHT endpoint
    print("Test 2: DHT sensor endpoint (/api/dht)")
    try:
        url = f"http://{ip}/api/dht"
        print(f"  URL: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        print(f"  Status Code: {response.status_code}")
        print(f"  Raw Response: {response.text}")

        data = response.json()
        print(f"  Parsed JSON:")
        for key, value in data.items():
            print(f"    {key}: {value}")

        if data.get('ok'):
            print(f"\n  Temperature: {data.get('temperature_c', 'N/A')} C")
            print(f"  Humidity: {data.get('humidity_percent', 'N/A')} %")
            print(f"  Sample Age: {data.get('sample_age_ms', 0)} ms")
            print("  Result: PASS\n")
        else:
            print(f"  Error from sensor: {data.get('error', 'Unknown')}")
            print("  Result: FAIL - Sensor error\n")
            return False

    except requests.exceptions.Timeout:
        print(f"  Result: FAIL - Timeout after {TIMEOUT}s\n")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  Result: FAIL - Connection error: {e}\n")
        return False
    except ValueError as e:
        print(f"  Result: FAIL - Invalid JSON: {e}\n")
        return False
    except Exception as e:
        print(f"  Result: FAIL - {e}\n")
        return False

    # Test 3: Multiple rapid requests
    print("Test 3: Multiple rapid requests (10 requests)")
    success_count = 0
    fail_count = 0
    total_time = 0

    for i in range(10):
        try:
            start = time.time()
            url = f"http://{ip}/api/dht"
            response = requests.get(url, timeout=TIMEOUT)
            elapsed = time.time() - start
            total_time += elapsed

            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    success_count += 1
                    print(f"  Request {i+1}: OK ({elapsed*1000:.0f}ms)")
                else:
                    fail_count += 1
                    print(f"  Request {i+1}: FAIL - {data.get('error', 'Unknown')}")
            else:
                fail_count += 1
                print(f"  Request {i+1}: FAIL - HTTP {response.status_code}")

            time.sleep(0.2)  # Small delay between requests

        except Exception as e:
            fail_count += 1
            print(f"  Request {i+1}: FAIL - {e}")

    print(f"\n  Success: {success_count}/10")
    print(f"  Failed: {fail_count}/10")
    print(f"  Average response time: {(total_time/10)*1000:.0f}ms")

    if success_count >= 8:
        print("  Result: PASS\n")
    else:
        print("  Result: FAIL - Too many failures\n")

    return success_count >= 8

def main():
    ip = sys.argv[1] if len(sys.argv) > 1 else ESP_IP

    print("\nESP32 DHT Sensor Connection Diagnostic Tool")
    print("=" * 60)

    result = test_connection(ip)

    print("\n" + "="*60)
    if result:
        print("OVERALL RESULT: ALL TESTS PASSED")
        print("\nYour ESP32 is working correctly!")
        print("The dashboard should be able to connect now.")
    else:
        print("OVERALL RESULT: TESTS FAILED")
        print("\nTroubleshooting steps:")
        print("1. Check if ESP32 is powered on")
        print("2. Verify the IP address is correct")
        print("3. Make sure ESP32 is connected to WiFi")
        print("4. Check if ESP32 and your computer are on the same network")
        print("5. Try rebooting the ESP32")
        print("6. Re-upload the main.py file to the ESP32")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
