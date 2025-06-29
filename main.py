import asyncio
import os
from pathlib import Path

from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent


server = Server("file-server")
ROOT_DIR = Path.cwd()

def resolve_path(path: str) -> Path:
    resolved_path = ROOT_DIR.joinpath(path).resolve()
    if ROOT_DIR not in resolved_path.parents and resolved_path != ROOT_DIR:
        raise ValueError("Path is outside the root directory")
    return resolved_path


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file", 
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_directory",
            description="List the contents of a directory", 
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the directory to list"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object", 
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the directory to create"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string", 
                        "description": "The path to the file to delete"
                    }
                },
                "required": ["path"]
            }
        )
    ]


async def read_file_tool(arguments: dict) -> list[TextContent]:
    if "path" not in arguments or not isinstance(arguments["path"], str):
        return [TextContent(type="text", text="Invalid path argument")]
    try:
        path = resolve_path(arguments["path"])
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return [TextContent(type="text", text=content)]
    except (ValueError, FileNotFoundError) as e:
        return [TextContent(type="text", text=str(e))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error reading file: {str(e)}")]

async def write_file_tool(arguments: dict) -> list[TextContent]:
    if "path" not in arguments or not isinstance(arguments["path"], str):
        return [TextContent(type="text", text="Invalid path argument")]
    if "content" not in arguments or not isinstance(arguments["content"], str):
        return [TextContent(type="text", text="Invalid content argument")]
    try:
        path = resolve_path(arguments["path"])
        content = arguments["content"]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return [TextContent(type="text", text=f"Successfully wrote to {path}")]
    except ValueError as e:
        return [TextContent(type="text", text=str(e))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error writing file: {str(e)}")]

async def list_directory_tool(arguments: dict) -> list[TextContent]:
    if "path" not in arguments or not isinstance(arguments["path"], str):
        return [TextContent(type="text", text="Invalid path argument")]
    try:
        path = resolve_path(arguments["path"])
        if not path.exists():
            return [TextContent(type="text", text=f"Directory does not exist: {path}")]
        if not path.is_dir():
            return [TextContent(type="text", text=f"Path is not a directory: {path}")]
        
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            items.append(f"{item} ({item_type})")
        
        if not items:
            return [TextContent(type="text", text="Directory is empty")]
        
        return [TextContent(type="text", text="\n".join(items))]
    except ValueError as e:
        return [TextContent(type="text", text=str(e))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error listing directory: {str(e)}")]

async def create_directory_tool(arguments: dict) -> list[TextContent]:
    if "path" not in arguments or not isinstance(arguments["path"], str):
        return [TextContent(type="text", text="Invalid path argument")]
    try:
        path = resolve_path(arguments["path"])
        path.mkdir(parents=True, exist_ok=True)
        return [TextContent(type="text", text=f"Successfully created directory: {path}")]
    except ValueError as e:
        return [TextContent(type="text", text=str(e))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating directory: {str(e)}")]

async def delete_file_tool(arguments: dict) -> list[TextContent]:
    if "path" not in arguments or not isinstance(arguments["path"], str):
        return [TextContent(type="text", text="Invalid path argument")]
    try:
        path = resolve_path(arguments["path"])
        if not path.exists():
            return [TextContent(type="text", text=f"File does not exist: {path}")]
        if path.is_dir():
            return [TextContent(type="text", text=f"Path is a directory, not a file: {path}")]
        
        os.remove(path)
        return [TextContent(type="text", text=f"Successfully deleted file: {path}")]
    except ValueError as e:
        return [TextContent(type="text", text=str(e))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error deleting file: {str(e)}")]

tool_handlers = {
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    "list_directory": list_directory_tool,
    "create_directory": create_directory_tool,
    "delete_file": delete_file_tool,
}

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if name in tool_handlers:
        return await tool_handlers[name](arguments)
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


def main():
    asyncio.run(run_server())


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="file-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    main()
