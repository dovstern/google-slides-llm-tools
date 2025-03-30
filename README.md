# Google Slides LLM Tools

A Python package providing tools for large language models (LLMs) to interact with Google Slides. This package integrates with LangChain and provides a comprehensive set of tools for creating and manipulating Google Slides presentations.

## Features

- **Authentication**: Easily authenticate with Google APIs
- **Slide Operations**: Create presentations, add/delete/reorder slides
- **Text Formatting**: Modify text styles, apply paragraph styles
- **Multimedia Management**: Add images, videos, and links to audio
- **Data Integration**: Import charts and tables from Google Sheets
- **Template Management**: Apply predefined layouts, create custom templates
- **Collaboration**: Manage permissions and sharing settings
- **Transitions & Animations**: Apply slide transitions and animations
- **Export**: Export presentations and individual slides as PDFs
- **Visual Feedback**: All modification functions return PDF paths for immediate visual feedback

## Installation

```bash
pip install google-slides-llm-tools
```

## Usage

```python
from google_slides_llm_tools.auth import authenticate
from google_slides_llm_tools.slides import create_presentation, add_slide
from google_slides_llm_tools.formatting import add_text_to_slide

# Authenticate with Google
credentials = authenticate()

# Create a presentation and get the presentation ID and PDF path
result = create_presentation(credentials, "My Amazing Presentation")
presentation_id = result["presentationId"]
presentation_pdf = result["pdfPath"]
print(f"Created presentation with ID: {presentation_id}")
print(f"View the initial presentation PDF at: {presentation_pdf}")

# Add a slide and get updated PDFs
slide_result = add_slide(credentials, presentation_id, "TITLE")
slide_id = slide_result['replies'][0]['createSlide']['objectId']
presentation_pdf = slide_result["presentationPdfPath"]
slide_pdf = slide_result["slidePdfPath"]
print(f"Added slide with ID: {slide_id}")
print(f"View updated presentation PDF: {presentation_pdf}")
print(f"View individual slide PDF: {slide_pdf}")

# Add text to the slide and get updated PDFs
text_result = add_text_to_slide(credentials, presentation_id, slide_id, 
                               "Hello World", 100, 100, 400, 50)
presentation_pdf = text_result["presentationPdfPath"]
slide_pdf = text_result["slidePdfPath"]
print(f"Added text to slide")
print(f"View updated presentation PDF: {presentation_pdf}")
print(f"View individual slide PDF: {slide_pdf}")
```

## Using with LangChain or LangGraph

The package is designed to work seamlessly with both LangChain and LangGraph. Every function that modifies slides or presentations returns PDF paths that can be used by agents to visually verify their changes.

```python
from langchain.agents import initialize_agent, Tool
import json

# Create tools that provide visual feedback
tools = [
    Tool(
        name="CreatePresentation",
        func=lambda title: json.dumps({
            "presentationId": create_presentation(credentials, title)["presentationId"],
            "message": f"Created presentation titled '{title}'",
            "pdf_path": create_presentation(credentials, title)["pdfPath"]
        }),
        description="Creates a new Google Slides presentation and returns its ID and PDF"
    ),
    # Add more tools as needed
]

# Initialize LangChain agent with the tools
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# Run the agent
agent.run("Create a presentation titled 'My Amazing Presentation' and add a title slide")
```

## Authentication

To use this package, you need to:

1. Create a project in the Google Cloud Console
2. Enable the Google Slides API
3. Create OAuth credentials and download the credentials file
4. Save the credentials file as `credentials.json` in your project directory

For more details, see the [Google API documentation](https://developers.google.com/workspace/slides/api/quickstart/python).

## License

MIT 