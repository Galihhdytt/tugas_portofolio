#!/usr/bin/env python
"""
API Test untuk Contact Endpoint
Pastikan aplikasi sudah running: python app.py
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 60)
print("TEST CONTACT API ENDPOINT")
print("=" * 60)

# Test data
test_payload = {
    "name": "Galih Test User",
    "email": "test@example.com",
    "message": "Ini adalah test message dari API test script"
}

print(f"\n📤 Sending POST request to /api/contact")
print(f"   Payload: {json.dumps(test_payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/contact",
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"   Body: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Contact form berhasil!")
        print("   Email akan dikirim ke galihhdytt@gmail.com")
    else:
        print(f"\n❌ Error: {response.json().get('error', 'Unknown error')}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Tidak bisa terhubung ke http://localhost:5000")
    print("   Pastikan aplikasi sudah running: python app.py")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
