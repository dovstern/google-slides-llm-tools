"""
Google Slides LLM Tools

A comprehensive toolkit for creating, editing, and managing Google Slides presentations
using Large Language Models. This package provides easy-to-use functions for:

- Creating and managing presentations
- Adding and formatting text
- Inserting multimedia content (images, videos, audio)
- Applying layouts and templates
- Setting animations and transitions
- Exporting presentations
- Managing collaboration and permissions

All functions are designed to work seamlessly with LLM frameworks like LangChain.
"""

# Import all tool functions from their respective modules
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

from google_slides_llm_tools.animations import (
    set_slide_transition,
    apply_auto_advance,
    set_slide_background
)

from google_slides_llm_tools.templates import (
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template
)

from google_slides_llm_tools.export import (
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail
)

from google_slides_llm_tools.data import (
    create_sheets_chart,
    create_table_from_sheets,
    get_slide_data,
    get_presentation_data,
    find_element_ids
)

from google_slides_llm_tools.collaboration import (
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
)

# Import utility functions
from google_slides_llm_tools.utils.add_credentials_to_langchain_tool_call import (
    add_credentials_to_langchain_tool_call
)

# Create a list of all LangChain tools
langchain_tools = [
    # Slides operations
    create_presentation,
    get_presentation,
    add_slide,
    delete_slide,
    reorder_slides,
    duplicate_slide,
    
    # Formatting
    add_text_to_slide,
    update_text_style,
    update_paragraph_style,
    
    # Multimedia
    add_image_to_slide,
    add_video_to_slide,
    insert_audio_link,
    add_shape_to_slide,
    create_shape,
    group_elements,
    ungroup_elements,
    
    # Animations
    set_slide_transition,
    apply_auto_advance,
    set_slide_background,
    
    # Templates
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template,
    
    # Export
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail,
    
    # Data
    create_sheets_chart,
    create_table_from_sheets,
    get_slide_data,
    get_presentation_data,
    find_element_ids,
    
    # Collaboration
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
]

def get_langchain_tools():
    """
    Get all available LangChain tools for Google Slides operations.
    
    Returns:
        List of LangChain tools that can be used with LangChain agents and frameworks.
    """
    return langchain_tools

# List of all available tools for easy access
__all__ = [
    # Slides operations
    'create_presentation',
    'get_presentation',
    'add_slide',
    'delete_slide',
    'reorder_slides',
    'duplicate_slide',
    
    # Formatting
    'add_text_to_slide',
    'update_text_style',
    'update_paragraph_style',
    
    # Multimedia
    'add_image_to_slide',
    'add_video_to_slide',
    'insert_audio_link',
    'add_shape_to_slide',
    'create_shape',
    'group_elements',
    'ungroup_elements',
    
    # Animations
    'set_slide_transition',
    'apply_auto_advance',
    'set_slide_background',
    
    # Templates
    'apply_predefined_layout',
    'duplicate_presentation',
    'list_available_layouts',
    'create_custom_template',
    
    # Export
    'export_presentation_as_pdf',
    'export_slide_as_pdf',
    'get_presentation_thumbnail',
    
    # Data
    'create_sheets_chart',
    'create_table_from_sheets',
    'get_slide_data',
    'get_presentation_data',
    'find_element_ids',
    
    # Collaboration
    'add_editor_permission',
    'add_viewer_permission',
    'add_commenter_permission',
    'remove_permission',
    'list_permissions',
    'make_public',
    
    # Utilities
    'add_credentials_to_langchain_tool_call',
    'get_langchain_tools',
    'langchain_tools'
]
