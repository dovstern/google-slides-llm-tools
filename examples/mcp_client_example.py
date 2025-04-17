"""
MCP Client Example for Google Slides LLM Tools

This example demonstrates how to use the MCP client to interact with
Google Slides LLM Tools exposed as an MCP server.
"""

from mcp import Client
import os
from pprint import pprint
from google_slides_llm_tools import get_langchain_tools

# Initialize the MCP client
# Adjust the server address as needed
client = Client(server_address="http://localhost:8000")

def main():
    """Run the example using MCP client to interact with Google Slides."""
    print("Google Slides LLM Tools - MCP Client Example")
    print("============================================")
    
    # Get all available tools and create a dictionary by name
    tools = get_langchain_tools()
    tool_names = {tool.name: tool for tool in tools}
    
    # Create a new presentation
    print("\n1. Creating a new presentation...")
    response = client.call_tool(
        tool_names["create_presentation"].name,
        title="MCP Example Presentation"
    )
    presentation_id = response["presentationId"]
    print(f"Presentation created with ID: {presentation_id}")
    
    # Add a slide
    print("\n2. Adding a slide...")
    slide_response = client.call_tool(
        tool_names["add_slide"].name,
        presentation_id=presentation_id,
        layout="TITLE_AND_BODY"
    )
    slide_id = slide_response["slideId"]
    print(f"Slide added with ID: {slide_id}")
    
    # Add text to the slide
    print("\n3. Adding text to the slide...")
    text_response = client.call_tool(
        tool_names["add_text_to_slide"].name,
        presentation_id=presentation_id,
        slide_id=slide_id,
        text="This slide was created using MCP client!",
        position={
            "x": 100,
            "y": 100,
            "width": 400,
            "height": 200
        }
    )
    print("Text added to slide")
    
    # Add an image to the slide
    print("\n4. Adding an image to the slide...")
    image_response = client.call_tool(
        tool_names["add_image_to_slide"].name,
        presentation_id=presentation_id,
        slide_id=slide_id,
        image_url="https://picsum.photos/200/300",
        x=300,
        y=200,
        width=200,
        height=150
    )
    print("Image added to slide")
    
    # Export the presentation as PDF
    pdf_path = os.path.join(os.getcwd(), "example_presentation.pdf")
    print(f"\n5. Exporting presentation as PDF to {pdf_path}...")
    pdf_response = client.call_tool(
        tool_names["export_presentation_as_pdf"].name,
        presentation_id=presentation_id,
        output_path=pdf_path
    )
    print(f"Presentation exported to: {pdf_response}")
    
    print("\nExample completed successfully!")
    print(f"Presentation ID: {presentation_id}")
    print(f"PDF exported to: {pdf_path}")

if __name__ == "__main__":
    main() 