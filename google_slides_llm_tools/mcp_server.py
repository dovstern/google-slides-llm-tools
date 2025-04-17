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
from google_slides_llm_tools.auth import authenticate, get_slides_service, get_drive_service
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
    add_shape_to_slide
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
    set_element_animation,
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

# Define slide operations tools
@server.tool()
def create_presentation_tool(title: str) -> dict:
    """Creates a new Google Slides presentation with the specified title."""
    return create_presentation_auth(title)

@server.tool()
def get_presentation_tool(presentation_id: str) -> dict:
    """Gets information about a Google Slides presentation."""
    return get_presentation_auth(presentation_id)

@server.tool()
def add_slide_tool(presentation_id: str, layout: str = None) -> dict:
    """Adds a new slide to a presentation with the specified layout."""
    return add_slide_auth(presentation_id, layout)

@server.tool()
def delete_slide_tool(presentation_id: str, slide_id: str) -> dict:
    """Deletes a slide from a presentation."""
    return delete_slide_auth(presentation_id, slide_id)

@server.tool()
def reorder_slides_tool(presentation_id: str, slide_ids: list, insertion_index: int) -> dict:
    """Reorders slides in a presentation by moving them to a new position."""
    return reorder_slides_auth(presentation_id, slide_ids, insertion_index)

@server.tool()
def duplicate_slide_tool(presentation_id: str, slide_id: str) -> dict:
    """Duplicates a slide in a presentation."""
    return duplicate_slide_auth(presentation_id, slide_id)

# Define formatting tools
@server.tool()
def add_text_to_slide_tool(presentation_id: str, slide_id: str, text: str, position: dict = None) -> dict:
    """Adds text to a slide at the specified position."""
    return add_text_to_slide_auth(presentation_id, slide_id, text, position)

@server.tool()
def update_text_style_tool(presentation_id: str, slide_object_id: str, text_style: dict) -> dict:
    """Updates the style of text in a text box or shape."""
    return update_text_style_auth(presentation_id, slide_object_id, text_style)

@server.tool()
def update_paragraph_style_tool(presentation_id: str, slide_object_id: str, paragraph_style: dict) -> dict:
    """Updates the paragraph style in a text box or shape."""
    return update_paragraph_style_auth(presentation_id, slide_object_id, paragraph_style)

# Define multimedia tools
@server.tool()
def add_image_to_slide_tool(presentation_id: str, slide_id: str, image_url: str, 
                           x: float, y: float, width: float, height: float) -> dict:
    """Adds an image to a slide from a URL."""
    return add_image_to_slide_auth(presentation_id, slide_id, image_url, x, y, width, height)

@server.tool()
def add_video_to_slide_tool(presentation_id: str, slide_id: str, video_url: str, 
                          x: float, y: float, width: float, height: float, 
                          auto_play: bool = False, start_time: int = 0, 
                          end_time: int = None, mute: bool = False) -> dict:
    """Embeds a video into a slide."""
    return add_video_to_slide_auth(presentation_id, slide_id, video_url, 
                                 x, y, width, height, auto_play, start_time, end_time, mute)

@server.tool()
def insert_audio_link_tool(presentation_id: str, slide_id: str, audio_url: str, 
                          x: float, y: float, width: float, height: float, 
                          link_text: str = "Play Audio") -> dict:
    """Inserts a text box with a hyperlink to an external audio file."""
    return insert_audio_link_auth(presentation_id, slide_id, audio_url, 
                                x, y, width, height, link_text)

@server.tool()
def add_shape_to_slide_tool(presentation_id: str, slide_id: str, shape_type: str, 
                           x: float, y: float, width: float, height: float, 
                           fill_color: dict = None) -> dict:
    """Adds a shape to a slide."""
    return add_shape_to_slide_auth(presentation_id, slide_id, shape_type, 
                                 x, y, width, height, fill_color)

# Export tools
@server.tool()
def export_presentation_as_pdf_tool(presentation_id: str, output_path: str) -> str:
    """Exports a presentation as a PDF file."""
    return export_presentation_as_pdf_auth(presentation_id, output_path)

@server.tool()
def export_slide_as_pdf_tool(presentation_id: str, slide_index: int, output_path: str) -> str:
    """Exports a specific slide as a PDF file."""
    return export_slide_as_pdf_auth(presentation_id, slide_index, output_path)

@server.tool()
def get_presentation_thumbnail_tool(presentation_id: str, thumbnail_size: tuple = None) -> str:
    """Gets a thumbnail image of the first slide in a presentation."""
    return get_presentation_thumbnail_auth(presentation_id, thumbnail_size)

# Function to run the MCP server
def run_server(port=8000):
    """
    Run the MCP server.
    
    Args:
        port (int): Port to run the server on. Default is 8000.
    """
    # Initialize credentials before starting the server
    credentials_manager.get_credentials()
    server.run()

def main():
    """
    Main entry point for the MCP server when run as a script.
    Parses command line arguments and starts the server.
    """
    parser = argparse.ArgumentParser(description='Google Slides MCP Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    
    # Add argument for credentials file path
    parser.add_argument('--credentials', help='Path to Google OAuth credentials JSON file')
    
    # Add argument for using application default credentials
    parser.add_argument('--use-adc', action='store_true', help='Use Application Default Credentials (set via gcloud auth application-default login)')
    
    # Add the new argument to the parser
    parser.add_argument('--test-create-presentation', action='store_true', help='Test the create_presentation tool and exit')
    
    # Add argument for specifying the GCP project
    parser.add_argument('--project', help='Google Cloud project ID to use for ADC')
    
    args = parser.parse_args()
    
    # Set authentication method in the credentials manager
    credentials_manager.set_use_adc(args.use_adc, args.project)
    
    # Set credentials path in the credentials manager if provided
    if args.credentials:
        credentials_manager.set_credentials_path(args.credentials)
        # Also set the environment variable for backward compatibility
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    # Test create_presentation_tool if requested
    if hasattr(args, 'test_create_presentation') and args.test_create_presentation:
        print("Testing create_presentation_tool...")
        result = create_presentation_tool("Test Presentation from MCP Server")
        print("Result:", result)
        sys.exit(0)

    print(f"Starting Google Slides MCP server on port {args.port}")
    print(f"Authentication method: {'Application Default Credentials' if args.use_adc else 'Service Account/OAuth'}")
    run_server(port=args.port)

if __name__ == "__main__":
    main()