from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import httpx

from app.tools.base import BaseTool
from app.utils import configure_logging


class MCPClient(BaseTool):
    """Model Context Protocol client for external data integration."""
    
    def __init__(self, server_url: str = "http://localhost:3000"):
        super().__init__(
            name="mcp_client",
            description="Connect to MCP servers for external data and tools"
        )
        self.server_url = server_url
        self.logger = configure_logging()
    
    async def execute(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute MCP method call."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {}
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.server_url}/mcp",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"MCP server returned {response.status_code}"}
                    
        except httpx.ConnectError:
            # Fallback when MCP server unavailable
            return self._mock_mcp_response(method, params)
        except Exception as e:
            self.logger.error(f"MCP call failed: {e}")
            return {"error": str(e)}
    
    def _mock_mcp_response(self, method: str, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock MCP responses for demo purposes."""
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "tools": [
                        {
                            "name": "drug_database",
                            "description": "Query comprehensive drug database"
                        },
                        {
                            "name": "medical_guidelines", 
                            "description": "Access clinical practice guidelines"
                        }
                    ]
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name") if params else "unknown"
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Mock response from {tool_name} tool"
                        }
                    ]
                }
            }
        else:
            return {"error": f"Unknown MCP method: {method}"}