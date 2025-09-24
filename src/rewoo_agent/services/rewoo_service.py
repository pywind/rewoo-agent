"""
Main ReWOO service that orchestrates planning and execution.
"""

from typing import Dict, Any, Optional, AsyncIterator

from datetime import datetime

from loguru import logger
from ...models import TaskRequest, TaskResult, TaskStatus, Plan, TaskRegistry
from .planner import PlannerService
from .executor import ExecutorService
from .redis_service import RedisService, ActiveTaskData



class ReWOOService:
    """Main service that coordinates ReWOO planning and execution."""
    
    def __init__(self):
        self.planner = PlannerService()
        self.executor = ExecutorService()
        self.task_registry = TaskRegistry()
        self.redis_service = RedisService()
        self.logger = logger
    
    async def execute_task(self, task_request: TaskRequest) -> TaskResult:
        """Execute a task using ReWOO methodology."""
        try:
            self.logger.info(f"Starting task execution: {task_request.request_id}")
            
            # Create task result
            task_result = TaskResult(
                request_id=task_request.request_id,
                status=TaskStatus.PLANNING,
                started_at=datetime.now()
            )

            # Store active task in Redis
            task_data = ActiveTaskData(request=task_request, result=task_result, plan=None)
            self.redis_service.store_active_task(task_request.request_id, task_data)
            
            # Step 1: Generate plan
            plan = await self.planner.create_plan(task_request)
            task_result.plan_id = plan.plan_id
            self.redis_service.update_task_plan(task_request.request_id, plan)
            
            # Step 2: Execute plan
            task_result.status = TaskStatus.EXECUTING
            executed_plan = await self.executor.execute_plan(plan)
            
            # Step 3: Finalize result
            task_result.status = TaskStatus.COMPLETED if executed_plan.status.value == "completed" else TaskStatus.FAILED
            task_result.result = executed_plan.final_answer
            task_result.completed_at = datetime.now()
            task_result.duration = task_result.calculate_duration()
            task_result.steps_completed = len(executed_plan.get_completed_steps())
            task_result.total_steps = len(executed_plan.steps)

            # Clean up active task from Redis
            self.redis_service.remove_active_task(task_request.request_id)
            
            self.logger.info(f"Task execution completed: {task_request.request_id}")
            return task_result
            
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            
            # Update task result with error
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.completed_at = datetime.now()
            task_result.duration = task_result.calculate_duration()

            # Clean up active task from Redis
            self.redis_service.remove_active_task(task_request.request_id)
            
            return task_result
    
    async def execute_task_streaming(self, task_request: TaskRequest) -> AsyncIterator[Dict[str, Any]]:
        """Execute a task with streaming updates."""
        try:
            self.logger.info(f"Starting streaming task execution: {task_request.request_id}")
            
            # Create task result
            task_result = TaskResult(
                request_id=task_request.request_id,
                status=TaskStatus.PLANNING,
                started_at=datetime.now()
            )
            
            # Store active task in Redis
            task_data = ActiveTaskData(request=task_request, result=task_result, plan=None)
            self.redis_service.store_active_task(task_request.request_id, task_data)

            yield {
                "type": "task_started",
                "data": {
                    "request_id": task_request.request_id,
                    "description": task_request.task_description
                }
            }
            
            # Step 1: Generate plan with streaming
            yield {
                "type": "task_status",
                "data": {"status": "planning", "message": "Generating execution plan"}
            }
            
            plan = None
            async for update in self.planner.create_plan_streaming(task_request):
                if update["type"] == "plan_created":
                    plan = Plan(**update["data"]["plan"])
                    task_result.plan_id = plan.plan_id
                    self.redis_service.update_task_plan(task_request.request_id, plan)
                
                yield {
                    "type": "planning_update",
                    "data": update
                }
            
            if not plan:
                raise ValueError("Failed to generate plan")
            
            # Step 2: Execute plan with streaming
            yield {
                "type": "task_status",
                "data": {"status": "executing", "message": "Executing plan"}
            }
            
            task_result.status = TaskStatus.EXECUTING
            
            async for update in self.executor.execute_plan_streaming(plan):
                if update["type"] == "execution_completed":
                    # Update task result
                    task_result.status = TaskStatus.COMPLETED if update["data"]["status"] == "completed" else TaskStatus.FAILED
                    task_result.result = update["data"]["final_answer"]
                    task_result.completed_at = datetime.now()
                    task_result.duration = task_result.calculate_duration()
                    task_result.steps_completed = len(plan.get_completed_steps())
                    task_result.total_steps = len(plan.steps)
                
                yield {
                    "type": "execution_update",
                    "data": update
                }
            
            # Final task completion
            yield {
                "type": "task_completed",
                "data": {
                    "request_id": task_request.request_id,
                    "status": task_result.status,
                    "result": task_result.result,
                    "duration": task_result.duration
                }
            }

            # Clean up active task from Redis
            self.redis_service.remove_active_task(task_request.request_id)
            
        except Exception as e:
            self.logger.error(f"Error in streaming task execution: {e}")
            
            # Update task result with error
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.completed_at = datetime.now()
            task_result.duration = task_result.calculate_duration()
            
            yield {
                "type": "task_failed",
                "data": {
                    "request_id": task_request.request_id,
                    "error": str(e)
                }
            }

            # Clean up active task from Redis
            self.redis_service.remove_active_task(task_request.request_id)
    
    async def cancel_task(self, request_id: str) -> bool:
        """Cancel an active task."""
        task_data = self.redis_service.get_active_task(request_id)
        if task_data:
            task_data.result.status = TaskStatus.CANCELLED
            task_data.result.completed_at = datetime.now()
            task_data.result.duration = task_data.result.calculate_duration()

            # Update the task in Redis
            self.redis_service.store_active_task(request_id, task_data)

            # Note: In a real implementation, you would need to handle
            # cancellation of ongoing operations more gracefully

            self.logger.info(f"Task cancelled: {request_id}")
            return True

        return False
    
    def get_task_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task."""
        task_data = self.redis_service.get_active_task(request_id)
        if task_data:
            status = {
                "request_id": request_id,
                "status": task_data.result.status,
                "started_at": task_data.result.started_at,
                "duration": task_data.result.calculate_duration(),
            }

            # Add plan information if available
            if task_data.plan:
                plan = task_data.plan
                status["plan"] = {
                    "plan_id": plan.plan_id,
                    "total_steps": len(plan.steps),
                    "completed_steps": len(plan.get_completed_steps()),
                    "failed_steps": len(plan.get_failed_steps()),
                    "progress_percentage": (len(plan.get_completed_steps()) / len(plan.steps) * 100) if plan.steps else 0
                }

            return status

        return None
    
    def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all active tasks."""
        return self.redis_service.get_active_tasks_summary()
    
    def get_task_registry(self) -> TaskRegistry:
        """Get the task registry."""
        return self.task_registry

    
    async def test_tools(self) -> Dict[str, Any]:
        """Test all available tools."""
        from ..tools import tool_registry
        
        results = {}
        
        for tool_name in tool_registry.get_tool_names():
            try:
                # Test with a simple input
                test_input = "test" if tool_name != "calculator" else "2+2"
                result = await tool_registry.execute_tool(tool_name, test_input)
                results[tool_name] = {
                    "status": "success" if result.success else "failed",
                    "error": result.error if not result.success else None
                }
            except Exception as e:
                results[tool_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tools": results
        } 