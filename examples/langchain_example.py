"""
LangChain Example for Google Slides LLM Tools

This example demonstrates how to use the Google Slides LLM Tools with LangChain.
"""

from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
import os
from google_slides_llm_tools import get_langchain_tools

# Ensure you have set your OpenAI API key in the environment
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

def main():
    """Run the example using LangChain agent with Google Slides tools."""
    print("Google Slides LLM Tools - LangChain Example")
    print("===========================================")
    
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
    
    # Run the agent with a task
    result = agent.run(
        "Create a presentation about artificial intelligence with 3 slides: "
        "an introduction, key concepts, and future trends. Add an image of a robot to the first slide."
    )
    
    print("\nAgent execution completed.")
    print("Result:", result)

if __name__ == "__main__":
    main() 