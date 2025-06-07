#!/usr/bin/env python3
"""
HTTP server wrapper for MCP file server to integrate with n8n.

This creates REST endpoints that n8n can call to use the MCP file tools.
"""

import asyncio
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from langchain_simple import SimpleMCPFileTools


# Pydantic models for request/response
class FileOperation(BaseModel):
    operation: str
    path: str
    content: str = None


class OperationResponse(BaseModel):
    success: bool
    result: str
    error: str = None


# Global MCP toolkit instance
mcp_toolkit = None


app = FastAPI(
    title="MCP File Server API for n8n",
    description="HTTP API wrapper for MCP file operations",
    version="1.0.0"
)


async def get_toolkit():
    """Get or create MCP toolkit instance."""
    global mcp_toolkit
    if mcp_toolkit is None:
        config = {
            "mcpServers": {
                "file-server": {
                    "command": "uv",
                    "args": ["run", "python", "main.py"],
                    "cwd": "/Users/ravi/Work/Source/py/mcp"
                }
            }
        }
        mcp_toolkit = SimpleMCPFileTools(config)
        await mcp_toolkit.initialize()
    return mcp_toolkit


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "MCP File Server API for n8n",
        "version": "1.0.0",
        "endpoints": {
            "file_operation": "/file-operation",
            "tools": "/tools",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        toolkit = await get_toolkit()
        return {"status": "healthy", "mcp_connected": True}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/tools")
async def list_tools():
    """List available file operations."""
    return {
        "tools": [
            {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": ["path"]
            },
            {
                "name": "write_file", 
                "description": "Write content to a file",
                "parameters": ["path", "content"]
            },
            {
                "name": "list_directory",
                "description": "List the contents of a directory",
                "parameters": ["path"]
            },
            {
                "name": "create_directory",
                "description": "Create a new directory",
                "parameters": ["path"]
            },
            {
                "name": "delete_file",
                "description": "Delete a file",
                "parameters": ["path"]
            }
        ]
    }


@app.post("/file-operation", response_model=OperationResponse)
async def execute_file_operation(operation: FileOperation):
    """Execute a file operation through MCP."""
    try:
        toolkit = await get_toolkit()
        
        # Prepare arguments
        kwargs = {"path": operation.path}
        if operation.content is not None:
            kwargs["content"] = operation.content
        
        # Execute the operation
        result = await toolkit.call_tool_async(operation.operation, **kwargs)
        
        # Check if result indicates an error
        if result.startswith("Error"):
            return OperationResponse(
                success=False,
                result="",
                error=result
            )
        
        return OperationResponse(
            success=True,
            result=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Individual endpoints for each operation (alternative approach)
@app.post("/read-file")
async def read_file(path: str):
    """Read a file."""
    toolkit = await get_toolkit()
    result = await toolkit.call_tool_async("read_file", path=path)
    return {"result": result}


@app.post("/write-file")
async def write_file(path: str, content: str):
    """Write to a file."""
    toolkit = await get_toolkit()
    result = await toolkit.call_tool_async("write_file", path=path, content=content)
    return {"result": result}


@app.post("/list-directory")
async def list_directory(path: str):
    """List directory contents."""
    toolkit = await get_toolkit()
    result = await toolkit.call_tool_async("list_directory", path=path)
    return {"result": result}


@app.post("/create-directory")
async def create_directory(path: str):
    """Create a directory."""
    toolkit = await get_toolkit()
    result = await toolkit.call_tool_async("create_directory", path=path)
    return {"result": result}


@app.post("/delete-file")
async def delete_file(path: str):
    """Delete a file."""
    toolkit = await get_toolkit()
    result = await toolkit.call_tool_async("delete_file", path=path)
    return {"result": result}


if __name__ == "__main__":
    print("🚀 Starting MCP File Server API for n8n...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        "n8n_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )