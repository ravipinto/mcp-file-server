#!/usr/bin/env python3
"""
Example usage of OpenAI function calling with MCP file server.

This script demonstrates various ways to use OpenAI's function calling
capabilities with the MCP file server tools.
"""

import asyncio
import os
from openai_integration import create_openai_function_caller


async def basic_file_operations():
    """Demo basic file operations with OpenAI function calling."""
    print("📁 Basic File Operations Demo")
    print("-" * 40)
    
    caller = await create_openai_function_caller()
    
    messages = [
        {
            "role": "user",
            "content": """
            Please help me with these file operations:
            1. Create a directory called /tmp/openai_demo
            2. Write a file called /tmp/openai_demo/example.txt with some sample content
            3. List the contents of the /tmp/openai_demo directory 
            4. Read the file back to verify it was created correctly
            """
        }
    ]
    
    result = await caller.chat_with_functions(messages, model="gpt-4")
    
    print(f"🤖 Response: {result['response']}")
    print(f"🔧 Functions called: {len(result['function_calls'])}")
    for call in result['function_calls']:
        print(f"  • {call['function']}: {call['result'][:100]}...")


async def code_analysis_demo():
    """Demo using OpenAI to analyze code files with function calling."""
    print("\n🔍 Code Analysis Demo")
    print("-" * 40)
    
    caller = await create_openai_function_caller()
    
    messages = [
        {
            "role": "user",
            "content": "Read the main.py file and give me a summary of what it does. Also check if there are any other Python files in the current directory."
        }
    ]
    
    result = await caller.chat_with_functions(messages, model="gpt-4")
    
    print(f"🤖 Analysis: {result['response']}")


async def interactive_file_manager():
    """Demo interactive file management conversation."""
    print("\n💬 Interactive File Manager Demo")
    print("-" * 40)
    
    caller = await create_openai_function_caller()
    
    # Multi-turn conversation
    conversation = [
        {
            "role": "user",
            "content": "I want to organize some files. First, create a directory structure: /tmp/organized with subdirectories: docs, scripts, and temp"
        }
    ]
    
    # First request
    result1 = await caller.chat_with_functions(conversation, model="gpt-4")
    print(f"🤖 Step 1: {result1['response']}")
    
    # Continue conversation
    conversation.extend(result1['conversation'][-2:])  # Add last assistant message and any tool results
    conversation.append({
        "role": "user", 
        "content": "Now create a sample Python script in the scripts directory that prints 'Hello World'"
    })
    
    result2 = await caller.chat_with_functions(conversation, model="gpt-4")
    print(f"🤖 Step 2: {result2['response']}")
    
    # Final step
    conversation.extend(result2['conversation'][-2:])
    conversation.append({
        "role": "user",
        "content": "Show me the contents of the entire organized directory structure"
    })
    
    result3 = await caller.chat_with_functions(conversation, model="gpt-4")
    print(f"🤖 Step 3: {result3['response']}")


async def function_definitions_demo():
    """Show the OpenAI function definitions being used."""
    print("\n📋 Function Definitions Demo")
    print("-" * 40)
    
    caller = await create_openai_function_caller()
    functions = caller.get_function_definitions()
    
    print("Available functions for OpenAI:")
    for func in functions:
        name = func['function']['name']
        desc = func['function']['description']
        params = list(func['function']['parameters']['properties'].keys())
        print(f"  • {name}: {desc}")
        print(f"    Parameters: {', '.join(params)}")
        print()


async def error_handling_demo():
    """Demo error handling in function calling."""
    print("\n⚠️ Error Handling Demo")
    print("-" * 40)
    
    caller = await create_openai_function_caller()
    
    messages = [
        {
            "role": "user",
            "content": "Try to read a file that doesn't exist: /nonexistent/path/file.txt. Then create it with some content and read it successfully."
        }
    ]
    
    result = await caller.chat_with_functions(messages, model="gpt-4")
    
    print(f"🤖 Error handling response: {result['response']}")
    print("Function calls and results:")
    for call in result['function_calls']:
        print(f"  • {call['function']}: {call['result']}")


async def main():
    """Run all OpenAI function calling demos."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    print("🚀 OpenAI Function Calling with MCP File Server")
    print("=" * 50)
    
    try:
        await function_definitions_demo()
        await basic_file_operations()
        await code_analysis_demo() 
        await interactive_file_manager()
        await error_handling_demo()
        
        print("\n✅ All demos completed successfully!")
        print("\n💡 Next steps:")
        print("   • Customize the function definitions for your use case")
        print("   • Integrate with your own OpenAI applications")
        print("   • Use the FastAPI server endpoints for web integration")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure the MCP server is accessible and OpenAI API key is valid")


if __name__ == "__main__":
    asyncio.run(main())