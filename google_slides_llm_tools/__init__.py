"""
Google Slides LLM Tools

A Python package providing tools for LLMs to interact with Google Slides.
This package integrates with LangChain and provides a comprehensive set of tools
for creating and manipulating Google Slides presentations.

It now also supports MCP (Model Context Protocol) server functionality to enable
integration with LangGraph agents.
"""

__version__ = '0.2.0'

# Auth module
from google_slides_llm_tools.auth import authenticate, get_slides_service, get_drive_service, get_sheets_service

# Slides operations
from google_slides_llm_tools.slides_operations import (
    create_presentation,
    get_presentation,
    add_slide,
    delete_slide,
    reorder_slides,
    duplicate_slide
)

# Text formatting
from google_slides_llm_tools.formatting import (
    add_text_to_slide,
    update_text_style,
    update_paragraph_style
)

# Multimedia management
from google_slides_llm_tools.multimedia import (
    add_image_to_slide,
    add_video_to_slide,
    insert_audio_link,
    add_shape_to_slide
)

# External data integration
from google_slides_llm_tools.data import (
    create_sheets_chart,
    create_table_from_sheets
)

# Templates and layouts
from google_slides_llm_tools.templates import (
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template
)

# Collaboration and sharing
from google_slides_llm_tools.collaboration import (
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
)

# Animations and transitions
from google_slides_llm_tools.animations import (
    set_slide_transition,
    set_element_animation,
    apply_auto_advance,
    set_slide_background
)

# Export functions
from google_slides_llm_tools.export import (
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail
)

# Utility functions
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


# LangChain tool wrappers
from langchain.tools import Tool

# ===============================================================
# LANGCHAIN INTEGRATION
# ===============================================================

# Slides Operations
create_presentation_tool = Tool(
    name="create_presentation",
    description="Creates a new Google Slides presentation with the specified title",
    func=lambda title: create_presentation(authenticate(), title)
)

get_presentation_tool = Tool(
    name="get_presentation",
    description="Gets information about a Google Slides presentation",
    func=lambda presentation_id: get_presentation(authenticate(), presentation_id)
)

add_slide_tool = Tool(
    name="add_slide",
    description="Adds a new slide to a presentation with the specified layout",
    func=lambda **kwargs: add_slide(authenticate(), kwargs.get("presentation_id"), kwargs.get("layout"))
)

delete_slide_tool = Tool(
    name="delete_slide",
    description="Deletes a slide from a presentation",
    func=lambda **kwargs: delete_slide(authenticate(), kwargs.get("presentation_id"), kwargs.get("slide_id"))
)

reorder_slides_tool = Tool(
    name="reorder_slides",
    description="Reorders slides in a presentation by moving them to a new position",
    func=lambda **kwargs: reorder_slides(authenticate(), kwargs.get("presentation_id"), 
                                        kwargs.get("slide_ids"), kwargs.get("insertion_index"))
)

duplicate_slide_tool = Tool(
    name="duplicate_slide",
    description="Duplicates a slide in a presentation",
    func=lambda **kwargs: duplicate_slide(authenticate(), kwargs.get("presentation_id"), kwargs.get("slide_id"))
)

# Formatting Tools
add_text_to_slide_tool = Tool(
    name="add_text_to_slide",
    description="Adds text to a slide at the specified position",
    func=lambda **kwargs: add_text_to_slide(authenticate(), kwargs.get("presentation_id"), 
                                           kwargs.get("slide_id"), kwargs.get("text"), 
                                           kwargs.get("position"))
)

update_text_style_tool = Tool(
    name="update_text_style",
    description="Updates the style of text in a text box or shape",
    func=lambda **kwargs: update_text_style(authenticate(), kwargs.get("presentation_id"), 
                                           kwargs.get("slide_object_id"), kwargs.get("text_style"))
)

update_paragraph_style_tool = Tool(
    name="update_paragraph_style",
    description="Updates the paragraph style in a text box or shape",
    func=lambda **kwargs: update_paragraph_style(authenticate(), kwargs.get("presentation_id"), 
                                                kwargs.get("slide_object_id"), kwargs.get("paragraph_style"))
)

# Multimedia Tools
add_image_to_slide_tool = Tool(
    name="add_image_to_slide",
    description="Adds an image to a slide from a URL",
    func=lambda **kwargs: add_image_to_slide(authenticate(), kwargs.get("presentation_id"), 
                                            kwargs.get("slide_id"), kwargs.get("image_url"), 
                                            kwargs.get("x"), kwargs.get("y"), 
                                            kwargs.get("width"), kwargs.get("height"))
)

