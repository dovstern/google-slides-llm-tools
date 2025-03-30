"""
Example of using Google Slides LLM Tools with LangGraph.

This example demonstrates how to:
1. Authenticate with Google
2. Create a LangGraph agent with Google Slides tools
3. Use the agent to create and modify a presentation
"""

import os
import json
from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_to_tool_node
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from google_slides_llm_tools import (
    authenticate,
    create_presentation,
    add_slide,
    add_text_to_slide,
    add_image_to_slide,
    export_presentation_as_pdf
)

# Set up Google Credentials
credentials = authenticate()

# Define tools for Google Slides operations
@tool
def create_new_presentation(title: str) -> Dict[str, Any]:
    """Create a new Google Slides presentation with the given title."""
    result = create_presentation(credentials, title)
    return {
        "presentationId": result["presentationId"],
        "message": f"Created presentation titled '{title}'",
        "pdf_path": result["pdfPath"]
    }

@tool
def add_new_slide(presentation_id: str, layout: str = "TITLE") -> Dict[str, Any]:
    """Add a new slide to the presentation."""
    result = add_slide(credentials, presentation_id, layout)
    slide_id = result['replies'][0]['createSlide']['objectId']
    return {
        "slideId": slide_id,
        "message": f"Added a new slide with layout '{layout}'",
        "presentationPdfPath": result["presentationPdfPath"],
        "slidePdfPath": result.get("slidePdfPath", "No individual slide PDF available")
    }

@tool
def add_text(presentation_id: str, slide_id: str, text: str, x: float, y: float, width: float, height: float) -> Dict[str, Any]:
    """Add text to a slide at the specified position and size."""
    result = add_text_to_slide(credentials, presentation_id, slide_id, text, x, y, width, height)
    return {
        "message": f"Added text '{text}' to slide",
        "presentationPdfPath": result["presentationPdfPath"],
        "slidePdfPath": result.get("slidePdfPath", "No individual slide PDF available")
    }

@tool
def add_image(presentation_id: str, slide_id: str, image_url: str, x: float, y: float, width: float, height: float) -> Dict[str, Any]:
    """Add an image to a slide at the specified position and size."""
    result = add_image_to_slide(credentials, presentation_id, slide_id, image_url, x, y, width, height)
    return {
        "message": f"Added image from {image_url} to slide",
        "presentationPdfPath": result["presentationPdfPath"],
        "slidePdfPath": result.get("slidePdfPath", "No individual slide PDF available")
    }

@tool
def export_pdf(presentation_id: str, output_path: str) -> Dict[str, Any]:
    """Export the presentation as a PDF file."""
    pdf_path = export_presentation_as_pdf(credentials, presentation_id, output_path)
    return {
        "message": f"Exported presentation as PDF",
        "pdfPath": pdf_path
    }

# Define the state
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    next: Annotated[str, END]

# Create the agent
agent_llm = ChatOpenAI(model="gpt-4", temperature=0)
tools_list = [create_new_presentation, add_new_slide, add_text, add_image, export_pdf]
tool_node = tools_to_tool_node(tools_list)

# Create the graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_llm)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")

# Connect the nodes
workflow.add_edge("agent", "tools")
workflow.add_edge("tools", "agent")

# Define the conditional edges
def decide_to_continue(state: AgentState) -> str:
    """Decide whether to continue or end."""
    messages = state["messages"]
    last_message = messages[-1]["content"]
    
    if "FINISH" in last_message or "finished" in last_message.lower():
        return END
    return "agent"

workflow.add_conditional_edges("agent", decide_to_continue)

# Compile the graph
app = workflow.compile()

# Run the agent
def main():
    # Set your OpenAI API key
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    
    # Initialize state
    state = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant that helps create presentations using Google Slides. "
                    "You will perform each step one at a time and check the generated PDF after each operation to ensure it looks correct."
                )
            },
            {
                "role": "user",
                "content": (
                    "Create a presentation titled 'AI-Generated Presentation'. "
                    "Add a title slide. "
                    "Add the title 'AI-Generated Presentation' at position x=40, y=100 with width=600 and height=60. "
                    "Add a subtitle 'Created by LangGraph Agent' at position x=40, y=180 with width=600 and height=40. "
                    "Add an image of a robot from https://picsum.photos/id/1020/800/600 at position x=200, y=250 with width=400 and height=300. "
                    "Export the presentation as a PDF named 'langgraph_example.pdf'. "
                    "After each operation, check the PDF output to verify the changes look as expected."
                    "After completing all tasks, respond with FINISH."
                )
            }
        ],
        "next": "agent"
    }
    
    # Run the agent
    print("Running the agent...")
    final_state = app.invoke(state)
    
    # Print the final message
    print("\nFinal message:")
    print(final_state["messages"][-1]["content"])

if __name__ == "__main__":
    main() 