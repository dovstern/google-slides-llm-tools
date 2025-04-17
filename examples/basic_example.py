"""
Basic example of using Google Slides LLM Tools.

This example demonstrates how to:
1. Get and use LangChain tools from Google Slides LLM Tools
2. Create a presentation
3. Add slides and text
4. Export the presentation as a PDF
"""

from google_slides_llm_tools import get_langchain_tools

def main():
    # Get all Google Slides tools as LangChain tools
    tools = get_langchain_tools()
    
    # Create a dictionary for easy access to tools by name
    tools_dict = {tool.name: tool for tool in tools}
    
    # Create a new presentation
    result = tools_dict["create_presentation"].func(title="Example Presentation")
    presentation_id = result["presentationId"]
    pdf_path = result["pdfPath"]
    print(f"Created presentation with ID: {presentation_id}")
    print(f"Initial PDF available at: {pdf_path}")
    
    # Add a slide
    slide_response = tools_dict["add_slide"].func(
        presentation_id=presentation_id, 
        layout="TITLE"
    )
    slide_id = slide_response['replies'][0]['createSlide']['objectId']
    presentation_pdf = slide_response["presentationPdfPath"]
    slide_pdf = slide_response["slidePdfPath"]
    print(f"Added slide with ID: {slide_id}")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Slide PDF: {slide_pdf}")
    
    # Add title text
    text_response = tools_dict["add_text_to_slide"].func(
        presentation_id=presentation_id,
        slide_id=slide_id,
        text="Hello, Google Slides!",
        x=100,  # x position
        y=100,  # y position
        width=400,  # width
        height=50    # height
    )
    presentation_pdf = text_response["presentationPdfPath"]
    slide_pdf = text_response["slidePdfPath"]
    print(f"Added title text")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Updated slide PDF: {slide_pdf}")
    
    # Add subtitle text
    subtitle_response = tools_dict["add_text_to_slide"].func(
        presentation_id=presentation_id,
        slide_id=slide_id,
        text="Created with Google Slides LLM Tools",
        x=100,  # x position
        y=200,  # y position
        width=400,  # width
        height=50    # height
    )
    presentation_pdf = subtitle_response["presentationPdfPath"]
    slide_pdf = subtitle_response["slidePdfPath"]
    print(f"Added subtitle text")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Updated slide PDF: {slide_pdf}")
    
    # Add an image
    image_response = tools_dict["add_image_to_slide"].func(
        presentation_id=presentation_id,
        slide_id=slide_id,
        image_url="https://picsum.photos/800/600",  # random image from Lorem Picsum
        x=200,  # x position
        y=250,  # y position
        width=400,  # width
        height=300   # height
    )
    presentation_pdf = image_response["presentationPdfPath"]
    slide_pdf = image_response["slidePdfPath"]
    print(f"Added image")
    print(f"Updated presentation PDF: {presentation_pdf}")
    print(f"Updated slide PDF: {slide_pdf}")
    
    # Export the presentation as PDF with a custom filename
    output_path = "example_presentation.pdf"
    content, artifact = tools_dict["export_presentation_as_pdf"].func(
        presentation_id=presentation_id, 
        output_path=output_path
    )
    print(f"{content}: {artifact}")

if __name__ == "__main__":
    main() 