from ..auth import get_slides_service, get_drive_service
from langchain.tools import tool
import os
import tempfile

@tool
def apply_predefined_layout(credentials, presentation_id, slide_id, layout):
    """
    Applies a predefined layout to a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide to which the layout will be applied
        layout (str): The predefined layout to apply (e.g., 'TITLE_AND_BODY')
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    requests = [
        {
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'layoutProperties': {
                        'predefinedLayout': layout
                    }
                },
                'fields': 'layoutProperties.predefinedLayout'
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
def duplicate_presentation(credentials, template_id, new_title):
    """
    Duplicates a presentation from a template.
    
    Args:
        credentials: Authorized Google credentials
        template_id (str): ID of the template presentation
        new_title (str): Title for the new presentation
        
    Returns:
        dict: Contains the ID of the new presentation and a path to its PDF
    """
    drive_service = get_drive_service(credentials)
    
    body = {
        'name': new_title
    }
    
    # Copy the template presentation
    new_presentation = drive_service.files().copy(
        fileId=template_id, body=body).execute()
    
    new_presentation_id = new_presentation['id']
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{new_presentation_id}.pdf")
    export_presentation_as_pdf(credentials, new_presentation_id, pdf_path)
    
    return {
        "presentationId": new_presentation_id,
        "pdfPath": pdf_path
    }

@tool
def list_available_layouts(credentials, presentation_id):
    """
    Lists all available slide layouts in a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        dict: Available slide layouts and a path to the PDF of the presentation
    """
    service = get_slides_service(credentials)
    
    # Get the presentation
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    # Get the list of layouts from the masters
    layouts = []
    for master in presentation.get('masters', []):
        for layout in master.get('layouts', []):
            layout_info = {
                'layoutId': layout['objectId'],
                'layoutName': layout.get('layoutProperties', {}).get('displayName', 'Unknown Layout'),
                'predefinedLayout': layout.get('layoutProperties', {}).get('name', 'BLANK')
            }
            layouts.append(layout_info)
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    return {
        "layouts": layouts,
        "pdfPath": pdf_path
    }

@tool
def create_custom_template(credentials, presentation_id, template_name, description=None):
    """
    Saves a presentation as a template for future use.
    
    This function doesn't actually create a template in the Google Slides API sense
    (as the API doesn't natively support templates), but it creates a copy of the
    presentation and labels it as a template in Google Drive.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation to use as a template
        template_name (str): Name for the template
        description (str, optional): Description of the template
        
    Returns:
        dict: Contains the ID of the template presentation and a path to its PDF
    """
    drive_service = get_drive_service(credentials)
    
    # Create properties for the template
    body = {
        'name': template_name,
        'properties': {},
        'appProperties': {
            'isTemplate': 'true'
        }
    }
    
    if description:
        body['description'] = description
    
    # Copy the presentation as a template
    template = drive_service.files().copy(
        fileId=presentation_id, body=body).execute()
    
    template_id = template['id']
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"template_{template_id}.pdf")
    export_presentation_as_pdf(credentials, template_id, pdf_path)
    
    return {
        "templateId": template_id,
        "pdfPath": pdf_path
    }
