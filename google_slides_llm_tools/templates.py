from google_slides_llm_tools.auth import get_slides_service, get_drive_service
from langchain.tools import tool
import os
import tempfile
import time

@tool
def apply_predefined_layout(credentials, presentation_id, slide_id, layout_name):
    """
    Applies a predefined layout to a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        layout_name (str): Name of the predefined layout (e.g., 'TITLE', 'TITLE_AND_BODY')
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and slide
    """
    service = get_slides_service(credentials)
    
    # Create request to apply layout
    requests = [
        {
            'updateSlideProperties': {
                'objectId': slide_id,
                'slideProperties': {
                    'layoutObjectId': layout_name
                },
                'fields': 'layoutObjectId'
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

@tool
def duplicate_presentation(credentials, presentation_id, new_title=None):
    """
    Duplicates an existing presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation to duplicate
        new_title (str, optional): Title for the new presentation
        
    Returns:
        dict: Information about the new presentation, including ID and PDF path
    """
    drive_service = get_drive_service(credentials)
    
    # Get the original presentation's metadata
    original = drive_service.files().get(
        fileId=presentation_id, fields='name').execute()
    
    # Set the new title
    if new_title is None:
        new_title = f"Copy of {original['name']}"
    
    # Create a copy of the presentation
    body = {
        'name': new_title
    }
    
    copied_presentation = drive_service.files().copy(
        fileId=presentation_id, body=body).execute()
    
    # Export as PDF
    from google_slides_llm_tools.export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{copied_presentation['id']}.pdf")
    export_presentation_as_pdf(credentials, copied_presentation['id'], pdf_path)
    
    # Return information about the new presentation
    result = {
        "presentationId": copied_presentation['id'],
        "title": new_title,
        "pdfPath": pdf_path
    }
    
    return result

@tool
def list_available_layouts(credentials, presentation_id):
    """
    Lists all available layouts in a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        list: Available layouts in the presentation
    """
    service = get_slides_service(credentials)
    
    # Get the presentation
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    # Extract available layouts
    layouts = []
    if 'layouts' in presentation:
        for layout in presentation['layouts']:
            layouts.append({
                'objectId': layout['objectId'],
                'layoutProperties': layout.get('layoutProperties', {})
            })
    
    return layouts

@tool
def create_custom_template(credentials, title, slide_layouts=None):
    """
    Creates a new presentation to be used as a custom template.
    
    Args:
        credentials: Authorized Google credentials
        title (str): Title of the template
        slide_layouts (list, optional): List of slide layout configurations to add
        
    Returns:
        dict: Information about the new template, including ID and PDF path
    """
    service = get_slides_service(credentials)
    
    # Create a new presentation
    body = {
        'title': title
    }
    presentation = service.presentations().create(body=body).execute()
    presentation_id = presentation['presentationId']
    
    # Add custom slide layouts if provided
    if slide_layouts:
        requests = []
        for layout in slide_layouts:
            # Example: layout = {'layoutId': 'customLayout1', 'name': 'My Custom Layout'}
            requests.append({
                'createSlide': {
                    'objectId': layout.get('layoutId', f'custom_{int(time.time())}'),
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    },
                    'insertionIndex': 0
                }
            })
        
        if requests:
            body = {'requests': requests}
            service.presentations().batchUpdate(
                presentationId=presentation_id, body=body).execute()
    
    # Export as PDF
    from google_slides_llm_tools.export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    # Return information about the new template
    result = {
        "presentationId": presentation_id,
        "title": title,
        "pdfPath": pdf_path
    }
    
    return result 