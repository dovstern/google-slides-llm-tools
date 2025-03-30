from ..auth import get_slides_service
from langchain.tools import tool
import time
import os
import tempfile

@tool
def create_presentation(credentials, title):
    """
    Creates a new Google Slides presentation with the given title.
    
    Args:
        credentials: Authorized Google credentials
        title (str): Title of the new presentation
        
    Returns:
        dict: Contains the presentation ID and a path to the PDF file of the created presentation
    """
    service = get_slides_service(credentials)
    body = {
        'title': title
    }
    presentation = service.presentations().create(body=body).execute()
    presentation_id = presentation['presentationId']
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    return {
        "presentationId": presentation_id,
        "pdfPath": pdf_path
    }

@tool
def get_presentation(credentials, presentation_id):
    """
    Gets information about a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        dict: Presentation information and a path to the PDF file
    """
    service = get_slides_service(credentials)
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    presentation["pdfPath"] = pdf_path
    return presentation

@tool
def add_slide(credentials, presentation_id, layout='TITLE'):
    """
    Adds a new slide to the specified presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        layout (str): Layout of the slide. Options include: 
                      'TITLE', 'TITLE_AND_BODY', 'SECTION_HEADER', etc.
        
    Returns:
        dict: Response containing the ID of the new slide and paths to PDFs of the presentation and the specific slide
    """
    service = get_slides_service(credentials)
    
    requests = [
        {
            'createSlide': {
                'objectId': f'slide_{int(time.time())}',
                'slideLayoutReference': {
                    'predefinedLayout': layout
                }
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Get the new slide ID
    slide_id = response['replies'][0]['createSlide']['objectId']
    
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
def delete_slide(credentials, presentation_id, slide_id):
    """
    Deletes a slide from the presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide to delete
        
    Returns:
        dict: Response from the API and a path to the PDF of the updated presentation
    """
    service = get_slides_service(credentials)
    
    requests = [
        {
            'deleteObject': {
                'objectId': slide_id
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    response["pdfPath"] = pdf_path
    return response

@tool
def reorder_slides(credentials, presentation_id, slide_ids, insertion_index):
    """
    Reorders slides in the presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_ids (list): List of slide IDs to reorder
        insertion_index (int): Index where the slides should be moved to
        
    Returns:
        dict: Response from the API and a path to the PDF of the updated presentation
    """
    service = get_slides_service(credentials)
    
    requests = [
        {
            'updateSlidesPosition': {
                'slideObjectIds': slide_ids,
                'insertionIndex': insertion_index
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    response["pdfPath"] = pdf_path
    return response

@tool
def duplicate_slide(credentials, presentation_id, slide_id, insertion_index=None):
    """
    Duplicates a slide in the presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide to duplicate
        insertion_index (int, optional): Index where to insert the duplicated slide
        
    Returns:
        dict: Response from the API and a path to the PDF of the updated presentation
    """
    service = get_slides_service(credentials)
    
    request = {
        'duplicateObject': {
            'objectId': slide_id
        }
    }
    
    if insertion_index is not None:
        request['duplicateObject']['insertionIndex'] = insertion_index
    
    body = {'requests': [request]}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Export as PDF
    from ..export import export_presentation_as_pdf
    pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, pdf_path)
    
    response["pdfPath"] = pdf_path
    return response
