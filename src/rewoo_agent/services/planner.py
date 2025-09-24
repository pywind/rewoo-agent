"""
Planner service for generating ReWOO plans.
"""
import uuid
from typing import List, Dict, Any, Optional, AsyncIterator

from loguru import logger
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage

from ...models import Plan, PlanStep, PlanStepType, TaskRequest, TaskType
from ..tools import tool_registry
from ...config.settings import settings




class PlannerService:
    """Service for generating execution plans using ReWOO methodology."""
    
    def __init__(self):
        self.llm = init_chat_model(
            model=settings.model.model_name,
            model_provider=settings.model.model_provider,
            temperature=settings.model.temperature
        )
        self.logger = logger
    
    async def create_plan(self, task_request: TaskRequest) -> Plan:
        """Create a plan for the given task request."""
        try:
            self.logger.info(f"Creating plan for task: {task_request.task_description}")
            
            # Generate plan steps using LLM
            plan_steps = await self._generate_plan_steps(task_request)
            
            # Create the plan
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                task_description=task_request.task_description,
                steps=plan_steps,
                metadata={
                    "task_request_id": task_request.request_id,
                    "task_type": task_request.task_type,
                    "created_by": "planner_service"
                }
            )
            
            self.logger.info(f"Created plan with {len(plan_steps)} steps \n {plan_steps}")
            return plan
            
        except Exception as e:
            self.logger.error(f"Error creating plan: {e}")
            raise
    
    async def create_plan_streaming(self, task_request: TaskRequest) -> AsyncIterator[Dict[str, Any]]:
        """Create a plan with streaming updates."""
        try:
            yield {
                "type": "status",
                "data": {"message": "Starting plan generation", "progress": 10}
            }
            
            # Generate plan steps using LLM
            plan_steps = await self._generate_plan_steps(task_request)
            
            yield {
                "type": "status",
                "data": {"message": f"Generated {len(plan_steps)} steps", "progress": 80}
            }
            
            # Create the plan
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                task_description=task_request.task_description,
                steps=plan_steps,
                metadata={
                    "task_request_id": task_request.request_id,
                    "task_type": task_request.task_type,
                    "created_by": "planner_service"
                }
            )
            
            yield {
                "type": "status",
                "data": {"message": "Plan creation completed", "progress": 100}
            }
            
            yield {
                "type": "plan_created",
                "data": {"plan": plan.model_dump()}
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"error": f"Plan generation failed: {str(e)}"}
            }
    
    async def _generate_plan_steps(self, task_request: TaskRequest) -> List[PlanStep]:
        """Generate plan steps using LLM."""
        try:
            # Get available tools
            available_tools = tool_registry.list_tools()
            tool_descriptions = []
            
            for tool in available_tools:
                tool_descriptions.append(
                    f"- {tool['name']}: {tool['description']}"
                )
            
            # Create prompt for plan generation
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(
                task_request.task_description,
                tool_descriptions,
                task_request.task_type
            )
            
            # Generate plan using LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            plan_text = response.generations[0][0].text
            
            # Parse the plan text into steps
            plan_steps = self._parse_plan_text(plan_text)
            
            return plan_steps
            
        except Exception as e:
            self.logger.error(f"Error generating plan steps: {e}")
            # Return a basic fallback plan
            return self._create_fallback_plan(task_request.task_description)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for plan generation."""
        return """You are a expert planner. Your task is to break down complex tasks into a series of steps that can be executed by available tools.

