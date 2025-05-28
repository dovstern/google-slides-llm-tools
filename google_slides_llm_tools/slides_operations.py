"""
Slides operations module for Google Slides LLM Tools.
Provides functionality to create, read, update, and delete slides and presentations.
"""

import os
import tempfile
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union
from googleapiclient.discovery import build
from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from google_slides_llm_tools.utils import get_slides_service, get_drive_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf


@tool(response_format="content_and_artifact")
def create_presentation(
    credentials: Annotated[Any, InjectedToolArg], 
    title: Annotated[str, "Title of the new presentation"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifact) with presentation info and PDF"]:
    """
    Create a new Google Slides presentation.
    """
    slides_service = get_slides_service(credentials)
    drive_service = get_drive_service(credentials)
    
    # Create a new presentation
    presentation = {
        'title': title
    }
    
    presentation = slides_service.presentations().create(body=presentation).execute()
    presentation_id = presentation.get('presentationId')
    
    # Export the presentation as PDF
    content, artifacts = export_presentation_as_pdf(credentials, presentation_id)
    
    return content, artifacts

@tool
def get_presentation(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"]
) -> Annotated[Dict[str, Any], "Presentation metadata"]:
    """
    Get information about a Google Slides presentation.
    """
    slides_service = get_slides_service(credentials)
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    return presentation

@tool(response_format="content_and_artifact")
def add_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    layout: Annotated[str, "Layout type for the new slide"] = "BLANK"
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with slide info and PDFs"]:
    """
    Add a new slide to a Google Slides presentation.
    """
    slides_service = get_slides_service(credentials)
    
    # Get the presentation to find all slide layout IDs
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()
    
    # Find the layout ID that matches the requested layout type
    layout_id = None
    for master in presentation.get('masters', []):
        for layout in master.get('layouts', []):
            if layout.get('layoutProperties', {}).get('displayName') == layout:
                layout_id = layout.get('objectId')
                break
        if layout_id:
            break
    
    # If no matching layout was found, use the first layout available
    if not layout_id and presentation.get('masters', []) and presentation.get('masters', [])[0].get('layouts', []):
        layout_id = presentation.get('masters', [])[0].get('layouts', [])[0].get('objectId')
    
    # Request body for adding a new slide
    requests = [{
        'createSlide': {
            'objectId': f'slide_{layout}',
            'insertionIndex': 1,
            'slideLayoutReference': {
                'layoutId': layout_id
            } if layout_id else {}
        }
    }]
    
    # Execute the request
    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    slide_id = response.get('replies', [{}])[0].get('createSlide', {}).get('objectId')
    
    # Export presentation and slide as PDF
    _, presentation_artifacts = export_presentation_as_pdf(credentials, presentation_id)
    _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, 1)  # New slide is at index 1
    
    content = f"Added new slide with ID {slide_id}"
    artifacts = presentation_artifacts + slide_artifacts
    
    return content, artifacts

@tool(response_format="content_and_artifact")
def delete_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide to delete"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with success status and PDF"]:
    """
    Delete a slide from a Google Slides presentation.
    """
    slides_service = get_slides_service(credentials)
    
    # Request to delete the slide
    requests = [{
        'deleteObject': {
            'objectId': slide_id
        }
    }]
    
    # Execute the request
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    # Export the updated presentation as PDF
    content, artifacts = export_presentation_as_pdf(credentials, presentation_id)
    
    return f"Deleted slide {slide_id}. {content}", artifacts

@tool(response_format="content_and_artifact")
def reorder_slides(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_ids: Annotated[List[str], "List of slide IDs to move"], 
    insertion_index: Annotated[int, "Index to insert the slides at"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with updated slide order and PDF"]:
    """
    Reorder slides in a Google Slides presentation.
    """
    slides_service = get_slides_service(credentials)
    
    # Request to reorder slides
    requests = [{
        'updateSlidesPosition': {
            'slideObjectIds': slide_ids,
            'insertionIndex': insertion_index
        }
    }]
    
    # Execute the request
    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    # Export the updated presentation as PDF
    content, artifacts = export_presentation_as_pdf(credentials, presentation_id)
    
    # Get the updated list of slide IDs in order
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()
    
    updated_slide_ids = [slide.get('objectId') for slide in presentation.get('slides', [])]
    
    return f"Reordered slides. New order: {updated_slide_ids}. {content}", artifacts

@tool(response_format="content_and_artifact")
def duplicate_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide to duplicate"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with new slide info and PDFs"]:
    """
    Duplicate a slide in a Google Slides presentation.
    """
    slides_service = get_slides_service(credentials)
    
    # Get the current slide index
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            slide_index = i
            break
    
    if slide_index is None:
        raise ValueError(f"Slide with ID {slide_id} not found in presentation")
    
    # Create a request to duplicate the slide
    requests = [{
        'duplicateObject': {
            'objectId': slide_id
        }
    }]
    
    # Execute the request
    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    new_slide_id = response.get('replies', [{}])[0].get('duplicateObject', {}).get('objectId')
    
    # Export presentation and the new slide as PDF
    _, presentation_artifacts = export_presentation_as_pdf(credentials, presentation_id)
    
    # Find the index of the new slide
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()
    
    new_slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == new_slide_id:
            new_slide_index = i
            break
    
    slide_artifacts = []
    if new_slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, new_slide_index)
    
    content = f"Duplicated slide {slide_id} to new slide {new_slide_id}"
    artifacts = presentation_artifacts + slide_artifacts
    
    return content, artifacts