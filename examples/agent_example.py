"""
Example of using Google Slides LLM Tools with a LangChain agent.

This example demonstrates how to:
1. Authenticate with Google
2. Create LangChain tools from the Google Slides functions
3. Create a LangChain agent with these tools
4. Use the agent to create and modify a presentation
"""

import os
import json
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import Tool

from google_slides_llm_tools import (
    authenticate,
    create_presentation,
    add_slide,
    add_text_to_slide,
    add_image_to_slide,
    export_presentation_as_pdf
)

def main():
    # Set your OpenAI API key
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    
    # Authenticate with Google
    print("Authenticating with Google...")
    credentials = authenticate()
    
    # Create LangChain tools
    tools = [
        Tool(
            name="CreatePresentation",
            func=lambda title: json.dumps({
                "presentationId": create_presentation(credentials, title)["presentationId"],
                "message": f"Created presentation titled '{title}'",
                "pdf_path": create_presentation(credentials, title)["pdfPath"]
            }),
            description="Creates a new Google Slides presentation with the given title. Returns the ID of the new presentation and a path to its PDF."
        ),
        Tool(
            name="AddSlide",
            func=lambda p_id, layout='TITLE': json.dumps({
                "slideId": add_slide(credentials, p_id, layout)['replies'][0]['createSlide']['objectId'],
                "message": f"Added a new slide with layout '{layout}'",
                "presentationPdfPath": add_slide(credentials, p_id, layout)["presentationPdfPath"],
                "slidePdfPath": add_slide(credentials, p_id, layout).get("slidePdfPath", "No individual slide PDF available")
            }),
            description="Adds a new slide to the presentation. Input should include 'presentation_id' and optionally 'layout' (default is 'TITLE'). Returns information about the new slide, including its ID and paths to PDFs."
        ),
        Tool(
            name="AddTextToSlide",
            func=lambda p_id, s_id, text, x, y, w, h: json.dumps({
                "message": f"Added text '{text}' to slide",
                "presentationPdfPath": add_text_to_slide(credentials, p_id, s_id, text, float(x), float(y), float(w), float(h))["presentationPdfPath"],
                "slidePdfPath": add_text_to_slide(credentials, p_id, s_id, text, float(x), float(y), float(w), float(h)).get("slidePdfPath", "No individual slide PDF available")
            }),
            description="Adds text to a slide. Input should include 'presentation_id', 'slide_id', 'text', 'x', 'y', 'width', and 'height'. Returns paths to PDFs showing the result."
        ),
        Tool(
            name="AddImageToSlide",
            func=lambda p_id, s_id, img_url, x, y, w, h: json.dumps({
                "message": f"Added image from {img_url} to slide",
                "presentationPdfPath": add_image_to_slide(credentials, p_id, s_id, img_url, float(x), float(y), float(w), float(h))["presentationPdfPath"],
                "slidePdfPath": add_image_to_slide(credentials, p_id, s_id, img_url, float(x), float(y), float(w), float(h)).get("slidePdfPath", "No individual slide PDF available")
            }),
            description="Adds an image to a slide. Input should include 'presentation_id', 'slide_id', 'image_url', 'x', 'y', 'width', and 'height'. Returns paths to PDFs showing the result."
        ),
        Tool(
            name="ExportAsPDF",
            func=lambda p_id, path: json.dumps({
                "message": f"Exported presentation as PDF",
                "pdfPath": export_presentation_as_pdf(credentials, p_id, path)
            }),
            description="Exports a presentation as a PDF file. Input should include 'presentation_id' and 'output_path'. Returns the path to the exported PDF."
        )
    ]
    
    # Initialize the language model
    llm = OpenAI(temperature=0)
    
    # Create the agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    # Use the agent
    agent.run("""
    Create a presentation titled "AI-Generated Presentation". 
    Add a title slide with the text "AI-Generated Presentation" at position x=40, y=100 with width=600 and height=60. 
    Also add a subtitle "Created by LangChain Agent" at position x=40, y=180 with width=600 and height=40.
    Add an image of a robot from https://picsum.photos/id/1020/800/600 at position x=200, y=250 with width=400 and height=300.
    Export the presentation as a PDF file named "ai_generated.pdf".
    
    After each operation, check the PDF output to verify the changes are as expected.
    """)

if __name__ == "__main__":
    main() 