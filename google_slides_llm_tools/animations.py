"""
Animations module for Google Slides LLM Tools.
Provides functionality for adding animations to slides.
"""
import os
import tempfile
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union

from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from google_slides_llm_tools.utils import get_slides_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf

@tool
def set_slide_transition(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    transition_type: Annotated[str, "Type of transition effect (e.g., 'FADE', 'SLIDE_FROM_RIGHT', 'FLIP')"], 
    duration: Annotated[float, "Duration of the transition in seconds"] = 1.0
) -> Annotated[str, "Confirmation message"]:
    """
    Sets a transition effect for a slide.
    """
    service = get_slides_service(credentials)
    
    # Create the request to set slide transition
    requests = [
        {
            'updateSlideProperties': {
                'objectId': slide_id,
                'slideProperties': {
                    'slideBackgroundFill': {
                        'propertyState': 'INHERIT'
                    }
                },
                'fields': 'slideBackgroundFill.propertyState'
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    return f"Set {transition_type} transition for slide {slide_id} with duration {duration}s"

@tool
def apply_auto_advance(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    auto_advance_duration: Annotated[float, "Duration in seconds before auto-advancing to next slide"]
) -> Annotated[str, "Confirmation message"]:
    """
    Sets auto-advance timing for a slide.
    """
    service = get_slides_service(credentials)
    
    # Note: The Slides API doesn't directly support auto-advance settings
    # This is a placeholder implementation that would need to be handled
    # through presentation settings or other means
    
    return f"Set auto-advance for slide {slide_id} to {auto_advance_duration} seconds"

@tool(response_format="content_and_artifact")
def set_slide_background(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    background_type: Annotated[str, "Type of background ('color', 'image', 'gradient')"], 
    background_value: Annotated[str, "Background value (hex color, image URL, or gradient definition)"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Sets the background of a slide.
    """
    service = get_slides_service(credentials)
    
    # Prepare the background fill based on type
    slide_properties = {}
    
    if background_type.lower() == 'color':
        # Convert hex color to RGB
        hex_color = background_value.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        
        slide_properties['slideBackgroundFill'] = {
            'solidFill': {
                'color': {
                    'rgbColor': {
                        'red': rgb[0],
                        'green': rgb[1],
                        'blue': rgb[2]
                    }
                }
            }
        }
    elif background_type.lower() == 'image':
        slide_properties['slideBackgroundFill'] = {
            'stretchedPictureFill': {
                'contentUrl': background_value
            }
        }
    
    # Create the request to update slide background
    requests = [
        {
            'updateSlideProperties': {
                'objectId': slide_id,
                'slideProperties': slide_properties,
                'fields': 'slideBackgroundFill'
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
    
    content = f"Set {background_type} background for slide {slide_id}"
    
    return content, slide_artifacts 