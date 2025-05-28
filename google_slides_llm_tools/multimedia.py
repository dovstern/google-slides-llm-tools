"""
Multimedia module for Google Slides LLM Tools.
Provides functionality for adding multimedia elements to slides.
"""
import os
import tempfile
import uuid
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union

from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from google_slides_llm_tools.utils import get_slides_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
from google_slides_llm_tools.utils import Position, RGBColor

@tool(response_format="content_and_artifact")
def add_image_to_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    image_url: Annotated[str, "URL of the image to add"], 
    position: Annotated[Position, "Position and size of the image with x, y coordinates and width, height"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Adds an image to a slide from a URL.
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
                        'height': {'magnitude': position.height, 'unit': 'PT'},
                        'width': {'magnitude': position.width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': position.x,
                        'translateY': position.y,
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
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Added image from {image_url} to slide {slide_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def add_video_to_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    video_url: Annotated[str, "URL of the video to embed (e.g., YouTube link)"], 
    position: Annotated[Position, "Position and size of the video with x, y coordinates and width, height"], 
    auto_play: Annotated[bool, "Whether the video should autoplay when the slide is presented"] = False, 
    start_time: Annotated[int, "Start time of the video (in seconds)"] = 0, 
    end_time: Annotated[Optional[int], "End time of the video (in seconds)"] = None, 
    mute: Annotated[bool, "Whether to mute the video's audio"] = False
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Embeds a video (e.g., YouTube) into a slide.
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
                        'height': {'magnitude': position.height, 'unit': 'PT'},
                        'width': {'magnitude': position.width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': position.x,
                        'translateY': position.y,
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
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Added video from {video_url} to slide {slide_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def insert_audio_link(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    audio_url: Annotated[str, "URL of the external audio file or streaming service"], 
    position: Annotated[Position, "Position and size of the text box with x, y coordinates and width, height"], 
    link_text: Annotated[str, "Text to display in the text box"] = "Play Audio"
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Inserts a text box with a hyperlink to an external audio file.
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
                        'height': {'magnitude': position.height, 'unit': 'PT'},
                        'width': {'magnitude': position.width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': position.x,
                        'translateY': position.y,
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
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Added audio link '{link_text}' to slide {slide_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def add_shape_to_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    shape_type: Annotated[str, "Type of shape (e.g., 'RECTANGLE', 'ELLIPSE', 'ARROW')"], 
    position: Annotated[Position, "Position and size of the shape with x, y coordinates and width, height"], 
    fill_color: Annotated[Optional[RGBColor], "RGB color for the shape"] = None
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Adds a shape to a slide.
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the shape
    shape_id = f'Shape_{int(time.time())}'
    
    # Prepare the shape properties
    element_properties = {
        'pageObjectId': slide_id,
        'size': {
            'height': {'magnitude': position.height, 'unit': 'PT'},
            'width': {'magnitude': position.width, 'unit': 'PT'},
        },
        'transform': {
            'scaleX': 1,
            'scaleY': 1,
            'translateX': position.x,
            'translateY': position.y,
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
                                'rgbColor': {
                                    'red': fill_color.red,
                                    'green': fill_color.green,
                                    'blue': fill_color.blue
                                }
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
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Added {shape_type} shape to slide {slide_id}"
    
    return content, slide_artifacts

@tool
def create_shape(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    shape_type: Annotated[str, "Type of shape (e.g., 'RECTANGLE', 'ELLIPSE', 'ARROW')"], 
    position: Annotated[Position, "Position and size of the shape with x, y coordinates and width, height"], 
    fill_color: Annotated[Optional[RGBColor], "RGB color for the shape"] = None
) -> Annotated[Dict[str, str], "Response containing the objectId of the new shape"]:
    """
    Creates a shape on a slide.
    """
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the shape
    shape_id = f'Shape_{int(time.time())}'
    
    # Prepare the shape properties
    element_properties = {
        'pageObjectId': slide_id,
        'size': {
            'height': {'magnitude': position.height, 'unit': 'PT'},
            'width': {'magnitude': position.width, 'unit': 'PT'},
        },
        'transform': {
            'scaleX': 1,
            'scaleY': 1,
            'translateX': position.x,
            'translateY': position.y,
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
                                'rgbColor': {
                                    'red': fill_color.red,
                                    'green': fill_color.green,
                                    'blue': fill_color.blue
                                }
                            }
                        }
                    }
                }
            }
        })
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Extract the objectId from the response
    object_id = response.get('replies', [{}])[0].get('createShape', {}).get('objectId')
    
    return {
        "objectId": object_id
    }

@tool
def group_elements(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    element_ids: Annotated[List[str], "List of element IDs to group"]
) -> Annotated[Dict[str, str], "Response containing the groupId of the new group"]:
    """
    Groups multiple elements on a slide.
    """
    service = get_slides_service(credentials)
    
    # Create the request to group elements
    requests = [
        {
            'createGroup': {
                'childrenObjectIds': element_ids,
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Extract the groupId from the response
    group_id = response.get('replies', [{}])[0].get('createGroup', {}).get('objectId')
    
    return {
        "groupId": group_id
    }

@tool
def ungroup_elements(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    group_id: Annotated[str, "ID of the group to ungroup"]
) -> Annotated[Dict, "Empty dict on success"]:
    """
    Ungroups elements in a group.
    """
    service = get_slides_service(credentials)
    
    # Create the request to ungroup elements
    requests = [
        {
            'ungroupObjects': {
                'objectIds': [group_id],
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Return empty dict on success
    return {} 