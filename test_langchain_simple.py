#!/usr/bin/env python3
"""
Simple test for LangChain integration with MCP File Server.
"""

import asyncio
from langchain_integration import create_file_tools


async def test_basic_connection():
    """Test basic MCP connection and tool creation."""
    print("🔧 Testing basic MCP connection...")
    
    config = {
        "mcpServers": {
            "file-server": {
                "command": "uv",
                "args": ["run", "python", "main.py"],
                "cwd": "/Users/ravi/Work/Source/py/mcp"
            }
        }
    }
    
    try:
        print("📡 Creating MCP file tools...")
        tools = await create_file_tools(config)
        print(f"✅ Successfully created {len(tools)} tools!")
        
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test a simple operation
        write_tool = next(t for t in tools if t.name == "write_file")
        
        print("\n📝 Testing write_file tool...")
        result = await write_tool._arun(
            path="/tmp/langchain_test_simple.txt",
            content="Hello from LangChain integration test!"
        )
        print(f"Result: {result}")
        
        # Test read operation
        read_tool = next(t for t in tools if t.name == "read_file")
        
        print("\n📖 Testing read_file tool...")
        result = await read_tool._arun(path="/tmp/langchain_test_simple.txt")
        print(f"Content: {result}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_basic_connection())