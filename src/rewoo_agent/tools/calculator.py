"""
Calculator tool for mathematical calculations.
"""

import ast
import operator
import re
from typing import Dict, Any, AsyncIterator
from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """Tool for performing mathematical calculations."""

    # Safe operators for calculation
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Safe functions
    SAFE_FUNCTIONS = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        "pow": pow,
    }

    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform arithmetic calculations and solve equations",
            version="1.0.0",
            tags=["math", "calculation", "arithmetic"],
            parameters={
                "expression": {
                    "type": "string",
                    "description": "The arithmetic expression to calculate",
                    "required": True,
                }
            },
            examples=[
                {"input": "2 + 3 * 4", "output": "14"},
                {"input": "sqrt(16) + 2^3", "output": "12"},
                {"input": "(10 + 5) * 2 - 3", "output": "27"},
            ],
        )

    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        """Execute a mathematical calculation."""
        try:
            if not self.validate_input(input_data):
                return ToolResult.error_result("Invalid mathematical expression")

            expression = input_data.strip()
            self.logger.info(f"Calculating: {expression}")

            # Preprocess the expression
            processed_expr = self._preprocess_expression(expression)

            # Evaluate the expression safely
            result = self._safe_eval(processed_expr)

            return ToolResult.success_result(
                result=result,
                metadata={
                    "expression": expression,
                    "processed_expression": processed_expr,
                    "result_type": type(result).__name__,
                },
            )

        except Exception as e:
            self.logger.error(f"Calculation error: {e}")
            return ToolResult.error_result(f"Calculation failed: {str(e)}")

    async def execute_streaming(
        self, input_data: str, **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute calculation with streaming support."""
        try:
            if not self.validate_input(input_data):
                yield {
                    "type": "error",
                    "data": {"error": "Invalid mathematical expression"},
                }
                return

            expression = input_data.strip()

            yield {
                "type": "status",
                "data": {"message": f"Processing: {expression}", "progress": 25},
            }

            # Preprocess the expression
            processed_expr = self._preprocess_expression(expression)

            yield {
                "type": "status",
                "data": {"message": "Evaluating expression", "progress": 50},
            }

            # Evaluate the expression safely
            result = self._safe_eval(processed_expr)

            yield {
                "type": "status",
                "data": {"message": "Calculation completed", "progress": 100},
            }

            # Final result
            yield {
                "type": "result",
                "data": {
                    "success": True,
                    "result": result,
                    "metadata": {
                        "expression": expression,
                        "processed_expression": processed_expr,
                        "result_type": type(result).__name__,
                    },
                },
            }

        except Exception as e:
            yield {"type": "error", "data": {"error": f"Calculation failed: {str(e)}"}}

    def _preprocess_expression(self, expression: str) -> str:
        """Preprocess mathematical expression to handle common notations."""
        # Handle common mathematical notations
        expression = expression.replace("^", "**")  # Power notation
        expression = expression.replace("÷", "/")  # Division symbol
        expression = expression.replace("×", "*")  # Multiplication symbol

        # Handle functions
        expression = re.sub(r"sqrt\(([^)]+)\)", r"(\1)**0.5", expression)
        expression = re.sub(r"log\(([^)]+)\)", r"log(\1)", expression)

        # Handle implicit multiplication (e.g., "2(3+4)" -> "2*(3+4)")
        expression = re.sub(r"(\d)\(", r"\1*(", expression)
        expression = re.sub(r"\)(\d)", r")*\1", expression)

        return expression

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate a mathematical expression."""
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode="eval")

            # Evaluate the AST safely
            return self._eval_ast(tree.body)

        except (SyntaxError, ValueError):
            raise ValueError(f"Invalid expression: {expression}")

    def _eval_ast(self, node) -> float:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_ast(node.left)
            right = self._eval_ast(node.right)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op)}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_ast(node.operand)
            op = self.SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op)}")
            return op(operand)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in self.SAFE_FUNCTIONS:
                    args = [self._eval_ast(arg) for arg in node.args]
                    return self.SAFE_FUNCTIONS[func_name](*args)
                else:
                    raise ValueError(f"Unsupported function: {func_name}")
            else:
                raise ValueError("Complex function calls not supported")
        else:
            raise ValueError(f"Unsupported AST node type: {type(node)}")

    def validate_input(self, input_data: str) -> bool:
        """Validate mathematical expression input."""
        if not super().validate_input(input_data):
            return False

        expression = input_data.strip()

        # Check for reasonable expression length
        if len(expression) > 1000:
            return False

        # Check for dangerous patterns
        dangerous_patterns = [
            "import",
            "exec",
            "eval",
            "open",
            "file",
            "input",
            "raw_input",
            "__",
            "getattr",
            "setattr",
            "delattr",
        ]

        expression_lower = expression.lower()
        for pattern in dangerous_patterns:
            if pattern in expression_lower:
                return False

        return True
