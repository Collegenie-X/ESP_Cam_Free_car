#!/usr/bin/env python3
"""
ESP32 제어 테스트 스크립트

LED와 카메라 설정을 독립적으로 테스트합니다.
"""

import requests
import time

# ESP32 설정
ESP32_IP = "192.168.0.65"
BASE_URL = f"http://{ESP32_IP}"

def test_connection():
    """연결 테스트"""
    print("=" * 60)
    print("🔍 ESP32 Connection Test")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=2)
        print(f"✅ Connected: {BASE_URL}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_led():
    """LED 테스트"""
    print("\n" + "=" * 60)
    print("💡 LED Control Test")
    print("=" * 60)
    
    # LED ON
    try:
        url = f"{BASE_URL}/led?state=on"
        print(f"\n1️⃣ Testing: {url}")
        response = requests.get(url, timeout=2)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        time.sleep(2)
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # LED OFF
    try:
        url = f"{BASE_URL}/led?state=off"
        print(f"\n2️⃣ Testing: {url}")
        response = requests.get(url, timeout=2)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        time.sleep(2)
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # LED Toggle
    try:
        url = f"{BASE_URL}/led?state=toggle"
        print(f"\n3️⃣ Testing: {url}")
        response = requests.get(url, timeout=2)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

def test_camera_controls():
    """카메라 제어 테스트"""
    print("\n" + "=" * 60)
    print("📷 Camera Control Test")
    print("=" * 60)
    
    params = [
        ("brightness", 2),
        ("brightness", 0),
        ("contrast", 1),
        ("saturation", -1),
    ]
    
    for param, value in params:
        try:
            url = f"{BASE_URL}/camera?param={param}&value={value}"
            print(f"\n🔧 Testing: {url}")
            response = requests.get(url, timeout=2)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ Failed: {e}")

def main():
    """메인 테스트"""
    print("\n" + "=" * 60)
    print("🧪 ESP32 Controls Test Script")
    print(f"   Target: {BASE_URL}")
    print("=" * 60)
    
    # 1. 연결 테스트
    if not test_connection():
        print("\n❌ Cannot connect to ESP32. Exiting...")
        return
    
    # 2. LED 테스트
    test_led()
    
    # 3. 카메라 제어 테스트
    test_camera_controls()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

