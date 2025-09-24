"""
Custom tool example demonstrating how to create and register custom tools.
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, AsyncIterator
import random
import time

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rewoo_agent.tools.base import BaseTool, ToolResult
from src.rewoo_agent.tools import tool_registry
from src.models import TaskRequest, TaskType
from src.rewoo_agent.services import ReWOOService


class WeatherTool(BaseTool):
    """Example custom tool for weather information."""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get current weather information for a city",
            version="1.0.0",
            tags=["weather", "information"],
            parameters={
                "city": {
                    "type": "string",
                    "description": "Name of the city to get weather for",
                    "required": True
                }
            },
            examples=[
                {
                    "input": "New York",
                    "output": "Current weather in New York: 22°C, Sunny"
                },
                {
                    "input": "London",
                    "output": "Current weather in London: 15°C, Cloudy"
                }
            ]
        )
    
    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        """Execute weather lookup."""
        try:
            if not self.validate_input(input_data):
                return ToolResult.error_result("Invalid city name")
            
            city = input_data.strip()
            
            # Simulate API call delay
            await asyncio.sleep(1)
            
            # Mock weather data
            weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Partly Cloudy"]
            temperature = random.randint(-10, 35)
            condition = random.choice(weather_conditions)
            
            weather_info = {
                "city": city,
                "temperature": f"{temperature}°C",
                "condition": condition,
                "humidity": f"{random.randint(30, 90)}%",
                "wind_speed": f"{random.randint(5, 25)} km/h"
            }
            
            return ToolResult.success_result(
                result=weather_info,
                metadata={"city": city, "source": "mock_weather_api"}
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Weather lookup failed: {str(e)}")
    
    async def execute_streaming(self, input_data: str, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Execute weather lookup with streaming updates."""
        try:
            if not self.validate_input(input_data):
                yield {
                    "type": "error",
                    "data": {"error": "Invalid city name"}
                }
                return
            
            city = input_data.strip()
            
            yield {
                "type": "status",
                "data": {"message": f"Looking up weather for {city}", "progress": 25}
            }
            
            # Simulate API call
            await asyncio.sleep(0.5)
            
            yield {
                "type": "status",
                "data": {"message": "Fetching weather data", "progress": 50}
            }
            
            await asyncio.sleep(0.5)
            
            yield {
                "type": "status",
                "data": {"message": "Processing weather information", "progress": 75}
            }
            
            # Mock weather data
            weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Partly Cloudy"]
            temperature = random.randint(-10, 35)
            condition = random.choice(weather_conditions)
            
            weather_info = {
                "city": city,
                "temperature": f"{temperature}°C",
                "condition": condition,
                "humidity": f"{random.randint(30, 90)}%",
                "wind_speed": f"{random.randint(5, 25)} km/h"
            }
            
            yield {
                "type": "status",
                "data": {"message": "Weather lookup completed", "progress": 100}
            }
            
            yield {
                "type": "result",
                "data": {
                    "success": True,
                    "result": weather_info,
                    "metadata": {"city": city, "source": "mock_weather_api"}
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"error": f"Weather lookup failed: {str(e)}"}
            }


class TranslatorTool(BaseTool):
    """Example custom tool for text translation."""
    
    def __init__(self):
        super().__init__(
            name="translator",
            description="Translate text between languages",
            version="1.0.0",
            tags=["translation", "language", "nlp"],
            parameters={
                "text": {
                    "type": "string",
                    "description": "Text to translate",
                    "required": True
                },
                "target_language": {
                    "type": "string",
                    "description": "Target language code (e.g., 'es', 'fr', 'de')",
                    "required": False,
                    "default": "es"
                }
            },
            examples=[
                {
                    "input": "Hello world",
                    "output": "Hola mundo"
                },
                {
                    "input": "Good morning",
                    "output": "Buenos días"
                }
            ]
        )
    
    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        """Execute translation."""
        try:
            if not self.validate_input(input_data):
                return ToolResult.error_result("Invalid text to translate")
            
            text = input_data.strip()
            target_language = kwargs.get('target_language', 'es')
            
            # Simulate translation delay
            await asyncio.sleep(0.5)
            
            # Mock translation (simple mapping for demo)
            translations = {
                "hello": {"es": "hola", "fr": "bonjour", "de": "hallo"},
                "world": {"es": "mundo", "fr": "monde", "de": "welt"},
                "good": {"es": "bueno", "fr": "bon", "de": "gut"},
                "morning": {"es": "mañana", "fr": "matin", "de": "morgen"},
                "thank you": {"es": "gracias", "fr": "merci", "de": "danke"}
            }
            
            # Simple word-by-word translation
            words = text.lower().split()
            translated_words = []
            
            for word in words:
                if word in translations and target_language in translations[word]:
                    translated_words.append(translations[word][target_language])
                else:
                    # If translation not found, keep original word
                    translated_words.append(f"[{word}]")
            
            translated_text = " ".join(translated_words)
            
            translation_result = {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": "en",
                "target_language": target_language
            }
            
            return ToolResult.success_result(
                result=translation_result,
                metadata={"source": "mock_translator", "target_language": target_language}
            )
            
        except Exception as e:
            return ToolResult.error_result(f"Translation failed: {str(e)}")


async def main():
    """Main function to demonstrate custom tools."""
    print("=== Custom Tool Example ===")
    
    # Register custom tools
    print("\n1. Registering Custom Tools")
    weather_tool = WeatherTool()
    translator_tool = TranslatorTool()
    
    tool_registry.register_tool(weather_tool)
    tool_registry.register_tool(translator_tool)
    
    print(f"Registered tools: {tool_registry.get_tool_names()}")
    
    # Test custom tools individually
    print("\n2. Testing Custom Tools")
    
    # Test weather tool
    print("\nTesting Weather Tool:")
    result = await weather_tool.execute("Paris")
    print(f"Weather in Paris: {result.result}")
    
    # Test translator tool
    print("\nTesting Translator Tool:")
    result = await translator_tool.execute("Hello world")
    print(f"Translation: {result.result}")
    
    # Use custom tools in ReWOO system
    print("\n3. Using Custom Tools in ReWOO")
    rewoo_service = ReWOOService()
    
    # Task that uses custom tools
    task_request = TaskRequest(
        task_description="Get the weather for Tokyo and translate 'good morning' to Spanish",
        task_type=TaskType.CUSTOM
    )
    
    print(f"Task: {task_request.task_description}")
    print("Executing with custom tools...")
    
    result = await rewoo_service.execute_task(task_request)
    print(f"Result: {result.result}")
    print(f"Status: {result.status}")
    
    # Streaming example with custom tools
    print("\n4. Streaming with Custom Tools")
    task_request = TaskRequest(
        task_description="Check weather in London and translate the result to French",
        task_type=TaskType.CUSTOM
    )
    
    print(f"Task: {task_request.task_description}")
    print("Executing with streaming...")
    
    async for update in rewoo_service.execute_task_streaming(task_request):
        update_type = update.get("type", "unknown")
        data = update.get("data", {})
        
        if update_type == "task_completed":
            print(f"Final Result: {data.get('result')}")
            break
        elif update_type == "task_failed":
            print(f"Task failed: {data.get('error')}")
            break
    
    print("\n=== Custom Tool Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main()) 