#!/usr/bin/env python3
"""
Test script for the n8n HTTP API integration.
"""

import requests
import json


def test_n8n_api():
    """Test the HTTP API endpoints for n8n integration."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MCP File Server HTTP API for n8n")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: List tools
    print("\n2. Testing tools list...")
    try:
        response = requests.get(f"{base_url}/tools")
        tools = response.json()
        print(f"   Found {len(tools['tools'])} tools:")
        for tool in tools['tools']:
            print(f"     - {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Write file using general endpoint
    print("\n3. Testing write file (general endpoint)...")
    try:
        payload = {
            "operation": "write_file",
            "path": "/tmp/n8n_api_test.txt",
            "content": "Hello from n8n API test!\nThis file was created via HTTP API."
        }
        response = requests.post(f"{base_url}/file-operation", json=payload)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Success: {result.get('success')}")
        print(f"   Result: {result.get('result')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Read file using specific endpoint
    print("\n4. Testing read file (specific endpoint)...")
    try:
        params = {"path": "/tmp/n8n_api_test.txt"}
        response = requests.post(f"{base_url}/read-file", params=params)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Content: {result.get('result')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: List directory
    print("\n5. Testing list directory...")
    try:
        payload = {
            "operation": "list_directory",
            "path": "/tmp"
        }
        response = requests.post(f"{base_url}/file-operation", json=payload)
        result = response.json()
        print(f"   Success: {result.get('success')}")
        # Show only first few files to avoid clutter
        files = result.get('result', '').split('\n')[:5]
        print(f"   Directory contents (first 5): {files}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Create directory
    print("\n6. Testing create directory...")
    try:
        params = {"path": "/tmp/n8n_test_dir"}
        response = requests.post(f"{base_url}/create-directory", params=params)
        result = response.json()
        print(f"   Result: {result.get('result')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 7: Error handling (try to read non-existent file)
    print("\n7. Testing error handling...")
    try:
        payload = {
            "operation": "read_file",
            "path": "/nonexistent/file.txt"
        }
        response = requests.post(f"{base_url}/file-operation", json=payload)
        result = response.json()
        print(f"   Success: {result.get('success')}")
        print(f"   Error: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ API testing completed!")
    print("🔗 You can now use these endpoints in n8n workflows")
    print("📖 See N8N_INTEGRATION.md for detailed instructions")


if __name__ == "__main__":
    test_n8n_api()