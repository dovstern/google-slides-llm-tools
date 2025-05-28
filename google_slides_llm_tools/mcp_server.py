"""
Google Slides LLM Tools - MCP Server

This module provides MCP (Model Context Protocol) server integration for
Google Slides LLM Tools. It allows the tools to be exposed as an MCP server
that can be used by LangGraph agents and other MCP clients.
"""

import sys
import os
import argparse
import functools
from mcp.server import FastMCP

# Import all the necessary functions
from google_slides_llm_tools.utils import authenticate, get_slides_service, get_drive_service
from google_slides_llm_tools.slides_operations import (
    create_presentation,
    get_presentation,
    add_slide,
    delete_slide,
    reorder_slides,
    duplicate_slide
)
from google_slides_llm_tools.formatting import (
    add_text_to_slide,
    update_text_style,
    update_paragraph_style
)
from google_slides_llm_tools.multimedia import (
    add_image_to_slide,
    add_video_to_slide,
    insert_audio_link,
    add_shape_to_slide,
    create_shape,
    group_elements,
    ungroup_elements
)
from google_slides_llm_tools.data import (
    create_sheets_chart,
    create_table_from_sheets
)
from google_slides_llm_tools.templates import (
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template
)
from google_slides_llm_tools.collaboration import (
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
)
from google_slides_llm_tools.animations import (
    set_slide_transition,
    apply_auto_advance,
    set_slide_background
)
from google_slides_llm_tools.export import (
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail
)
from google_slides_llm_tools.utils import (
    slide_id_to_index,
    index_to_slide_id,
    get_element_id_by_name,
    rgb_to_hex,
    hex_to_rgb,
    points_to_emu,
    emu_to_points,
    get_page_size
)

# Import the LangChain tool adapter
from langchain_tool_to_mcp_adapter import add_langchain_tool_to_server

# Import the LangChain tools
from google_slides_llm_tools import get_langchain_tools, langchain_tools

class CredentialsManager:
    """Manages authentication credentials for Google API calls."""
    
    def __init__(self):
        self.credentials = None
        self.use_adc = False
        self.credentials_path = None
        self.project_id = None
    
    def set_use_adc(self, use_adc, project_id=None):
        """Set whether to use Application Default Credentials."""
        self.use_adc = use_adc
        self.project_id = project_id
    
    def set_credentials_path(self, credentials_path):
        """Set the path to the credentials file."""
        self.credentials_path = credentials_path
    
    def get_credentials(self):
        """Get or initialize credentials."""
        if self.credentials is None:
            if self.use_adc:
                # Use Application Default Credentials (gcloud auth application-default login)
                self.credentials = authenticate(use_adc=True, project_id=self.project_id)
            elif self.credentials_path:
                # Use service account or OAuth credentials from file
                self.credentials = authenticate(credentials_path=self.credentials_path)
            else:
                # Try to use default credentials from environment variable
                self.credentials = authenticate(use_adc=True)
        return self.credentials

# Initialize the MCP server
server = FastMCP('google-slides-mcp')

# Initialize credentials manager
credentials_manager = CredentialsManager()

def with_auth(func):
    """
    Decorator to inject credentials into functions.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with credentials automatically injected
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        creds = credentials_manager.get_credentials()
        return func(creds, *args, **kwargs)
    return wrapper

# Create authenticated versions of all functions
create_presentation_auth = with_auth(create_presentation)
get_presentation_auth = with_auth(get_presentation)
add_slide_auth = with_auth(add_slide)
delete_slide_auth = with_auth(delete_slide)
reorder_slides_auth = with_auth(reorder_slides)
duplicate_slide_auth = with_auth(duplicate_slide)

add_text_to_slide_auth = with_auth(add_text_to_slide)
update_text_style_auth = with_auth(update_text_style)
update_paragraph_style_auth = with_auth(update_paragraph_style)

add_image_to_slide_auth = with_auth(add_image_to_slide)
add_video_to_slide_auth = with_auth(add_video_to_slide)
insert_audio_link_auth = with_auth(insert_audio_link)
add_shape_to_slide_auth = with_auth(add_shape_to_slide)

export_presentation_as_pdf_auth = with_auth(export_presentation_as_pdf)
export_slide_as_pdf_auth = with_auth(export_slide_as_pdf)
get_presentation_thumbnail_auth = with_auth(get_presentation_thumbnail)

# Auth wrapper functions
@with_auth
def create_shape_auth(presentation_id, slide_id, shape_type, x, y, width, height, fill_color=None):
    """Auth wrapper for create_shape."""
    return create_shape(credentials_manager.get_credentials(), presentation_id, 
                       slide_id, shape_type, x, y, width, height, fill_color)

@with_auth
def group_elements_auth(presentation_id, element_ids):
    """Auth wrapper for group_elements."""
    return group_elements(credentials_manager.get_credentials(), presentation_id, element_ids)

@with_auth
def ungroup_elements_auth(presentation_id, group_id):
    """Auth wrapper for ungroup_elements."""
    return ungroup_elements(credentials_manager.get_credentials(), presentation_id, group_id)

# Add all LangChain tools to the MCP server
def register_all_langchain_tools():
    """Register all LangChain tools with the MCP server."""
    for tool in get_langchain_tools():
        add_langchain_tool_to_server(server, tool)

# Register all LangChain tools when this module is imported
register_all_langchain_tools()

def run_server(port=8000):
    """
    Run the MCP server.
    
    Args:
        port (int): Port to run the server on
    """
    server.run(port=port)

def main():
    """Command-line entrypoint for running the server."""
    parser = argparse.ArgumentParser(description='Run the Google Slides MCP server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--adc', action='store_true', help='Use Application Default Credentials')
    parser.add_argument('--project', type=str, help='Google Cloud project ID (for ADC)')
    parser.add_argument('--credentials', type=str, help='Path to credentials file')
    
    args = parser.parse_args()
    
    # Configure credentials
    if args.adc:
        credentials_manager.set_use_adc(True, args.project)
    elif args.credentials:
        credentials_manager.set_credentials_path(args.credentials)
    
    # Run the server
    run_server(port=args.port)

if __name__ == "__main__":
    main()