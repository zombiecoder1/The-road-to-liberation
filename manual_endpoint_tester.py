#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Endpoint Tester for Liberation AI Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script allows manual testing of each endpoint to verify functionality.
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(url, method="GET", data=None, description=""):
    """Test a single endpoint and display results."""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    print(f"   Method: {method}")
    
    try:
        start_time = time.time()
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   🕐 Response Time: {response_time:.2f} ms")
        print(f"   📦 Content Length: {len(response.content)} bytes")
        
        # Show a preview of the response (first 200 chars)
        content_preview = response.text[:200]
        if len(response.text) > 200:
            content_preview += "..."
        print(f"   📄 Preview: {content_preview}")
        
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Error: Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Error: Connection failed")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Main function to run manual endpoint tests."""
    base_url = "http://localhost:8080"
    
    print("=" * 60)
    print("🔧 MANUAL ENDPOINT TESTER")
    print("=" * 60)
    print(f"Testing endpoints at: {base_url}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define endpoints to test
    endpoints = [
        {
            "url": f"{base_url}/",
            "method": "GET",
            "description": "Root Endpoint"
        },
        {
            "url": f"{base_url}/status",
            "method": "GET",
            "description": "Status Endpoint"
        },
        {
            "url": f"{base_url}/models",
            "method": "GET",
            "description": "Models Endpoint"
        },
        {
            "url": f"{base_url}/system",
            "method": "GET",
            "description": "System Information Endpoint"
        },
        {
            "url": f"{base_url}/health",
            "method": "GET",
            "description": "Health Check Endpoint"
        },
        {
            "url": f"{base_url}/chat",
            "method": "POST",
            "data": {"prompt": "Hello, how are you?"},
            "description": "Chat Endpoint"
        }
    ]
    
    # Test each endpoint
    passed_tests = 0
    total_tests = len(endpoints)
    
    for endpoint in endpoints:
        success = test_endpoint(
            endpoint["url"],
            endpoint["method"],
            endpoint.get("data"),
            endpoint["description"]
        )
        
        if success:
            passed_tests += 1
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All endpoints are functioning correctly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} endpoint(s) failed.")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()