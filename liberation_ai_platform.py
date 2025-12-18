#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Road to Liberation - Local AI Development Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script creates a completely local, independent AI development and testing platform
that connects directly to Ollama without any cloud dependencies.

Author: AI Liberation Initiative
Version: 1.0
"""

import json
import os
import sys
import time
import subprocess
import psutil
from ollama import Client
from typing import Dict, List, Any, Optional

class LocalAIPlatform:
    """A completely local AI development platform that connects directly to Ollama."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """
        Initialize the Local AI Platform.
        
        Args:
            ollama_host: The host URL for the local Ollama instance
        """
        self.ollama_host = ollama_host
        self.client = Client(host=ollama_host)
        self.status = {
            "platform_initialized": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "ollama_host": ollama_host
        }
        
    def check_ollama_status(self) -> Dict[str, Any]:
        """
        Check if Ollama is running locally.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Try to get Ollama version
            result = subprocess.run(
                ["ollama", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            ollama_running = result.returncode == 0
            version_info = result.stdout.strip() if ollama_running else "Not available"
            
            # Check if Ollama service is listening on port 11434
            ollama_port_open = self._is_port_open(11434)
            
            status = {
                "ollama_installed": True,
                "ollama_running": ollama_running and ollama_port_open,
                "ollama_version": version_info,
                "port_11434_open": ollama_port_open,
                "check_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status.update(status)
            return status
            
        except Exception as e:
            error_status = {
                "ollama_installed": False,
                "ollama_running": False,
                "ollama_version": "Unknown",
                "port_11434_open": False,
                "error": str(e),
                "check_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status.update(error_status)
            return error_status
    
    def _is_port_open(self, port: int) -> bool:
        """
        Check if a specific port is open on localhost.
        
        Args:
            port: The port number to check
            
        Returns:
            True if port is open, False otherwise
        """
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def list_available_models(self) -> Dict[str, Any]:
        """
        List all available models in the local Ollama instance.
        
        Returns:
            Dictionary with model information
        """
        try:
            response = self.client.list()
            models = response.get('models', [])
            
            model_list = []
            for model in models:
                # Convert datetime objects to strings for JSON serialization
                modified_at = model.get('modified_at', 'Unknown')
                if hasattr(modified_at, 'isoformat'):
                    modified_at = modified_at.isoformat()
                    
                model_info = {
                    "name": model.get('name', 'Unknown'),
                    "digest": model.get('digest', 'Unknown'),
                    "size": model.get('size', 0),
                    "modified_at": modified_at
                }
                model_list.append(model_info)            
            result = {
                "models_found": len(model_list),
                "models": model_list,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["model_list"] = result
            return result
            
        except Exception as e:
            error_result = {
                "models_found": 0,
                "models": [],
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["model_list"] = error_result
            return error_result
    
    def send_test_prompt(self, model_name: str = "llama3.1:latest", prompt: str = "Hello, are you running locally?") -> Dict[str, Any]:
        """
        Send a test prompt to verify local AI processing.
        
        Args:
            model_name: The name of the model to use
            prompt: The prompt to send
            
        Returns:
            Dictionary with response information
        """
        try:
            response = self.client.chat(
                model=model_name,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                }]
            )
            
            result = {
                "success": True,
                "model_used": model_name,
                "prompt": prompt,
                "response": response.get('message', {}).get('content', ''),
                "total_duration": response.get('total_duration', 0),
                "load_duration": response.get('load_duration', 0),
                "prompt_eval_count": response.get('prompt_eval_count', 0),
                "eval_count": response.get('eval_count', 0),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["last_test_prompt"] = result
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "model_used": model_name,
                "prompt": prompt,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["last_test_prompt"] = error_result
            return error_result
    
    def get_system_resources(self) -> Dict[str, Any]:
        """
        Get information about system resources to verify local processing.
        
        Returns:
            Dictionary with system resource information
        """
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            memory_percent = memory.percent
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            disk_percent = (disk.used / disk.total) * 100 if disk.total > 0 else 0
            
            result = {
                "cpu": {
                    "physical_cores": cpu_count,
                    "logical_cores": cpu_count_logical,
                    "usage_percent": cpu_percent
                },
                "memory": {
                    "total_gb": round(memory_gb, 2),
                    "available_gb": round(memory_available_gb, 2),
                    "usage_percent": memory_percent
                },
                "disk": {
                    "total_gb": round(disk_total_gb, 2),
                    "free_gb": round(disk_free_gb, 2),
                    "usage_percent": round(disk_percent, 2)
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["system_resources"] = result
            return result
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["system_resources"] = error_result
            return error_result
    
    def create_local_proxy_service(self) -> Dict[str, Any]:
        """
        Create a local proxy service for editor binding.
        This service runs completely locally without any cloud dependencies.
        
        Returns:
            Dictionary with proxy service information
        """
        try:
            # For this implementation, we're documenting the approach
            # A full implementation would involve creating a local HTTP server
            # that acts as a proxy between editors and Ollama
            
            proxy_info = {
                "service_name": "Local Liberation AI Proxy",
                "description": "A completely local proxy service for connecting editors to Ollama",
                "implementation_approach": [
                    "Create a lightweight HTTP server using Python's built-in http.server",
                    "Implement endpoints for model listing, chat completion, and status checks",
                    "Ensure all data stays local and never leaves the machine",
                    "Provide editor-agnostic API endpoints",
                    "Include health checks and resource monitoring"
                ],
                "security_features": [
                    "Local-only binding (127.0.0.1)",
                    "No external network access",
                    "No data collection or telemetry",
                    "Complete transparency in data flow"
                ],
                "status": "Implementation planned",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["local_proxy_service"] = proxy_info
            return proxy_info
            
        except Exception as e:
            error_result = {
                "status": "Failed to plan proxy service",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.status["local_proxy_service"] = error_result
            return error_result
    
    def generate_json_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive JSON report of the platform status.
        
        Returns:
            Dictionary with complete platform status
        """
        report = {
            "project": "The Road to Liberation - Local AI Development Platform",
            "version": "1.0",
            "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status
        }
        
        return report
    
    def save_json_report(self, filepath: str = "liberation_platform_report.json") -> bool:
        """
        Save the JSON report to a file.
        
        Args:
            filepath: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            report = self.generate_json_report()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False

def main():
    """Main function to run the Local AI Platform diagnostics."""
    print("🚀 The Road to Liberation - Local AI Development Platform")
    print("=" * 60)
    
    # Initialize the platform
    platform = LocalAIPlatform()
    
    # Run diagnostics
    print("\n🔍 Checking Ollama Status...")
    ollama_status = platform.check_ollama_status()
    print(json.dumps(ollama_status, indent=2, ensure_ascii=False))
    
    print("\n🖥️  Checking System Resources...")
    system_resources = platform.get_system_resources()
    print(json.dumps(system_resources, indent=2, ensure_ascii=False))
    
    print("\n📚 Listing Available Models...")
    models = platform.list_available_models()
    print(json.dumps(models, indent=2, ensure_ascii=False))
    
    # Only run test prompt if Ollama is running
    if ollama_status.get("ollama_running", False):
        print("\n💬 Sending Test Prompt...")
        test_response = platform.send_test_prompt()
        print(json.dumps(test_response, indent=2, ensure_ascii=False))
    else:
        print("\n⚠️  Ollama is not running. Skipping test prompt.")
    
    print("\n🔌 Planning Local Proxy Service...")
    proxy_info = platform.create_local_proxy_service()
    print(json.dumps(proxy_info, indent=2, ensure_ascii=False))
    
    # Generate and save comprehensive report
    print("\n📄 Generating Comprehensive Report...")
    if platform.save_json_report():
        print("✅ Report saved successfully as 'liberation_platform_report.json'")
    else:
        print("❌ Failed to save report")
    
    # Display final status
    final_report = platform.generate_json_report()
    print("\n📊 Final Platform Status:")
    print(json.dumps(final_report, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✅ The Road to Liberation platform check completed!")
    print("💡 All processing happens locally - no cloud data transmission")
    return final_report

if __name__ == "__main__":
    # Ensure we're using the virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
    
    result = main()
    
    # Exit with success code
    sys.exit(0)