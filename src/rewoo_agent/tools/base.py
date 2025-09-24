"""
Base tool class for the ReWOO application.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator
from pydantic import BaseModel, Field
from loguru import logger


class ToolMetadata(BaseModel):
    """Metadata for a tool."""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    version: str = Field(default="1.0.0", description="Version of the tool")
    author: str = Field(default="ReWOO", description="Author of the tool")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the tool")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")


class ToolResult(BaseModel):
    """Result from a tool execution."""
    
    success: bool = Field(..., description="Whether the tool execution was successful")
    result: Optional[Any] = Field(None, description="The result of the tool execution")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    duration: Optional[float] = Field(None, description="Execution duration in seconds")
    
    @classmethod
    def success_result(cls, result: Any, metadata: Optional[Dict[str, Any]] = None) -> "ToolResult":
        """Create a successful result."""
        return cls(
            success=True,
            result=result,
            metadata=metadata or {}
        )
    
    @classmethod
    def error_result(cls, error: str, metadata: Optional[Dict[str, Any]] = None) -> "ToolResult":
        """Create an error result."""
        return cls(
            success=False,
            error=error,
            metadata=metadata or {}
        )


class BaseTool(ABC):
    """Base class for all tools in the ReWOO system."""
    
    def __init__(self, name: str, description: str, **kwargs):
        self.name = name
        self.description = description
        self.metadata = self._create_metadata(**kwargs)
        self.logger = logger
        
    def _create_metadata(self, **kwargs) -> ToolMetadata:
        """Create metadata for the tool."""
        return ToolMetadata(
            name=self.name,
            description=self.description,
            **kwargs
        )
    
    @abstractmethod
    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        """
        Execute the tool with the given input.
        
        Args:
            input_data: The input string for the tool
            **kwargs: Additional keyword arguments
            
        Returns:
            ToolResult containing the execution result
        """
        pass
    
    async def execute_streaming(self, input_data: str, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute the tool with streaming support.
        
        Args:
            input_data: The input string for the tool
            **kwargs: Additional keyword arguments
            
        Yields:
            Dict containing streaming updates
        """
        # Default implementation - just yield the final result
        try:
            result = await self.execute(input_data, **kwargs)
            yield {
                "type": "result",
                "data": result.model_dump()
            }
        except Exception as e:
            yield {
                "type": "error",
                "data": {"error": str(e)}
            }
    
    def validate_input(self, input_data: str) -> bool:
        """
        Validate the input data for the tool.
        
        Args:
            input_data: The input string to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(input_data, str) and len(input_data.strip()) > 0
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema information."""
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata.model_dump(),
            "parameters": self.metadata.parameters
        }
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Get usage examples for the tool."""
        return self.metadata.examples
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class ToolRegistry:
    """Registry for managing tools in the ReWOO system."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.logger = logger
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool in the registry."""
        if tool.name in self._tools:
            self.logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")
        
        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool from the registry."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            self.logger.info(f"Unregistered tool: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_tool_names(self) -> List[str]:
        """Get names of all registered tools."""
        return list(self._tools.keys())
    
    def get_tools_by_tag(self, tag: str) -> List[BaseTool]:
        """Get tools that have a specific tag."""
        return [tool for tool in self._tools.values() if tag in tool.metadata.tags]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools with their metadata."""
        return [tool.get_schema() for tool in self._tools.values()]
    
    async def execute_tool(self, tool_name: str, input_data: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult.error_result(f"Tool '{tool_name}' not found")
        
        try:
            return await tool.execute(input_data, **kwargs)
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {e}")
            return ToolResult.error_result(f"Tool execution failed: {str(e)}")
    
    async def execute_tool_streaming(self, tool_name: str, input_data: str, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Execute a tool with streaming support."""
        tool = self.get_tool(tool_name)
        if not tool:
            yield {
                "type": "error",
                "data": {"error": f"Tool '{tool_name}' not found"}
            }
            return
        
        try:
            async for update in tool.execute_streaming(input_data, **kwargs):
                yield update
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}' with streaming: {e}")
            yield {
                "type": "error",
                "data": {"error": f"Tool execution failed: {str(e)}"}
            }
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools
    
    def __iter__(self):
        return iter(self._tools.values())


# Global tool registry instance
tool_registry = ToolRegistry() 