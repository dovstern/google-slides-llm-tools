from ..auth import get_slides_service
from langchain.tools import tool
import os
import tempfile

@tool
def set_slide_transition(credentials, presentation_id, slide_id, transition_type, duration=1):
    """
    Sets a transition effect for a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        transition_type (str): Type of transition (e.g., 'FADE', 'SLIDE', 'CUBE')
        duration (float, optional): Duration of the transition in seconds
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Create the request to set a slide transition
    requests = [
        {
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'pageTransition': {
                        'type': transition_type,
                        'duration': {
                            'seconds': duration
                        }
                    }
                },
                'fields': 'pageTransition'
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
def set_element_animation(credentials, presentation_id, slide_id, element_id, animation_type, start_time=0, duration=1):
    """
    Sets an animation for a slide element.
    
    Note: The Google Slides API doesn't directly support animations at the element level yet.
    This function is a placeholder for future API capabilities.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide containing the element
        element_id (str): ID of the element to animate
        animation_type (str): Type of animation (e.g., 'FADE_IN', 'FLY_IN')
        start_time (float, optional): Start time of the animation in seconds
        duration (float, optional): Duration of the animation in seconds
        
    Returns:
        dict: Response from the API or a message about the limitation, with paths to PDFs
    """
    # This is a placeholder as the Google Slides API doesn't fully support
    # element-level animations through the API yet
    message = {
        "message": "Element animations are not directly supported by the Google Slides API yet. "
                  "You would need to use the Google Slides UI to add these animations."
    }
    
    # Even though we can't add the animation, we can still provide PDFs for reference
    # Get the slide index
    service = get_slides_service(credentials)
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
    message["presentationPdfPath"] = presentation_pdf_path
    if slide_pdf_path:
        message["slidePdfPath"] = slide_pdf_path
    
    return message

@tool
def apply_auto_advance(credentials, presentation_id, slide_id, auto_advance_time):
    """
    Sets a slide to automatically advance after a specified time.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        auto_advance_time (float): Time in seconds after which the slide should auto-advance
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Create the request to set auto-advance
    requests = [
        {
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'autoAdvanceTime': {
                        'seconds': auto_advance_time
                    }
                },
                'fields': 'autoAdvanceTime'
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
def set_slide_background(credentials, presentation_id, slide_id, color=None, image_url=None):
    """
    Sets a background color or image for a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        color (dict, optional): RGB color for the background (e.g., {'red': 0.9, 'green': 0.9, 'blue': 0.9})
        image_url (str, optional): URL of an image to use as background
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Create the request based on whether we're setting a color or image background
    if color is not None:
        background = {
            'solidFill': {
                'color': {
                    'rgbColor': color
                }
            }
        }
    elif image_url is not None:
        background = {
            'stretchedPictureFill': {
                'contentUrl': image_url
            }
        }
    else:
        error_response = {"error": "Either color or image_url must be provided"}
        return error_response
    
    # Create the request to set background
    requests = [
        {
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'pageBackgroundFill': background
                },
                'fields': 'pageBackgroundFill'
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
