"""std/http - HTTP server and client for Flo.

This is a stub implementation that will be expanded in future versions.
"""

from typing import Dict, Any, Callable, Optional, List
import asyncio


class HTTPRequest:
    """HTTP request object."""
    
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: str):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.params: Dict[str, str] = {}
        self.query: Dict[str, str] = {}
    
    def parse_json(self) -> Dict[str, Any]:
        """Parse JSON body."""
        import json
        return json.loads(self.body)


class HTTPResponse:
    """HTTP response object."""
    
    def __init__(self, status: int, body: Any, headers: Optional[Dict[str, str]] = None):
        self.status = status
        self.body = body
        self.headers = headers or {}


class HTTPApp:
    """HTTP application."""
    
    def __init__(self):
        self.routes: Dict[str, Dict[str, Callable]] = {}
    
    def route(self, path: str):
        """Define a route."""
        class RouteBuilder:
            def __init__(self, app, path):
                self.app = app
                self.path = path
            
            def get(self, handler):
                if self.path not in self.app.routes:
                    self.app.routes[self.path] = {}
                self.app.routes[self.path]['GET'] = handler
                return self
            
            def post(self, handler):
                if self.path not in self.app.routes:
                    self.app.routes[self.path] = {}
                self.app.routes[self.path]['POST'] = handler
                return self
            
            def put(self, handler):
                if self.path not in self.app.routes:
                    self.app.routes[self.path] = {}
                self.app.routes[self.path]['PUT'] = handler
                return self
            
            def delete(self, handler):
                if self.path not in self.app.routes:
                    self.app.routes[self.path] = {}
                self.app.routes[self.path]['DELETE'] = handler
                return self
        
        return RouteBuilder(self, path)
    
    def listen(self, port: int):
        """Start HTTP server."""
        print(f"[HTTP] Server listening on port {port}")
        print("[HTTP] Note: This is a stub implementation")


class HTTPClient:
    """HTTP client."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None):
        """Send GET request."""
        print(f"[HTTP] GET {url}")
        return HTTPResponse(200, {"message": "Stub response"})
    
    async def post(self, url: str, data: Any, headers: Optional[Dict[str, str]] = None):
        """Send POST request."""
        print(f"[HTTP] POST {url}")
        return HTTPResponse(200, {"message": "Stub response"})


def app() -> HTTPApp:
    """Create HTTP application."""
    return HTTPApp()


def client(config: Optional[Dict[str, Any]] = None) -> HTTPClient:
    """Create HTTP client."""
    return HTTPClient(config)


def json(status: int, data: Any) -> HTTPResponse:
    """Create JSON response."""
    return HTTPResponse(status, data, {"Content-Type": "application/json"})
