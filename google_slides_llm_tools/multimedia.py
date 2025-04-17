from google_slides_llm_tools.auth import get_slides_service
import time
import os
import tempfile

def add_image_to_slide(credentials, presentation_id, slide_id, image_url, x, y, width, height):
    """
    Adds an image to a slide from a URL.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        image_url (str): URL of the image to add
        x (float): X coordinate (in points) of the image's top-left corner
        y (float): Y coordinate (in points) of the image's top-left corner
        width (float): Width of the image (in points)
        height (float): Height of the image (in points)
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the image
    image_id = f'Image_{int(time.time())}'
    
    # Create request to add an image
    requests = [
        {
            'createImage': {
                'objectId': image_id,
                'url': image_url,
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

def add_video_to_slide(credentials, presentation_id, slide_id, video_url, x, y, width, height, 
                      auto_play=False, start_time=0, end_time=None, mute=False):
    """
    Embeds a video (e.g., YouTube) into a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        video_url (str): URL of the video to embed (e.g., YouTube link)
        x (float): X coordinate (in points) of the video's top-left corner
        y (float): Y coordinate (in points) of the video's top-left corner
        width (float): Width of the video (in points)
        height (float): Height of the video (in points)
        auto_play (bool, optional): Whether the video should autoplay when the slide is presented
        start_time (int, optional): Start time of the video (in seconds)
        end_time (int, optional): End time of the video (in seconds)
        mute (bool, optional): Whether to mute the video's audio
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the video
    video_id = f'Video_{int(time.time())}'
    
    # Prepare video properties
    video_properties = {
        'autoPlay': auto_play,
        'mute': mute
    }
    
    if start_time is not None:
        video_properties['start'] = start_time
        
    if end_time is not None:
        video_properties['end'] = end_time
    
    # Create request to add a video
    requests = [
        {
            'createVideo': {
                'objectId': video_id,
                'source': 'YOUTUBE',
                'url': video_url,
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
                },
                'videoProperties': video_properties
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

def insert_audio_link(credentials, presentation_id, slide_id, audio_url, x, y, width, height, link_text="Play Audio"):
    """
    Inserts a text box with a hyperlink to an external audio file.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        audio_url (str): URL of the external audio file or streaming service
        x (float): X coordinate (in points) of the text box's top-left corner
        y (float): Y coordinate (in points) of the text box's top-left corner
        width (float): Width of the text box (in points)
        height (float): Height of the text box (in points)
        link_text (str, optional): Text to display in the text box
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the text box
    text_box_id = f'AudioLink_{int(time.time())}'
    
    # Create requests to add a text box with a hyperlink to audio
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
                'text': link_text
            }
        },
        {
            'updateTextStyle': {
                'objectId': text_box_id,
                'textRange': {
                    'type': 'ALL'
                },
                'style': {
                    'link': {
                        'url': audio_url
                    },
                    'underline': True,
                    'foregroundColor': {
                        'opaqueColor': {
                            'rgbColor': {
                                'red': 0,
                                'green': 0,
                                'blue': 0.8
                            }
                        }
                    }
                },
                'fields': 'link,underline,foregroundColor'
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

def add_shape_to_slide(credentials, presentation_id, slide_id, shape_type, x, y, width, height, fill_color=None):
    """
    Adds a shape to a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        shape_type (str): Type of shape (e.g., 'RECTANGLE', 'ELLIPSE', 'ARROW')
        x (float): X coordinate (in points) of the shape's top-left corner
        y (float): Y coordinate (in points) of the shape's top-left corner
        width (float): Width of the shape (in points)
        height (float): Height of the shape (in points)
        fill_color (dict, optional): RGB color for the shape (e.g., {'red': 0.9, 'green': 0.9, 'blue': 0.9})
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the shape
    shape_id = f'Shape_{int(time.time())}'
    
    # Prepare the shape properties
    element_properties = {
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
    
    # Create the request to add a shape
    requests = [
        {
            'createShape': {
                'objectId': shape_id,
                'shapeType': shape_type,
                'elementProperties': element_properties
            }
        }
    ]
    
    # Add fill color if specified
    if fill_color is not None:
        requests.append({
            'updateShapeProperties': {
                'objectId': shape_id,
                'fields': 'shapeBackgroundFill.solidFill.color',
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': fill_color
                            }
                        }
                    }
                }
            }
        })
    
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