"""
Streaming example demonstrating the ReWOO system with real-time updates.
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
    """Main function to demonstrate ReWOO streaming."""
    print("=== ReWOO Streaming Example ===")
    
    # Initialize the ReWOO service
    rewoo_service = ReWOOService()
    register_default_tools()
    setup_logging(
        app_name="rewoo_streaming_example",
        console_level="INFO",
        file_level="CRITICAL"
    )
    # Example: Complex research task with streaming
    print("\nComplex Research Task with Streaming")
    task_request = TaskRequest(
        task_description="",
        task_type=TaskType.RESEARCH,
        user_id="example_user",
        priority="high",
        context={"topic": "Latest advancements in renewable energy technologies"},
        configuration=None
    )
    
    print(f"Task: {task_request.task_description}")
    print("Executing with streaming updates...")
    print("-" * 50)
    
    # Execute with streaming
    async for update in rewoo_service.execute_task_streaming(task_request):
        update_type = update.get("type", "unknown")
        data = update.get("data", {})
        
        if update_type == "task_started":
            print(f"✓ Task started: {data.get('request_id')}")
        
        elif update_type == "task_status":
            print(f"📊 Status: {data.get('status')} - {data.get('message')}")
        
        elif update_type == "planning_update":
            planning_data = data.get("data", {})
            if planning_data.get("type") == "status":
                status_data = planning_data.get("data", {})
                print(f"🎯 Planning: {status_data.get('message')} ({status_data.get('progress', 0)}%)")
        
        elif update_type == "execution_update":
            exec_data = data.get("data", {})
            if exec_data.get("type") == "step_started":
                step_data = exec_data.get("data", {})
                print(f"▶️  Step {step_data.get('step_number')}: {step_data.get('description')}")
            
            elif exec_data.get("type") == "step_progress":
                step_data = exec_data.get("data", {})
                tool_update = step_data.get("tool_update", {})
                if tool_update.get("type") == "status":
                    tool_data = tool_update.get("data", {})
                    print(f"   ⏳ {tool_data.get('message')} ({tool_data.get('progress', 0)}%)")
            
            elif exec_data.get("type") == "step_completed":
                step_data = exec_data.get("data", {})
                print(f"✅ Step {step_data.get('step_number')} completed")
            
            elif exec_data.get("type") == "execution_completed":
                exec_result = exec_data.get("data", {})
                print(f"🎉 Execution completed: {exec_result.get('status')}")
        
        elif update_type == "task_completed":
            print(f"✅ Task completed: {data.get('status')}")
            print(f"⏱️  Duration: {data.get('duration', 0):.2f}s")
            print("-" * 50)
            print("Final Result:")
            print(data.get('result', 'No result'))
        
        elif update_type == "task_failed":
            print(f"❌ Task failed: {data.get('error')}")
        
        # Add a small delay to make the output more readable
        await asyncio.sleep(0.1)
    
    print("\n=== Streaming Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main()) 