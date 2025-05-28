"""
Templates module for Google Slides LLM Tools.
Provides functionality to work with templates in Google Slides.
"""
import os
import tempfile
import time
from typing import Annotated, Any, List, Optional, Dict, Tuple

from google_slides_llm_tools.utils import get_slides_service, get_drive_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
from langchain.tools import tool
from langchain_core.tools import InjectedToolArg

@tool(response_format="content_and_artifact")
def apply_predefined_layout(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    layout_name: Annotated[str, "Name of the layout to apply"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Applies a predefined layout to a slide.
    """
    service = get_slides_service(credentials)
    
    # Get the presentation to find available layouts
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    # Find the layout by name
    layout_id = None
    for layout in presentation.get('layouts', []):
        if layout.get('layoutProperties', {}).get('displayName') == layout_name:
            layout_id = layout.get('objectId')
            break
    
    if not layout_id:
        return f"Layout '{layout_name}' not found", []
    
    # Apply the layout to the slide
    requests = [
        {
            'updateSlideProperties': {
                'objectId': slide_id,
                'slideProperties': {
                    'layoutObjectId': layout_id
                },
                'fields': 'layoutObjectId'
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Get the slide index
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            slide_index = i
            break
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Applied layout '{layout_name}' to slide {slide_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def duplicate_presentation(
    credentials: Annotated[Any, "Authorized Google credentials"], 
    presentation_id: Annotated[str, "ID of the presentation to duplicate"], 
    new_title: Annotated[Optional[str], "Title for the new presentation"] = None
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with new presentation info and PDF"]:
    """
    Duplicates an existing presentation.
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
    
    # Export the new presentation as PDF
    content, artifacts = export_presentation_as_pdf(credentials, copied_presentation['id'])
    
    return f"Duplicated presentation as '{new_title}' with ID {copied_presentation['id']}. {content}", artifacts

@tool
def list_available_layouts(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"]
) -> Annotated[List[Dict[str, str]], "List of available layouts with their IDs and names"]:
    """
    Lists all available layouts in a presentation.
    """
    service = get_slides_service(credentials)
    
    # Get the presentation layouts
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    layouts = []
    for layout in presentation.get('layouts', []):
        layout_info = {
            'id': layout.get('objectId'),
            'name': layout.get('layoutProperties', {}).get('displayName', 'Unnamed Layout')
        }
        layouts.append(layout_info)
    
    return layouts

@tool(response_format="content_and_artifact")
def create_custom_template(
    credentials: Annotated[Any, InjectedToolArg], 
    title: Annotated[str, "Title of the new template presentation"], 
    template_slides: Annotated[List[Dict[str, Any]], "List of slide configurations for the template"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Creates a custom template presentation with specified slide configurations.
    """
    service = get_slides_service(credentials)
    
    # Create a new presentation
    presentation = {
        'title': title
    }
    
    response = service.presentations().create(body=presentation).execute()
    presentation_id = response['presentationId']
    
    # Get the default slide ID to remove it later
    presentation_data = service.presentations().get(
        presentationId=presentation_id).execute()
    default_slide_id = presentation_data['slides'][0]['objectId']
    
    # Create requests for template slides
    requests = []
    
    # Add new slides based on template_slides configuration
    for i, slide_config in enumerate(template_slides):
        slide_id = f'template_slide_{i}'
        requests.append({
            'createSlide': {
                'objectId': slide_id,
                'insertionIndex': i,
                'slideLayoutReference': {
                    'predefinedLayout': slide_config.get('layout', 'BLANK')
                }
            }
        })
        
        # Add any text elements specified in the configuration
        if 'text_elements' in slide_config:
            for text_element in slide_config['text_elements']:
                text_box_id = f'text_{slide_id}_{len(requests)}'
                requests.append({
                    'createShape': {
                        'objectId': text_box_id,
                        'shapeType': 'TEXT_BOX',
                        'elementProperties': {
                            'pageObjectId': slide_id,
                            'size': {
                                'height': {'magnitude': text_element.get('height', 100), 'unit': 'PT'},
                                'width': {'magnitude': text_element.get('width', 400), 'unit': 'PT'},
                            },
                            'transform': {
                                'scaleX': 1,
                                'scaleY': 1,
                                'translateX': text_element.get('x', 100),
                                'translateY': text_element.get('y', 100),
                                'unit': 'PT'
                            }
                        }
                    }
                })
                
                requests.append({
                    'insertText': {
                        'objectId': text_box_id,
                        'text': text_element.get('text', '')
                    }
                })
    
    # Remove the default slide
    requests.append({
        'deleteObject': {
            'objectId': default_slide_id
        }
    })
    
    # Execute all requests
    if requests:
        body = {'requests': requests}
        service.presentations().batchUpdate(
            presentationId=presentation_id, body=body).execute()
    
    # Export the template as PDF
    _, presentation_artifacts = export_presentation_as_pdf(credentials, presentation_id)
    
    content = f"Created custom template '{title}' with {len(template_slides)} slides"
    
    return content, presentation_artifacts 