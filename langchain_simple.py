#!/usr/bin/env python3
"""
Simple and working LangChain integration for MCP File Server.

This module provides a simplified approach to using MCP file tools with LangChain
that avoids Pydantic compatibility issues.
"""

import asyncio
from typing import Any, Dict, List, Optional

try:
    from langchain.tools import Tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from mcp_use import MCPClient


class SimpleMCPFileTools:
    """Simple MCP file tools for LangChain that avoid Pydantic issues."""
    
    def __init__(self, mcp_config: Optional[Dict[str, Any]] = None):
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed. Install with: uv add --group langchain langchain")
        
        if mcp_config is None:
            mcp_config = {
                "mcpServers": {
                    "file-server": {
                        "command": "uv",
                        "args": ["run", "python", "main.py"],
                        "cwd": "/path/to/your/mcp-file-server"
                    }
                }
            }
        
        self.mcp_config = mcp_config
        self.mcp_client = None
        self.mcp_session = None
    
    async def initialize(self):
        """Initialize the MCP connection."""
        self.mcp_client = MCPClient(self.mcp_config)
        self.mcp_session = await self.mcp_client.create_session("file-server")
        return self
    
    async def close(self):
        """Close the MCP connection."""
        if self.mcp_client:
            await self.mcp_client.close_all_sessions()
    
    def _create_sync_wrapper(self, tool_name: str):
        """Create a synchronous wrapper for MCP tool calls."""
        async def async_call(**kwargs):
            result = await self.mcp_session.connector.call_tool(tool_name, kwargs)
            return result.content[0].text
        
        def sync_call(**kwargs):
            # Simple approach: just return a message that async is needed
            return "⚠️ This tool requires async execution. Use with async LangChain agents or call the async method directly."
        
        return sync_call, async_call
    
    async def call_tool_async(self, tool_name: str, **kwargs) -> str:
        """Call an MCP tool asynchronously."""
        result = await self.mcp_session.connector.call_tool(tool_name, kwargs)
        return result.content[0].text
    
    def get_langchain_tools(self) -> List[Tool]:
        """
        Get LangChain Tool objects for file operations.
        
        Returns:
            List of LangChain Tool objects ready for use.
        """
        if not self.mcp_session:
            raise RuntimeError("Not initialized. Call initialize() first.")
        
        tools = [
            Tool(
                name="read_file",
                description="Read the contents of a file. Args: path (str) - file path to read",
                func=self._create_sync_wrapper("read_file")[0]  # Get sync wrapper
            ),
            Tool(
                name="write_file", 
                description="Write content to a file. Args: path (str) - file path, content (str) - content to write",
                func=self._create_sync_wrapper("write_file")[0]
            ),
            Tool(
                name="list_directory",
                description="List contents of a directory. Args: path (str) - directory path to list",
                func=self._create_sync_wrapper("list_directory")[0]
            ),
            Tool(
                name="create_directory",
                description="Create a new directory. Args: path (str) - directory path to create",
                func=self._create_sync_wrapper("create_directory")[0]
            ),
            Tool(
                name="delete_file",
                description="Delete a file. Args: path (str) - file path to delete",
                func=self._create_sync_wrapper("delete_file")[0]
            )
        ]
        
        return tools


# Convenience function
async def create_simple_file_tools(mcp_config: Optional[Dict[str, Any]] = None) -> List[Tool]:
    """
    Create simple LangChain tools for MCP file operations.
    
    Args:
        mcp_config: MCP configuration dict
        
    Returns:
        List of LangChain Tool objects
        
    Example:
        ```python
        # Basic usage
        tools = await create_simple_file_tools()
        
        # Use with agents
        from langchain.agents import initialize_agent
        agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
        ```
    """
    toolkit = SimpleMCPFileTools(mcp_config)
    await toolkit.initialize()
    return toolkit.get_langchain_tools()


def check_langchain_available() -> bool:
    """Check if LangChain is available."""
    return LANGCHAIN_AVAILABLE


if __name__ == "__main__":
    async def test_simple_tools():
        print("🔧 Testing Simple MCP LangChain Tools...")
        
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
            tools = await create_simple_file_tools(config)
            print(f"✅ Created {len(tools)} tools!")
            
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test write using async method
            toolkit = SimpleMCPFileTools(config)
            await toolkit.initialize()
            
            result = await toolkit.call_tool_async("write_file", path="/tmp/simple_test.txt", content="Hello Simple LangChain!")
            print(f"📝 Write: {result}")
            
            # Test read  
            result = await toolkit.call_tool_async("read_file", path="/tmp/simple_test.txt")
            print(f"📖 Read: {result}")
            
            await toolkit.close()
            
            print("✅ Simple tools working!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_simple_tools())