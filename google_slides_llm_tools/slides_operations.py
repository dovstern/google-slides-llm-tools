"""
Slides operations module for Google Slides LLM Tools.
Provides core functionality for creating and manipulating Google Slides presentations.
"""

import tempfile
import os
from googleapiclient.discovery import build
from google_slides_llm_tools.auth import get_slides_service, get_drive_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf

def create_presentation(credentials, title):
    """
    Create a new Google Slides presentation.
    
    Args:
        credentials: Google credentials object.
        title (str): Title of the new presentation.
        
    Returns:
        dict: Dictionary containing the presentation ID and PDF path.
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
    pdf_path = export_presentation_as_pdf(credentials, presentation_id)
    
    return {
        'presentationId': presentation_id,
        'pdfPath': pdf_path
    }

def get_presentation(credentials, presentation_id):
    """
    Get information about a Google Slides presentation.
    
    Args:
        credentials: Google credentials object.
        presentation_id (str): ID of the presentation.
        
    Returns:
        dict: Presentation metadata.
    """
    slides_service = get_slides_service(credentials)
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    return presentation

def add_slide(credentials, presentation_id, layout="BLANK"):
    """
    Add a new slide to a Google Slides presentation.
    
    Args:
        credentials: Google credentials object.
        presentation_id (str): ID of the presentation.
        layout (str): Layout type for the new slide.
        
    Returns:
        dict: Dictionary containing the slide ID and PDF paths.
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
    presentation_pdf = export_presentation_as_pdf(credentials, presentation_id)
    slide_pdf = export_slide_as_pdf(credentials, presentation_id, 1)  # New slide is at index 1
    
    return {
        'slideId': slide_id,
        'presentationPdfPath': presentation_pdf,
        'slidePdfPath': slide_pdf
    }

def delete_slide(credentials, presentation_id, slide_id):
    """
    Delete a slide from a Google Slides presentation.
    
    Args:
        credentials: Google credentials object.
        presentation_id (str): ID of the presentation.
        slide_id (str): ID of the slide to delete.
        
    Returns:
        dict: Dictionary containing success status and PDF path.
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
    pdf_path = export_presentation_as_pdf(credentials, presentation_id)
    
    return {
        'success': True,
        'pdfPath': pdf_path
    }

def reorder_slides(credentials, presentation_id, slide_ids, insertion_index):
    """
    Reorder slides in a Google Slides presentation.
    
    Args:
        credentials: Google credentials object.
        presentation_id (str): ID of the presentation.
        slide_ids (list): List of slide IDs to reorder.
        insertion_index (int): Index where to insert the slides.
        
    Returns:
        dict: Dictionary containing success status and slide IDs.
    """
    slides_service = get_slides_service(credentials)
    
    # Create requests for each slide to be moved
    requests = []
    for slide_id in slide_ids:
        requests.append({
            'updateSlidesPosition': {
                'slideObjectIds': [slide_id],
                'insertionIndex': insertion_index
            }
        })
    
    # Execute the request
    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    # Export the updated presentation as PDF
    pdf_path = export_presentation_as_pdf(credentials, presentation_id)
    
    return {
        'success': True,
        'slideIds': slide_ids,
        'pdfPath': pdf_path
    }

def duplicate_slide(credentials, presentation_id, slide_id):
    """
    Duplicate a slide in a Google Slides presentation.
    
    Args:
        credentials: Google credentials object.
        presentation_id (str): ID of the presentation.
        slide_id (str): ID of the slide to duplicate.
        
    Returns:
        dict: Dictionary containing the new slide ID and PDF paths.
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
    presentation_pdf = export_presentation_as_pdf(credentials, presentation_id)
    
    # Find the index of the new slide
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()
    
    new_slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == new_slide_id:
            new_slide_index = i
            break
    
    slide_pdf = None
    if new_slide_index is not None:
        slide_pdf = export_slide_as_pdf(credentials, presentation_id, new_slide_index)
    
    return {
        'slideId': new_slide_id,
        'presentationPdfPath': presentation_pdf,
        'slidePdfPath': slide_pdf
    }