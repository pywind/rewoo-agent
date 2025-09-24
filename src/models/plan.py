"""
Plan models for the ReWOO application.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class PlanStepType(str, Enum):
    """Types of plan steps."""
    TOOL = "tool"
    SOLVE = "solve"


class PlanStepStatus(str, Enum):
    """Status of a plan step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    """A single step in a ReWOO plan."""
    
    step_id: str = Field(..., description="Unique identifier for the step")
    step_type: PlanStepType = Field(..., description="Type of the step")
    step_number: int = Field(..., description="Order of the step in the plan")
    tool_name: Optional[str] = Field(None, description="Name of the tool to use")
    tool_input: Optional[str] = Field(None, description="Input for the tool")
    variable_name: Optional[str] = Field(None, description="Variable name to store result")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other steps")
    description: str = Field(..., description="Human-readable description of the step")
    status: PlanStepStatus = Field(default=PlanStepStatus.PENDING, description="Current status")
    result: Optional[Any] = Field(None, description="Result of the step execution")
    error: Optional[str] = Field(None, description="Error message if step failed")
    started_at: Optional[datetime] = Field(None, description="When step execution started")
    completed_at: Optional[datetime] = Field(None, description="When step execution completed")
    
    class Config:
        use_enum_values = True


class PlanStatus(str, Enum):
    """Status of a plan."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Plan(BaseModel):
    """A complete ReWOO plan."""
    
    plan_id: str = Field(..., description="Unique identifier for the plan")
    task_description: str = Field(..., description="Original task description")
    steps: List[PlanStep] = Field(default_factory=list, description="List of plan steps")
    status: PlanStatus = Field(default=PlanStatus.CREATED, description="Current plan status")
    created_at: datetime = Field(default_factory=datetime.now, description="When plan was created")
    started_at: Optional[datetime] = Field(None, description="When plan execution started")
    completed_at: Optional[datetime] = Field(None, description="When plan execution completed")
    final_answer: Optional[str] = Field(None, description="Final answer from the plan")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True
    
    def get_step_by_id(self, step_id: str) -> Optional[PlanStep]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next step to execute."""
        for step in self.steps:
            if step.status == PlanStepStatus.PENDING:
                # Check if all dependencies are completed
                if self._are_dependencies_completed(step):
                    return step
        return None
    
    def get_completed_steps(self) -> List[PlanStep]:
        """Get all completed steps."""
        return [step for step in self.steps if step.status == PlanStepStatus.COMPLETED]
    
    def get_failed_steps(self) -> List[PlanStep]:
        """Get all failed steps."""
        return [step for step in self.steps if step.status == PlanStepStatus.FAILED]
    
    def is_completed(self) -> bool:
        """Check if all steps are completed."""
        return all(step.status == PlanStepStatus.COMPLETED for step in self.steps)
    
    def has_failed_steps(self) -> bool:
        """Check if any step has failed."""
        return any(step.status == PlanStepStatus.FAILED for step in self.steps)
    
    def get_variables(self) -> Dict[str, Any]:
        """Get all variables from completed steps."""
        variables = {}
        for step in self.steps:
            if step.status == PlanStepStatus.COMPLETED and step.variable_name:
                variables[step.variable_name] = step.result
        return variables
    
    def _are_dependencies_completed(self, step: PlanStep) -> bool:
        """Check if all dependencies of a step are completed."""
        for dep_id in step.dependencies:
            dep_step = self.get_step_by_id(dep_id)
            if not dep_step or dep_step.status != PlanStepStatus.COMPLETED:
                return False
        return True


class ExecutionContext(BaseModel):
    """Context for plan execution."""
    
    plan: Plan = Field(..., description="The plan being executed")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Variables available in context")
    current_step: Optional[PlanStep] = Field(None, description="Currently executing step")
    iteration: int = Field(default=0, description="Current iteration number")
    max_iterations: int = Field(default=10, description="Maximum number of iterations")
    
    class Config:
        arbitrary_types_allowed = True
    
    def update_variable(self, name: str, value: Any) -> None:
        """Update a variable in the context."""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable from the context."""
        return self.variables.get(name)
    
    def substitute_variables(self, text: str) -> str:
        """Substitute variables in text with their values."""
        result = text
        for var_name, var_value in self.variables.items():
            placeholder = f"#{var_name}#"
            if placeholder in result:
                result = result.replace(placeholder, str(var_value))
        return result 