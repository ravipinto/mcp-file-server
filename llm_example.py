#!/usr/bin/env python3
"""
Example of using the MCP file server with an LLM via mcp-use library.
"""

import asyncio
from mcp_use import MCPClient
from dotenv import load_dotenv

# Load environment variables (for API keys)
load_dotenv()

async def demo_llm_with_file_server():
    """Demonstrate using the file server with an LLM"""
    
    # Configure the MCP client to use our file server
    config = {
        "mcpServers": {
            "file-server": {
                "command": "uv",
                "args": ["run", "python", "main.py"],
                "cwd": "/Users/ravi/Work/Source/py/mcp"
            }
        }
    }
    
    print("Starting MCP client with file server...")
    client = MCPClient(config)
    
    try:
        # Create session with the file server
        session = await client.create_session("file-server")
        print("✅ Connected to file server")
        
        # List available tools
        tools = await session.connector.list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        
        # Example 1: Create a file
        print("\n📝 Creating a test file...")
        result = await session.connector.call_tool("write_file", {
            "path": "/tmp/mcp_test.txt",
            "content": "Hello from MCP file server!\nThis file was created via LLM integration."
        })
        print(f"Write result: {result.content[0].text}")
        
        # Example 2: Read the file back
        print("\n📖 Reading the file...")
        result = await session.connector.call_tool("read_file", {
            "path": "/tmp/mcp_test.txt"
        })
        print(f"File contents:\n{result.content[0].text}")
        
        # Example 3: List directory contents
        print("\n📁 Listing /tmp directory...")
        result = await session.connector.call_tool("list_directory", {
            "path": "/tmp"
        })
        # Show only first few lines to avoid clutter
        lines = result.content[0].text.split('\n')
        print(f"Directory contents (first 10): {lines[:10]}")
        
        print("\n🎉 MCP file server is ready for LLM integration!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close_all_sessions()


async def demo_with_openai():
    """Example showing how to integrate with OpenAI's API"""
    print("\n🤖 Example: Using with OpenAI (requires OPENAI_API_KEY)")
    
    try:
        from openai import AsyncOpenAI
        
        # This would require: pip install openai
        # and OPENAI_API_KEY in your .env file
        
        # MCP setup
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
        
        # Get available tools for OpenAI function calling
        tools = await session.connector.list_tools()
        
        # Convert MCP tools to OpenAI function format
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        
        print(f"🔧 Converted {len(openai_tools)} MCP tools for OpenAI")
        print("Tools available:", [t["function"]["name"] for t in openai_tools])
        
        # Now you could use these with OpenAI's chat completions
        # client = AsyncOpenAI()
        # response = await client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": "Create a file with my notes"}],
        #     tools=openai_tools
        # )
        
        await client.close_all_sessions()
        
    except ImportError:
        print("OpenAI library not installed. Run: uv add openai")
    except Exception as e:
        print(f"Error in OpenAI demo: {e}")


if __name__ == "__main__":
    print("🚀 MCP File Server + LLM Integration Demo")
    print("=" * 50)
    asyncio.run(demo_llm_with_file_server())
    asyncio.run(demo_with_openai())