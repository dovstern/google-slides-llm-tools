"""
Test the MCP server functionality with LangChain tools.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import server components
from mcp.server import FastMCP
from google_slides_llm_tools.mcp_server import register_all_langchain_tools
from google_slides_llm_tools import get_langchain_tools

class TestMCPServer(unittest.TestCase):
    """Test the MCP server functionality with LangChain tools."""
    
    def test_register_all_tools(self):
        """Test that all LangChain tools are registered with the MCP server."""
        # Create a mock server
        mock_server = MagicMock(spec=FastMCP)
        
        # Mock the get_langchain_tools function to return a small subset
        mock_tools = []
        for i in range(3):
            mock_tool = MagicMock()
            mock_tool.name = f"tool_{i}"
            mock_tool.description = f"Description for tool {i}"
            mock_tool.func = lambda: f"Result from tool {i}"
            mock_tools.append(mock_tool)
        
        # Patch get_langchain_tools to return our mock tools
        with patch('google_slides_llm_tools.mcp_server.get_langchain_tools', return_value=mock_tools):
            # Register all tools
            register_all_langchain_tools.__globals__['server'] = mock_server
            register_all_langchain_tools()
            
            # Check that tool decorator was called for each mock tool
            self.assertEqual(mock_server.tool.call_count, 3)
            
            # Check that the tool decorator was called with the correct tool names
            for i in range(3):
                tool_name = f"tool_{i}"
                tool_description = f"Description for tool {i}"
                mock_server.tool.assert_any_call(name=tool_name, description=tool_description)
            

if __name__ == '__main__':
    unittest.main() 