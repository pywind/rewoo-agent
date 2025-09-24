"""
Simple example demonstrating the ReWOO system.
"""
import asyncio
import sys
from pathlib import Path



# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from src.models import TaskRequest, TaskType
from src.rewoo_agent.services import ReWOOService
from src.rewoo_agent.tools import register_default_tools
from src.helpers.log_factory import setup_logging

    
async def main():
    """Main function to demonstrate ReWOO."""
    print("=== ReWOO Simple Example ===")
    register_default_tools()
    setup_logging(
        app_name="rewoo_simple_example",
        console_level="INFO",
        file_level="CRITICAL"
    )
    # Initialize the ReWOO service
    rewoo_service = ReWOOService()
    
    # Example 1: Simple search task
    # print("\n1. Simple Search Task")
    # task_request = TaskRequest(
    #     task_description="What is the news about the new iPhone 17?",
    #     task_type=TaskType.SEARCH
    # )
    
    # print(f"Task: {task_request.task_description}")
    # print("Executing...")
    
    # result = await rewoo_service.execute_task(task_request)
    # print(f"Result: {result.result}")
    # print(f"Status: {result.status}")
    # print(f"Duration: {result.duration:.2f}s")
    
    # Example 2: Calculation task
    # print("\n2. Calculation Task")
    # task_request = TaskRequest(
    #     task_description="Calculate the square root of 144 and multiply by 5",
    #     task_type=TaskType.CALCULATION
    # )
    
    # print(f"Task: {task_request.task_description}")
    # print("Executing...")
    
    # result = await rewoo_service.execute_task(task_request)
    # print(f"Result: {result.result}")
    # print(f"Status: {result.status}")
    # print(f"Duration: {result.duration:.2f}s")
    
    # Example 3: Research task
    print("\n3. Research Task")
    task_request = TaskRequest(
        task_description="Research information about scaled_dot_product_attention and its implementation in the transformer model",
        task_type=TaskType.RESEARCH
    )
    
    print(f"Task: {task_request.task_description}")
    print("Executing...")
    
    result = await rewoo_service.execute_task(task_request)
    print(f"Result: {result.result}")
    print(f"Status: {result.status}")
    print(f"Duration: {result.duration:.2f}s")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main()) 