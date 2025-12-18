#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Fix Script for Liberation AI Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script identifies and fixes the file path configuration issue
that prevents the proxy service from starting correctly.
"""

import json
import os
from pathlib import Path

def fix_launcher_configuration():
    """Fix the launcher configuration file path issue."""
    
    # Define the expected configuration structure
    fixed_config = {
        "target_ports": [8080, 11434],
        "waz_doc_path": "waz_doc.json",
        "services": {
            "proxy_service": {
                "script": "Server/enhanced_proxy_service.py",  # Fixed path
                "port": 8080,
                "name": "Liberation AI Proxy Service",
                "description": "Local HTTP proxy service for connecting editors to Ollama"
            }
        },
        "environment_variables": {
            "OLLAMA_HOST": "http://localhost:11434",
            "LIBERATION_AI_LOCAL_ONLY": "true",
            "LIBERATION_AI_NO_DATA_COLLECTION": "true"
        },
        "cleanup_on_startup": True,
        "monitor_waz_doc": True,
        "cloud_handshake_management": {
            "enabled": True,
            "redirect_to_local": True,
            "blocked_external_domains": [
                "*.alibaba.com",
                "*.aliyun.com",
                "*.qoder.ai",
                "*.qoder.sh",
                "8.212.*",
                "139.196.*",
                "cursor.sh",
                "openai.com",
                "anthropic.com",
                "hwsdigitalbd.com",
                "exchange.xinewallet.com",
                "center.qoder.sh",
                "openapi.qoder.sh",
                "qts1.qoder.sh",
                "qts2.qoder.sh",
                "repo2.qoder.sh",
                "api2.qoder.sh",
                "marketplace.qoder.sh",
                "amazonaws.com",
                "aws.amazon.com"
            ]
        },
        "challenge_based_tests": {
            "local_startup_fluency": {
                "enabled": True,
                "timeout": 30
            },
            "port_conflict_resolution": {
                "enabled": True,
                "test_port": 8080
            },
            "environment_variable_access": {
                "enabled": True,
                "required_vars": ["OLLAMA_HOST"]
            },
            "service_startup_sequence": {
                "enabled": True,
                "services_to_test": ["proxy_service"]
            },
            "cloud_local_switching_stability": {
                "enabled": True,
                "test_duration": 60
            },
            "waz_doc_change_reaction": {
                "enabled": True,
                "monitor_interval": 5
            }
        }
    }
    
    # Write the fixed configuration to file
    config_path = "launcher_config.json"
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully created fixed configuration file: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create configuration file: {e}")
        return False

def verify_file_structure():
    """Verify that required files exist in the correct locations."""
    
    required_files = [
        "Server/enhanced_proxy_service.py",
        "Adapter/editor_adapter.js",
        "Test/adapter_test.js"
    ]
    
    print("🔍 Verifying file structure...")
    all_files_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_files_exist = False
    
    return all_files_exist

def main():
    """Main function to execute the path fix."""
    print("🔧 Liberation AI Development Environment - Path Fix Utility")
    print("=" * 60)
    
    # Verify current file structure
    files_ok = verify_file_structure()
    
    if not files_ok:
        print("\n⚠️  Some required files are missing. Please ensure the complete project structure exists.")
        return False
    
    # Fix the launcher configuration
    print("\n⚙️  Fixing launcher configuration...")
    config_fixed = fix_launcher_configuration()
    
    if config_fixed:
        print("\n✅ Path fix completed successfully!")
        print("\n📋 To test the fix, run:")
        print("   python universal_launcher.py --test")
        print("\n🚀 To start the full system, run:")
        print("   python universal_launcher.py")
        return True
    else:
        print("\n❌ Failed to fix path configuration.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)