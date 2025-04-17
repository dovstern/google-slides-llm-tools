from google_slides_llm_tools.auth import get_slides_service
import time
import os
import tempfile

def set_slide_transition(credentials, presentation_id, slide_id, transition_type="FADE", duration_ms=500):
    """
    Sets the transition effect for a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        transition_type (str, optional): Type of transition effect. Options include: 
            'FADE', 'SLIDE', 'WIPE', 'CHECKERBOARD', etc.
        duration_ms (int, optional): Duration of the transition in milliseconds
        
    Returns:
        dict: Response from the API
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
                            'milliseconds': duration_ms
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

def set_element_animation(credentials, presentation_id, slide_id, element_id, animation_type, 
                         start_on="ON_CLICK", duration_ms=500, order=None):
    """
    Adds an animation effect to an element on a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        element_id (str): ID of the element to animate
        animation_type (str): Type of animation effect. Options include:
            'APPEAR', 'FADE_IN', 'FLY_IN', etc.
        start_on (str, optional): Trigger for the animation. Options:
            'ON_CLICK', 'WITH_PREVIOUS', 'AFTER_PREVIOUS'
        duration_ms (int, optional): Duration of the animation in milliseconds
        order (int, optional): Order of the animation in the sequence
        
    Returns:
        dict: Response from the API
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
    from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
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

def apply_auto_advance(credentials, presentation_id, slide_id, auto_advance_after_ms):
    """
    Sets a slide to automatically advance after a specified time.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        auto_advance_after_ms (int): Time in milliseconds after which to advance to the next slide
        
    Returns:
        dict: Response from the API
    """
    service = get_slides_service(credentials)
    
    # Create the request to set auto-advance
    requests = [
        {
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'autoAdvanceTime': {
                        'milliseconds': auto_advance_after_ms
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

def set_slide_background(credentials, presentation_id, slide_id, background_type, background_value):
    """
    Sets the background for a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        background_type (str): Type of background ('SOLID', 'GRADIENT', or 'IMAGE')
        background_value: Value for the background, depends on type:
            - For 'SOLID': RGB color (e.g., {'red': 0.9, 'green': 0.9, 'blue': 0.9})
            - For 'GRADIENT': Dict with start and end colors and angle (e.g., 
              {'startColor': {'red': 1, 'green': 0, 'blue': 0}, 
               'endColor': {'red': 0, 'green': 0, 'blue': 1}, 
               'angle': 45})
            - For 'IMAGE': URL of the image
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Create the request based on whether we're setting a color or image background
    if background_type == 'SOLID':
        background = {
            'solidFill': {
                'color': background_value
            }
        }
    elif background_type == 'GRADIENT':
        background = {
            'gradientFill': {
                'startColor': background_value['startColor'],
                'endColor': background_value['endColor'],
                'angle': background_value['angle']
            }
        }
    elif background_type == 'IMAGE':
        background = {
            'stretchedPictureFill': {
                'contentUrl': background_value
            }
        }
    else:
        error_response = {"error": "Invalid background type"}
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