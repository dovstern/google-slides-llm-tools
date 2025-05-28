"""
Test the LangChain to MCP tool adapter.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.server import FastMCP
from langchain.tools import Tool
from langchain_tool_to_mcp_adapter import add_langchain_tool_to_server


class TestLangchainAdapter(unittest.TestCase):
    """Test the LangChain to MCP tool adapter."""
    
    def setUp(self):
        """Set up the test environment."""
        self.server = FastMCP('test-server')
    
    def test_basic_tool_conversion(self):
        """Test basic conversion of a LangChain tool to MCP tool."""
        # Create a simple LangChain tool
        def multiply(a, b):
            return a * b
        
        tool = Tool(
            name="multiply",
            description="Multiply two numbers",
            func=multiply
        )
        
        # Mock the server.tool decorator
        mock_decorator = MagicMock()
        mock_decorator.return_value = lambda x: x  # Return the function unchanged
        
        with patch.object(self.server, 'tool', return_value=mock_decorator):
            # Add the tool to the server
            add_langchain_tool_to_server(self.server, tool)
            
            # Check if tool decorator was called with correct name and description
            self.server.tool.assert_called_once_with(name="multiply", description="Multiply two numbers")
    
    def test_content_and_artifact_conversion(self):
        """Test conversion of a LangChain tool with content_and_artifact response format."""
        # Create a LangChain tool that returns content and artifact
        def get_image():
            content = "Here is the image"
            data_url = "data:image/png;base64,abc123"
            return content, data_url
        
        tool = Tool(
            name="get_image",
            description="Get an image",
            func=get_image,
            response_format="content_and_artifact"
        )
        
        # Create a mock decorator that captures the decorated function
        captured_func = None
        def mock_decorator(func):
            nonlocal captured_func
            captured_func = func
            return func
            
        # Mock the server.tool method
        with patch.object(self.server, 'tool', return_value=mock_decorator):
            # Add the tool to the server
            add_langchain_tool_to_server(self.server, tool)
            
            # Check if tool decorator was called with correct name and description
            self.server.tool.assert_called_once_with(name="get_image", description="Get an image")
            
            # Ensure a function was captured
            self.assertIsNotNone(captured_func)
            
            # Call the captured function and test its behavior
            result = captured_func()
            
            # Check if the result is in the expected format
            self.assertIsInstance(result, dict)
            self.assertIn("content", result)
            self.assertIn("artifacts", result)
            self.assertEqual(result["content"], "Here is the image")
            self.assertIsInstance(result["artifacts"], list)
            self.assertEqual(len(result["artifacts"]), 1)
            self.assertEqual(result["artifacts"][0]["type"], "file")
            self.assertIn("file_data", result["artifacts"][0]["file"])
    
    def test_list_artifact_passthrough(self):
        """Test that a list of artifacts is passed through correctly."""
        # Create a LangChain tool that returns content and a list of artifacts
        def get_multiple_files():
            content = "Here are the files"
            artifacts = [
                {
                    "type": "file",
                    "file": {
                        "filename": "file1.pdf",
                        "file_data": "data:application/pdf;base64,abc123",
                    }
                },
                {
                    "type": "file",
                    "file": {
                        "filename": "file2.pdf",
                        "file_data": "data:application/pdf;base64,def456",
                    }
                }
            ]
            return content, artifacts
        
        tool = Tool(
            name="get_multiple_files",
            description="Get multiple files",
            func=get_multiple_files,
            response_format="content_and_artifact"
        )
        
        # Create a mock decorator that captures the decorated function
        captured_func = None
        def mock_decorator(func):
            nonlocal captured_func
            captured_func = func
            return func
            
        # Mock the server.tool method
        with patch.object(self.server, 'tool', return_value=mock_decorator):
            # Add the tool to the server
            add_langchain_tool_to_server(self.server, tool)
            
            # Ensure a function was captured
            self.assertIsNotNone(captured_func)
            
            # Call the captured function and test its behavior
            result = captured_func()
            
            # Check if the result is in the expected format
            self.assertIsInstance(result, dict)
            self.assertIn("content", result)
            self.assertIn("artifacts", result)
            self.assertEqual(result["content"], "Here are the files")
            self.assertIsInstance(result["artifacts"], list)
            self.assertEqual(len(result["artifacts"]), 2)
            self.assertEqual(result["artifacts"][0]["file"]["filename"], "file1.pdf")
            self.assertEqual(result["artifacts"][1]["file"]["filename"], "file2.pdf")


if __name__ == '__main__':
    unittest.main() 