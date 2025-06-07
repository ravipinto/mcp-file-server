# LangChain Integration for MCP File Server

This guide shows how to integrate your MCP file server with LangChain for building AI agents with file system capabilities.

## Installation

Install LangChain dependencies:

```bash
uv add --group langchain langchain
# or
uv sync --group langchain
```

## Quick Start

### Basic Usage

```python
import asyncio
from langchain_simple import create_simple_file_tools

async def main():
    # Create file tools
    tools = await create_simple_file_tools()
    
    # Tools are now ready for use with LangChain agents
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

asyncio.run(main())
```

### With Custom Configuration

```python
from langchain_simple import SimpleMCPFileTools

async def main():
    config = {
        "mcpServers": {
            "file-server": {
                "command": "/path/to/your/mcp-file-server/run_server.sh"
            }
        }
    }
    
    toolkit = SimpleMCPFileTools(config)
    await toolkit.initialize()
    
    # Use async methods directly
    result = await toolkit.call_tool_async("write_file", 
        path="/tmp/test.txt", 
        content="Hello from LangChain!"
    )
    print(result)
    
    await toolkit.close()

asyncio.run(main())
```

## Available Tools

The integration provides 5 file system tools:

| Tool Name | Description | Arguments |
|-----------|-------------|-----------|
| `read_file` | Read file contents | `path` (str) |
| `write_file` | Write content to file | `path` (str), `content` (str) |
| `list_directory` | List directory contents | `path` (str) |
| `create_directory` | Create new directory | `path` (str) |
| `delete_file` | Delete a file | `path` (str) |

## Integration Examples

### 1. Basic Agent with OpenAI

```python
import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_simple import create_simple_file_tools

async def create_file_agent():
    # Initialize LLM
    llm = ChatOpenAI(temperature=0)
    
    # Get file tools
    tools = await create_simple_file_tools()
    
    # Create agent
    agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    # Example: Ask agent to work with files
    response = agent.run(
        "Create a file called 'notes.txt' with a list of 3 important reminders"
    )
    
    return response

# Run the agent
result = asyncio.run(create_file_agent())
print(result)
```

### 2. Custom Workflow

```python
from langchain_simple import SimpleMCPFileTools

async def process_files_workflow():
    toolkit = SimpleMCPFileTools()
    await toolkit.initialize()
    
    try:
        # Step 1: Create project structure
        await toolkit.call_tool_async("create_directory", path="/tmp/my_project")
        await toolkit.call_tool_async("create_directory", path="/tmp/my_project/src")
        
        # Step 2: Create files
        readme_content = "# My Project\n\nA sample project created with MCP + LangChain"
        await toolkit.call_tool_async("write_file", 
            path="/tmp/my_project/README.md", 
            content=readme_content
        )
        
        main_py = "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()"
        await toolkit.call_tool_async("write_file",
            path="/tmp/my_project/src/main.py",
            content=main_py
        )
        
        # Step 3: List the results
        structure = await toolkit.call_tool_async("list_directory", path="/tmp/my_project")
        print("Project structure:")
        print(structure)
        
    finally:
        await toolkit.close()

asyncio.run(process_files_workflow())
```

### 3. Document Processing Agent

```python
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_simple import SimpleMCPFileTools

async def document_processor():
    # Setup
    llm = ChatOpenAI(temperature=0)
    toolkit = SimpleMCPFileTools()
    await toolkit.initialize()
    
    # Read a document
    content = await toolkit.call_tool_async("read_file", path="/path/to/document.txt")
    
    # Process with LLM
    prompt = PromptTemplate(
        input_variables=["content"],
        template="Summarize the following document in 3 bullet points:\n\n{content}"
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run(content=content)
    
    # Save summary
    await toolkit.call_tool_async("write_file",
        path="/path/to/summary.txt",
        content=summary
    )
    
    await toolkit.close()
    return summary

# result = asyncio.run(document_processor())
```

## Advanced Usage

### Error Handling

```python
from langchain_simple import SimpleMCPFileTools

async def safe_file_operations():
    toolkit = SimpleMCPFileTools()
    await toolkit.initialize()
    
    try:
        # Try to read a file that might not exist
        result = await toolkit.call_tool_async("read_file", path="/nonexistent/file.txt")
        
        if result.startswith("Error"):
            print(f"File operation failed: {result}")
            # Handle the error appropriately
        else:
            print(f"File content: {result}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await toolkit.close()

asyncio.run(safe_file_operations())
```

### Custom Tool Configuration

```python
from langchain.tools import Tool
from langchain_simple import SimpleMCPFileTools

async def create_custom_tools():
    toolkit = SimpleMCPFileTools()
    await toolkit.initialize()
    
    # Create a custom higher-level tool
    def backup_file(filepath: str) -> str:
        """Backup a file by copying it with a .bak extension."""
        try:
            # Read original file
            content = asyncio.run(toolkit.call_tool_async("read_file", path=filepath))
            
            if content.startswith("Error"):
                return f"Failed to read {filepath}: {content}"
            
            # Write backup
            backup_path = f"{filepath}.bak"
            result = asyncio.run(toolkit.call_tool_async("write_file", 
                path=backup_path, 
                content=content
            ))
            
            return f"Backed up {filepath} to {backup_path}: {result}"
            
        except Exception as e:
            return f"Backup failed: {e}"
    
    # Create custom LangChain tool
    backup_tool = Tool(
        name="backup_file",
        description="Create a backup copy of a file with .bak extension",
        func=backup_file
    )
    
    # Get standard tools
    standard_tools = toolkit.get_langchain_tools()
    
    # Combine with custom tool
    all_tools = standard_tools + [backup_tool]
    
    return all_tools

# tools = asyncio.run(create_custom_tools())
```

## Async vs Sync Considerations

**Important Note:** The MCP file server is inherently asynchronous. The LangChain integration provides:

1. **Async methods** (recommended): Use `toolkit.call_tool_async()` for direct async calls
2. **Sync tool wrappers**: LangChain Tool objects with sync interfaces (may have limitations)

For best performance and compatibility, prefer async workflows when possible.

## Troubleshooting

### Common Issues

1. **"Tool requires async execution"**: The sync tool wrapper returned this message
   - **Solution**: Use `toolkit.call_tool_async()` instead

2. **Connection errors**: MCP server not found or failed to start
   - **Solution**: Check your MCP server configuration and paths

3. **Event loop errors**: Issues with async/sync mixing
   - **Solution**: Use `asyncio.run()` for top-level calls

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
```

## Best Practices

1. **Always close connections**: Use `await toolkit.close()` when done
2. **Handle errors gracefully**: Check tool return values for error messages
3. **Use async when possible**: Better performance and compatibility
4. **Validate file paths**: Ensure paths are safe and accessible
5. **Test thoroughly**: File operations can have side effects

## Examples Repository

Complete working examples are available in:
- `langchain_simple.py` - Simple integration
- `langchain_example.py` - Advanced examples
- `langchain_integration.py` - Full-featured (with Pydantic complexities)

## Next Steps

- Try the examples with your own files
- Build custom agents for your specific use cases
- Combine with other LangChain tools and chains
- Explore error handling and validation patterns