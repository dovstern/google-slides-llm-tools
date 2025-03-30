from ..auth import get_drive_service, get_slides_service
from langchain.tools import tool
import os

@tool
def export_presentation_as_pdf(credentials, presentation_id, output_path):
    """
    Exports a Google Slides presentation as a PDF file.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation to export
        output_path (str): Path to save the exported PDF
        
    Returns:
        str: Path to the exported PDF file
    """
    drive_service = get_drive_service(credentials)
    
    # Export the presentation as PDF
    request = drive_service.files().export_media(
        fileId=presentation_id,
        mimeType='application/pdf'
    )
    
    # Write the PDF to the specified path
    with open(output_path, 'wb') as pdf_file:
        pdf_file.write(request.execute())
    
    return output_path

@tool
def export_slide_as_pdf(credentials, presentation_id, slide_index, output_path):
    """
    Exports a specific slide from a Google Slides presentation as a PDF.
    
    This is accomplished by creating a temporary copy of the original presentation,
    removing all slides except the one to export, exporting it as PDF, and then
    deleting the temporary copy.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the original presentation
        slide_index (int): Index of the slide to export (0-based)
        output_path (str): Path to save the exported PDF
        
    Returns:
        str: Path to the exported PDF file
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
        
        # Write the PDF to the specified path
        with open(output_path, 'wb') as pdf_file:
            pdf_file.write(request.execute())
        
        return output_path
    
    finally:
        # Step 7: Clean up by deleting the copied presentation
        drive_service.files().delete(fileId=copied_presentation_id).execute()

@tool
def get_presentation_thumbnail(credentials, presentation_id, slide_index=0, output_path=None):
    """
    Gets a thumbnail image of a specific slide in a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_index (int, optional): Index of the slide (0-based)
        output_path (str, optional): Path to save the thumbnail image
        
    Returns:
        str: Path to the thumbnail image, or the thumbnail data if no output_path provided
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
        import requests
        response = requests.get(thumbnail_url)
        with open(output_path, 'wb') as image_file:
            image_file.write(response.content)
        return output_path
    
    return thumbnail_url
