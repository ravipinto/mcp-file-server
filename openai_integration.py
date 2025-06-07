#!/usr/bin/env python3
"""
OpenAI function calling integration for MCP file server.

This module provides OpenAI-compatible function definitions and a client wrapper
that enables using the MCP file server tools with OpenAI's function calling API.
"""

import json
import os
from typing import Any, Dict, List, Optional
from openai import OpenAI
from langchain_simple import SimpleMCPFileTools


class OpenAIFunctionCaller:
    """OpenAI client wrapper with MCP file server function calling support."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client with MCP tools."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.mcp_toolkit = None
        
    async def initialize_mcp(self):
        """Initialize the MCP toolkit."""
        if self.mcp_toolkit is None:
            config = {
                "mcpServers": {
                    "file-server": {
                        "command": "uv",
                        "args": ["run", "python", "main.py"],
                        "cwd": "/Users/ravi/Work/Source/py/mcp"
                    }
                }
            }
            self.mcp_toolkit = SimpleMCPFileTools(config)
            await self.mcp_toolkit.initialize()
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI function definitions for all MCP file tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file from the filesystem",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The absolute or relative path to the file to read"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file, creating it if it doesn't exist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The absolute or relative path to the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write to the file"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List the contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The absolute or relative path to the directory to list"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "Create a new directory, including parent directories if needed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The absolute or relative path to the directory to create"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file from the filesystem",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The absolute or relative path to the file to delete"
                            }
                        },
                        "required": ["path"]
                    }
                }
            }
        ]
    
    async def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP function with the given arguments."""
        await self.initialize_mcp()
        
        try:
            result = await self.mcp_toolkit.call_tool_async(function_name, **arguments)
            return result
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}"
    
    async def chat_with_functions(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        max_function_calls: int = 5
    ) -> Dict[str, Any]:
        """
        Chat with OpenAI using function calling support.
        
        Args:
            messages: List of conversation messages
            model: OpenAI model to use
            max_function_calls: Maximum number of function calls to allow
            
        Returns:
            Dictionary with response and function call results
        """
        await self.initialize_mcp()
        
        function_definitions = self.get_function_definitions()
        conversation_messages = messages.copy()
        function_call_count = 0
        function_results = []
        
        while function_call_count < max_function_calls:
            # Make API call with function definitions
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation_messages,
                tools=function_definitions,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            conversation_messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [tc.dict() for tc in message.tool_calls] if message.tool_calls else None
            })
            
            # Check if the model wants to call functions
            if not message.tool_calls:
                break
                
            # Execute each function call
            for tool_call in message.tool_calls:
                function_call_count += 1
                if function_call_count > max_function_calls:
                    break
                    
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Executing function: {function_name} with args: {function_args}")
                
                # Execute the function
                result = await self.execute_function(function_name, function_args)
                
                function_results.append({
                    "function": function_name,
                    "arguments": function_args,
                    "result": result
                })
                
                # Add function result to conversation
                conversation_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        return {
            "response": message.content or "",
            "function_calls": function_results,
            "conversation": conversation_messages,
            "usage": response.usage.dict() if response.usage else None
        }


async def create_openai_function_caller(api_key: Optional[str] = None) -> OpenAIFunctionCaller:
    """Factory function to create and initialize OpenAI function caller."""
    caller = OpenAIFunctionCaller(api_key)
    await caller.initialize_mcp()
    return caller


def get_openai_tools_json() -> str:
    """Get OpenAI function definitions as JSON for external use."""
    caller = OpenAIFunctionCaller("dummy-key-for-function-definitions")
    return json.dumps(caller.get_function_definitions(), indent=2)


if __name__ == "__main__":
    import asyncio
    
    async def demo():
        """Demo the OpenAI function calling integration."""
        print("🚀 OpenAI Function Calling Demo")
        
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Please set OPENAI_API_KEY environment variable")
            return
        
        caller = await create_openai_function_caller()
        
        # Example conversation with function calling
        messages = [
            {
                "role": "user", 
                "content": "Create a file called /tmp/openai_test.txt with the content 'Hello from OpenAI function calling!' and then read it back to confirm it worked."
            }
        ]
        
        print("💬 Starting conversation with function calling...")
        result = await caller.chat_with_functions(messages)
        
        print(f"\n🤖 Assistant Response: {result['response']}")
        print(f"\n🔧 Function Calls Made: {len(result['function_calls'])}")
        
        for i, call in enumerate(result['function_calls'], 1):
            print(f"  {i}. {call['function']}({call['arguments']}) -> {call['result']}")
        
        if result['usage']:
            print(f"\n📊 Token Usage: {result['usage']}")
    
    asyncio.run(demo())