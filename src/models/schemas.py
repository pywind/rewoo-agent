


# Request/Response models
from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from .task import TaskPriority, TaskType

class APIResponse(BaseModel):
    """Response model for API."""
    success: bool
    message: str
    error_code: str
    data: Optional[Any] = None

class TaskExecutionRequest(BaseModel):
    """Request model for task execution."""
    description: str
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    context: Optional[Dict[str, Any]] = None
    streaming: bool = True

class TaskExecutionResponse(BaseModel):
    """Response model for task execution."""
    request_id: str
    status: str
    message: str
    streaming_url: Optional[str] = None

class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    request_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    plan: Optional[Dict[str, Any]] = None


