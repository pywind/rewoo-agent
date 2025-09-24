# ReWOO (Reasoning without Observation)

A modern implementation of the ReWOO (Reasoning without Observation) architecture for multi-step task planning and execution with streaming support, configurable tasks, and an extensible tool system.

## Features

- **🎯 Multi-step Planning**: Automatically generates execution plans for complex tasks
- **⚡ Streaming Support**: Real-time updates during task execution
- **🔧 Extensible Tool System**: Easy to add custom tools for specific domains
- **📊 Task Configuration**: Configurable task types and execution parameters
- **🌐 REST API**: FastAPI-based API with comprehensive endpoints
- **📡 WebSocket Support**: Real-time updates via WebSocket connections
- **🔍 Built-in Tools**: Search, Calculator, Wikipedia, and more
- **📝 OOP Architecture**: Clean, modular design following SOLID principles

## Architecture

The ReWOO system follows a three-component architecture:

1. **Planner**: Generates step-by-step execution plans using LLM
2. **Worker/Executor**: Executes individual steps using available tools
3. **Solver**: Combines results to provide final answers

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Planner   │───▶│   Executor  │───▶│   Solver    │
│             │    │             │    │             │
│ - Plan Gen  │    │ - Tool Exec │    │ - Result    │
│ - LLM-based │    │ - Streaming │    │ - Synthesis │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd rewoo
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp config/env.example .env
# Edit .env with your configuration
```

4. **Required environment variables**:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

## Quick Start

### 1. Running the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Using the Python API

```python
import asyncio
from src.rewoo.models import TaskRequest, TaskType
from src.rewoo.services import ReWOOService

async def main():
    # Initialize the service
    rewoo_service = ReWOOService()
    
    # Create a task request
    task_request = TaskRequest(
        task_description="What is the capital of France and what's its population?",
        task_type=TaskType.RESEARCH
    )
    
    # Execute the task
    result = await rewoo_service.execute_task(task_request)
    print(f"Result: {result.result}")

asyncio.run(main())
```

### 3. Using the REST API

```bash
# Execute a task
curl -X POST "http://localhost:8000/tasks/execute-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Calculate the square root of 144 and multiply by 5",
    "task_type": "calculation",
    "streaming": true
  }'

# Get available tools
curl "http://localhost:8000/tools"

# Health check
curl "http://localhost:8000/health"
```

## Examples

The `examples/` directory contains comprehensive examples:

### Simple Usage
```bash
python examples/simple_example.py
```

### Streaming with Real-time Updates
```bash
python examples/streaming_example.py
```

### Custom Tool Development
```bash
python examples/custom_tool_example.py
```

## Built-in Tools

### Search Tool
- **Name**: `search`
- **Description**: Search the web for information
- **Example**: `"python programming best practices"`

### Calculator Tool
- **Name**: `calculator`
- **Description**: Perform mathematical calculations
- **Example**: `"2 + 3 * 4"`, `"sqrt(16) + 2^3"`

### Wikipedia Tool
- **Name**: `wikipedia`
- **Description**: Retrieve information from Wikipedia
- **Example**: `"Machine learning"`

## Creating Custom Tools

### 1. Define Your Tool

```python
from src.rewoo.tools.base import BaseTool, ToolResult

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Description of what the tool does",
            version="1.0.0",
            tags=["category", "type"],
            parameters={
                "input_param": {
                    "type": "string",
                    "description": "Parameter description",
                    "required": True
                }
            }
        )
    
    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        try:
            # Your tool logic here
            result = process_input(input_data)
            return ToolResult.success_result(result)
        except Exception as e:
            return ToolResult.error_result(str(e))
```

### 2. Register Your Tool

```python
from src.rewoo.tools import tool_registry

# Create and register the tool
my_tool = MyCustomTool()
tool_registry.register_tool(my_tool)
```

### 3. Use in Tasks

```python
task_request = TaskRequest(
    task_description="Use my custom tool to process data",
    task_type=TaskType.CUSTOM
)
```

## Task Configuration

### Task Types

- **RESEARCH**: Information gathering and analysis
- **CALCULATION**: Mathematical computations
- **ANALYSIS**: Data analysis and interpretation
- **SEARCH**: Web search and information retrieval
- **CUSTOM**: Custom task types

### Task Templates

```python
from src.rewoo.models import TaskTemplate, TaskType

template = TaskTemplate(
    template_id="research_template",
    name="Research Template",
    description="Template for research tasks",
    task_type=TaskType.RESEARCH,
    required_tools=["search", "wikipedia"],
    optional_tools=["calculator"],
    parameters={
        "max_sources": 5,
        "include_citations": True
    }
)
```

## API Endpoints

### Core Endpoints

- `POST /tasks/execute-stream`: Execute task with streaming
- `GET /tasks/{request_id}/status`: Get task status
- `DELETE /tasks/{request_id}`: Cancel task
- `GET /tasks`: List active tasks

### Tool Endpoints

- `GET /tools`: List available tools
- `POST /tools/test`: Test all tools

### WebSocket

- `WS /ws/tasks/{request_id}`: Real-time task updates

### Example Endpoints

- `POST /examples/search?query={query}`: Example search
- `POST /examples/calculate?expression={expr}`: Example calculation
- `POST /examples/research?topic={topic}`: Example research

## Configuration

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4

# ReWOO Configuration
MAX_ITERATIONS=10
STREAMING_ENABLED=true
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Task Configuration
DEFAULT_TASK_TIMEOUT=300
MAX_CONCURRENT_TASKS=5
```

### Programmatic Configuration

```python
from config.settings import settings

# Access configuration
print(settings.openai.model)
print(settings.rewoo.max_iterations)
print(settings.api.port)
```

## Streaming

### Server-Sent Events (SSE)

```javascript
const eventSource = new EventSource('/tasks/execute-stream');
eventSource.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Update:', update);
};
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tasks/123');
ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Update:', update);
};
```

### Python Streaming

```python
async for update in rewoo_service.execute_task_streaming(task_request):
    print(f"Update: {update['type']} - {update['data']}")
```

## Testing

### Run Examples

```bash
# Test basic functionality
python examples/simple_example.py

# Test streaming
python examples/streaming_example.py

# Test custom tools
python examples/custom_tool_example.py
```

### Test Tools

```bash
curl -X POST "http://localhost:8000/tools/test"
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

## Development

### Project Structure

```
rewoo/
├── src/rewoo/           # Main application code
│   ├── models/          # Data models
│   ├── tools/           # Tool implementations
│   ├── services/        # Business logic services
│   ├── controllers/     # API controllers
│   └── utils/           # Utility functions
├── config/              # Configuration management
├── examples/            # Usage examples
├── tests/               # Test suite
├── docs/                # Documentation
├── requirements.txt     # Dependencies
├── main.py             # Application entry point
└── README.md           # This file
```

### Key Principles

1. **OOP Design**: All components use object-oriented design
2. **No Nested Functions**: Clean, flat function structure
3. **Modular Architecture**: Separate concerns and responsibilities
4. **Configuration Management**: Environment-based configuration
5. **Streaming First**: Built for real-time updates
6. **Extensible**: Easy to add new tools and features

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes following the OOP principles
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the ReWOO (Reasoning without Observation) research
- Built with FastAPI, LangChain, and Pydantic
- Inspired by the need for modular, streaming-capable AI systems

## Support

For questions and support:

1. Check the examples in the `examples/` directory
2. Review the API documentation at `/docs`
3. Open an issue on GitHub
4. Check the health endpoint for system status 