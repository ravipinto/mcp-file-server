"""
LangChain integration for MCP File Server.

This module provides LangChain tool wrappers for the MCP file server,
allowing easy integration with LangChain agents and workflows.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field

try:
    from langchain.tools import BaseTool
    from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create dummy classes for when LangChain is not installed
    class BaseTool:
        pass
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None

from mcp_use import MCPClient


class FileReadInput(BaseModel):
    """Input for read_file tool."""
    path: str = Field(description="The path to the file to read")


class FileWriteInput(BaseModel):
    """Input for write_file tool."""
    path: str = Field(description="The path to the file to write")
    content: str = Field(description="The content to write to the file")


class DirectoryListInput(BaseModel):
    """Input for list_directory tool."""
    path: str = Field(description="The path to the directory to list")


class DirectoryCreateInput(BaseModel):
    """Input for create_directory tool."""
    path: str = Field(description="The path of the directory to create")


class FileDeleteInput(BaseModel):
    """Input for delete_file tool."""
    path: str = Field(description="The path to the file to delete")


def create_mcp_tool(mcp_session, tool_name: str, tool_description: str, args_schema: Type[BaseModel]) -> BaseTool:
    """Factory function to create MCP tools with closure for session storage."""
    
    def _run_sync(**kwargs) -> str:
        """Run the tool synchronously."""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an event loop, create a new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(_run_async(**kwargs)))
                return future.result()
        except RuntimeError:
            # No running event loop, safe to use asyncio.run
            return asyncio.run(_run_async(**kwargs))
    
    async def _run_async(**kwargs) -> str:
        """Run the tool asynchronously."""
        try:
            result = await mcp_session.connector.call_tool(tool_name, kwargs)
            return result.content[0].text
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    # Create the tool class dynamically
    tool_class = type(f"MCP{tool_name.title()}Tool", (BaseTool,), {
        'name': tool_name,
        'description': tool_description,
        'args_schema': args_schema,
        '_run': _run_sync,
        '_arun': _run_async,
    })
    
    return tool_class()


# Tool creation functions using the factory
def create_read_file_tool(mcp_session) -> BaseTool:
    """Create a read file tool."""
    return create_mcp_tool(
        mcp_session, 
        "read_file",
        "Read the contents of a file from the file system",
        FileReadInput
    )


def create_write_file_tool(mcp_session) -> BaseTool:
    """Create a write file tool."""
    return create_mcp_tool(
        mcp_session,
        "write_file", 
        "Write content to a file on the file system",
        FileWriteInput
    )


def create_list_directory_tool(mcp_session) -> BaseTool:
    """Create a list directory tool."""
    return create_mcp_tool(
        mcp_session,
        "list_directory",
        "List the contents of a directory", 
        DirectoryListInput
    )


def create_create_directory_tool(mcp_session) -> BaseTool:
    """Create a create directory tool."""
    return create_mcp_tool(
        mcp_session,
        "create_directory",
        "Create a new directory",
        DirectoryCreateInput
    )


def create_delete_file_tool(mcp_session) -> BaseTool:
    """Create a delete file tool."""
    return create_mcp_tool(
        mcp_session,
        "delete_file", 
        "Delete a file from the file system",
        FileDeleteInput
    )


class MCPFileToolkit:
    """Toolkit for creating LangChain tools from MCP file server."""
    
    def __init__(self, mcp_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP File Toolkit.
        
        Args:
            mcp_config: Configuration for MCP client. If None, uses default config.
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install it with: uv add --group langchain langchain"
            )
        
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
        """Initialize the MCP client and session."""
        self.mcp_client = MCPClient(self.mcp_config)
        self.mcp_session = await self.mcp_client.create_session("file-server")
        return self
    
    async def close(self):
        """Close the MCP client and session."""
        if self.mcp_client:
            await self.mcp_client.close_all_sessions()
    
    def get_tools(self) -> List[BaseTool]:
        """
        Get all available LangChain tools for file operations.
        
        Returns:
            List of LangChain tools ready for use with agents.
        """
        if not self.mcp_session:
            raise RuntimeError("Toolkit not initialized. Call initialize() first.")
        
        return [
            create_read_file_tool(self.mcp_session),
            create_write_file_tool(self.mcp_session),
            create_list_directory_tool(self.mcp_session),
            create_create_directory_tool(self.mcp_session),
            create_delete_file_tool(self.mcp_session),
        ]


async def create_file_tools(mcp_config: Optional[Dict[str, Any]] = None) -> List[BaseTool]:
    """
    Convenience function to create and initialize MCP file tools for LangChain.
    
    Args:
        mcp_config: Configuration for MCP client. If None, uses default config.
    
    Returns:
        List of initialized LangChain tools.
    
    Example:
        ```python
        # Basic usage
        tools = await create_file_tools()
        
        # Custom config
        config = {
            "mcpServers": {
                "file-server": {
                    "command": "/custom/path/to/run_server.sh"
                }
            }
        }
        tools = await create_file_tools(config)
        ```
    """
    toolkit = MCPFileToolkit(mcp_config)
    await toolkit.initialize()
    return toolkit.get_tools()


def check_langchain_availability() -> bool:
    """Check if LangChain is available."""
    return LANGCHAIN_AVAILABLE