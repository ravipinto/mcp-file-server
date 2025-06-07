#!/usr/bin/env python3
"""
LangChain integration examples for MCP File Server.

This script demonstrates various ways to use the MCP file server with LangChain:
1. Basic tool usage
2. Agent with file tools
3. Custom workflows with file operations
4. Error handling and best practices
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv

# Import our LangChain integration
from langchain_integration import (
    MCPFileToolkit, 
    create_file_tools, 
    check_langchain_availability
)

# Load environment variables
load_dotenv()


async def example_1_basic_tools():
    """Example 1: Basic tool usage without agents."""
    print("🔧 Example 1: Basic MCP File Tools Usage")
    print("=" * 50)
    
    # Create MCP file tools
    config = {
        "mcpServers": {
            "file-server": {
                "command": "/Users/ravi/Work/Source/py/mcp/run_server_local.sh"
            }
        }
    }
    
    try:
        tools = await create_file_tools(config)
        print(f"✅ Created {len(tools)} file tools")
        
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Example: Use tools directly
        write_tool = next(t for t in tools if t.name == "write_file")
        list_tool = next(t for t in tools if t.name == "list_directory")
        read_tool = next(t for t in tools if t.name == "read_file")
        
        # Write a test file
        result = await write_tool._arun(
            path="/tmp/langchain_test.txt",
            content="Hello from LangChain + MCP integration!\nThis file was created using LangChain tools."
        )
        print(f"📝 Write result: {result}")
        
        # List directory to verify
        result = await list_tool._arun(path="/tmp")
        print(f"📁 Directory listing (first few files):")
        files = result.split('\n')[:5]
        for file in files:
            if 'langchain_test.txt' in file:
                print(f"  ✅ {file}")
                break
        
        # Read the file back
        result = await read_tool._arun(path="/tmp/langchain_test.txt")
        print(f"📖 File contents:\n{result[:100]}...")
        
    except Exception as e:
        print(f"❌ Error in basic tools example: {e}")
        print("💡 Make sure to update the config with correct paths!")


async def example_2_agent_with_openai():
    """Example 2: LangChain agent with OpenAI and file tools."""
    print("\n🤖 Example 2: LangChain Agent with File Tools")
    print("=" * 50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY not found in environment")
        print("💡 Set your API key or skip this example")
        return
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain.prompts import ChatPromptTemplate
        
        # Create tools
        config = {
            "mcpServers": {
                "file-server": {
                    "command": "/Users/ravi/Work/Source/py/mcp/run_server_local.sh"
                }
            }
        }
        tools = await create_file_tools(config)
        
        # Create LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with file system access. "
                      "You can read, write, list, create, and delete files and directories. "
                      "Always be careful with file operations and ask for confirmation for destructive actions."),
            ("user", "{input}"),
            ("assistant", "I'll help you with that file operation. Let me use the available tools."),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create agent
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Example tasks
        tasks = [
            "Create a file called 'todo.txt' with a simple todo list",
            "List the files in the /tmp directory",
            "Read the contents of the todo.txt file you just created",
        ]
        
        for task in tasks:
            print(f"\n📋 Task: {task}")
            try:
                result = await agent_executor.ainvoke({"input": task})
                print(f"✅ Result: {result['output']}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install with: uv add --group langchain langchain")
    except Exception as e:
        print(f"❌ Error in agent example: {e}")


async def example_3_custom_workflow():
    """Example 3: Custom workflow for file processing."""
    print("\n⚙️ Example 3: Custom File Processing Workflow")
    print("=" * 50)
    
    try:
        # Create toolkit for manual management
        toolkit = MCPFileToolkit({
            "mcpServers": {
                "file-server": {
                    "command": "/Users/ravi/Work/Source/py/mcp/run_server_local.sh"
                }
            }
        })
        
        await toolkit.initialize()
        tools = toolkit.get_tools()
        
        # Get specific tools
        tools_dict = {tool.name: tool for tool in tools}
        
        # Workflow: Create a project structure
        print("📁 Creating project structure...")
        
        # 1. Create project directory
        await tools_dict["create_directory"]._arun(path="/tmp/my_project")
        print("✅ Created /tmp/my_project")
        
        # 2. Create subdirectories
        subdirs = ["src", "tests", "docs"]
        for subdir in subdirs:
            await tools_dict["create_directory"]._arun(path=f"/tmp/my_project/{subdir}")
            print(f"✅ Created /tmp/my_project/{subdir}")
        
        # 3. Create some files
        files = {
            "README.md": "# My Project\n\nThis is a sample project created with MCP + LangChain.",
            "src/main.py": "#!/usr/bin/env python3\n\ndef main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()",
            "tests/test_main.py": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_placeholder(self):\n        self.assertTrue(True)",
        }
        
        for file_path, content in files.items():
            await tools_dict["write_file"]._arun(
                path=f"/tmp/my_project/{file_path}",
                content=content
            )
            print(f"✅ Created /tmp/my_project/{file_path}")
        
        # 4. List the final structure
        print("\n📋 Final project structure:")
        structure = await tools_dict["list_directory"]._arun(path="/tmp/my_project")
        print(structure)
        
        # 5. Show content of README
        readme_content = await tools_dict["read_file"]._arun(path="/tmp/my_project/README.md")
        print(f"\n📖 README.md content:\n{readme_content}")
        
        # Cleanup
        await toolkit.close()
        print("🧹 Cleaned up MCP connections")
        
    except Exception as e:
        print(f"❌ Error in workflow example: {e}")


async def example_4_error_handling():
    """Example 4: Error handling and best practices."""
    print("\n🛡️ Example 4: Error Handling and Best Practices")
    print("=" * 50)
    
    try:
        toolkit = MCPFileToolkit()
        await toolkit.initialize()
        tools = toolkit.get_tools()
        read_tool = next(t for t in tools if t.name == "read_file")
        
        # Try to read a non-existent file
        print("🔍 Attempting to read non-existent file...")
        result = await read_tool._arun(path="/non/existent/file.txt")
        print(f"📄 Result: {result}")
        
        # Try to read a directory as a file
        print("\n🔍 Attempting to read directory as file...")
        result = await read_tool._arun(path="/tmp")
        print(f"📄 Result: {result}")
        
        await toolkit.close()
        
    except Exception as e:
        print(f"❌ Error in error handling example: {e}")


async def main():
    """Run all examples."""
    print("🚀 MCP File Server + LangChain Integration Examples")
    print("=" * 60)
    
    # Check if LangChain is available
    if not check_langchain_availability():
        print("❌ LangChain is not available!")
        print("💡 Install with: uv add --group langchain langchain")
        return
    
    print("✅ LangChain is available")
    print("\n💡 Note: Update the MCP config paths in examples to match your setup!")
    print("💡 For OpenAI examples, set OPENAI_API_KEY environment variable")
    
    # Run examples
    await example_1_basic_tools()
    await example_2_agent_with_openai()
    await example_3_custom_workflow()
    await example_4_error_handling()
    
    print("\n🎉 All examples completed!")
    print("📚 Check the LangChain documentation for more advanced usage patterns.")


if __name__ == "__main__":
    asyncio.run(main())