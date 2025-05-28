"""
Utilities package for Google Slides LLM Tools.
Contains authentication, helper functions, and data models.
"""

# Import authentication functions
from .auth import (
    authenticate,
    get_slides_service,
    get_drive_service,
    get_sheets_service
)

# Import helper functions
from .helpers import (
    slide_id_to_index,
    index_to_slide_id,
    get_element_id_by_name,
    rgb_to_hex,
    hex_to_rgb,
    points_to_emu,
    emu_to_points,
    get_page_size
)

# Import data models
from .models import (
    Position,
    RGBColor,
    TextStyle,
    ParagraphStyle
)

__all__ = [
    # Authentication
    'authenticate',
    'get_slides_service',
    'get_drive_service',
    'get_sheets_service',
    
    # Helper functions
    'slide_id_to_index',
    'index_to_slide_id',
    'get_element_id_by_name',
    'rgb_to_hex',
    'hex_to_rgb',
    'points_to_emu',
    'emu_to_points',
    'get_page_size',
    
    # Data models
    'Position',
    'RGBColor',
    'TextStyle',
    'ParagraphStyle'
] 