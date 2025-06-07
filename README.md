# MCP File Server

An MCP (Model Context Protocol) server that provides file system access tools for AI assistants.

## Features

The server provides the following tools:
- `read_file` - Read the contents of a file
- `write_file` - Write content to a file (creates directories as needed)
- `list_directory` - List the contents of a directory
- `create_directory` - Create a new directory
- `delete_file` - Delete a file

## Installation

This project uses `uv` for dependency management. To install:

```bash
uv sync
```

## Usage

There are three ways to run the file server:

### 1. Using uv run (Recommended)
```bash
uv run python main.py
```

### 2. Using the console script
```bash
uv run mcp-file-server
```

### 3. Direct execution (after installing)
```bash
uv pip install -e .
mcp-file-server
```

## Testing

You can test the server using the included test script:

```bash
uv run python simple_test.py
```

## Protocol

The server communicates using the MCP protocol over stdio. It accepts JSON-RPC messages and responds accordingly.

Example initialization:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
```

## Security Note

This server provides file system access. Only use it in trusted environments and be cautious about the paths you allow it to access.