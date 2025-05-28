# Google Slides LLM Tools

A Python package providing tools for LLMs to interact with Google Slides, supporting both LangChain tools and an MCP (Model Context Protocol) server for integration with various LLM clients and agents. This project also includes a Node.js CLI wrapper (`google-slides-mcp`) for easy server startup via `npx`.

## Features

- **Slides Operations**: Create, read, update, and delete slides and presentations
- **Formatting**: Add and format text with custom styles and paragraph formatting
- **Multimedia**: Add images, videos, audio links, and shapes to slides
- **Data Integration**: Create charts and tables from Google Sheets data
- **Templates**: Apply layouts, duplicate presentations, and create custom templates
- **Collaboration**: Manage permissions and sharing (editor, viewer, commenter, public)
- **Animations**: Set slide transitions and auto-advance timing
- **Export**: Export presentations/slides to PDF and get thumbnails
- **Integration**: Works with both LangChain agents and MCP server for various LLM clients

---

## Quick Start

### Option 1: MCP Server (Node.js CLI Wrapper)

Run the MCP server directly using `npx` - no installation required:

```bash
# Using Application Default Credentials (Recommended)
npx google-slides-mcp --use-adc --project YOUR_PROJECT_ID

# Using credentials file
npx google-slides-mcp --credentials /path/to/your/credentials.json
```

### Option 2: Python Package

Install and use directly in Python:

```bash
pip install google-slides-llm-tools
```

```python
from google_slides_llm_tools import authenticate, create_presentation, add_slide

# Authenticate
credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')

# Create a presentation
presentation = create_presentation(credentials, "My Presentation")
```

---

## MCP Server Usage

The MCP server enables LLM clients (like Cursor, Claude Desktop, etc.) to interact with Google Slides via a local HTTP server.

### Prerequisites

- **Node.js 14+**: Required for the CLI wrapper. [Download](https://nodejs.org/)
- **Python 3.8+**: Required for the backend. [Download](https://www.python.org/)
- **Google Cloud Credentials**: See [Authentication Setup](#authentication-setup) below

### Installation & Quick Start

No installation required - just use `npx`:

```bash
# Using Application Default Credentials (ADC) - Recommended
npx google-slides-mcp --use-adc --project YOUR_PROJECT_ID

# OR Using a Credentials File (OAuth or Service Account JSON)
npx google-slides-mcp --credentials /path/to/your/credentials.json
```

The server will start on port 8000 by default. Connect your MCP client to `http://localhost:8000`.

### Command-Line Options

```
Usage: google-slides-mcp [options]

Options:
  -V, --version                   output the version number
  --credentials <path>            Path to Google OAuth credentials JSON file
  --use-adc                       Use Application Default Credentials
  --project <id>                  Google Cloud project ID (required with --use-adc)
  -p, --port <number>             Port to run the server on (default: "8000")
  -h, --help                      display help for command
```

### Client Configuration

#### Cursor / Generic MCP Clients
1. Start the server as shown above
2. Configure your client to connect to `http://localhost:8000`

#### Claude Desktop
Add to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-slides": {
      "command": "npx",
      "args": [
        "google-slides-mcp",
        "--use-adc",
        "--project", "YOUR_PROJECT_ID"
      ]
    }
  }
}
```

For credentials file instead of ADC:
```json
{
  "mcpServers": {
    "google-slides": {
      "command": "npx", 
      "args": [
        "google-slides-mcp",
        "--credentials", "/path/to/your/credentials.json"
      ]
    }
  }
}
```

### Programmatic Usage (Node.js)

```javascript
const { startServer } = require('google-slides-mcp');

startServer({ 
    port: 8001,
    useAdc: true,
    project: 'your-project-id'
}).then(childProcess => {
    console.log('MCP Server started (PID:', childProcess.pid, ')');
}).catch(err => {
    console.error('Failed to start server:', err);
});
```

---

## Python Package Usage

### Installation

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install google-slides-llm-tools
```

### Authentication Setup

Choose one method:

#### Method 1: Application Default Credentials (ADC) - Recommended

1. **Install Google Cloud SDK**: [Instructions](https://cloud.google.com/sdk/docs/install)
2. **Login and set project**:
   ```bash
   gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive
   gcloud auth application-default set-quota-project YOUR_PROJECT_ID
   ```
3. **Use in Python**:
   ```python
   from google_slides_llm_tools import authenticate
   credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')
   ```

#### Method 2: OAuth Credentials File

1. **Create OAuth credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
   - Create OAuth 2.0 Client ID (Desktop application)
   - Download the JSON file
2. **Use in Python**:
   ```python
   from google_slides_llm_tools import authenticate
   credentials = authenticate(credentials_path='/path/to/oauth_credentials.json')
   ```

#### Method 3: Service Account Key

1. **Create service account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/) → IAM & Admin → Service Accounts
   - Create service account and download JSON key
2. **Use in Python**:
   ```python
   from google_slides_llm_tools import authenticate
   credentials = authenticate(credentials_path='/path/to/service_account.json')
   ```

### Direct Python Usage

```python
from google_slides_llm_tools import (
    authenticate, create_presentation, add_slide, 
    add_text_to_slide, add_image_to_slide
)

# Authenticate
credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')

# Create a presentation
presentation = create_presentation(credentials, "My AI Presentation")
presentation_id = presentation['presentationId']

# Add a slide
slide_response = add_slide(credentials, presentation_id, layout="TITLE_AND_BODY")
slide_id = slide_response['replies'][0]['createSlide']['objectId']

# Add text to the slide
add_text_to_slide(
    credentials, 
    presentation_id, 
    slide_id, 
    "Welcome to AI Tools",
    position={'x': 100, 'y': 100, 'width': 400, 'height': 50}
)

# Add an image
add_image_to_slide(
    credentials,
    presentation_id, 
    slide_id,
    "https://example.com/image.jpg",
    position={'x': 100, 'y': 200, 'width': 300, 'height': 200}
)
```

