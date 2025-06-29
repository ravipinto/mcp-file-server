import unittest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

from main import read_file_tool, write_file_tool, list_directory_tool, create_directory_tool, delete_file_tool
from mcp.types import TextContent

class TestMain(unittest.TestCase):

    def test_read_file_tool(self):
        async def run_test():
            # Create a dummy file
            dummy_file = Path("test_file.txt")
            dummy_file.write_text("hello world")

            # Test reading the file
            result = await read_file_tool({"path": "test_file.txt"})
            self.assertEqual(result, [TextContent(type="text", text="hello world")])

            # Clean up the dummy file
            dummy_file.unlink()

        asyncio.run(run_test())

    def test_write_file_tool(self):
        async def run_test():
            # Test writing to a file
            result = await write_file_tool({"path": "test_file.txt", "content": "hello world"})
            self.assertEqual(result, [TextContent(type="text", text=f"Successfully wrote to {Path('test_file.txt').resolve()}")])

            # Check that the file was created and has the correct content
            self.assertTrue(Path("test_file.txt").exists())
            self.assertEqual(Path("test_file.txt").read_text(), "hello world")

            # Clean up the dummy file
            Path("test_file.txt").unlink()

        asyncio.run(run_test())

    def test_list_directory_tool(self):
        async def run_test():
            # Create a dummy directory and file
            dummy_dir = Path("test_dir")
            dummy_dir.mkdir()
            dummy_file = dummy_dir / "test_file.txt"
            dummy_file.write_text("hello world")

            # Test listing the directory
            result = await list_directory_tool({"path": "test_dir"})
            self.assertEqual(result, [TextContent(type="text", text="test_file.txt (file)")])

            # Clean up the dummy directory and file
            dummy_file.unlink()
            dummy_dir.rmdir()

        asyncio.run(run_test())

    def test_create_directory_tool(self):
        async def run_test():
            # Test creating a directory
            dummy_dir = Path("test_dir")
            result = await create_directory_tool({"path": str(dummy_dir)})
            self.assertEqual(result, [TextContent(type="text", text=f"Successfully created directory: {dummy_dir.resolve()}")])

            # Check that the directory was created
            self.assertTrue(dummy_dir.exists())

            # Clean up the dummy directory
            dummy_dir.rmdir()

        asyncio.run(run_test())

    def test_delete_file_tool(self):
        async def run_test():
            # Create a dummy file
            dummy_file = Path("test_file.txt")
            dummy_file.write_text("hello world")

            # Test deleting the file
            result = await delete_file_tool({"path": "test_file.txt"})
            self.assertEqual(result, [TextContent(type="text", text=f"Successfully deleted file: {dummy_file.resolve()}")])

            # Check that the file was deleted
            self.assertFalse(dummy_file.exists())

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()