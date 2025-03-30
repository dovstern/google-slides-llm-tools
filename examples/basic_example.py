"""
Basic example for using the Google Slides LLM Tools package.

This example demonstrates how to:
1. Authenticate with Google
2. Create a new presentation
3. Add a slide
4. Add text to the slide
5. Add an image to the slide
6. Export the presentation as PDF
"""

import os
from google_slides_llm_tools import (
    authenticate,
    create_presentation,
    add_slide,
    add_text_to_slide,
    add_image_to_slide,
    export_presentation_as_pdf
)

def main():
    # Authenticate with Google
    print("Authenticating with Google...")
    credentials = authenticate()
    
    # Create a new presentation
    print("Creating a new presentation...")
    result = create_presentation(credentials, "Example Presentation")
    presentation_id = result["presentationId"]
    pdf_path = result["pdfPath"]
    print(f"Presentation created with ID: {presentation_id}")
    print(f"PDF available at: {pdf_path}")
    
    # Add a title slide
    print("Adding a title slide...")
    slide_response = add_slide(credentials, presentation_id, "TITLE")
    slide_id = slide_response['replies'][0]['createSlide']['objectId']
    presentation_pdf = slide_response["presentationPdfPath"]
    slide_pdf = slide_response["slidePdfPath"]
    print(f"Slide created with ID: {slide_id}")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Slide PDF: {slide_pdf}")
    
    # Add title text
    print("Adding title text...")
    text_response = add_text_to_slide(
        credentials,
        presentation_id,
        slide_id,
        "Google Slides LLM Tools Example",
        x=40,  # in points
        y=100,  # in points
        width=600,  # in points
        height=60  # in points
    )
    presentation_pdf = text_response["presentationPdfPath"]
    slide_pdf = text_response["slidePdfPath"]
    print(f"Title text added")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Updated slide PDF: {slide_pdf}")
    
    # Add subtitle text
    print("Adding subtitle text...")
    subtitle_response = add_text_to_slide(
        credentials,
        presentation_id,
        slide_id,
        "Created programmatically using LangChain tools",
        x=40,  # in points
        y=180,  # in points
        width=600,  # in points
        height=40  # in points
    )
    presentation_pdf = subtitle_response["presentationPdfPath"]
    slide_pdf = subtitle_response["slidePdfPath"]
    print(f"Subtitle text added")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Updated slide PDF: {slide_pdf}")
    
    # Add an image (replace with a valid image URL)
    print("Adding an image...")
    image_response = add_image_to_slide(
        credentials,
        presentation_id,
        slide_id,
        "https://picsum.photos/800/600",  # Random image from Lorem Picsum
        x=200,  # in points
        y=250,  # in points
        width=400,  # in points
        height=300  # in points
    )
    presentation_pdf = image_response["presentationPdfPath"]
    slide_pdf = image_response["slidePdfPath"]
    print(f"Image added")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Updated slide PDF: {slide_pdf}")
    
    # Export as PDF (custom filename if needed)
    custom_pdf_path = "example_presentation.pdf"
    print(f"Exporting presentation as PDF to {custom_pdf_path}...")
    final_pdf_path = export_presentation_as_pdf(credentials, presentation_id, custom_pdf_path)
    
    print("Done! Example presentation has been created and exported.")
    print(f"View your presentation at: https://docs.google.com/presentation/d/{presentation_id}/edit")
    print(f"Final PDF saved at: {final_pdf_path}")

if __name__ == "__main__":
    main() 