add_video_to_slide_tool = Tool(
    name="add_video_to_slide",
    description="Embeds a video into a slide",
    func=lambda **kwargs: add_video_to_slide(authenticate(), kwargs.get("presentation_id"), 
                                            kwargs.get("slide_id"), kwargs.get("video_url"), 
                                            kwargs.get("x"), kwargs.get("y"), 
                                            kwargs.get("width"), kwargs.get("height"), 
                                            kwargs.get("auto_play", False), 
                                            kwargs.get("start_time", 0), 
                                            kwargs.get("end_time"), 
                                            kwargs.get("mute", False))
)

insert_audio_link_tool = Tool(
    name="insert_audio_link",
    description="Inserts a text box with a hyperlink to an external audio file",
    func=lambda **kwargs: insert_audio_link(authenticate(), kwargs.get("presentation_id"), 
                                           kwargs.get("slide_id"), kwargs.get("audio_url"), 
                                           kwargs.get("x"), kwargs.get("y"), 
                                           kwargs.get("width"), kwargs.get("height"), 
                                           kwargs.get("link_text", "Play Audio"))
)

add_shape_to_slide_tool = Tool(
    name="add_shape_to_slide",
    description="Adds a shape to a slide",
    func=lambda **kwargs: add_shape_to_slide(authenticate(), kwargs.get("presentation_id"), 
                                            kwargs.get("slide_id"), kwargs.get("shape_type"), 
                                            kwargs.get("x"), kwargs.get("y"), 
                                            kwargs.get("width"), kwargs.get("height"), 
                                            kwargs.get("fill_color"))
)

# Data Tools
create_sheets_chart_tool = Tool(
    name="create_sheets_chart",
    description="Creates a chart from Google Sheets data",
    func=lambda **kwargs: create_sheets_chart(authenticate(), kwargs.get("presentation_id"), 
                                             kwargs.get("slide_id"), kwargs.get("spreadsheet_id"), 
                                             kwargs.get("sheet_id"), kwargs.get("chart_id"), 
                                             kwargs.get("x"), kwargs.get("y"), 
                                             kwargs.get("width"), kwargs.get("height"))
)

create_table_from_sheets_tool = Tool(
    name="create_table_from_sheets",
    description="Creates a table from Google Sheets data",
    func=lambda **kwargs: create_table_from_sheets(authenticate(), kwargs.get("presentation_id"), 
                                                  kwargs.get("slide_id"), kwargs.get("spreadsheet_id"), 
                                                  kwargs.get("sheet_id"), kwargs.get("range"), 
                                                  kwargs.get("x"), kwargs.get("y"), 
                                                  kwargs.get("width"), kwargs.get("height"))
)

# Templates Tools
apply_predefined_layout_tool = Tool(
    name="apply_predefined_layout",
    description="Applies a predefined layout to a slide",
    func=lambda **kwargs: apply_predefined_layout(authenticate(), kwargs.get("presentation_id"), 
                                                 kwargs.get("slide_id"), kwargs.get("layout_id"))
)

duplicate_presentation_tool = Tool(
    name="duplicate_presentation",
    description="Duplicates an existing presentation",
    func=lambda **kwargs: duplicate_presentation(authenticate(), kwargs.get("presentation_id"), 
                                                kwargs.get("new_title"))
)

list_available_layouts_tool = Tool(
    name="list_available_layouts",
    description="Lists all available layouts in a presentation",
    func=lambda presentation_id: list_available_layouts(authenticate(), presentation_id)
)

create_custom_template_tool = Tool(
    name="create_custom_template",
    description="Creates a custom template from an existing presentation",
    func=lambda **kwargs: create_custom_template(authenticate(), kwargs.get("presentation_id"), 
                                                kwargs.get("template_name"))
)

# Animation Tools
set_slide_transition_tool = Tool(
    name="set_slide_transition",
    description="Sets the transition effect for a slide",
    func=lambda **kwargs: set_slide_transition(authenticate(), kwargs.get("presentation_id"), 
                                              kwargs.get("slide_id"), kwargs.get("transition_type", "FADE"), 
                                              kwargs.get("duration_ms", 500))
)

set_element_animation_tool = Tool(
    name="set_element_animation",
    description="Adds an animation effect to an element on a slide",
    func=lambda **kwargs: set_element_animation(authenticate(), kwargs.get("presentation_id"), 
                                               kwargs.get("slide_id"), kwargs.get("element_id"), 
                                               kwargs.get("animation_type"), 
                                               kwargs.get("start_on", "ON_CLICK"), 
                                               kwargs.get("duration_ms", 500), 
                                               kwargs.get("order"))
)

