#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for The Road to Liberation Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script tests the core functionality of the local AI platform.
"""

import json
import sys
import os

# Add the parent directory to the path so we can import our platform module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from liberation_ai_platform import LocalAIPlatform

def test_platform_initialization():
    """Test platform initialization."""
    print("🧪 Testing Platform Initialization...")
    try:
        platform = LocalAIPlatform()
        assert platform.status["platform_initialized"] == True
        print("✅ Platform initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Platform initialization failed: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection."""
    print("\n🧪 Testing Ollama Connection...")
    try:
        platform = LocalAIPlatform()
        status = platform.check_ollama_status()
        
        # Print detailed status
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        if status.get("ollama_running", False):
            print("✅ Ollama is running locally")
            return True
        else:
            print("⚠️  Ollama is not running or not accessible")
            return False
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")
        return False

def test_model_listing():
    """Test model listing functionality."""
    print("\n🧪 Testing Model Listing...")
    try:
        platform = LocalAIPlatform()
        models = platform.list_available_models()
        
        # Print detailed model information
        print(json.dumps(models, indent=2, ensure_ascii=False))
        
        if models.get("models_found", 0) > 0:
            print("✅ Models listed successfully")
            return True
        else:
            print("⚠️  No models found or error occurred")
            return False
    except Exception as e:
        print(f"❌ Model listing test failed: {e}")
        return False

def test_system_resources():
    """Test system resources monitoring."""
    print("\n🧪 Testing System Resources Monitoring...")
    try:
        platform = LocalAIPlatform()
        resources = platform.get_system_resources()
        
        # Print detailed resource information
        print(json.dumps(resources, indent=2, ensure_ascii=False))
        
        if "error" not in resources:
            print("✅ System resources monitored successfully")
            return True
        else:
            print("⚠️  Error in system resources monitoring")
            return False
    except Exception as e:
        print(f"❌ System resources monitoring test failed: {e}")
        return False

def test_json_report_generation():
    """Test JSON report generation."""
    print("\n🧪 Testing JSON Report Generation...")
    try:
        platform = LocalAIPlatform()
        
        # Run some basic checks first to populate status
        platform.check_ollama_status()
        platform.get_system_resources()
        platform.list_available_models()
        
        report = platform.generate_json_report()
        
        # Save the report
        if platform.save_json_report("test_report.json"):
            print("✅ JSON report generated and saved successfully")
            
            # Verify the report can be read back
            try:
                with open("test_report.json", 'r', encoding='utf-8') as f:
                    loaded_report = json.load(f)
                print("✅ JSON report verified successfully")
                return True
            except Exception as e:
                print(f"⚠️  JSON report verification failed: {e}")
                return False
        else:
            print("❌ Failed to save JSON report")
            return False
    except Exception as e:
        print(f"❌ JSON report generation test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and generate a final JSON output."""
    print("🚀 Running All Tests for The Road to Liberation Platform")
    print("=" * 60)
    
    test_results = {
        "project": "The Road to Liberation - Platform Tests",
        "version": "1.0",
        "timestamp": "",
        "tests": {},
        "overall_status": "pending"
    }
    
    # Run individual tests
    tests = [
        ("platform_initialization", test_platform_initialization),
        ("ollama_connection", test_ollama_connection),
        ("model_listing", test_model_listing),
        ("system_resources", test_system_resources),
        ("json_report_generation", test_json_report_generation)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results["tests"][test_name] = {
                "passed": result,
                "status": "passed" if result else "failed"
            }
            if result:
                passed_tests += 1
        except Exception as e:
            test_results["tests"][test_name] = {
                "passed": False,
                "status": "error",
                "error": str(e)
            }
    
    # Calculate overall status
    if passed_tests == total_tests:
        test_results["overall_status"] = "all_tests_passed"
    elif passed_tests > 0:
        test_results["overall_status"] = "some_tests_passed"
    else:
        test_results["overall_status"] = "all_tests_failed"
    
    # Add timestamp
    import time
    test_results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Save test results
    try:
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Test results saved to 'test_results.json'")
    except Exception as e:
        print(f"\n❌ Failed to save test results: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Overall Status: {test_results['overall_status']}")
    
    for test_name, result in test_results["tests"].items():
        status_icon = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "💥"
        print(f"{status_icon} {test_name}: {result['status']}")
    
    print("\n" + "=" * 60)
    
    # Print final JSON output for transparency
    print("📊 FINAL TEST RESULTS (JSON FORMAT):")
    print(json.dumps(test_results, indent=2, ensure_ascii=False))
    
    return test_results

if __name__ == "__main__":
    results = run_all_tests()
    # Exit with code based on results
    if results["overall_status"] == "all_tests_passed":
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure