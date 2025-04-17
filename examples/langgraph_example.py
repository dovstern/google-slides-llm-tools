"""
Example of using Google Slides LLM Tools with LangGraph ReAct Agent.

This example demonstrates how to:
1. Authenticate with Google
2. Create a LangGraph ReAct agent with Google Slides tools from get_langchain_tools()
3. Use the agent to create and modify a presentation
"""

import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END
from typing import Dict, TypedDict, List, Any, Optional

from google_slides_llm_tools import get_langchain_tools

# Define the state schema
class AgentState(TypedDict):
    messages: List[Any]
    template_presentation_id: Optional[str]

def print_stream(stream):
    """Helper function to print the streaming output"""
    for s in stream:
        message = s.get("messages", [])[-1] if s.get("messages") else None
        if message:
            if isinstance(message, tuple):
                print(f"Human: {message[1]}")
            else:
                print(f"AI: {message.content}")

def main():
    """Run the agent with a sample task"""
    # Set your OpenAI API key
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    
    # Create the LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Get all Google Slides tools
    tools = get_langchain_tools()
    
    # Create the ReAct agent using the prebuilt function
    agent = create_react_agent(llm, tools)
    
    # Create a graph with the agent
    workflow = StateGraph(AgentState)
    
    # Add the agent node to the graph
    workflow.add_node("agent", agent)
    
    # Set the entry point for the graph
    workflow.set_entry_point("agent")
    
    # Set the exit condition
    workflow.add_edge("agent", END)
    
    # Compile the graph
    app = workflow.compile()
    
    # Define the input with template presentation ID
    # You can set this to None if not using a template, or provide a valid presentation ID
    template_id = "your-template-presentation-id"  # Replace with actual ID or None
    
    inputs = {
        "messages": [
            ("user", """
            Create a presentation titled 'AI-Generated Presentation'.
            Add a title slide.
            Add the title 'AI-Generated Presentation' at position x=0.1, y=0.1 with width=0.8 and height=0.1.
            Add a subtitle 'Created by LangGraph Agent' at position x=0.1, y=0.3 with width=0.8 and height=0.1.
            Add an image of a robot from https://picsum.photos/id/1020/800/600 at position x=0.2, y=0.4 with width=0.6 and height=0.4.
            Export the presentation as a PDF named 'langgraph_example.pdf'.
            After each operation, check the PDF output to verify the changes look as expected.
            """)
        ],
        "template_presentation_id": template_id
    }
    
    # Run the agent with streaming output
    print("Running the ReAct agent...")
    print_stream(app.stream(inputs))
    
    print("\nAgent execution completed!")

if __name__ == "__main__":
    main() 