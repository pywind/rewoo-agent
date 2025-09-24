"""
FastAPI controllers for the ReWOO application.
"""
import json
from datetime import datetime
from typing import Any

from loguru import logger
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
# WebSocket support for real-time updates
from fastapi import WebSocket, WebSocketDisconnect

from ...models import TaskRequest, TaskType, TaskPriority, TaskExecutionRequest, TaskExecutionResponse, TaskStatusResponse
from ..services.rewoo_service import ReWOOService
from ..tools import tool_registry


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


router = APIRouter(prefix="/agent", tags=["Tools API"])


# Initialize ReWOO service
rewoo_service = ReWOOService()

# API Routes

@router.get("/tools")
async def get_available_tools():
    """Get available tools."""
    try:
        tools = tool_registry.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/execute", response_model=TaskExecutionResponse)
async def execute_task(request: TaskExecutionRequest):
    """Execute a task."""
    try:
        # Create task request
        task_request = TaskRequest(
            task_description=request.description,
            task_type=request.task_type,
            priority=request.priority or TaskPriority.MEDIUM,
            context=request.context or {},
            user_id="default_user",
            configuration=None
        )
        
        if request.streaming:
            # Return streaming response
            return TaskExecutionResponse(
                request_id=task_request.request_id,
                status="started",
                message="Task started with streaming",
                streaming_url=f"/tasks/{task_request.request_id}/stream"
            )
        else:
            # Execute synchronously (not recommended for long tasks)
            result = await rewoo_service.execute_task(task_request)
            return TaskExecutionResponse(
                request_id=task_request.request_id,
                status=result.status,
                message="Task completed"
            )
    
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{request_id}/stream")
async def stream_task_execution(request_id: str):
    """Stream task execution results."""
    try:
        # Create task request (in a real implementation, you might store this)
        # For now, we'll create a dummy request
        task_request = TaskRequest(
            request_id=request_id,
            task_description="Stream task execution",
            task_type=TaskType.SEARCH,
            user_id="default_user",
            configuration=None
        )
        
        async def generate_stream():
            try:
                async for update in rewoo_service.execute_task_streaming(task_request):
                    yield f"data: {json.dumps(update, cls=DateTimeEncoder)}\n\n"
            except Exception as e:
                error_update = {
                    "type": "error",
                    "data": {"error": str(e)}
                }
                yield f"data: {json.dumps(error_update, cls=DateTimeEncoder)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    
    except Exception as e:
        logger.error(f"Error streaming task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/execute-stream")
async def execute_task_stream(request: TaskExecutionRequest):
    """Execute a task with streaming response."""
    try:
        # Create task request
        task_request = TaskRequest(
            task_description=request.description,
            task_type=request.task_type,
            priority=request.priority or TaskPriority.MEDIUM,
            context=request.context or {},
            user_id="default_user",
            configuration=None
        )
        
        async def generate_stream():
            try:
                async for update in rewoo_service.execute_task_streaming(task_request):
                    yield f"data: {json.dumps(update, cls=DateTimeEncoder)}\n\n"
            except Exception as e:
                error_update = {
                    "type": "error",
                    "data": {"error": str(e)}
                }
                yield f"data: {json.dumps(error_update, cls=DateTimeEncoder)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    
    except Exception as e:
        logger.error(f"Error executing streaming task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{request_id}/status", response_model=TaskStatusResponse)
async def get_task_status(request_id: str):
    """Get task status."""
    try:
        status = rewoo_service.get_task_status(request_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskStatusResponse(**status)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{request_id}")
async def cancel_task(request_id: str):
    """Cancel a task."""
    try:
        success = await rewoo_service.cancel_task(request_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task cancelled successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks")
async def get_active_tasks():
    """Get all active tasks."""
    try:
        active_tasks = rewoo_service.get_active_tasks()
        return {"active_tasks": active_tasks}
    
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/tasks/{request_id}")
async def websocket_task_updates(websocket: WebSocket, request_id: str):
    """WebSocket endpoint for real-time task updates."""
    await websocket.accept()
    
    try:
        # Create task request
        task_request = TaskRequest(
            request_id=request_id,
            task_description="WebSocket task execution",
            task_type=TaskType.SEARCH,
            user_id="default_user",
            configuration=None
        )
        
        async for update in rewoo_service.execute_task_streaming(task_request):
            await websocket.send_json(update)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task: {request_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {request_id}: {e}")
        await websocket.send_json({
            "type": "error",
            "data": {"error": str(e)}
        })
    finally:
        await websocket.close()

