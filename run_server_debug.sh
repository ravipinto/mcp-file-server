#!/bin/bash

# MCP File Server Debug Launcher Script
# Usage: ./run_server_debug.sh [directory]
# This version includes debug output - use for testing, not with Claude Desktop

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "MCP File Server Debug Launcher"
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
    echo ""
    echo "Note: This version includes debug output and should NOT be used with Claude Desktop."
    echo "      Use run_server_local.sh for Claude Desktop integration."
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

# Change to the MCP directory and run the server with debug output
echo "🚀 Starting MCP file server from: $MCP_DIR"
echo "📁 Working directory: $(pwd)"
echo "🐍 Python path: $(which python)"
echo "📦 UV path: /opt/homebrew/bin/uv"
echo "🔧 Running: uv run python main.py"
echo "---"
cd "$MCP_DIR"
exec /opt/homebrew/bin/uv run python main.py