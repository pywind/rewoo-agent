"""
Tests for the ReWOO tool system.
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rewoo.tools.base import BaseTool, ToolResult, ToolRegistry
from src.rewoo.tools.calculator import CalculatorTool
from src.rewoo.tools.wikipedia import WikipediaTool
from src.rewoo.tools.search import SearchTool


class TestBaseTool:
    """Test the base tool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata creation."""
        tool = CalculatorTool()
        
        assert tool.name == "calculator"
        assert tool.description == "Perform mathematical calculations and solve equations"
        assert tool.metadata.version == "1.0.0"
        assert "math" in tool.metadata.tags
    
    def test_tool_validation(self):
        """Test input validation."""
        tool = CalculatorTool()
        
        # Valid input
        assert tool.validate_input("2 + 2") == True
        
        # Invalid input
        assert tool.validate_input("") == False
        assert tool.validate_input("   ") == False
    
    def test_tool_schema(self):
        """Test tool schema generation."""
        tool = CalculatorTool()
        schema = tool.get_schema()
        
        assert "name" in schema
        assert "description" in schema
        assert "metadata" in schema
        assert schema["name"] == "calculator"


class TestToolRegistry:
    """Test the tool registry functionality."""
    
    def test_registry_operations(self):
        """Test basic registry operations."""
        registry = ToolRegistry()
        tool = CalculatorTool()
        
        # Register tool
        registry.register_tool(tool)
        assert len(registry) == 1
        assert "calculator" in registry
        
        # Get tool
        retrieved_tool = registry.get_tool("calculator")
        assert retrieved_tool is not None
        assert retrieved_tool.name == "calculator"
        
        # Unregister tool
        success = registry.unregister_tool("calculator")
        assert success == True
        assert len(registry) == 0
        assert "calculator" not in registry
    
    def test_tool_listing(self):
        """Test tool listing functionality."""
        registry = ToolRegistry()
        
        calc_tool = CalculatorTool()
        wiki_tool = WikipediaTool()
        
        registry.register_tool(calc_tool)
        registry.register_tool(wiki_tool)
        
        # Test get_tool_names
        names = registry.get_tool_names()
        assert "calculator" in names
        assert "wikipedia" in names
        
        # Test list_tools
        tools = registry.list_tools()
        assert len(tools) == 2
        assert any(tool["name"] == "calculator" for tool in tools)
        assert any(tool["name"] == "wikipedia" for tool in tools)


class TestCalculatorTool:
    """Test the calculator tool."""
    
    @pytest.mark.asyncio
    async def test_basic_calculation(self):
        """Test basic mathematical calculations."""
        tool = CalculatorTool()
        
        # Simple addition
        result = await tool.execute("2 + 3")
        assert result.success == True
        assert result.result == 5
        
        # Simple multiplication
        result = await tool.execute("4 * 5")
        assert result.success == True
        assert result.result == 20
        
        # Power operation
        result = await tool.execute("2 ** 3")
        assert result.success == True
        assert result.result == 8
    
    @pytest.mark.asyncio
    async def test_complex_calculation(self):
        """Test complex mathematical expressions."""
        tool = CalculatorTool()
        
        # Complex expression
        result = await tool.execute("(2 + 3) * 4 - 1")
        assert result.success == True
        assert result.result == 19
        
        # Square root
        result = await tool.execute("sqrt(16)")
        assert result.success == True
        assert result.result == 4.0
    
    @pytest.mark.asyncio
    async def test_invalid_calculation(self):
        """Test invalid calculations."""
        tool = CalculatorTool()
        
        # Division by zero
        result = await tool.execute("1 / 0")
        assert result.success == False
        assert "error" in result.error.lower()
        
        # Invalid expression
        result = await tool.execute("invalid expression")
        assert result.success == False


class TestWikipediaTool:
    """Test the Wikipedia tool."""
    
    @pytest.mark.asyncio
    async def test_wikipedia_search(self):
        """Test Wikipedia search functionality."""
        tool = WikipediaTool()
        
        # Search for a well-known topic
        result = await tool.execute("Python programming language")
        
        # The result should be successful
        assert result.success == True
        assert result.result is not None
        
        # Check result structure
        if isinstance(result.result, dict):
            assert "title" in result.result
            assert "summary" in result.result
            assert "url" in result.result
    
    @pytest.mark.asyncio
    async def test_wikipedia_streaming(self):
        """Test Wikipedia tool streaming."""
        tool = WikipediaTool()
        
        updates = []
        async for update in tool.execute_streaming("Python"):
            updates.append(update)
        
        assert len(updates) > 0
        
        # Check for final result
        final_update = updates[-1]
        assert final_update["type"] == "result"
        assert final_update["data"]["success"] == True


class TestSearchTool:
    """Test the search tool."""
    
    @pytest.mark.asyncio
    async def test_search_execution(self):
        """Test search tool execution."""
        tool = SearchTool()
        
        # Perform a search
        result = await tool.execute("Python programming")
        
        # The result should be successful
        assert result.success == True
        assert result.result is not None
        
        # Check result structure
        if isinstance(result.result, list) and len(result.result) > 0:
            first_result = result.result[0]
            assert "title" in first_result
            assert "url" in first_result
            assert "snippet" in first_result
    
    @pytest.mark.asyncio
    async def test_search_streaming(self):
        """Test search tool streaming."""
        tool = SearchTool()
        
        updates = []
        async for update in tool.execute_streaming("test query"):
            updates.append(update)
        
        assert len(updates) > 0
        
        # Check for status updates
        status_updates = [u for u in updates if u["type"] == "status"]
        assert len(status_updates) > 0
        
        # Check for final result
        result_updates = [u for u in updates if u["type"] == "result"]
        assert len(result_updates) > 0


if __name__ == "__main__":
    pytest.main([__file__]) 