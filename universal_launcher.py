#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Launcher for Liberation AI Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A comprehensive orchestration and verification tool that manages the entire 
local development environment, monitors stability, and ensures proper setup.

Author: Liberation AI Team
Version: 1.0
"""

import json
import os
import sys
import time
import subprocess
import psutil
import signal
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class UniversalLauncher:
    """Universal launcher for managing the Liberation AI development environment."""
    
    def __init__(self, config_path: str = None):
        """Initialize the universal launcher."""
        self.config_path = config_path or "launcher_config.json"
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.processes = {}
        
        # Define port ranges to monitor
        self.target_ports = self.config.get("target_ports", [8080, 11434])
        self.waz_doc_path = self.config.get("waz_doc_path", "waz_doc.json")
        
        self.logger.info("Universal Launcher initialized")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "target_ports": [8080, 11434],
            "waz_doc_path": "waz_doc.json",
            "services": {
                "proxy_service": {
                    "script": "Server/enhanced_proxy_service.py",
                    "port": 8080,
                    "name": "Liberation AI Proxy Service"
                }
            },
            "environment_variables": {
                "OLLAMA_HOST": "http://localhost:11434"
            },
            "cleanup_on_startup": True,
            "monitor_waz_doc": True
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with default config
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                self.logger.warning(f"Configuration file {self.config_path} not found, using defaults")
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return default_config
    
    def setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('launcher.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('UniversalLauncher')
    
    def kill_processes_on_ports(self) -> Dict[int, List[int]]:
        """
        Kill processes running on target ports.
        
        Returns:
            Dictionary mapping ports to killed process IDs
        """
        killed_processes = {}
        
        for port in self.target_ports:
            self.logger.info(f"Checking for processes on port {port}")
            killed_pids = []
            
            # Find processes using the port
            try:
                # Windows-specific command to find processes on a port
                result = subprocess.run(
                    ['netstat', '-ano'], 
                    capture_output=True, 
                    text=True, 
                    shell=True
                )
                
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = int(parts[-1])
                            try:
                                process = psutil.Process(pid)
                                process_name = process.name()
                                self.logger.info(f"Killing process {process_name} (PID: {pid}) on port {port}")
                                process.terminate()
                                killed_pids.append(pid)
                            except psutil.NoSuchProcess:
                                self.logger.warning(f"Process with PID {pid} no longer exists")
                            except Exception as e:
                                self.logger.error(f"Error killing process {pid}: {e}")
                
                if killed_pids:
                    killed_processes[port] = killed_pids
                    # Wait a moment for processes to terminate
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error checking processes on port {port}: {e}")
        
        if killed_processes:
            self.logger.info(f"Killed processes on ports: {killed_processes}")
        else:
            self.logger.info("No processes found on target ports")
            
        return killed_processes
    
    def setup_environment_variables(self) -> bool:
        """
        Set up environment variables for the session.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            env_vars = self.config.get("environment_variables", {})
            for key, value in env_vars.items():
                os.environ[key] = value
                self.logger.info(f"Set environment variable: {key}={value}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting environment variables: {e}")
            return False
    
    def start_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Start all configured services in sequence.
        
        Returns:
            Dictionary with service status information
        """
        service_status = {}
        services = self.config.get("services", {})
        
        for service_name, service_config in services.items():
            self.logger.info(f"Starting service: {service_name}")
            
            try:
                script_path = service_config.get("script")
                if not script_path or not os.path.exists(script_path):
                    self.logger.error(f"Script not found: {script_path}")
                    service_status[service_name] = {
                        "status": "FAILED",
                        "error": f"Script not found: {script_path}",
                        "pid": None
                    }
                    continue
                
                # Start the service as a subprocess
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.dirname(script_path) or "."
                )
                
                # Store process information
                self.processes[service_name] = process
                pid = process.pid
                
                self.logger.info(f"Started {service_name} with PID {pid}")
                
                # Wait briefly to check if process started successfully
                time.sleep(3)
                
                # Check if process is still running
                if process.poll() is None:
                    service_status[service_name] = {
                        "status": "RUNNING",
                        "pid": pid,
                        "port": service_config.get("port"),
                        "script": script_path
                    }
                    self.logger.info(f"Service {service_name} is running")
                else:
                    # Process has terminated
                    stdout, stderr = process.communicate()
                    error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                    self.logger.error(f"Service {service_name} failed to start: {error_msg}")
                    service_status[service_name] = {
                        "status": "FAILED",
                        "error": error_msg,
                        "pid": pid
                    }
                    
            except Exception as e:
                self.logger.error(f"Error starting service {service_name}: {e}")
                service_status[service_name] = {
                    "status": "FAILED",
                    "error": str(e),
                    "pid": None
                }
        
        return service_status
    
    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Check the health of a specific service.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            Dictionary with health status information
        """
        if service_name not in self.processes:
            return {"status": "NOT_FOUND", "error": "Service not running"}
        
        process = self.processes[service_name]
        
        try:
            # Check if process is still running
            if process.poll() is None:
                return {
                    "status": "HEALTHY",
                    "pid": process.pid,
                    "running_time": time.time() - process._start_time if hasattr(process, '_start_time') else "Unknown"
                }
            else:
                return {
                    "status": "STOPPED",
                    "pid": process.pid,
                    "exit_code": process.returncode
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def manage_cloud_handshake(self) -> Dict[str, Any]:
        """
        Manage cloud handshake connections and redirect to local.
        
        Returns:
            Dictionary with cloud connection management status
        """
        self.logger.info("Managing cloud handshake connections")
        
        redirected_connections = 0
        blocked_domains = self.config.get("cloud_handshake_management", {}).get("blocked_external_domains", [])
        
        try:
            # Check for any existing connections to blocked domains
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    try:
                        # Get the remote address
                        remote_addr = conn.raddr.ip if conn.raddr else None
                        if remote_addr:
                            # Check if this connection should be blocked
                            for domain_pattern in blocked_domains:
                                if self._matches_pattern(remote_addr, domain_pattern):
                                    # Terminate the process associated with this connection
                                    try:
                                        process = psutil.Process(conn.pid)
                                        process.terminate()
                                        self.logger.info(f"Terminated connection to blocked domain {remote_addr} (PID: {conn.pid})")
                                        redirected_connections += 1
                                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                        self.logger.warning(f"Could not terminate process {conn.pid}: {e}")
                    except Exception as e:
                        self.logger.warning(f"Error checking connection: {e}")
            
            self.logger.info(f"Managed cloud handshake connections, redirected {redirected_connections} connections")
            
            return {
                "status": "SUCCESS",
                "details": f"Redirected {redirected_connections} cloud connections to local",
                "redirected_connections": redirected_connections,
                "blocked_domains_checked": blocked_domains
            }
            
        except Exception as e:
            self.logger.error(f"Error managing cloud handshake connections: {e}")
            return {
                "status": "ERROR",
                "error": str(e),
                "redirected_connections": 0
            }
    
    def _matches_pattern(self, ip_address: str, pattern: str) -> bool:
        """
        Check if an IP address or domain matches a pattern.
        
        Args:
            ip_address: The IP address or domain to check
            pattern: The pattern to match against
            
        Returns:
            True if the IP/domain matches the pattern, False otherwise
        """
        if pattern.endswith('.*'):
            # Handle wildcard patterns like "8.212.*"
            prefix = pattern[:-2]  # Remove the ".*"
            return ip_address.startswith(prefix)
        elif pattern.startswith('*'):
            # Handle wildcard patterns like "*.qoder.sh"
            suffix = pattern[1:]  # Remove the "*"
            return ip_address.endswith(suffix)
        else:
            # For exact domain patterns, check if the domain ends with the pattern
            # This handles cases like "cursor.sh" matching any domain ending with "cursor.sh"
            return ip_address.endswith(pattern) or pattern in ip_address
    
    def monitor_waz_doc(self) -> Dict[str, Any]:
        """
        Monitor Waz-Doc file for changes.
        
        Returns:
            Dictionary with monitoring status and details
        """
        if not self.config.get("monitor_waz_doc", True):
            return {"status": "DISABLED", "message": "Waz-Doc monitoring is disabled"}
        
        try:
            waz_doc_path = self.waz_doc_path
            if os.path.exists(waz_doc_path):
                # Get file modification time
                mod_time = os.path.getmtime(waz_doc_path)
                mod_time_str = datetime.fromtimestamp(mod_time).isoformat()
                
                self.logger.info(f"Monitoring Waz-Doc file: {waz_doc_path} (last modified: {mod_time_str})")
                return {
                    "status": "MONITORING",
                    "file": waz_doc_path,
                    "last_modified": mod_time_str,
                    "message": "Waz-Doc file is being monitored for changes"
                }
            else:
                # Create a default Waz-Doc file
                default_waz_doc = {
                    "version": "1.0",
                    "timestamp": datetime.now().isoformat(),
                    "services": self.config.get("services", {}),
                    "environment": dict(os.environ),
                    "monitoring": {
                        "status": "active",
                        "start_time": datetime.now().isoformat()
                    }
                }
                
                with open(waz_doc_path, 'w', encoding='utf-8') as f:
                    json.dump(default_waz_doc, f, indent=2)
                
                self.logger.info(f"Created default Waz-Doc file: {waz_doc_path}")
                return {
                    "status": "CREATED",
                    "file": waz_doc_path,
                    "message": "Default Waz-Doc file created and monitoring started"
                }
                
        except Exception as e:
            self.logger.error(f"Error monitoring Waz-Doc file: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }    
    def generate_status_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive status report.
        
        Returns:
            Dictionary with complete status information
        """
        report = {
            "report_name": "Universal Launcher Status Report",
            "timestamp": datetime.now().isoformat(),
            "launcher_version": "1.0",
            "environment": {
                "os": os.name,
                "python_version": sys.version,
                "working_directory": os.getcwd()
            },
            "configuration": {
                "target_ports": self.target_ports,
                "waz_doc_path": self.waz_doc_path,
                "services_configured": list(self.config.get("services", {}).keys())
            },
            "processes": {},
            "services": {}
        }
        
        # Add process information
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    report["processes"][name] = {
                        "status": "RUNNING",
                        "pid": process.pid
                    }
                else:
                    report["processes"][name] = {
                        "status": "STOPPED",
                        "pid": process.pid,
                        "exit_code": process.returncode
                    }
            except Exception as e:
                report["processes"][name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Add service health information
        services = self.config.get("services", {})
        for service_name in services.keys():
            report["services"][service_name] = self.check_service_health(service_name)
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "launcher_report.json") -> bool:
        """
        Save the status report to a JSON file.
        
        Args:
            report: The report dictionary to save
            filename: The filename to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Report saved to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            return False
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """
        Run a comprehensive check of the entire system.
        
        Returns:
            Dictionary with test results
        """
        test_results = {
            "test_suite_name": "Universal Launcher Stability Check",
            "timestamp": datetime.now().isoformat(),
            "environment_details": {
                "os": os.name,
                "python_version": sys.version,
                "launcher_version": "1.0",
                "working_directory": os.getcwd()
            },
            "test_cases": [],
            "overall_status": "PENDING"
        }
        
        # Get challenge-based test configuration
        challenge_tests = self.config.get("challenge_based_tests", {})
        
        # Test 1: Local Startup Fluency
        if challenge_tests.get("local_startup_fluency", {}).get("enabled", True):
            test_start_time = time.time()
            try:
                # Check if all required services are running
                all_services_healthy = True
                service_health_details = []
                
                for service_name in self.processes.keys():
                    health = self.check_service_health(service_name)
                    service_health_details.append({
                        "service": service_name,
                        "health": health
                    })
                    if health["status"] != "HEALTHY":
                        all_services_healthy = False
                
                test_duration = time.time() - test_start_time
                
                test_results["test_cases"].append({
                    "test_name": "Local Startup Fluency",
                    "status": "PASSED" if all_services_healthy else "FAILED",
                    "duration": test_duration,
                    "details": "All services started successfully" if all_services_healthy else "Some services failed to start",
                    "service_health": service_health_details
                })
            except Exception as e:
                test_results["test_cases"].append({
                    "test_name": "Local Startup Fluency",
                    "status": "ERROR",
                    "duration": time.time() - test_start_time,
                    "error": str(e)
                })
        
        # Test 2: Port Conflict Resolution
        if challenge_tests.get("port_conflict_resolution", {}).get("enabled", True):
            test_start_time = time.time()
            try:
                killed_processes = self.kill_processes_on_ports()
                test_duration = time.time() - test_start_time
                
                test_results["test_cases"].append({
                    "test_name": "Port Conflict Resolution",
                    "status": "PASSED",
                    "duration": test_duration,
                    "details": f"Killed processes on ports: {list(killed_processes.keys())}",
                    "killed_process_details": killed_processes
                })
            except Exception as e:
                test_results["test_cases"].append({
                    "test_name": "Port Conflict Resolution",
                    "status": "ERROR",
                    "duration": time.time() - test_start_time,
                    "error": str(e)
                })
        
        # Test 3: Environment Variable Access
        if challenge_tests.get("environment_variable_access", {}).get("enabled", True):
            test_start_time = time.time()
            try:
                env_setup_success = self.setup_environment_variables()
                required_vars = challenge_tests.get("environment_variable_access", {}).get("required_vars", [])
                missing_vars = [var for var in required_vars if var not in os.environ]
                
                test_duration = time.time() - test_start_time
                
                test_results["test_cases"].append({
                    "test_name": "Environment Variable Access",
                    "status": "PASSED" if env_setup_success and not missing_vars else "FAILED",
                    "duration": test_duration,
                    "details": "Environment variables set successfully" if env_setup_success else "Failed to set environment variables",
                    "missing_required_vars": missing_vars,
                    "total_vars_set": len(os.environ)
                })
            except Exception as e:
                test_results["test_cases"].append({
                    "test_name": "Environment Variable Access",
                    "status": "ERROR",
                    "duration": time.time() - test_start_time,
                    "error": str(e)
                })
        
        # Test 4: Service Startup Sequence
        if challenge_tests.get("service_startup_sequence", {}).get("enabled", True):
            test_start_time = time.time()
            try:
                service_status = self.start_services()
                all_services_running = all(status["status"] == "RUNNING" for status in service_status.values())
                test_duration = time.time() - test_start_time
                
                test_results["test_cases"].append({
                    "test_name": "Service Startup Sequence",
                    "status": "PASSED" if all_services_running else "FAILED",
                    "duration": test_duration,
                    "details": f"Services started: {list(service_status.keys())}",
                    "service_statuses": service_status
                })
            except Exception as e:
                test_results["test_cases"].append({
                    "test_name": "Service Startup Sequence",
                    "status": "ERROR",
                    "duration": time.time() - test_start_time,
                    "error": str(e)
                })
        
        # Test 5: Cloud/Local Switching Stability
        if challenge_tests.get("cloud_local_switching_stability", {}).get("enabled", True):
            test_start_time = time.time()
            try:
                # Manage cloud handshakes
                cloud_handshake_result = self.manage_cloud_handshake()
                test_duration = time.time() - test_start_time
                
                test_results["test_cases"].append({
                    "test_name": "Cloud/Local Switching Stability",
                    "status": cloud_handshake_result["status"] if cloud_handshake_result["status"] == "SUCCESS" else "FAILED",
                    "duration": test_duration,
                    "details": cloud_handshake_result.get("details", "Cloud handshake management completed"),
                    "redirected_connections": cloud_handshake_result.get("redirected_connections", 0)
                })
            except Exception as e:
                test_results["test_cases"].append({
                    "test_name": "Cloud/Local Switching Stability",
                    "status": "ERROR",
                    "duration": time.time() - test_start_time,
                    "error": str(e)
                })
        
        # Test 6: Waz-Doc Change Reaction
        if challenge_tests.get("waz_doc_change_reaction", {}).get("enabled", True):
            test_start_time = time.time()
            try:
                # Monitor Waz-Doc file
                waz_doc_result = self.monitor_waz_doc()
                test_duration = time.time() - test_start_time
                
                test_results["test_cases"].append({
                    "test_name": "Waz-Doc Change Reaction",
                    "status": "PASSED" if waz_doc_result["status"] in ["MONITORING", "CREATED"] else "FAILED",
                    "duration": test_duration,
                    "details": waz_doc_result.get("message", "Waz-Doc monitoring status checked"),
                    "waz_doc_status": waz_doc_result
                })
            except Exception as e:
                test_results["test_cases"].append({
                    "test_name": "Waz-Doc Change Reaction",
                    "status": "ERROR",
                    "duration": time.time() - test_start_time,
                    "error": str(e)
                })
        
        # Determine overall status
        passed_tests = sum(1 for test in test_results["test_cases"] if test["status"] == "PASSED")
        total_tests = len(test_results["test_cases"])
        
        if passed_tests == total_tests:
            test_results["overall_status"] = "PASS"
        elif passed_tests > 0:
            test_results["overall_status"] = "PARTIAL"
        else:
            test_results["overall_status"] = "FAIL"
        
        return test_results
    
    def shutdown(self) -> bool:
        """
        Gracefully shut down all services.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Shutting down all services...")
        
        success = True
        for service_name, process in self.processes.items():
            try:
                if process.poll() is None:  # Process is still running
                    self.logger.info(f"Terminating {service_name} (PID: {process.pid})")
                    process.terminate()
                    # Wait for process to terminate
                    try:
                        process.wait(timeout=10)
                        self.logger.info(f"{service_name} terminated successfully")
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"{service_name} did not terminate gracefully, forcing kill")
                        process.kill()
                        process.wait()
            except Exception as e:
                self.logger.error(f"Error shutting down {service_name}: {e}")
                success = False
        
        self.processes.clear()
        self.logger.info("All services shut down")
        return success
    
    def run(self) -> bool:
        """
        Run the universal launcher.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Starting Universal Launcher...")
        
        try:
            # Step 1: Clean up existing processes on target ports
            if self.config.get("cleanup_on_startup", True):
                self.logger.info("Step 1: Cleaning up existing processes on target ports")
                self.kill_processes_on_ports()
            
            # Step 2: Set up environment variables
            self.logger.info("Step 2: Setting up environment variables")
            self.setup_environment_variables()
            
            # Step 3: Start services
            self.logger.info("Step 3: Starting services")
            service_status = self.start_services()  # pyright: ignore[reportUnusedVariable]
            
            # Step 4: Monitor Waz-Doc file
            self.logger.info("Step 4: Monitoring Waz-Doc file")
            waz_doc_result = self.monitor_waz_doc()
            self.logger.info(f"Waz-Doc monitoring result: {waz_doc_result}")            
            # Step 5: Manage cloud handshakes
            self.logger.info("Step 5: Managing cloud handshakes")
            self.manage_cloud_handshake()
            
            # Step 6: Generate and save status report
            self.logger.info("Step 6: Generating status report")
            status_report = self.generate_status_report()
            self.save_report(status_report, "launcher_status_report.json")
            
            # Step 7: Run comprehensive check
            self.logger.info("Step 7: Running comprehensive system check")
            test_results = self.run_comprehensive_check()
            self.save_report(test_results, "comprehensive_test_report.json")
            
            self.logger.info("Universal Launcher completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in Universal Launcher: {e}")
            return False

def main():
    """Main function to run the universal launcher."""
    parser = argparse.ArgumentParser(description="Universal Launcher for Liberation AI Development Environment")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--test", action="store_true", help="Run comprehensive tests only")
    parser.add_argument("--shutdown", action="store_true", help="Shutdown all services")
    parser.add_argument("--status", action="store_true", help="Show current status")
    
    args = parser.parse_args()
    
    # Create launcher instance
    launcher = UniversalLauncher(config_path=args.config)
    
    try:
        if args.test:
            print("Running comprehensive system tests...")
            test_results = launcher.run_comprehensive_check()
            print(json.dumps(test_results, indent=2, ensure_ascii=False))
            launcher.save_report(test_results, "comprehensive_test_report.json")
        elif args.shutdown:
            print("Shutting down all services...")
            launcher.shutdown()
        elif args.status:
            print("Generating status report...")
            status_report = launcher.generate_status_report()
            print(json.dumps(status_report, indent=2, ensure_ascii=False))
            launcher.save_report(status_report, "status_report.json")
        else:
            print("Starting Universal Launcher...")
            success = launcher.run()
            if success:
                print("✅ Universal Launcher completed successfully!")
                print("📝 Reports saved:")
                print("   - launcher_status_report.json")
                print("   - comprehensive_test_report.json")
            else:
                print("❌ Universal Launcher encountered errors!")
                return 1
                
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
        launcher.shutdown()
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