### Usage with LangChain

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from google_slides_llm_tools import get_langchain_tools

# Get all available tools
tools = get_langchain_tools()

# Create an agent
llm = ChatOpenAI(model="gpt-4", temperature=0.1)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that creates Google Slides presentations."),
    ("human", "{input}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent
result = agent_executor.invoke({
    "input": "Create a presentation about AI tools with a title slide and one content slide"
})
```

#### Credentials Injection for LangChain/LangGraph

When using LangChain or LangGraph, you need to inject Google credentials into tool calls since the tools use `InjectedToolArg` for the credentials parameter. Use the `add_credentials_to_langchain_tool_call` function as a post-message hook:

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from google_slides_llm_tools import get_langchain_tools, add_credentials_to_langchain_tool_call
from google_slides_llm_tools.utils import authenticate

# Authenticate and get credentials
credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')

# Create LLM and get tools
llm = ChatOpenAI(model="gpt-4", temperature=0)
tools = get_langchain_tools()

# Create a credentials injection function
def inject_credentials(state, messages_key="messages"):
    return add_credentials_to_langchain_tool_call(credentials, state, messages_key)

# Create LangGraph agent with credentials injection
workflow = create_react_agent(llm, tools, post_message_hook=inject_credentials)
app = workflow.compile()

# Run the agent
inputs = {
    "messages": [("user", "Create a presentation titled 'My AI Presentation'")]
}
result = app.invoke(inputs)
```

The `add_credentials_to_langchain_tool_call` function automatically injects your Google credentials into all tool calls, ensuring that the tools can authenticate with the Google APIs without requiring manual credential passing.

---

## Available Tools

The package provides the following categories of tools:

### Slides Operations
- `create_presentation` - Create a new presentation
- `get_presentation` - Get presentation details
- `add_slide` - Add a new slide
- `delete_slide` - Delete a slide
- `reorder_slides` - Reorder slides in presentation
- `duplicate_slide` - Duplicate an existing slide

### Formatting
- `add_text_to_slide` - Add text to a slide
- `update_text_style` - Update text formatting (font, size, color, etc.)
- `update_paragraph_style` - Update paragraph formatting (alignment, spacing, etc.)

### Multimedia
- `add_image_to_slide` - Add images to slides
- `add_video_to_slide` - Add videos to slides
- `insert_audio_link` - Add audio links
- `add_shape_to_slide` - Add shapes (rectangles, circles, etc.)
- `create_shape` - Create custom shapes
- `group_elements` - Group slide elements
- `ungroup_elements` - Ungroup slide elements

### Data Integration
- `create_sheets_chart` - Create charts from Google Sheets data
- `create_table_from_sheets` - Create tables from Google Sheets data
- `get_slide_data` - Extract data from slides
- `get_presentation_data` - Extract data from presentations
- `find_element_ids` - Find element IDs on slides

### Templates
- `apply_predefined_layout` - Apply predefined layouts
- `duplicate_presentation` - Duplicate entire presentations
- `list_available_layouts` - List available layouts
- `create_custom_template` - Create custom templates

### Collaboration
- `add_editor_permission` - Grant editor access
- `add_viewer_permission` - Grant viewer access
- `add_commenter_permission` - Grant commenter access
- `remove_permission` - Remove access permissions
- `list_permissions` - List all permissions
- `make_public` - Make presentation public

### Animations
- `set_slide_transition` - Set slide transition effects
- `apply_auto_advance` - Set auto-advance timing
- `set_slide_background` - Set slide backgrounds

### Export
- `export_presentation_as_pdf` - Export entire presentation as PDF
- `export_slide_as_pdf` - Export specific slide as PDF
- `get_presentation_thumbnail` - Get presentation thumbnail

---

## Examples

See the `examples/` directory for complete examples:

- `basic_example.py` - Basic usage examples
- `langchain_example.py` - LangChain integration
- `langgraph_example.py` - LangGraph integration
- `mcp_client_example.py` - MCP client usage
- `combined_integration_example.py` - Advanced integration patterns

---

## API Requirements

Before using this package, ensure the following APIs are enabled in your Google Cloud project:

1. **Google Slides API**
2. **Google Drive API** 
3. **Google Sheets API** (if using data integration features)

Enable them at: https://console.cloud.google.com/apis/library

---

## Converting LangChain Tools to MCP Tools

This package uses the `langchain-tool-to-mcp-adapter` to convert LangChain tools to MCP server tools:

```python
from mcp.server import FastMCP
from google_slides_llm_tools import get_langchain_tools
from langchain_tool_to_mcp_adapter import add_langchain_tool_to_server

# Create MCP server
server = FastMCP('google-slides-mcp')

# Add all tools
for tool in get_langchain_tools():
    add_langchain_tool_to_server(server, tool)

# Run server
server.run(port=8000)
```

---

## Testing

Run the test suite:

```bash
python -m unittest discover tests
# or
./run_tests.py
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/dovstern/google-slides-llm-tools/issues)
- **Documentation**: See function docstrings for detailed parameter information
- **Examples**: Check the `examples/` directory for usage patterns 