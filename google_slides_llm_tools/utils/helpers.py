from google_slides_llm_tools.utils.auth import get_slides_service

def slide_id_to_index(credentials, presentation_id, slide_id):
    """
    Converts a slide ID to its index in the presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        
    Returns:
        int: Zero-based index of the slide in the presentation, or None if not found
    """
    service = get_slides_service(credentials)
    
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            return i
    
    raise ValueError(f"Slide with ID {slide_id} not found in presentation")

def index_to_slide_id(credentials, presentation_id, slide_index):
    """
    Converts a slide index to its ID in the presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_index (int): Zero-based index of the slide in the presentation
        
    Returns:
        str: ID of the slide, or None if the index is invalid
    """
    service = get_slides_service(credentials)
    
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slides = presentation.get('slides', [])
    
    if 0 <= slide_index < len(slides):
        return slides[slide_index]['objectId']
    
    raise ValueError(f"Index {slide_index} out of range. Presentation has {len(slides)} slides.")

def get_element_id_by_name(credentials, presentation_id, slide_id=None, element_name=None):
    """
    Finds the ID of an element by its name/alt text property.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str, optional): ID of the slide, if not provided will search all slides
        element_name (str, optional): Name or alt text of the element to find
                                    If not provided, will use the slide_id parameter as element_name
        
    Returns:
        str: ID of the element, or None if not found
    """
    service = get_slides_service(credentials)
    
    # Handle case where function is called with just 3 parameters
    if element_name is None and slide_id is not None:
        element_name = slide_id
        slide_id = None
    
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    # If no slide_id is provided, search all slides
    if slide_id is None:
        for slide in presentation.get('slides', []):
            # Search for elements in the slide that match the name/content
            for element in slide.get('pageElements', []):
                element_id = element.get('objectId')
                
                # Check shape elements with text
                if 'shape' in element and 'text' in element['shape']:
                    text_content = ""
                    for text_element in element['shape']['text'].get('textElements', []):
                        if 'textRun' in text_element:
                            text_content += text_element['textRun'].get('content', '')
                    
                    if element_name.lower() in text_content.lower():
                        return element_id
                
                # Check if title matches element name
                if element.get('title', '').lower() == element_name.lower():
                    return element_id
        
        return None
    
    # Find the slide
    target_slide = None
    for slide in presentation.get('slides', []):
        if slide.get('objectId') == slide_id:
            target_slide = slide
            break
    
    if not target_slide:
        raise ValueError(f"Slide with ID {slide_id} not found in presentation")
    
    # Search for elements in the slide that match the name/content
    for element in target_slide.get('pageElements', []):
        element_id = element.get('objectId')
        
        # Check shape elements with text
        if 'shape' in element and 'text' in element['shape']:
            text_content = ""
            for text_element in element['shape']['text'].get('textElements', []):
                if 'textRun' in text_element:
                    text_content += text_element['textRun'].get('content', '')
            
            if element_name.lower() in text_content.lower():
                return element_id
        
        # Check if title matches element name
        if element.get('title', '').lower() == element_name.lower():
            return element_id
    
    return None

def rgb_to_hex(r, g, b):
    """
    Converts RGB values (0-1 float) to a hex color code.
    
    Args:
        r (float): Red value (0-1)
        g (float): Green value (0-1)
        b (float): Blue value (0-1)
        
    Returns:
        str: Hex color code (e.g., '#FF0000' for red)
    """
    # Convert 0-1 range to 0-255 integer range
    r_int = int(r * 255) if 0 <= r <= 1 else int(r)
    g_int = int(g * 255) if 0 <= g <= 1 else int(g)
    b_int = int(b * 255) if 0 <= b <= 1 else int(b)
    
    # Ensure values are in valid range
    r_int = max(0, min(255, r_int))
    g_int = max(0, min(255, g_int))
    b_int = max(0, min(255, b_int))
    
    # Convert to hex
    return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

def hex_to_rgb(hex_color):
    """
    Converts a hex color code to RGB values (0-1 float).
    
    Args:
        hex_color (str): Hex color code (e.g., '#FF0000' for red)
        
    Returns:
        dict: RGB values as a dict (e.g., {'red': 1.0, 'green': 0.0, 'blue': 0.0})
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Parse hex values
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    
    # Return in Google Slides API format
    return {
        'red': r,
        'green': g,
        'blue': b
    }

def points_to_emu(points):
    """
    Converts points to EMU (English Metric Units).
    1 point = 12700 EMU
    
    Args:
        points (float): Value in points
        
    Returns:
        int: Value in EMU
    """
    return int(points * 12700)

def emu_to_points(emu):
    """
    Converts EMU (English Metric Units) to points.
    1 EMU = 1/12700 points
    
    Args:
        emu (int): Value in EMU
        
    Returns:
        float: Value in points
    """
    return emu / 12700

def get_page_size(credentials, presentation_id):
    """
    Gets the page size of a presentation in points.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        dict: Dictionary with width and height in points
    """
    service = get_slides_service(credentials)
    
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    page_size = presentation.get('pageSize', {})
    
    # Convert EMU to points if needed
    width_data = page_size.get('width', {})
    height_data = page_size.get('height', {})
    
    width = width_data.get('magnitude', 0)
    height = height_data.get('magnitude', 0)
    
    # Check if units are EMU and convert to points if necessary
    if width_data.get('unit') == 'EMU':
        width = emu_to_points(width)
    
    if height_data.get('unit') == 'EMU':
        height = emu_to_points(height)
    
    return {
        'width': width,
        'height': height
    } 