from google_slides_llm_tools.auth import get_drive_service, get_slides_service
import os
import base64

def export_presentation_as_pdf(credentials, presentation_id, output_path=None):
    """
    Exports a Google Slides presentation as a PDF file.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation to export
        output_path (str, optional): Path to save the exported PDF
        
    Returns:
        tuple: (content, artifact) where content is a message string and 
               artifact is the PDF data URL or file path
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
    return content, data_url

def export_slide_as_pdf(credentials, presentation_id, slide_index, output_path=None):
    """
    Exports a specific slide from a Google Slides presentation as a PDF.
    
    This is accomplished by creating a temporary copy of the original presentation,
    removing all slides except the one to export, exporting it as PDF, and then
    deleting the temporary copy.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the original presentation
        slide_index (int): Index of the slide to export (0-based)
        output_path (str, optional): Path to save the exported PDF
        
    Returns:
        tuple: (content, artifact) where content is a message string and 
               artifact is the PDF data URL or file path
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
        return content, data_url
    
    finally:
        # Step 7: Clean up by deleting the copied presentation
        drive_service.files().delete(fileId=copied_presentation_id).execute()

def get_presentation_thumbnail(credentials, presentation_id, slide_index=0, output_path=None):
    """
    Gets a thumbnail image of a specific slide in a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_index (int, optional): Index of the slide (0-based)
        output_path (str, optional): Path to save the thumbnail image
        
    Returns:
        tuple: (content, artifact) where content is a message string and 
               artifact is the image data URL or file path
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
        content = f"Thumbnail of slide {slide_index + 1} saved to {output_path}"
        return content, output_path
    
    # Otherwise, download the image and encode it as base64
    import requests
    response = requests.get(thumbnail_url)
    base64_image = base64.b64encode(response.content).decode('utf-8')
    data_url = f"data:image/png;base64,{base64_image}"
    content = f"Thumbnail of slide {slide_index + 1}"
    return content, data_url 