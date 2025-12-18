#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Liberation AI Proxy Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A completely local HTTP proxy service that connects editors to Ollama
without any cloud dependencies.

This service provides:
- Local-only binding (127.0.0.1)
- RESTful API endpoints for AI operations
- Complete transparency in data flow
- No external network access
"""

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from ollama import Client
import psutil

class LiberationAIProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Local Liberation AI Proxy Service."""
    
    def __init__(self, *args, **kwargs):
        # Initialize Ollama client
        self.client = Client(host="http://localhost:11434")
        super().__init__(*args, **kwargs)
    
    def _send_json_response(self, data, status_code=200):
        """Send a JSON response to the client."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Convert any non-serializable objects to strings
        json_data = json.dumps(data, default=str, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def _get_post_data(self):
        """Extract JSON data from POST request."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode('utf-8'))
        except:
            return {}
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self._handle_root()
        elif path == '/status':
            self._handle_status()
        elif path == '/models':
            self._handle_models()
        elif path == '/system':
            self._handle_system_info()
        else:
            self._send_json_response({
                "error": "Endpoint not found",
                "path": path
            }, 404)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/chat':
            self._handle_chat()
        else:
            self._send_json_response({
                "error": "Endpoint not found",
                "path": path
            }, 404)
    
    def _handle_root(self):
        """Handle root endpoint."""
        response = {
            "service": "Local Liberation AI Proxy Service",
            "version": "1.0",
            "description": "A completely local proxy service for connecting editors to Ollama",
            "endpoints": {
                "GET /status": "Check service status",
                "GET /models": "List available models",
                "GET /system": "Get system information",
                "POST /chat": "Send chat messages to AI model"
            },
            "security": {
                "local_only": True,
                "no_external_access": True,
                "no_data_collection": True
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self._send_json_response(response)
    
    def _handle_status(self):
        """Handle status endpoint."""
        # Check if Ollama is running
        try:
            # Simple check by listing models
            self.client.list()
            ollama_status = "running"
        except:
            ollama_status = "not accessible"
        
        response = {
            "service_status": "operational",
            "ollama_status": ollama_status,
            "uptime": getattr(self.server, 'start_time', 'unknown'),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self._send_json_response(response)
    
    def _handle_models(self):
        """Handle models endpoint."""
        try:
            response = self.client.list()
            models = response.get('models', [])
            
            # Process models to ensure JSON serializability
            processed_models = []
            for model in models:
                processed_model = {
                    "name": model.get('name', 'Unknown'),
                    "digest": model.get('digest', 'Unknown'),
                    "size": model.get('size', 0),
                    "modified_at": str(model.get('modified_at', 'Unknown'))
                }
                processed_models.append(processed_model)
            
            response_data = {
                "models": processed_models,
                "count": len(processed_models),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self._send_json_response(response_data)
        except Exception as e:
            self._send_json_response({
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, 500)
    
    def _handle_system_info(self):
        """Handle system information endpoint."""
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
            
            response_data = {
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
            self._send_json_response(response_data)
        except Exception as e:
            self._send_json_response({
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, 500)
    
    def _handle_chat(self):
        """Handle chat endpoint with streaming support."""
        try:
            # Get POST data
            data = self._get_post_data()
            
            model = data.get('model', 'llama3.1:latest')
            messages = data.get('messages', [])
            stream = data.get('stream', False)
            
            if not messages:
                self._send_json_response({
                    "error": "Messages are required",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }, 400)
                return
            
            # Handle streaming response
            if stream:
                self._handle_streaming_chat(model, messages)
            else:
                # Handle non-streaming response
                self._handle_non_streaming_chat(model, messages)
            
        except Exception as e:
            self._send_json_response({
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, 500)
    
    def _handle_streaming_chat(self, model, messages):
        """Handle streaming chat response."""
        try:
            # Set streaming headers
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', 'http://localhost:*')
            self.end_headers()
            
            # Send request to Ollama with streaming
            response_stream = self.client.chat(
                model=model,
                messages=messages,
                stream=True
            )
            
            # Stream responses
            for response in response_stream:
                # Process response for JSON serialization
                processed_response = {
                    "model": response.get('model', model),
                    "created_at": str(response.get('created_at', '')),
                    "message": response.get('message', {}),
                    "done": response.get('done', False),
                    "total_duration": response.get('total_duration', 0),
                    "load_duration": response.get('load_duration', 0),
                    "prompt_eval_count": response.get('prompt_eval_count', 0),
                    "eval_count": response.get('eval_count', 0),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Send SSE formatted response
                sse_data = f"data: {json.dumps(processed_response, default=str)}\n\n"
                self.wfile.write(sse_data.encode('utf-8'))
                self.wfile.flush()
                
                # If done, break
                if response.get('done', False):
                    break
                    
        except Exception as e:
            error_response = {
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            sse_data = f"data: {json.dumps(error_response, default=str)}\n\n"
            self.wfile.write(sse_data.encode('utf-8'))
            self.wfile.flush()
    
    def _handle_non_streaming_chat(self, model, messages):
        """Handle non-streaming chat response."""
        try:
            # Send request to Ollama
            response = self.client.chat(
                model=model,
                messages=messages,
                stream=False
            )
            
            # Process response for JSON serialization
            processed_response = {
                "model": response.get('model', model),
                "created_at": str(response.get('created_at', '')),
                "message": response.get('message', {}),
                "done": response.get('done', True),
                "total_duration": response.get('total_duration', 0),
                "load_duration": response.get('load_duration', 0),
                "prompt_eval_count": response.get('prompt_eval_count', 0),
                "eval_count": response.get('eval_count', 0),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self._send_json_response(processed_response)
            
        except Exception as e:
            self._send_json_response({
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, 500)
class LiberationAIProxyService:
    """Main class for the Local Liberation AI Proxy Service."""
    
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start the proxy service."""
        if self.running:
            print("Service is already running")
            return False
        
        try:
            # Create HTTP server
            self.server = HTTPServer((self.host, self.port), LiberationAIProxyHandler)
            self.server.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            print(f"🚀 Local Liberation AI Proxy Service started on http://{self.host}:{self.port}")
            print("🔒 Service is local-only - no external network access")
            print("🛡️  All data stays on your machine")
            print("💡 Press Ctrl+C to stop the service")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            return False
    
    def stop(self):
        """Stop the proxy service."""
        if not self.running:
            print("Service is not running")
            return False
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            self.running = False
            print("⏹️  Local Liberation AI Proxy Service stopped")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return False
    
    def is_running(self):
        """Check if the service is running."""
        return self.running

def main():
    """Main function to run the proxy service."""
    print("🚀 The Road to Liberation - Local AI Proxy Service")
    print("=" * 50)
    
    # Create and start the service
    proxy_service = LiberationAIProxyService()
    
    try:
        if proxy_service.start():
            # Keep the service running
            try:
                while proxy_service.is_running():
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
        else:
            print("❌ Failed to start the service")
            return 1
            
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1
    finally:
        proxy_service.stop()
    
    print("✅ Service shutdown complete")
    return 0

if __name__ == "__main__":
    exit(main())