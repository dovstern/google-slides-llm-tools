"""
Export module for Google Slides LLM Tools.
Provides functionality to export presentations and slides as PDFs and images.
"""

import os
import tempfile
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union

from google_slides_llm_tools.utils import get_drive_service, get_slides_service
import base64
from googleapiclient.http import MediaIoBaseDownload
import uuid
import requests
from langchain.tools import tool
from langchain_core.tools import InjectedToolArg

@tool(response_format="content_and_artifact")
def export_presentation_as_pdf(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation to export"], 
    output_path: Annotated[Optional[str], "Path to save the exported PDF"] = None
) -> Annotated[Tuple[str, Union[str, List[Dict[str, Any]]]], "Tuple of (content message, artifact) where artifact is PDF data URL or file path"]:
    """
    Exports a Google Slides presentation as a PDF file.
    """
    drive_service = get_drive_service(credentials)
    
    # Export the presentation as PDF
    request = drive_service.files().export_media(
        fileId=presentation_id,
        mimeType='application/pdf'
    )
    
    # Get PDF content
    pdf_content = request.execute()
    
    # If output path is provided, save to file
    if output_path:
        with open(output_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)
        content = f"Presentation exported as PDF to {output_path}"
        return content, output_path
    
    # Otherwise, encode as base64 and return as data URL
    base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
    data_url = f"data:application/pdf;base64,{base64_pdf}"
    content = "Presentation exported as PDF"
    
    # Return in the format expected by LangChain tools with content_and_artifact
    artifact = {
        "type": "file",
        "file": {
            "filename": f"presentation_{presentation_id}.pdf",
            "file_data": data_url,
        }
    }
    return content, [artifact]

@tool(response_format="content_and_artifact")
def export_slide_as_pdf(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the original presentation"], 
    slide_index: Annotated[int, "Index of the slide to export (0-based)"], 
    output_path: Annotated[Optional[str], "Path to save the exported PDF"] = None
) -> Annotated[Tuple[str, Union[str, List[Dict[str, Any]]]], "Tuple of (content message, artifact) where artifact is PDF data URL or file path"]:
    """
    Exports a specific slide from a Google Slides presentation as a PDF.
    
    This is accomplished by creating a temporary copy of the original presentation,
    removing all slides except the one to export, exporting it as PDF, and then
    deleting the temporary copy.
    """
    drive_service = get_drive_service(credentials)
    slides_service = get_slides_service(credentials)
    
    # Step 1: Get presentation info
    presentation = drive_service.files().get(
        fileId=presentation_id, fields='name').execute()
    
    # Step 2: Create a copy of the presentation
    body = {
        'name': f"{presentation['name']} - Slide {slide_index + 1}"
    }
    copied_presentation = drive_service.files().copy(
        fileId=presentation_id, body=body).execute()
    copied_presentation_id = copied_presentation['id']
    
    try:
        # Step 3: Get all slides from the copied presentation
        copied_slides = slides_service.presentations().get(
            presentationId=copied_presentation_id).execute().get('slides', [])
        
        # Ensure slide_index is within bounds
        if slide_index < 0 or slide_index >= len(copied_slides):
            raise ValueError(f"Slide index {slide_index} is out of range. The presentation has {len(copied_slides)} slides.")
        
        # Step 4: Create a list of all slides to delete (all except the one we want to export)
        delete_requests = []
        for i, slide in enumerate(copied_slides):
            if i != slide_index:
                delete_requests.append({
                    'deleteObject': {
                        'objectId': slide['objectId']
                    }
                })
        
        # Step 5: If there are slides to delete, make the batchUpdate request
        if delete_requests:
            slides_service.presentations().batchUpdate(
                presentationId=copied_presentation_id,
                body={'requests': delete_requests}
            ).execute()
        
        # Step 6: Export the single-slide presentation as a PDF
        request = drive_service.files().export_media(
            fileId=copied_presentation_id,
            mimeType='application/pdf'
        )
        
        # Get PDF content
        pdf_content = request.execute()
        
        # If output path is provided, save to file
        if output_path:
            with open(output_path, 'wb') as pdf_file:
                pdf_file.write(pdf_content)
            content = f"Slide {slide_index + 1} exported as PDF to {output_path}"
            return content, output_path
        
        # Otherwise, encode as base64 and return as data URL
        base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
        data_url = f"data:application/pdf;base64,{base64_pdf}"
        content = f"Slide {slide_index + 1} exported as PDF"
        
        # Return in the format expected by LangChain tools with content_and_artifact
        artifact = {
            "type": "file",
            "file": {
                "filename": f"slide_{presentation_id}_{slide_index}.pdf",
                "file_data": data_url,
            }
        }
        return content, [artifact]
    
    finally:
        # Step 7: Clean up by deleting the copied presentation
        drive_service.files().delete(fileId=copied_presentation_id).execute()

@tool(response_format="content_and_artifact")
def get_presentation_thumbnail(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_index: Annotated[int, "Index of the slide (0-based)"] = 0, 
    output_path: Annotated[Optional[str], "Path to save the thumbnail image"] = None
) -> Annotated[Tuple[str, Union[str, List[Dict[str, Any]]]], "Tuple of (content message, artifact) where artifact is image data URL or file path"]:
    """
    Gets a thumbnail image of a specific slide in a presentation.
    """
    slides_service = get_slides_service(credentials)
    
    # Get the presentation to find the slide ID
    presentation = slides_service.presentations().get(
        presentationId=presentation_id).execute()
    
    # Check if slide_index is within bounds
    if slide_index < 0 or slide_index >= len(presentation.get('slides', [])):
        raise ValueError(f"Slide index {slide_index} is out of range. The presentation has {len(presentation.get('slides', []))} slides.")
    
    # Get the slide ID
    slide_id = presentation.get('slides', [])[slide_index]['objectId']
    
    # Get the thumbnail
    thumbnail = slides_service.presentations().pages().getThumbnail(
        presentationId=presentation_id,
        pageObjectId=slide_id
    ).execute()
    
    # Get the thumbnail URL
    thumbnail_url = thumbnail.get('contentUrl')
    
    # If an output path is provided, download the thumbnail
    if output_path:
        response = requests.get(thumbnail_url)
        with open(output_path, 'wb') as image_file:
            image_file.write(response.content)
        content = f"Thumbnail of slide {slide_index + 1} saved to {output_path}"
        return content, output_path
    
    # Otherwise, download the image and encode it as base64
    response = requests.get(thumbnail_url)
    base64_image = base64.b64encode(response.content).decode('utf-8')
    data_url = f"data:image/png;base64,{base64_image}"
    content = f"Thumbnail of slide {slide_index + 1}"
    
    # Return in the format expected by LangChain tools with content_and_artifact
    artifact = {
        "type": "file",
        "file": {
            "filename": f"thumbnail_{presentation_id}_{slide_index}.png",
            "file_data": data_url,
        }
    }
    return content, [artifact] 