Follow these rules:
1. Create steps that use available tools to gather information or perform calculations
2. Each step should have a clear purpose and produce a result stored in a variable
3. Use variable substitution (#{variable_name}#) to reference results from previous steps
4. The final step should be a SOLVE step that combines all information to answer the original question
5. Keep steps simple and focused on one task each
6. Consider dependencies between steps

Format your response as:
Plan: <step_number>. <step_type> <tool_name> <tool_input> -> <variable_name>

Example 1:
Plan: 1. TOOL search What is the capital of France? -> #search_result#
Plan: 2. TOOL wikipedia #{search_result}# -> #wiki_info#
Plan: 3. SOLVE Use the information from #{search_result}# and #{wiki_info}# to answer the question about the capital of France -> #answer#

Example 2:
Plan: 1. TOOL calculator sqrt(16) + 3 * 4 -> #result#
Plan: 2. SOLVE Use the result from #{result}# to answer the question about the mathematics-> #answer#
"""
    
    def _create_user_prompt(self, task_description: str, tool_descriptions: List[str], task_type: Optional[TaskType]) -> str:
        """Create the user prompt for plan generation."""
        tools_text = "\n".join(tool_descriptions)
        
        return f"""Task: {task_description}
Task Type: {task_type or 'General'}

Available Tools:
{tools_text}

Create a step-by-step plan to complete this task using the available tools. Each step should be clear and focused."""
    
    def _parse_plan_text(self, plan_text: str) -> List[PlanStep]:
        """Parse the LLM generated plan text into PlanStep objects."""
        steps = []
        lines = plan_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line.startswith('Plan:'):
                continue
            
            try:
                # Remove "Plan:" prefix
                step_text = line[5:].strip()
                
                # Parse step format: <number>. <type> <tool_name> <input> -> <variable>
                parts = step_text.split(' -> ')
                if len(parts) != 2:
                    continue
                
                left_part = parts[0].strip()
                variable_name = parts[1].strip().replace('#', '')
                
                # Parse left part: <number>. <type> <tool_name> <input>
                step_parts = left_part.split('.', 1)
                if len(step_parts) != 2:
                    continue
                
                step_number = int(step_parts[0].strip())
                rest = step_parts[1].strip()
                
                # Parse type and tool
                if rest.startswith('TOOL '):
                    step_type = PlanStepType.TOOL
                    tool_part = rest[5:].strip()
                    
                    # Split tool name and input
                    tool_parts = tool_part.split(' ', 1)
                    if len(tool_parts) >= 2:
                        tool_name = tool_parts[0]
                        tool_input = tool_parts[1]
                    else:
                        tool_name = tool_parts[0]
                        tool_input = ""
                        
                elif rest.startswith('SOLVE '):
                    step_type = PlanStepType.SOLVE
                    tool_name = None
                    tool_input = rest[6:].strip()
                else:
                    continue
                
                # Create the step
                step = PlanStep(
                    step_id=str(uuid.uuid4()),
                    step_type=step_type,
                    step_number=step_number,
                    tool_name=tool_name,
                    tool_input=tool_input,
                    variable_name=variable_name,
                    description=f"Step {step_number}: {step_type.value} - {tool_input[:50]}..."
                )
                
                steps.append(step)
                
            except Exception as e:
                self.logger.warning(f"Error parsing plan step: {line}, error: {e}")
                continue
        
        # Sort steps by step number
        steps.sort(key=lambda x: x.step_number)
        
        return steps
    
    def _create_fallback_plan(self, task_description: str) -> List[PlanStep]:
        """Create a simple fallback plan if LLM generation fails."""
        steps = []
        
        # Step 1: Search for information
        steps.append(PlanStep(
            step_id=str(uuid.uuid4()),
            step_type=PlanStepType.TOOL,
            step_number=1,
            tool_name="search",
            tool_input=task_description,
            variable_name="search_result",
            description=f"Search for information about: {task_description}"
        ))
        
        # Step 2: Get Wikipedia information
        steps.append(PlanStep(
            step_id=str(uuid.uuid4()),
            step_type=PlanStepType.TOOL,
            step_number=2,
            tool_name="wikipedia",
            tool_input=task_description,
            variable_name="wiki_info",
            description=f"Get Wikipedia information about: {task_description}"
        ))
        
        # Step 3: Solve
        steps.append(PlanStep(
            step_id=str(uuid.uuid4()),
            step_type=PlanStepType.SOLVE,
            step_number=3,
            tool_name=None,
            tool_input="Use the search results #{search_result}# and Wikipedia information #{wiki_info}# to provide a comprehensive answer to: {task_description}",
            variable_name="answer",
            description=f"Provide final answer for: {task_description}"
        ))
        
        return steps
    
    def validate_plan(self, plan: Plan) -> bool:
        """Validate that a plan is well-formed."""
        try:
            # Check if plan has steps
            if not plan.steps:
                return False
            
            # Check if all tools exist
            for step in plan.steps:
                if step.step_type == PlanStepType.TOOL:
                    if step.tool_name not in tool_registry:
                        self.logger.warning(f"Tool '{step.tool_name}' not found in registry")
                        return False
            
            # Check if there's at least one SOLVE step
            solve_steps = [s for s in plan.steps if s.step_type == PlanStepType.SOLVE]
            if not solve_steps:
                self.logger.warning("Plan has no SOLVE steps")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating plan: {e}")
            return False 