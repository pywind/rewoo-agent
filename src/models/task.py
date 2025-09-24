"""
Task models for the ReWOO application.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid


class TaskType(str, Enum):
    """Types of tasks."""
    RESEARCH = "research"
    CALCULATION = "calculation"
    ANALYSIS = "analysis"
    SEARCH = "search"
    CUSTOM = "custom"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskTemplate(BaseModel):
    """Template for creating tasks."""
    
    template_id: str = Field(..., description="Unique identifier for the template")
    name: str = Field(..., description="Name of the task template")
    description: str = Field(..., description="Description of what the task does")
    task_type: TaskType = Field(..., description="Type of task")
    required_tools: List[str] = Field(default_factory=list, description="Tools required for this task")
    optional_tools: List[str] = Field(default_factory=list, description="Optional tools that can be used")
    plan_template: Optional[str] = Field(None, description="Template for generating plans")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Example inputs and outputs")
    
    class Config:
        use_enum_values = True


class TaskConfiguration(BaseModel):
    """Configuration for a specific task."""
    
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique configuration ID")
    template_id: Optional[str] = Field(None, description="Template this config is based on")
    task_type: TaskType = Field(..., description="Type of task")
    enabled_tools: List[str] = Field(default_factory=list, description="Tools enabled for this task")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task-specific parameters")
    timeout: int = Field(default=300, description="Timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    streaming: bool = Field(default=True, description="Enable streaming for this task")
    
    class Config:
        use_enum_values = True


class TaskRequest(BaseModel):
    """Request to execute a task."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request ID")
    user_id: Optional[str] = Field(None, description="User who made the request")
    task_description: str = Field(..., description="Description of the task to execute")
    task_type: Optional[TaskType] = Field(None, description="Type of task (auto-detected if not provided)")
    configuration: Optional[TaskConfiguration] = Field(None, description="Task configuration")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the task")
    created_at: datetime = Field(default_factory=datetime.now, description="When the request was created")
    
    class Config:
        use_enum_values = True


class TaskResult(BaseModel):
    """Result of task execution."""
    
    request_id: str = Field(..., description="ID of the original request")
    plan_id: Optional[str] = Field(None, description="ID of the plan that was executed")
    status: TaskStatus = Field(..., description="Final status of the task")
    result: Optional[Any] = Field(None, description="Final result of the task")
    error: Optional[str] = Field(None, description="Error message if task failed")
    started_at: Optional[datetime] = Field(None, description="When task execution started")
    completed_at: Optional[datetime] = Field(None, description="When task execution completed")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    steps_completed: int = Field(default=0, description="Number of steps completed")
    total_steps: int = Field(default=0, description="Total number of steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True
    
    def calculate_duration(self) -> Optional[float]:
        """Calculate task duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class StreamingEvent(BaseModel):
    """Streaming event for task execution."""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    request_id: str = Field(..., description="ID of the task request")
    event_type: str = Field(..., description="Type of event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    
    class Config:
        use_enum_values = True


class TaskRegistry(BaseModel):
    """Registry for task templates and configurations."""
    
    templates: Dict[str, TaskTemplate] = Field(default_factory=dict, description="Task templates")
    configurations: Dict[str, TaskConfiguration] = Field(default_factory=dict, description="Task configurations")
    
    def register_template(self, template: TaskTemplate) -> None:
        """Register a task template."""
        self.templates[template.template_id] = template
    
    def register_configuration(self, config: TaskConfiguration) -> None:
        """Register a task configuration."""
        self.configurations[config.config_id] = config
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """Get a task template by ID."""
        return self.templates.get(template_id)
    
    def get_configuration(self, config_id: str) -> Optional[TaskConfiguration]:
        """Get a task configuration by ID."""
        return self.configurations.get(config_id)
    
    def get_templates_by_type(self, task_type: TaskType) -> List[TaskTemplate]:
        """Get all templates of a specific type."""
        return [t for t in self.templates.values() if t.task_type == task_type]
    
    def get_configurations_by_type(self, task_type: TaskType) -> List[TaskConfiguration]:
        """Get all configurations of a specific type."""
        return [c for c in self.configurations.values() if c.task_type == task_type] 