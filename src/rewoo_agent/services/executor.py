"""
Executor service for executing plans.
"""

from typing import Dict, Any, AsyncIterator

from loguru import logger
from datetime import datetime

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage

from ...models import Plan, PlanStep, PlanStepType, PlanStepStatus, PlanStatus, ExecutionContext
from ..tools import tool_registry
from ...config.settings import settings



class ExecutorService:
    """Service for executing plans."""
    
    def __init__(self):
        self.llm = init_chat_model(
            model=settings.model.model_name,
            model_provider=settings.model.model_provider,
            temperature=settings.model.temperature
        )
        self.logger = logger
    
    async def execute_plan(self, plan: Plan) -> Plan:
        """Execute a complete plan."""
        try:
            self.logger.info(f"Starting execution of plan: {plan.plan_id}")
            
            # Update plan status
            plan.status = PlanStatus.RUNNING
            plan.started_at = datetime.now()
            
            # Create execution context
            context = ExecutionContext(
                plan=plan,
                max_iterations=settings.rewoo.max_iterations
            )
            
            # Execute steps
            while context.iteration < context.max_iterations:
                context.iteration += 1
                
                # Get next step to execute
                next_step = plan.get_next_step()
                if not next_step:
                    break
                
                # Execute the step
                await self._execute_step(next_step, context)
                
                # Check if plan is completed
                if plan.is_completed():
                    break
                
                # Check if there are failed steps
                if plan.has_failed_steps():
                    plan.status = PlanStatus.FAILED
                    break
            
            # Finalize plan
            if plan.is_completed():
                plan.status = PlanStatus.COMPLETED
                # Get the final answer from the last SOLVE step
                solve_steps = [s for s in plan.steps if s.step_type == PlanStepType.SOLVE]
                if solve_steps:
                    final_step = solve_steps[-1]
                    plan.final_answer = str(final_step.result) if final_step.result else None
            elif plan.status != PlanStatus.FAILED:
                plan.status = PlanStatus.FAILED
                
            plan.completed_at = datetime.now()
            
            self.logger.info(f"Plan execution completed with status: {plan.status}")
            return plan
            
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            plan.status = PlanStatus.FAILED
            plan.completed_at = datetime.now()
            raise
    
    async def execute_plan_streaming(self, plan: Plan) -> AsyncIterator[Dict[str, Any]]:
        """Execute a plan with streaming updates."""
        try:
            self.logger.info(f"Starting streaming execution of plan: {plan.plan_id}")
            
            # Update plan status
            plan.status = PlanStatus.RUNNING
            plan.started_at = datetime.now()
            
            yield {
                "type": "execution_started",
                "data": {
                    "plan_id": plan.plan_id,
                    "total_steps": len(plan.steps)
                }
            }
            
            # Create execution context
            context = ExecutionContext(
                plan=plan,
                max_iterations=settings.rewoo.max_iterations
            )
            
            # Execute steps
            while context.iteration < context.max_iterations:
                context.iteration += 1
                
                # Get next step to execute
                next_step = plan.get_next_step()
                if not next_step:
                    break
                
                # Execute the step with streaming
                async for update in self._execute_step_streaming(next_step, context):
                    yield update
                
                # Check if plan is completed
                if plan.is_completed():
                    break
                
                # Check if there are failed steps
                if plan.has_failed_steps():
                    plan.status = PlanStatus.FAILED
                    break
            
            # Finalize plan
            if plan.is_completed():
                plan.status = PlanStatus.COMPLETED
                # Get the final answer from the last SOLVE step
                solve_steps = [s for s in plan.steps if s.step_type == PlanStepType.SOLVE]
                if solve_steps:
                    final_step = solve_steps[-1]
                    plan.final_answer = str(final_step.result) if final_step.result else None
            elif plan.status != PlanStatus.FAILED:
                plan.status = PlanStatus.FAILED
                
            plan.completed_at = datetime.now()
            
            yield {
                "type": "execution_completed",
                "data": {
                    "plan_id": plan.plan_id,
                    "status": plan.status,
                    "final_answer": plan.final_answer
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            plan.status = PlanStatus.FAILED
            plan.completed_at = datetime.now()
            yield {
                "type": "error",
                "data": {"error": f"Plan execution failed: {str(e)}"}
            }
    
    async def _execute_step(self, step: PlanStep, context: ExecutionContext) -> None:
        """Execute a single plan step."""
        try:
            self.logger.info(f"Executing step {step.step_number}: {step.description}")
            
            # Update step status
            step.status = PlanStepStatus.RUNNING
            step.started_at = datetime.now()
            context.current_step = step
            
            if step.step_type == PlanStepType.TOOL:
                # Execute tool step
                result = await self._execute_tool_step(step, context)
            elif step.step_type == PlanStepType.SOLVE:
                # Execute solve step
                result = await self._execute_solve_step(step, context)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
            
            # Update step with result
            step.result = result
            step.status = PlanStepStatus.COMPLETED
            step.completed_at = datetime.now()
            
            # Update context variables
            if step.variable_name:
                context.update_variable(step.variable_name, result)
            
            self.logger.info(f"Step {step.step_number} completed successfully")
            
        except Exception as e:
            self.logger.exception(f"Error executing step {step.step_number}: {e}")
            step.status = PlanStepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()
    
    async def _execute_step_streaming(self, step: PlanStep, context: ExecutionContext) -> AsyncIterator[Dict[str, Any]]:
        """Execute a single plan step with streaming updates."""
        try:
            yield {
                "type": "step_started",
                "data": {
                    "step_id": step.step_id,
                    "step_number": step.step_number,
                    "description": step.description
                }
            }
            
            # Update step status
            step.status = PlanStepStatus.RUNNING
            step.started_at = datetime.now()
            context.current_step = step
            
            if step.step_type == PlanStepType.TOOL:
                # Execute tool step with streaming
                async for update in self._execute_tool_step_streaming(step, context):
                    yield update
                
                # Get final result
                result = step.result
                
            elif step.step_type == PlanStepType.SOLVE:
                # Execute solve step
                result = await self._execute_solve_step(step, context)
                step.result = result
                
                yield {
                    "type": "step_progress",
                    "data": {
                        "step_id": step.step_id,
                        "progress": 100,
                        "message": "Solve step completed"
                    }
                }
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
            
            # Update step status
            step.status = PlanStepStatus.COMPLETED
            step.completed_at = datetime.now()
            
            # Update context variables
            if step.variable_name:
                context.update_variable(step.variable_name, result)
            
            yield {
                "type": "step_completed",
                "data": {
                    "step_id": step.step_id,
                    "step_number": step.step_number,
                    "result": result
                }
            }
            
        except Exception as e:
            self.logger.exception(f"Error executing step {step.step_number}: {e}")
            step.status = PlanStepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()
            
            yield {
                "type": "step_failed",
                "data": {
                    "step_id": step.step_id,
                    "step_number": step.step_number,
                    "error": str(e)
                }
            }
    
    async def _execute_tool_step(self, step: PlanStep, context: ExecutionContext) -> Any:
        """Execute a tool step."""
        if not step.tool_name:
            raise ValueError("Tool step must have a tool name")
        
        # Substitute variables in the tool input
        tool_input = context.substitute_variables(step.tool_input or "")
        
        # Execute the tool
        result = await tool_registry.execute_tool(step.tool_name, tool_input)
        
        if not result.success:
            raise ValueError(f"Tool execution failed: {result.error}")
        
        return result.result
    
    async def _execute_tool_step_streaming(self, step: PlanStep, context: ExecutionContext) -> AsyncIterator[Dict[str, Any]]:
        """Execute a tool step with streaming updates."""
        if not step.tool_name:
            raise ValueError("Tool step must have a tool name")
        
        # Substitute variables in the tool input
        tool_input = context.substitute_variables(step.tool_input or "")
        
        # Execute the tool with streaming
        async for update in tool_registry.execute_tool_streaming(step.tool_name, tool_input):
            if update["type"] == "result":
                # Store the final result
                result_data = update["data"]
                if result_data.get("success"):
                    step.result = result_data.get("result")
                else:
                    raise ValueError(f"Tool execution failed: {result_data.get('error')}")
            
            # Forward the update with step context
            yield {
                "type": "step_progress",
                "data": {
                    "step_id": step.step_id,
                    "step_number": step.step_number,
                    "tool_update": update
                }
            }
    
    async def _execute_solve_step(self, step: PlanStep, context: ExecutionContext) -> str:
        """Execute a solve step using LLM."""
        try:
            # Substitute variables in the solve input
            solve_input = context.substitute_variables(step.tool_input or "")
            
            # Create context for the solver
            variables_context = []
            for var_name, var_value in context.variables.items():
                variables_context.append(f"{var_name}: {var_value}")
            
            # Create prompt for solving
            system_prompt = """You are a professional solver. Your task is to analyze the provided information and generate a final answer.

Use the available information to provide a comprehensive, accurate answer to the original question. Be clear, concise, and factual."""
            
            user_prompt = f"""Original Task: {context.plan.task_description}

Available Information:
{chr(10).join(variables_context)}

Solve: {solve_input}

Please provide a final answer based on the available information."""
            
            # Generate answer using LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            answer = response.generations[0][0].text
            
            return answer.strip()
            
        except Exception as e:
            self.logger.error(f"Error in solve step: {e}")
            # Return a basic answer based on available information
            return f"Based on the available information: {', '.join([f'{k}: {v}' for k, v in context.variables.items()])}"
    
    def get_execution_status(self, plan: Plan) -> Dict[str, Any]:
        """Get the current execution status of a plan."""
        completed_steps = len(plan.get_completed_steps())
        failed_steps = len(plan.get_failed_steps())
        total_steps = len(plan.steps)
        
        return {
            "plan_id": plan.plan_id,
            "status": plan.status,
            "progress": {
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "total_steps": total_steps,
                "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
            },
            "started_at": plan.started_at,
            "completed_at": plan.completed_at,
            "final_answer": plan.final_answer
        } 