from google_slides_llm_tools.auth import get_slides_service
import time
import os
import tempfile

def add_text_to_slide(credentials, presentation_id, slide_id, text, position=None):
    """
    Adds text to a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        text (str): Text content to add
        position (dict, optional): Position and size of the text box. Format:
            {
                'x': float, # X coordinate (in points) of the text box's top-left corner
                'y': float, # Y coordinate (in points) of the text box's top-left corner
                'width': float, # Width of the text box (in points)
                'height': float # Height of the text box (in points)
            }
            If None, a default text box will be created
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
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
                        'height': {'magnitude': position['height'], 'unit': 'PT'},
                        'width': {'magnitude': position['width'], 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': position['x'],
                        'translateY': position['y'],
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
    from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
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

def update_text_style(credentials, presentation_id, slide_object_id, text_style):
    """
    Updates the style of text in a text box or shape.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_object_id (str): ID of the text box or shape containing the text
        text_style (dict): Style to apply to the text. Format:
            {
                'fontFamily': str, # e.g., 'Arial'
                'fontSize': int, # Point size
                'bold': bool,
                'italic': bool,
                'underline': bool,
                'foregroundColor': dict, # RGB color for the text (e.g., {'red': 0, 'green': 0, 'blue': 0})
                'backgroundColor': dict # RGB color for highlighting (e.g., {'red': 1, 'green': 1, 'blue': 0})
            }
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Build style fields to update
    style = {}
    fields = []
    
    if text_style['bold']:
        style['bold'] = True
        fields.append('bold')
        
    if text_style['italic']:
        style['italic'] = True
        fields.append('italic')
        
    if text_style['fontSize']:
        style['fontSize'] = {
            'magnitude': text_style['fontSize'],
            'unit': 'PT'
        }
        fields.append('fontSize')
        
    if text_style['fontFamily']:
        style['fontFamily'] = text_style['fontFamily']
        fields.append('fontFamily')
        
    if text_style['foregroundColor']:
        style['foregroundColor'] = {
            'opaqueColor': {
                'rgbColor': text_style['foregroundColor']
            }
        }
        fields.append('foregroundColor')
    
    # Create the update request
    requests = [
        {
            'updateTextStyle': {
                'objectId': slide_object_id,
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
            if element.get('objectId') == slide_object_id:
                slide_index = i
                break
        if slide_index is not None:
            break
    
    # Export presentation as PDF
    from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
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

def update_paragraph_style(credentials, presentation_id, slide_object_id, paragraph_style):
    """
    Updates the paragraph style in a text box or shape.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_object_id (str): ID of the text box or shape containing the text
        paragraph_style (dict): Style to apply to the paragraph. Format:
            {
                'alignment': str, # 'START', 'CENTER', 'END', or 'JUSTIFIED'
                'lineSpacing': int, # In percentage (e.g., 150 for 1.5 line spacing)
                'spaceAbove': float, # Space above in points
                'spaceBelow': float, # Space below in points
                'indentFirstLine': float, # First line indent in points
                'indentStart': float, # Left indent in points
                'indentEnd': float, # Right indent in points
                'direction': str, # 'LEFT_TO_RIGHT', 'RIGHT_TO_LEFT'
                'spacingMode': str # 'NEVER_COLLAPSE' or 'COLLAPSE_LISTS'
            }
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Build style fields to update
    style = {}
    fields = []
    
    if paragraph_style['alignment']:
        style['alignment'] = paragraph_style['alignment']
        fields.append('alignment')
        
    if paragraph_style['lineSpacing']:
        style['lineSpacing'] = {
            'magnitude': paragraph_style['lineSpacing'],
            'unit': 'PERCENT'
        }
        fields.append('lineSpacing')
        
    if paragraph_style['spaceAbove']:
        style['spaceAbove'] = {
            'magnitude': paragraph_style['spaceAbove'],
            'unit': 'PT'
        }
        fields.append('spaceAbove')
        
    if paragraph_style['spaceBelow']:
        style['spaceBelow'] = {
            'magnitude': paragraph_style['spaceBelow'],
            'unit': 'PT'
        }
        fields.append('spaceBelow')
        
    if paragraph_style['indentFirstLine']:
        style['indentFirstLine'] = {
            'magnitude': paragraph_style['indentFirstLine'],
            'unit': 'PT'
        }
        fields.append('indentFirstLine')
        
    if paragraph_style['indentStart']:
        style['indentStart'] = {
            'magnitude': paragraph_style['indentStart'],
            'unit': 'PT'
        }
        fields.append('indentStart')
        
    if paragraph_style['indentEnd']:
        style['indentEnd'] = {
            'magnitude': paragraph_style['indentEnd'],
            'unit': 'PT'
        }
        fields.append('indentEnd')
    
    # Create the update request
    requests = [
        {
            'updateParagraphStyle': {
                'objectId': slide_object_id,
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
            if element.get('objectId') == slide_object_id:
                slide_index = i
                break
        if slide_index is not None:
            break
    
    # Export presentation as PDF
    from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
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