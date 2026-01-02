"""Tool Registry for managing external tools"""
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from functools import wraps
import time

logger = logging.getLogger(__name__)


class ToolCallLog:
    """Log entry for tool calls"""
    def __init__(self, tool_name: str, params: Dict[str, Any]):
        self.tool_name = tool_name
        self.params = params
        self.timestamp = datetime.now()
        self.status = "pending"
        self.result_size = 0
        self.error_message = None
        self.duration = 0.0


class ToolRegistry:
    """
    Unified tool registry supporting:
    1. Decorator-based registration for custom tools
    2. MCP protocol registration (optional)
    """
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._tool_metadata: Dict[str, Dict[str, Any]] = {}
        self._call_logs: List[ToolCallLog] = []
        
    def register(
        self,
        name: Optional[str] = None,
        description: str = "",
        required_params: Optional[List[str]] = None
    ):
        """
        Decorator for registering a tool
        
        Usage:
            @tool_registry.register(name="arxiv_search", description="Search arXiv papers")
            async def search_arxiv(query: str, max_results: int = 10):
                ...
        """
        def decorator(func: Callable):
            tool_name = name or func.__name__
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            self._tools[tool_name] = wrapper
            self._tool_metadata[tool_name] = {
                "description": description,
                "required_params": required_params or [],
                "function": func
            }
            
            logger.info(f"Registered tool: {tool_name}")
            return wrapper
        
        return decorator
    
    def register_function(self, name: str, func: Callable, description: str = "", required_params: Optional[List[str]] = None):
        """Programmatically register a function as a tool"""
        self._tools[name] = func
        self._tool_metadata[name] = {
            "description": description,
            "required_params": required_params or [],
            "function": func
        }
        logger.info(f"Registered tool: {name}")
    
    async def call(self, tool_name: str, **kwargs) -> Any:
        """
        Call a registered tool
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found or required parameters missing
        """
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self._tools.keys())}")
        
        # Validate required parameters
        required = self._tool_metadata[tool_name].get("required_params", [])
        missing = [p for p in required if p not in kwargs]
        if missing:
            raise ValueError(f"Missing required parameters for '{tool_name}': {missing}")
        
        # Create log entry
        log = ToolCallLog(tool_name, kwargs)
        self._call_logs.append(log)
        
        start_time = time.time()
        
        try:
            tool_func = self._tools[tool_name]
            
            # Call tool (handle both sync and async)
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**kwargs)
            else:
                result = tool_func(**kwargs)
            
            # Update log
            log.status = "success"
            log.result_size = len(str(result)) if result else 0
            log.duration = time.time() - start_time
            
            logger.info(f"Tool '{tool_name}' executed successfully in {log.duration:.2f}s")
            return result
            
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.duration = time.time() - start_time
            logger.error(f"Tool '{tool_name}' failed: {e}")
            raise
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get metadata about a tool"""
        if tool_name not in self._tool_metadata:
            raise ValueError(f"Tool '{tool_name}' not found")
        return self._tool_metadata[tool_name]
    
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self._tools.keys())
    
    def get_call_history(self, tool_name: Optional[str] = None) -> List[ToolCallLog]:
        """Get call history, optionally filtered by tool name"""
        if tool_name:
            return [log for log in self._call_logs if log.tool_name == tool_name]
        return self._call_logs
    
    def clear_history(self):
        """Clear call history"""
        self._call_logs = []


# Global tool registry instance
tool_registry = ToolRegistry()