apply_auto_advance_tool = Tool(
    name="apply_auto_advance",
    description="Sets a slide to automatically advance after a specified time",
    func=lambda **kwargs: apply_auto_advance(authenticate(), kwargs.get("presentation_id"), 
                                            kwargs.get("slide_id"), kwargs.get("auto_advance_after_ms"))
)

set_slide_background_tool = Tool(
    name="set_slide_background",
    description="Sets the background for a slide",
    func=lambda **kwargs: set_slide_background(authenticate(), kwargs.get("presentation_id"), 
                                              kwargs.get("slide_id"), kwargs.get("background_type"), 
                                              kwargs.get("background_value"))
)

# Export Tools
export_presentation_as_pdf_tool = Tool(
    name="export_presentation_as_pdf",
    description="Exports a presentation as a PDF file",
    func=lambda **kwargs: export_presentation_as_pdf(authenticate(), kwargs.get("presentation_id"), 
                                                    kwargs.get("output_path")),
    response_format="content_and_artifact"
)

export_slide_as_pdf_tool = Tool(
    name="export_slide_as_pdf",
    description="Exports a specific slide as a PDF file",
    func=lambda **kwargs: export_slide_as_pdf(authenticate(), kwargs.get("presentation_id"), 
                                             kwargs.get("slide_index"), kwargs.get("output_path")),
    response_format="content_and_artifact"
)

get_presentation_thumbnail_tool = Tool(
    name="get_presentation_thumbnail",
    description="Gets a thumbnail image of a slide in a presentation",
    func=lambda **kwargs: get_presentation_thumbnail(authenticate(), kwargs.get("presentation_id"), 
                                                    kwargs.get("slide_index", 0), kwargs.get("output_path")),
    response_format="content_and_artifact"
)

# Utility Tools
slide_id_to_index_tool = Tool(
    name="slide_id_to_index",
    description="Converts a slide ID to its index in the presentation",
    func=lambda **kwargs: slide_id_to_index(authenticate(), kwargs.get("presentation_id"), 
                                           kwargs.get("slide_id"))
)

index_to_slide_id_tool = Tool(
    name="index_to_slide_id",
    description="Converts a slide index to its ID in the presentation",
    func=lambda **kwargs: index_to_slide_id(authenticate(), kwargs.get("presentation_id"), 
                                           kwargs.get("slide_index"))
)

get_element_id_by_name_tool = Tool(
    name="get_element_id_by_name",
    description="Finds the ID of an element by its name/alt text property",
    func=lambda **kwargs: get_element_id_by_name(authenticate(), kwargs.get("presentation_id"), 
                                                kwargs.get("slide_id"), kwargs.get("element_name"))
)

# Export a dictionary of all LangChain tools for easy access
langchain_tools = {
    # Slides Operations
    "create_presentation": create_presentation_tool,
    "get_presentation": get_presentation_tool,
    "add_slide": add_slide_tool,
    "delete_slide": delete_slide_tool,
    "reorder_slides": reorder_slides_tool,
    "duplicate_slide": duplicate_slide_tool,
    
    # Formatting
    "add_text_to_slide": add_text_to_slide_tool,
    "update_text_style": update_text_style_tool,
    "update_paragraph_style": update_paragraph_style_tool,
    
    # Multimedia
    "add_image_to_slide": add_image_to_slide_tool,
    "add_video_to_slide": add_video_to_slide_tool,
    "insert_audio_link": insert_audio_link_tool,
    "add_shape_to_slide": add_shape_to_slide_tool,
    
    # Data
    "create_sheets_chart": create_sheets_chart_tool,
    "create_table_from_sheets": create_table_from_sheets_tool,
    
    # Templates
    "apply_predefined_layout": apply_predefined_layout_tool,
    "duplicate_presentation": duplicate_presentation_tool,
    "list_available_layouts": list_available_layouts_tool,
    "create_custom_template": create_custom_template_tool,
    
    # Animations
    "set_slide_transition": set_slide_transition_tool,
    "set_element_animation": set_element_animation_tool,
    "apply_auto_advance": apply_auto_advance_tool,
    "set_slide_background": set_slide_background_tool,
    
    # Export
    "export_presentation_as_pdf": export_presentation_as_pdf_tool,
    "export_slide_as_pdf": export_slide_as_pdf_tool,
    "get_presentation_thumbnail": get_presentation_thumbnail_tool,
    
    # Utilities
    "slide_id_to_index": slide_id_to_index_tool,
    "index_to_slide_id": index_to_slide_id_tool,
    "get_element_id_by_name": get_element_id_by_name_tool,
}

# Function to get all LangChain tools as a list
def get_langchain_tools():
    """Returns all Google Slides tools as LangChain tools."""
    return list(langchain_tools.values())
