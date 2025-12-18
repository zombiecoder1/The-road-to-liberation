#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Usage Script for The Road to Liberation Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script demonstrates how to use the platform for local AI development.
"""

import json
import requests
import time

def demo_platform_check():
    """Demonstrate platform checking functionality."""
    print("🎯 DEMO: Platform Status Check")
    print("=" * 40)
    
    # Import and run our platform checker
    from liberation_ai_platform import LocalAIPlatform
    
    platform = LocalAIPlatform()
    
    # Check Ollama status
    print("🔍 Checking Ollama Status...")
    status = platform.check_ollama_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # List models
    print("\n📚 Listing Available Models...")
    models = platform.list_available_models()
    print(json.dumps(models, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 40)

def demo_local_proxy_service():
    """Demonstrate local proxy service usage."""
    print("🌐 DEMO: Local Proxy Service Usage")
    print("=" * 40)
    
    # Note: This assumes the proxy service is running on localhost:8080
    base_url = "http://127.0.0.1:8080"
    
    try:
        # Check if service is running
        print("📡 Checking if proxy service is running...")
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Proxy service is running!")
            print(json.dumps(status_data, indent=2, ensure_ascii=False))
        else:
            print("⚠️  Proxy service returned unexpected status")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Proxy service is not running. Please start it with run_proxy_service.bat")
        return
    except Exception as e:
        print(f"❌ Error connecting to proxy service: {e}")
        return
    
    try:
        # Get system information
        print("\n🖥️  Getting System Information...")
        response = requests.get(f"{base_url}/system")
        if response.status_code == 200:
            system_data = response.json()
            print(json.dumps(system_data, indent=2, ensure_ascii=False))
        
        # List models
        print("\n📚 Listing Models via Proxy...")
        response = requests.get(f"{base_url}/models")
        if response.status_code == 200:
            models_data = response.json()
            print(json.dumps(models_data, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"❌ Error communicating with proxy service: {e}")
    
    print("\n" + "=" * 40)

def demo_ai_interaction():
    """Demonstrate AI interaction through the platform."""
    print("🤖 DEMO: AI Interaction")
    print("=" * 40)
    
    from liberation_ai_platform import LocalAIPlatform
    
    platform = LocalAIPlatform()
    
    # Check if Ollama is running first
    status = platform.check_ollama_status()
    if not status.get("ollama_running", False):
        print("❌ Ollama is not running. Please start it first.")
        return
    
    # Send a test prompt
    print("💬 Sending Test Prompt to Local AI...")
    test_prompt = "Explain in one sentence why local AI development is important for privacy."
    
    response = platform.send_test_prompt(
        model_name="llama3.1:latest",
        prompt=test_prompt
    )
    
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response.get('response', 'No response')}")
    print(f"Processing Time: {response.get('total_duration', 0) / 1000000000:.2f} seconds")
    
    print("\n" + "=" * 40)

def demo_json_reporting():
    """Demonstrate JSON reporting capabilities."""
    print("📊 DEMO: JSON Reporting")
    print("=" * 40)
    
    from liberation_ai_platform import LocalAIPlatform
    
    platform = LocalAIPlatform()
    
    # Run some checks to populate the status
    platform.check_ollama_status()
    platform.get_system_resources()
    platform.list_available_models()
    
    # Generate and display report
    print("📄 Generating Platform Report...")
    report = platform.generate_json_report()
    
    # Pretty print a subset of the report
    print("Project:", report.get("project", "Unknown"))
    print("Version:", report.get("version", "Unknown"))
    print("Generation Time:", report.get("generation_time", "Unknown"))
    
    status = report.get("status", {})
    print("Platform Initialized:", status.get("platform_initialized", "Unknown"))
    print("Ollama Running:", status.get("ollama_running", "Unknown"))
    print("Models Found:", status.get("model_list", {}).get("models_found", "Unknown"))
    
    # Save the full report
    if platform.save_json_report("demo_report.json"):
        print("✅ Full report saved as 'demo_report.json'")
    else:
        print("❌ Failed to save report")
    
    print("\n" + "=" * 40)

def main():
    """Main demo function."""
    print("🚀 The Road to Liberation - Demo Usage")
    print("=" * 50)
    print("This script demonstrates the capabilities of the local AI platform.")
    print()
    
    # Run demos
    demo_platform_check()
    print()
    time.sleep(1)
    
    demo_json_reporting()
    print()
    time.sleep(1)
    
    demo_ai_interaction()
    print()
    time.sleep(1)
    
    print("💡 Note: To demo the proxy service, please run 'run_proxy_service.bat' first,")
    print("   then run this demo script again to see the proxy service in action.")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")

if __name__ == "__main__":
    main()