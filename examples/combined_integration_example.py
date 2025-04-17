"""
Combined LangChain and MCP Server Integration Example

This example demonstrates how to use both LangChain and MCP server integration 
with Google Slides LLM Tools in a single application.
"""

import os
import threading
import time
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from mcp import Client
from google_slides_llm_tools import (
    get_langchain_tools,
    run_server,
    authenticate
)

# Ensure you have set your OpenAI API key in the environment
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

def start_mcp_server():
    """Start the MCP server in a separate thread."""
    print("Starting MCP server...")
    run_server(host="localhost", port=8000)

def run_langchain_example():
    """Run the LangChain example with Google Slides tools."""
    print("\n=== LangChain Integration Example ===\n")
    
    # Get the Google Slides tools for LangChain
    tools = get_langchain_tools()
    
    # Create a ChatOpenAI instance
    llm = ChatOpenAI(temperature=0)
    
    # Initialize the agent with the tools
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    
    # Run the agent with a simple task
    print("Creating a presentation using LangChain agent...")
    result = agent.run(
        "Create a presentation titled 'LangChain Integration Example' with one title slide."
    )
    
    print("\nLangChain agent completed.")
    print("Result:", result)
    
    # Extract the presentation ID from the result (this will depend on your agent's output format)
    # For this example, we'll assume the presentation ID is returned in the result
    # In a real application, you would parse the result appropriately
    presentation_id = result.split("ID: ")[-1].split()[0] if "ID: " in result else None
    
    return presentation_id

def run_mcp_client_example(presentation_id=None):
    """Run the MCP client example with Google Slides tools."""
    print("\n=== MCP Server Integration Example ===\n")
    
    # Get all available tools and create a dictionary by name
    tools = get_langchain_tools()
    tool_names = {tool.name: tool for tool in tools}
    
    # Initialize the MCP client
    client = Client(server_address="http://localhost:8000")
    
    if presentation_id:
        print(f"Using existing presentation with ID: {presentation_id}")
    else:
        # Create a new presentation
        print("Creating a new presentation using MCP client...")
        response = client.call_tool(
            tool_names["create_presentation"].name,
            title="MCP Integration Example"
        )
        presentation_id = response["presentationId"]
        print(f"Presentation created with ID: {presentation_id}")
    
    # Add a slide
    print("Adding a slide using MCP client...")
    slide_response = client.call_tool(
        tool_names["add_slide"].name,
        presentation_id=presentation_id,
        layout="TITLE_AND_BODY"
    )
    slide_id = slide_response["slideId"]
    print(f"Slide added with ID: {slide_id}")
    
    # Add text to the slide
    print("Adding text to the slide using MCP client...")
    text_response = client.call_tool(
        tool_names["add_text_to_slide"].name,
        presentation_id=presentation_id,
        slide_id=slide_id,
        text="This slide was created using the MCP client!",
        position={
            "x": 100,
            "y": 100,
            "width": 400,
            "height": 200
        }
    )
    print("Text added to slide")
    
    return presentation_id

def main():
    """Run both LangChain and MCP server integration examples."""
    print("Google Slides LLM Tools - Combined Integration Example")
    print("=====================================================")
    
    # Verify authentication works
    print("Authenticating with Google...")
    authenticate()
    print("Authentication successful.")
    
    # Start the MCP server in a separate thread
    server_thread = threading.Thread(target=start_mcp_server)
    server_thread.daemon = True  # This ensures the thread will exit when the main program exits
    server_thread.start()
    
    # Wait for the server to start
    print("Waiting for MCP server to start...")
    time.sleep(2)
    
    # Run the LangChain example
    presentation_id = run_langchain_example()
    
    # Run the MCP client example with the presentation created by LangChain
    if presentation_id:
        run_mcp_client_example(presentation_id)
    else:
        run_mcp_client_example()
    
    print("\nCombined integration example completed!")
    print("Note: The MCP server is still running. Press Ctrl+C to exit.")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main() 