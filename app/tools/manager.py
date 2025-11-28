from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.tools.base import BaseTool
from app.tools.medical_lookup import GoogleSearchTool, MedicalLookupTool
from app.tools.mcp_client import MCPClient
from app.utils import configure_logging


class ToolManager:
    """Manages and coordinates all available tools for agents."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = configure_logging()
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all available tools."""
        self.tools["medical_lookup"] = MedicalLookupTool()
        self.tools["google_search"] = GoogleSearchTool()
        self.tools["mcp_client"] = MCPClient()
    
    def register_tool(self, tool: BaseTool):
        """Register a custom tool."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        
        try:
            result = await tool.execute(**kwargs)
            self.logger.info(f"Tool {name} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Tool {name} execution failed: {e}")
            return {"error": str(e)}