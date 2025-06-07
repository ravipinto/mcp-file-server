#!/bin/bash

# MCP File Server Launcher Script
# Usage: ./run_server_local.sh [directory]
# If no directory is provided, uses the script's directory

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "MCP File Server Launcher"
    echo ""
    echo "Usage: $0 [directory]"
    echo ""
    echo "Arguments:"
    echo "  directory    Path to MCP server directory (optional)"
    echo "               Default: current script directory"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run from script directory"
    echo "  $0 /path/to/mcp/server       # Run from specified directory"
    echo "  $0 .                         # Run from current directory"
    exit 0
fi

# Get the directory parameter or default to script's directory
MCP_DIR="${1:-$(dirname "$(realpath "$0")")}"

# Validate directory exists
if [ ! -d "$MCP_DIR" ]; then
    echo "Error: Directory '$MCP_DIR' does not exist"
    exit 1
fi

# Validate main.py exists in the directory
if [ ! -f "$MCP_DIR/main.py" ]; then
    echo "Error: main.py not found in '$MCP_DIR'"
    exit 1
fi

# Change to the MCP directory and run the server
# Note: Don't echo anything here as Claude Desktop expects pure JSON-RPC output
cd "$MCP_DIR"
exec /opt/homebrew/bin/uv run python main.py