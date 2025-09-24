"""
Tools package for the ReWOO application.
"""
from .base import BaseTool, ToolResult, ToolMetadata, ToolRegistry, tool_registry
from .search import SearchTool
from .calculator import CalculatorTool
from .wikipedia import WikipediaTool

# Auto-register all tools
def register_default_tools():
    """Register all default tools with the global registry."""
    tools = [
        SearchTool(),
        CalculatorTool(),
        WikipediaTool(),
    ]
    
    for tool in tools:
        tool_registry.register_tool(tool)

# Tools will be registered during app startup via lifespan manager

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolMetadata",
    "ToolRegistry",
    "tool_registry",
    "SearchTool",
    "CalculatorTool",
    "WikipediaTool",
    "register_default_tools",
]

