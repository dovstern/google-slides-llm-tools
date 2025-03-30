import re

def slide_id_to_index(presentation, slide_id):
    """
    Convert a slide ID to its index in the presentation.
    
    Args:
        presentation (dict): The presentation object
        slide_id (str): ID of the slide
        
    Returns:
        int: Index of the slide (0-based)
    """
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            return i
    raise ValueError(f"Slide with ID {slide_id} not found in the presentation")

def index_to_slide_id(presentation, index):
    """
    Convert a slide index to its ID in the presentation.
    
    Args:
        presentation (dict): The presentation object
        index (int): Index of the slide (0-based)
        
    Returns:
        str: ID of the slide
    """
    slides = presentation.get('slides', [])
    if index < 0 or index >= len(slides):
        raise ValueError(f"Slide index {index} is out of range. The presentation has {len(slides)} slides.")
    return slides[index].get('objectId')

def get_element_id_by_name(presentation, element_name_pattern):
    """
    Find an element ID by matching its name or content against a pattern.
    
    Args:
        presentation (dict): The presentation object
        element_name_pattern (str): Regular expression pattern to match element names or content
        
    Returns:
        str: ID of the first matching element, or None if no match found
    """
    pattern = re.compile(element_name_pattern)
    
    # Search in each slide for matching elements
    for slide in presentation.get('slides', []):
        # Check shapes (which can contain text)
        for element in slide.get('pageElements', []):
            # Check element title or description if available
            title = element.get('title', '')
            description = element.get('description', '')
            
            if pattern.search(title) or pattern.search(description):
                return element.get('objectId')
            
            # Check text content in shapes
            shape = element.get('shape', {})
            text = shape.get('text', {})
            text_content = ''
            
            # Extract text from all textElements
            for text_element in text.get('textElements', []):
                if 'textRun' in text_element:
                    text_content += text_element['textRun'].get('content', '')
            
            if pattern.search(text_content):
                return element.get('objectId')
    
    return None

def rgb_to_hex(rgb_dict):
    """
    Convert an RGB dictionary to a hex color string.
    
    Args:
        rgb_dict (dict): Dictionary with 'red', 'green', 'blue' keys (values in range 0-1)
        
    Returns:
        str: Hex color string (e.g., '#FF0000' for red)
    """
    r = int(rgb_dict.get('red', 0) * 255)
    g = int(rgb_dict.get('green', 0) * 255)
    b = int(rgb_dict.get('blue', 0) * 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def hex_to_rgb(hex_color):
    """
    Convert a hex color string to an RGB dictionary.
    
    Args:
        hex_color (str): Hex color string (e.g., '#FF0000' for red)
        
    Returns:
        dict: Dictionary with 'red', 'green', 'blue' keys (values in range 0-1)
    """
    # Remove '#' if present
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    # Convert hex to RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    return {'red': r, 'green': g, 'blue': b}

def points_to_emu(points):
    """
    Convert points to EMUs (English Metric Units).
    
    Args:
        points (float): Value in points
        
    Returns:
        float: Value in EMUs
    """
    return points * 12700  # 1 point = 12700 EMUs

def emu_to_points(emu):
    """
    Convert EMUs (English Metric Units) to points.
    
    Args:
        emu (float): Value in EMUs
        
    Returns:
        float: Value in points
    """
    return emu / 12700  # 1 point = 12700 EMUs

def get_page_size(presentation):
    """
    Get the page size of a presentation.
    
    Args:
        presentation (dict): The presentation object
        
    Returns:
        dict: Dictionary with 'width' and 'height' in points
    """
    page = presentation.get('pageSize', {})
    width = page.get('width', {})
    height = page.get('height', {})
    
    width_value = width.get('magnitude', 0)
    height_value = height.get('magnitude', 0)
    
    # Convert to points if in EMUs
    if width.get('unit', '') == 'EMU':
        width_value = emu_to_points(width_value)
    
    if height.get('unit', '') == 'EMU':
        height_value = emu_to_points(height_value)
    
    return {'width': width_value, 'height': height_value}
