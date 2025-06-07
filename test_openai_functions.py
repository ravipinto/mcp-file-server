import asyncio
from openai_integration import create_openai_function_caller
import os
from dotenv import load_dotenv

async def run_mcp_tests():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize the function caller with your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return
        
    caller = await create_openai_function_caller(api_key)

    # Create a single comprehensive request instead of multiple separate messages
    messages = [
        {
            "role": "user", 
            "content": """
            Please help me test the file operations. I want you to:
            1. Create a folder called /tmp/test-mcp
            2. Write a file /tmp/test-mcp/hello.txt with content "Hello from OpenAI!"
            3. List the files in /tmp/test-mcp
            4. Read the contents of /tmp/test-mcp/hello.txt to verify it was created correctly
            5. Delete the file /tmp/test-mcp/hello.txt
            
            Please execute these operations step by step and tell me the results.
            """
        }
    ]

    print("🚀 Running OpenAI function calling tests...")
    
    # Run the conversation
    result = await caller.chat_with_functions(messages, model="gpt-4")

    # Print results
    print("\n=== Assistant Response ===")
    print(result["response"])

    print(f"\n=== Function Calls ({len(result['function_calls'])}) ===")
    for i, call in enumerate(result["function_calls"], 1):
        print(f"{i}. {call['function']}({call['arguments']}) -> {call['result']}")

    print("\n=== Token Usage ===")
    if result["usage"]:
        usage = result["usage"]
        print(f"Input tokens: {usage.get('prompt_tokens', 'N/A')}")
        print(f"Output tokens: {usage.get('completion_tokens', 'N/A')}")
        print(f"Total tokens: {usage.get('total_tokens', 'N/A')}")
    else:
        print("No usage data available")

# Run the test
if __name__ == "__main__":
    asyncio.run(run_mcp_tests())