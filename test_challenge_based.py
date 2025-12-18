#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Challenge-Based Test Script for Universal Launcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script demonstrates and tests the challenge-based functionality 
of the Universal Launcher for the Liberation AI Development Environment.
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from universal_launcher import UniversalLauncher

def test_local_startup_fluency():
    """Test local startup fluency challenge."""
    print("🧪 Testing Local Startup Fluency...")
    
    # Create launcher instance
    launcher = UniversalLauncher()
    
    # Run the launcher
    success = launcher.run()
    
    if success:
        print("✅ Local Startup Fluency test PASSED")
        return True
    else:
        print("❌ Local Startup Fluency test FAILED")
        return False

def test_port_conflict_resolution():
    """Test port conflict resolution challenge."""
    print("🧪 Testing Port Conflict Resolution...")
    
    # Start a dummy process on port 8080 to create conflict
    print("   Starting dummy process on port 8080...")
    dummy_process = subprocess.Popen([
        sys.executable, "-c", 
        "import socket, time; s = socket.socket(); s.bind(('127.0.0.1', 8080)); s.listen(1); time.sleep(30)"
    ])
    
    time.sleep(2)  # Give the process time to start
    
    # Verify the port is occupied
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
        if ':8080' in result.stdout and 'LISTENING' in result.stdout:
            print("   Confirmed port 8080 is occupied")
        else:
            print("   Warning: Could not confirm port occupation")
    except Exception as e:
        print(f"   Warning: Could not check port status: {e}")
    
    # Now test the launcher's ability to resolve this conflict
    launcher = UniversalLauncher()
    killed_processes = launcher.kill_processes_on_ports()
    
    # Check if our dummy process was killed
    if 8080 in killed_processes:
        print("✅ Port Conflict Resolution test PASSED")
        dummy_process.terminate()  # Just in case
        return True
    else:
        print("❌ Port Conflict Resolution test FAILED")
        dummy_process.terminate()
        return False

def test_environment_variable_access():
    """Test environment variable access challenge."""
    print("🧪 Testing Environment Variable Access...")
    
    launcher = UniversalLauncher()
    success = launcher.setup_environment_variables()
    
    # Check if required variables are set
    required_vars = ["OLLAMA_HOST"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if success and not missing_vars:
        print("✅ Environment Variable Access test PASSED")
        print(f"   Environment variables set: {len(os.environ)}")
        return True
    else:
        print("❌ Environment Variable Access test FAILED")
        if missing_vars:
            print(f"   Missing required variables: {missing_vars}")
        return False

def test_cloud_local_switching_stability():
    """Test cloud/local switching stability challenge."""
    print("🧪 Testing Cloud/Local Switching Stability...")
    
    launcher = UniversalLauncher()
    result = launcher.manage_cloud_handshake()
    
    if result["status"] == "SUCCESS":
        print("✅ Cloud/Local Switching Stability test PASSED")
        print(f"   Redirected connections: {result.get('redirected_connections', 0)}")
        return True
    else:
        print("❌ Cloud/Local Switching Stability test FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False

def test_waz_doc_change_reaction():
    """Test Waz-Doc change reaction challenge."""
    print("🧪 Testing Waz-Doc Change Reaction...")
    
    launcher = UniversalLauncher()
    result = launcher.monitor_waz_doc()
    
    expected_statuses = ["MONITORING", "CREATED"]
    if result["status"] in expected_statuses:
        print("✅ Waz-Doc Change Reaction test PASSED")
        print(f"   Status: {result['status']}")
        if "file" in result:
            print(f"   File: {result['file']}")
        return True
    else:
        print("❌ Waz-Doc Change Reaction test FAILED")
        print(f"   Status: {result['status']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
        return False

def run_all_challenges():
    """Run all challenge-based tests."""
    print("🚀 Running Challenge-Based Tests for Universal Launcher")
    print("=" * 55)
    
    tests = [
        test_local_startup_fluency,
        test_port_conflict_resolution,
        test_environment_variable_access,
        test_cloud_local_switching_stability,
        test_waz_doc_change_reaction
    ]
    
    results = []
    for test in tests:
        print()
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"💥 Test failed with exception: {e}")
            results.append(False)
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 55)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL CHALLENGE TESTS PASSED!")
        print("✅ The Universal Launcher is functioning correctly")
        return True
    elif passed > 0:
        print("⚠️  SOME CHALLENGE TESTS PASSED")
        print("🔧 The Universal Launcher has partial functionality")
        return False
    else:
        print("❌ ALL CHALLENGE TESTS FAILED!")
        print("🔧 The Universal Launcher requires troubleshooting")
        return False

if __name__ == "__main__":
    success = run_all_challenges()
    sys.exit(0 if success else 1)