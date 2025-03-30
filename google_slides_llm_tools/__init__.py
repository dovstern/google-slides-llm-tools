"""
Google Slides LLM Tools

A Python package providing tools for LLMs to interact with Google Slides.
This package integrates with LangChain and provides a comprehensive set of tools
for creating and manipulating Google Slides presentations.
"""

__version__ = '0.1.0'

# Auth module
from .auth import authenticate, get_slides_service, get_drive_service, get_sheets_service

# Slides operations
from .slides import (
    create_presentation,
    get_presentation,
    add_slide,
    delete_slide,
    reorder_slides,
    duplicate_slide
)

# Text formatting
from .formatting import (
    add_text_to_slide,
    update_text_style,
    update_paragraph_style
)

# Multimedia management
from .multimedia import (
    add_image_to_slide,
    add_video_to_slide,
    insert_audio_link,
    add_shape_to_slide
)

# External data integration
from .data import (
    create_sheets_chart,
    create_table_from_sheets
)

# Templates and layouts
from .templates import (
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template
)

# Collaboration and sharing
from .collaboration import (
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
)

# Animations and transitions
from .animations import (
    set_slide_transition,
    set_element_animation,
    apply_auto_advance,
    set_slide_background
)

# Export functions
from .export import (
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail
)

# Utility functions
from .utils import (
    slide_id_to_index,
    index_to_slide_id,
    get_element_id_by_name,
    rgb_to_hex,
    hex_to_rgb,
    points_to_emu,
    emu_to_points,
    get_page_size
)
