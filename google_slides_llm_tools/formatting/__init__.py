from ..auth import get_slides_service
from langchain.tools import tool
import time
import os
import tempfile

@tool
def add_text_to_slide(credentials, presentation_id, slide_id, text, x, y, width, height):
    """
    Adds a text box with the specified text to a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        text (str): Text to add to the slide
        x (float): X coordinate (in points) of the text box's top-left corner
        y (float): Y coordinate (in points) of the text box's top-left corner
        width (float): Width of the text box (in points)
        height (float): Height of the text box (in points)
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the specific slide
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the text box
    text_box_id = f'TextBox_{int(time.time())}'
    
    # Create requests to add a text box and insert text
    requests = [
        {
            'createShape': {
                'objectId': text_box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': height, 'unit': 'PT'},
                        'width': {'magnitude': width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
                        'unit': 'PT'
                    }
                }
            }
        },
        {
            'insertText': {
                'objectId': text_box_id,
                'text': text
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Get the slide index
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            slide_index = i
            break
    
    # Export presentation as PDF
    from ..export import export_presentation_as_pdf, export_slide_as_pdf
    presentation_pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, presentation_pdf_path)
    
    # Export the specific slide as PDF if we found its index
    slide_pdf_path = None
    if slide_index is not None:
        slide_pdf_path = os.path.join(tempfile.gettempdir(), f"slide_{presentation_id}_{slide_index}.pdf")
        export_slide_as_pdf(credentials, presentation_id, slide_index, slide_pdf_path)
    
    # Add PDF paths to the response
    response["presentationPdfPath"] = presentation_pdf_path
    if slide_pdf_path:
        response["slidePdfPath"] = slide_pdf_path
    
    return response

@tool
def update_text_style(credentials, presentation_id, shape_id, text_range_start_index, text_range_end_index, 
                      bold=None, italic=None, font_size=None, font_family=None, color=None):
    """
    Updates the style of text within a shape.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        shape_id (str): ID of the shape containing the text
        text_range_start_index (int): Start index of the text range
        text_range_end_index (int): End index of the text range
        bold (bool, optional): Whether the text should be bold
        italic (bool, optional): Whether the text should be italic
        font_size (float, optional): Font size in points
        font_family (str, optional): Font family (e.g., 'Arial')
        color (dict, optional): Text color as an RGB dict (e.g., {'red': 0, 'green': 0, 'blue': 0})
        
    Returns:
        dict: Response from the API with paths to PDFs of the updated presentation and slide
    """
    service = get_slides_service(credentials)
    
    # Build style fields to update
    style = {}
    fields = []
    
    if bold is not None:
        style['bold'] = bold
        fields.append('bold')
        
    if italic is not None:
        style['italic'] = italic
        fields.append('italic')
        
    if font_size is not None:
        style['fontSize'] = {
            'magnitude': font_size,
            'unit': 'PT'
        }
        fields.append('fontSize')
        
    if font_family is not None:
        style['fontFamily'] = font_family
        fields.append('fontFamily')
        
    if color is not None:
        style['foregroundColor'] = {
            'opaqueColor': {
                'rgbColor': color
            }
        }
        fields.append('foregroundColor')
    
    # Create the update request
    requests = [
        {
            'updateTextStyle': {
                'objectId': shape_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': text_range_start_index,
                    'endIndex': text_range_end_index
                },
                'style': style,
                'fields': ','.join(fields)
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Find which slide contains this shape
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        for element in slide.get('pageElements', []):
            if element.get('objectId') == shape_id:
                slide_index = i
                break
        if slide_index is not None:
            break
    
    # Export presentation as PDF
    from ..export import export_presentation_as_pdf, export_slide_as_pdf
    presentation_pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, presentation_pdf_path)
    
    # Export the specific slide as PDF if we found its index
    slide_pdf_path = None
    if slide_index is not None:
        slide_pdf_path = os.path.join(tempfile.gettempdir(), f"slide_{presentation_id}_{slide_index}.pdf")
        export_slide_as_pdf(credentials, presentation_id, slide_index, slide_pdf_path)
    
    # Add PDF paths to the response
    response["presentationPdfPath"] = presentation_pdf_path
    if slide_pdf_path:
        response["slidePdfPath"] = slide_pdf_path
    
    return response

@tool
def update_paragraph_style(credentials, presentation_id, shape_id, start_index, end_index, 
                          alignment=None, line_spacing=None, space_above=None, space_below=None, 
                          indent_start=None, indent_end=None):
    """
    Updates the paragraph style within a shape.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        shape_id (str): ID of the shape containing the text
        start_index (int): Start index of the paragraph
        end_index (int): End index of the paragraph
        alignment (str, optional): Text alignment ('START', 'CENTER', 'END', 'JUSTIFIED')
        line_spacing (float, optional): Line spacing in points
        space_above (float, optional): Space above the paragraph in points
        space_below (float, optional): Space below the paragraph in points
        indent_start (float, optional): Left indent in points
        indent_end (float, optional): Right indent in points
        
    Returns:
        dict: Response from the API with paths to PDFs of the updated presentation and slide
    """
    service = get_slides_service(credentials)
    
    # Build style fields to update
    style = {}
    fields = []
    
    if alignment is not None:
        style['alignment'] = alignment
        fields.append('alignment')
        
    if line_spacing is not None:
        style['lineSpacing'] = line_spacing
        fields.append('lineSpacing')
        
    if space_above is not None:
        style['spaceAbove'] = {
            'magnitude': space_above,
            'unit': 'PT'
        }
        fields.append('spaceAbove')
        
    if space_below is not None:
        style['spaceBelow'] = {
            'magnitude': space_below,
            'unit': 'PT'
        }
        fields.append('spaceBelow')
        
    if indent_start is not None:
        style['indentStart'] = {
            'magnitude': indent_start,
            'unit': 'PT'
        }
        fields.append('indentStart')
        
    if indent_end is not None:
        style['indentEnd'] = {
            'magnitude': indent_end,
            'unit': 'PT'
        }
        fields.append('indentEnd')
    
    # Create the update request
    requests = [
        {
            'updateParagraphStyle': {
                'objectId': shape_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'style': style,
                'fields': ','.join(fields)
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Find which slide contains this shape
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        for element in slide.get('pageElements', []):
            if element.get('objectId') == shape_id:
                slide_index = i
                break
        if slide_index is not None:
            break
    
    # Export presentation as PDF
    from ..export import export_presentation_as_pdf, export_slide_as_pdf
    presentation_pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, presentation_pdf_path)
    
    # Export the specific slide as PDF if we found its index
    slide_pdf_path = None
    if slide_index is not None:
        slide_pdf_path = os.path.join(tempfile.gettempdir(), f"slide_{presentation_id}_{slide_index}.pdf")
        export_slide_as_pdf(credentials, presentation_id, slide_index, slide_pdf_path)
    
    # Add PDF paths to the response
    response["presentationPdfPath"] = presentation_pdf_path
    if slide_pdf_path:
        response["slidePdfPath"] = slide_pdf_path
    
    return response
