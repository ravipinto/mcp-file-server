# Using MCP File Server with LLMs

This guide shows how to integrate your MCP file server with various LLM platforms and libraries.

## Method 1: Claude Desktop (Easiest)

Claude Desktop has built-in MCP support. Just add this to your Claude config:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "file-server": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/Users/ravi/Work/Source/py/mcp"
    }
  }
}
```

After restarting Claude Desktop, you can ask Claude to:
- "Read the contents of my config file"
- "Create a new Python script in my project directory"
- "List all files in my Downloads folder"

## Method 2: OpenAI with Function Calling

Install OpenAI library:
```bash
uv add openai
```

Then use this pattern:

```python
import asyncio
from openai import AsyncOpenAI
from mcp_use import MCPClient

async def use_with_openai():
    # Set up MCP client
    config = {
        "mcpServers": {
            "file-server": {
                "command": "uv",
                "args": ["run", "python", "main.py"],
                "cwd": "/Users/ravi/Work/Source/py/mcp"
            }
        }
    }
    
    client = MCPClient(config)
    session = await client.create_session("file-server")
    
    # Get MCP tools and convert to OpenAI format
    mcp_tools = await session.connector.list_tools()
    openai_tools = []
    
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })
    
    # Use with OpenAI
    openai_client = AsyncOpenAI()
    
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Create a file called notes.txt with my meeting notes"}
        ],
        tools=openai_tools
    )
    
    # Handle function calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            # Execute the MCP tool
            result = await session.connector.call_tool(function_name, arguments)
            print(f"Tool {function_name} result: {result.content[0].text}")
    
    await client.close_all_sessions()
```

## Method 3: LangChain Integration

Install LangChain:
```bash
uv add langchain langchain-openai
```

```python
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from mcp_use import MCPClient

class MCPTool(BaseTool):
    def __init__(self, mcp_session, tool_name, tool_description, tool_schema):
        super().__init__()
        self.mcp_session = mcp_session
        self.name = tool_name
        self.description = tool_description
        self.args_schema = tool_schema
    
    async def _arun(self, **kwargs):
        result = await self.mcp_session.connector.call_tool(self.name, kwargs)
        return result.content[0].text

async def create_langchain_tools():
    # Set up MCP client
    config = {"mcpServers": {"file-server": {"command": "uv", "args": ["run", "python", "main.py"]}}}
    client = MCPClient(config)
    session = await client.create_session("file-server")
    
    # Convert MCP tools to LangChain tools
    mcp_tools = await session.connector.list_tools()
    langchain_tools = []
    
    for tool in mcp_tools:
        langchain_tool = MCPTool(
            mcp_session=session,
            tool_name=tool.name,
            tool_description=tool.description,
            tool_schema=tool.inputSchema
        )
        langchain_tools.append(langchain_tool)
    
    return langchain_tools, client
```

## Method 4: Custom LLM Integration

For any other LLM or framework:

```python
async def integrate_with_any_llm():
    # 1. Set up MCP client
    config = {
        "mcpServers": {
            "file-server": {
                "command": "uv",
                "args": ["run", "python", "main.py"],
                "cwd": "/Users/ravi/Work/Source/py/mcp"
            }
        }
    }
    
    client = MCPClient(config)
    session = await client.create_session("file-server")
    
    # 2. Get available tools
    tools = await session.connector.list_tools()
    
    # 3. Convert to your LLM's function calling format
    # (This depends on your LLM platform)
    
    # 4. When LLM wants to call a function:
    async def execute_tool(tool_name: str, arguments: dict):
        result = await session.connector.call_tool(tool_name, arguments)
        return result.content[0].text
    
    # 5. Example usage
    file_content = await execute_tool("read_file", {"path": "/path/to/file.txt"})
    await execute_tool("write_file", {"path": "/path/to/output.txt", "content": "New content"})
    
    await client.close_all_sessions()
```

## Available Tools

Your MCP file server provides these tools to any LLM:

- **`read_file`** - Read file contents
  - Parameters: `path` (string)
  - Returns: File contents as text

- **`write_file`** - Write content to a file
  - Parameters: `path` (string), `content` (string)
  - Returns: Success/error message

- **`list_directory`** - List directory contents
  - Parameters: `path` (string)
  - Returns: List of files and directories

- **`create_directory`** - Create a new directory
  - Parameters: `path` (string)
  - Returns: Success/error message

- **`delete_file`** - Delete a file
  - Parameters: `path` (string)
  - Returns: Success/error message

## Security Considerations

⚠️ **Important:** Your file server provides full file system access to the LLM. Only use in trusted environments and consider:

1. **Path restrictions** - Modify the server to only allow access to specific directories
2. **File type restrictions** - Limit which file types can be read/written
3. **Size limits** - Prevent reading/writing of very large files
4. **Logging** - Add audit logging for all file operations

## Example Use Cases

Once integrated with an LLM, you can ask it to:

- "Read my project's README and summarize it"
- "Create a new Python script that processes CSV files"
- "List all .py files in my project directory"
- "Back up my configuration files to a backup directory"
- "Find and read all error logs from yesterday"

The LLM will automatically use your file server tools to accomplish these tasks!