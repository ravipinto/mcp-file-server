#!/usr/bin/env python3

import os
import tempfile
import subprocess
import json
import time

def test_file_server_direct():
    """Test the file server by sending direct JSON-RPC messages"""
    
    # Create a test directory and file
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, "test.txt")
    
    print(f"Testing file server with directory: {test_dir}")
    
    try:
        # Start the file server
        server_process = subprocess.Popen(
            ['python', 'file_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialization request
        init_request = {
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
        
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response = server_process.stdout.readline()
        print(f"Init response: {response}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        server_process.stdin.write(json.dumps(initialized_notification) + "\n")
        server_process.stdin.flush()
        
        # Test write_file tool
        write_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "write_file",
                "arguments": {
                    "path": test_file,
                    "content": "Hello from MCP file server!"
                }
            }
        }
        
        server_process.stdin.write(json.dumps(write_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response = server_process.stdout.readline()
        print(f"Write response: {response}")
        
        # Verify file was actually created
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"File content verified: {content}")
        else:
            print("ERROR: File was not created!")
        
        # Test read_file tool
        read_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "read_file",
                "arguments": {
                    "path": test_file
                }
            }
        }
        
        server_process.stdin.write(json.dumps(read_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response = server_process.stdout.readline()
        print(f"Read response: {response}")
        
        # Test list_directory tool
        list_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "list_directory",
                "arguments": {
                    "path": test_dir
                }
            }
        }
        
        server_process.stdin.write(json.dumps(list_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response = server_process.stdout.readline()
        print(f"List response: {response}")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()
        
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    test_file_server_direct()