---
description: Workflow guide for software agent engineers working with REWOO framework
alwaysApply: false
---
# REWOO Agent Development Workflow

This rule provides guidance for software agent engineers working with the REWOO (Reasoning with External World Observation) framework.

## Architecture Overview

The REWOO agent follows a structured pattern:

1. **Planner** decomposes complex tasks into executable steps
2. **Executor** runs tasks using available tools
3. **Tools** provide external capabilities (search, calculation, etc.)
4. **Controllers** handle API routing and orchestration

## Codebase Navigation

### Core Components (`src/rewoo_agent/`)

**Models** (`models/`):

- [plan.py](mdc:src/rewoo_agent/models/plan.py) - Task decomposition and planning structures
- [task.py](mdc:src/rewoo_agent/models/task.py) - Individual task definitions and states

**Services** (`services/`):

- [planner.py](mdc:src/rewoo_agent/services/planner.py) - Task decomposition logic
- [executor.py](mdc:src/rewoo_agent/services/executor.py) - Task execution orchestration
- [rewoo_service.py](mdc:src/rewoo_agent/services/rewoo_service.py) - Main agent service coordinator

**Tools** (`tools/`):

- [base.py](mdc:src/rewoo_agent/tools/base.py) - Base tool interface and utilities
- [calculator.py](mdc:src/rewoo_agent/tools/calculator.py) - Mathematical computation tools
- [search.py](mdc:src/rewoo_agent/tools/search.py) - Web search capabilities
- [wikipedia.py](mdc:src/rewoo_agent/tools/wikipedia.py) - Wikipedia knowledge access

**Controllers** (`controllers/`):

- [agent_routers.py](mdc:src/rewoo_agent/controllers/agent_routers.py) - API endpoints for agent interaction

### Supporting Infrastructure

**APIs** (`src/apis/`):

- [api.py](mdc:src/apis/api.py) - Main API interface
- [exceptions.py](mdc:src/apis/exceptions.py) - Custom exception handling
- [log_factory.py](mdc:src/apis/log_factory.py) - Logging configuration

**Configuration** (`src/config/`):

- [settings.py](mdc:src/config/settings.py) - Application configuration management

**Data Models** (`src/models/`):

- [schemas.py](mdc:src/models/schemas.py) - Pydantic schemas for API contracts

## Development Workflow

### 1. Understanding Task Flow

When reading code, trace the execution path:

- Start from [agent_routers.py](mdc:src/rewoo_agent/controllers/agent_routers.py) for API entry points
- Follow to [rewoo_service.py](mdc:src/rewoo_agent/services/rewoo_service.py) for orchestration
- Examine [planner.py](mdc:src/rewoo_agent/services/planner.py) for task decomposition
- Check [executor.py](mdc:src/rewoo_agent/services/executor.py) for tool execution

### 2. Adding New Tools

To extend agent capabilities:

1. Create new tool in `tools/` inheriting from [base.py](mdc:src/rewoo_agent/tools/base.py)
2. Implement required methods (`execute`, `get_description`)
3. Register tool in service configuration
4. Add tests in `tests/test_tools.py`

### 3. Modifying Agent Behavior

For custom workflows:

- Modify planning logic in [planner.py](mdc:src/rewoo_agent/services/planner.py)
- Extend task models in [task.py](mdc:src/rewoo_agent/models/task.py)
- Update orchestration in [rewoo_service.py](mdc:src/rewoo_agent/services/rewoo_service.py)

### 4. API Extensions

To add new endpoints:

- Define schemas in [schemas.py](mdc:src/models/schemas.py)
- Add routes in [agent_routers.py](mdc:src/rewoo_agent/controllers/agent_routers.py)
- Handle requests in appropriate service classes

## Best Practices

### Code Reading

- Always check [main.py](mdc:main.py) for application entry point
- Review [examples/](mdc:examples/) for usage patterns
- Examine [logs/](mdc:logs/) for debugging information

### Error Handling

- Use structured logging via [log_factory.py](mdc:src/apis/log_factory.py)
- Handle exceptions through [exceptions.py](mdc:src/apis/exceptions.py)
- Check error logs in `logs/` directory

### Testing

- Run tests with `python -m pytest tests/`
- Check [test_tools.py](mdc:tests/test_tools.py) for tool testing patterns
- Use examples in [examples/](mdc:examples/) for integration testing

### Configuration

- Environment variables managed through [settings.py](mdc:src/config/settings.py)
- Check [env.example](mdc:env.example) for required variables
- Use [start.sh](mdc:start.sh) for consistent startup

## Common Patterns

### Tool Implementation

```python
from src.rewoo_agent.tools.base import BaseTool

class CustomTool(BaseTool):
    def execute(self, **kwargs) -> str:
        # Implementation
        pass

    def get_description(self) -> str:
        return "Tool description for planning"
```

### Task Creation

Tasks are created by the planner and executed by the executor. Always ensure tools are properly registered and task parameters match tool requirements.

### Logging

Use structured logging throughout:

```python
from src.apis.log_factory import get_logger
logger = get_logger(__name__)
logger.info("Operation completed", extra={"task_id": task_id})
```

Remember: REWOO agents excel at complex task decomposition. When adding features, consider how they fit into the plan-execute-observe cycle.
