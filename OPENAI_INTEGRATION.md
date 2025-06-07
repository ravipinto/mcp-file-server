# OpenAI Function Calling Integration

This document explains how to use OpenAI's function calling capabilities with the MCP file server.

## Overview

The OpenAI integration provides:
- **Function definitions** compatible with OpenAI's function calling API
- **Python client wrapper** for easy integration in Python applications
- **HTTP endpoints** for web-based applications and n8n workflows
- **Example scripts** demonstrating various use cases

## Quick Start

### 1. Set OpenAI API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 2. Install Dependencies

```bash
uv sync  # OpenAI SDK is already included
```

### 3. Basic Usage

```python
import asyncio
from openai_integration import create_openai_function_caller

async def main():
    # Create function caller
    caller = await create_openai_function_caller()
    
    # Use with OpenAI chat
    messages = [{"role": "user", "content": "Create a file called test.txt with hello world"}]
    result = await caller.chat_with_functions(messages)
    
    print(f"Response: {result['response']}")
    print(f"Functions called: {len(result['function_calls'])}")

asyncio.run(main())
```

## Available Functions

The MCP file server provides these OpenAI-compatible functions:

| Function | Description | Parameters |
|----------|-------------|------------|
| `read_file` | Read contents of a file | `path` (string) |
| `write_file` | Write content to a file | `path` (string), `content` (string) |
| `list_directory` | List directory contents | `path` (string) |
| `create_directory` | Create a directory | `path` (string) |
| `delete_file` | Delete a file | `path` (string) |

## Usage Methods

### 1. Python Integration

#### Direct Function Calling
```python
from openai_integration import create_openai_function_caller

caller = await create_openai_function_caller()
result = await caller.execute_function("write_file", {
    "path": "/tmp/test.txt", 
    "content": "Hello World"
})
```

#### Chat with Function Calling
```python
messages = [
    {"role": "user", "content": "Read the main.py file and summarize what it does"}
]
result = await caller.chat_with_functions(messages, model="gpt-4")
```

### 2. HTTP API Endpoints

#### Get Function Definitions
```bash
curl http://192.168.0.116:8000/openai/functions
```

#### Chat with Function Calling
```bash
curl -X POST http://192.168.0.116:8000/openai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "List files in /tmp directory"}],
    "model": "gpt-4",
    "api_key": "your-openai-api-key"
  }'
```

### 3. n8n Integration

Use the HTTP endpoints in n8n workflows:

**Node Configuration:**
- **Method**: POST
- **URL**: `http://192.168.0.116:8000/openai/chat`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "messages": [
    {"role": "user", "content": "Create a file /tmp/n8n_openai_test.txt"}
  ],
  "model": "gpt-4",
  "api_key": "{{ $env.OPENAI_API_KEY }}"
}
```

## Examples

### File Management Assistant
```python
messages = [
    {
        "role": "user", 
        "content": """
        Help me organize my files:
        1. Create a directory /tmp/organized
        2. Create subdirectories: docs, scripts, temp  
        3. Create a sample README.md in docs folder
        4. List the final structure
        """
    }
]

result = await caller.chat_with_functions(messages)
```

### Code Analysis
```python
messages = [
    {
        "role": "user",
        "content": "Read all Python files in the current directory and give me a summary of this codebase"
    }
]

result = await caller.chat_with_functions(messages, model="gpt-4")
```

### Interactive File Operations
```python
# Multi-turn conversation
conversation = [
    {"role": "user", "content": "What files are in the current directory?"}
]

result1 = await caller.chat_with_functions(conversation)
conversation.extend(result1['conversation'][-2:])

conversation.append({
    "role": "user", 
    "content": "Now read the main.py file and explain what it does"
})

result2 = await caller.chat_with_functions(conversation)
```

## Advanced Configuration

### Custom Model Selection
```python
result = await caller.chat_with_functions(
    messages, 
    model="gpt-4-turbo-preview",  # or gpt-3.5-turbo
    max_function_calls=10
)
```

### Error Handling
```python
try:
    result = await caller.chat_with_functions(messages)
    for call in result['function_calls']:
        if call['result'].startswith('Error'):
            print(f"Function {call['function']} failed: {call['result']}")
except Exception as e:
    print(f"OpenAI API error: {e}")
```

### Function Definitions Only
```python
from openai_integration import get_openai_tools_json
print(get_openai_tools_json())  # Get JSON format for external use
```

## Integration with Other Services

### Use with LangChain
```python
# Combine with existing LangChain integration
from langchain_simple import SimpleMCPFileTools
from openai_integration import create_openai_function_caller

# Use both approaches in the same application
langchain_tools = SimpleMCPFileTools(config)
openai_caller = await create_openai_function_caller()
```

### Use with n8n Workflows
1. **Set Environment Variable** in n8n: `OPENAI_API_KEY`
2. **HTTP Request Node** to `/openai/chat` endpoint
3. **Process Response** with function call results
4. **Chain Multiple Calls** for complex workflows

## Troubleshooting

### API Key Issues
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Test API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Function Call Limits
- Default max function calls: 5 per conversation
- Increase with `max_function_calls` parameter
- Monitor token usage in response

### MCP Server Connection
```python
# Test MCP connection
caller = await create_openai_function_caller()
await caller.initialize_mcp()  # Should not raise errors
```

## Example Scripts

Run the example script to see all features:

```bash
# Make sure OpenAI API key is set
export OPENAI_API_KEY="your-key-here"

# Run comprehensive demo
uv run python example_openai_usage.py
```

## Cost Considerations

Based on your session costs ($11.29 total):
- **Function calls** add to token usage (both input and output)
- **GPT-4** is more expensive but more capable than GPT-3.5-turbo
- **Function definitions** are included in every request
- **Consider caching** results for repeated operations

## Next Steps

1. **Integrate with your applications** using the Python client
2. **Create n8n workflows** using the HTTP endpoints  
3. **Combine with LangChain** for more complex agent behaviors
4. **Build custom tools** by extending the function definitions
5. **Monitor usage** and optimize for cost-effectiveness

The OpenAI integration provides a powerful way to combine natural language with file operations!