# Google Slides LLM Tools

A Python package providing tools for LLMs to interact with Google Slides, supporting both LangChain tools and an MCP (Model Context Protocol) server for integration with various LLM clients and agents. This project also includes a Node.js CLI wrapper (`google-slides-mcp`) for easy server startup via `npx`.

## Features

- Create and manipulate Google Slides presentations
- Format text and add multimedia content
- Apply templates and layouts
- Manage collaboration and sharing
- Set animations and transitions
- Export presentations to various formats
- Integration with both LangChain and MCP server (Python or via Node.js CLI)

---

## MCP Server (Node.js CLI Wrapper)

The MCP server enables LLM clients (like Cursor, Claude Desktop, etc.) to interact with Google Slides via a local HTTP server. You can run the server directly using the Node.js CLI wrapper, which launches the Python backend for you.

### Prerequisites

- **Node.js and npm:** Required for the CLI wrapper. [Download](https://nodejs.org/)
- **Python 3.8+**: Required for the backend. [Download](https://www.python.org/)
- **google-slides-llm-tools Python Package:**
    ```bash
    pip install google-slides-llm-tools
    ```
- **Google Cloud Credentials:** (see Authentication below)

### Installation & Quick Start

No installation is required for the CLI wrapper; just use `npx`:

```bash
# Using Application Default Credentials (ADC) - Recommended
npx google-slides-mcp --use-adc --project YOUR_PROJECT_ID

# OR Using a Credentials File (OAuth or Service Account JSON)
npx google-slides-mcp --credentials /path/to/your/credentials.json
```

The server will start on port 8000 by default. Connect your MCP client (e.g., Cursor, Claude) to `http://localhost:8000`.

### Authentication Setup

Choose one method:

#### Method 1: Application Default Credentials (ADC) - Recommended

1. **Install Google Cloud SDK:** [Instructions](https://cloud.google.com/sdk/docs/install)
2. **Login via `gcloud`:**
    ```bash
    gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive
    gcloud auth application-default set-quota-project YOUR_PROJECT_ID
    ```
3. **Run the server:**
    ```bash
    npx google-slides-mcp --use-adc --project YOUR_PROJECT_ID
    ```

#### Method 2: Credentials File (OAuth or Service Account)

1. **Create/Download Credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
    - Create an OAuth 2.0 Client ID (Desktop app) or Service Account Key (JSON)
    - Download the JSON file
2. **Run the server:**
    ```bash
    npx google-slides-mcp --credentials /path/to/your/credentials.json
    ```

### Command-Line Options

```
Usage: google-slides-mcp [options]

Options:
  -V, --version                   output the version number
  --credentials <path>            Path to Google OAuth credentials JSON file
  --use-adc                       Use Application Default Credentials (gcloud auth application-default login)
  --project <id>                  Google Cloud project ID to use for ADC
  -p, --port <number>             Port to run the server on (default: "8000")
  -h, --help                      display help for command
```

### Usage with Clients

#### Cursor / Generic Clients
1. Start the server as above.
2. Note the URL and port (e.g., `http://localhost:8000`).
3. Provide this URL to your client when configuring the MCP endpoint.

#### Claude Desktop
1. Locate the Claude Desktop configuration file (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`).
2. Edit the `mcpServers` section:
    ```json
    {
      "mcpServers": {
        "google-slides": {
          "command": "npx",
          "args": [
            "google-slides-mcp",
            "--credentials", // or --use-adc
            "/path/to/your/google_credentials.json" // or --project YOUR_PROJECT_ID if using ADC
          ]
        }
      }
    }
    ```
3. Replace the arguments as needed for your authentication method.
4. Restart Claude Desktop.

### Programmatic Usage (Node.js)

You can also start the server programmatically from Node.js:

```javascript
const { startServer } = require('google-slides-mcp');

startServer({ 
    port: 8001,
    credentials: '/path/to/creds.json' 
    // or useAdc: true, project: 'your-project-id'
}).then(childProcess => {
    console.log('MCP Server process started (PID: ', childProcess.pid, ')');
    // You can interact with childProcess if needed (e.g., childProcess.kill())
}).catch(err => {
    console.error('Failed to start server:', err);
});
```

---

## Python Package Usage (Direct or with LangChain)

## Guide 2: Using as Python/LangChain Tools

This guide explains how to install the package and use the tools directly within your Python scripts or integrate them with LangChain agents.

### Installation

1.  **Create and Activate Virtual Environment (Recommended):**
    ```bash
    # If starting a new project
    # mkdir my-slides-project && cd my-slides-project
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\\Scripts\\activate`
    ```
2.  **Install the Package:**
    ```bash
    pip install google-slides-llm-tools
    ```

    *Optional: For development or running examples directly from the repository, clone it and install in editable mode or install requirements:* 
    ```bash
    # git clone https://github.com/your-username/google-slides-llm-tools.git
    # cd google-slides-llm-tools
    # pip install -e .
    # OR
    # pip install -r requirements.txt
    ```

### Authentication for Python Usage

When using the tools directly in Python, you need to authenticate first. The `authenticate` function simplifies this.

```python
from google_slides_llm_tools import authenticate

# Option 1: Use Application Default Credentials (ADC)
# Ensure gcloud auth application-default login has been run with necessary scopes
# and gcloud auth application-default set-quota-project YOUR_PROJECT_ID
credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')

# Option 2: Use OAuth Credentials File (client_secrets.json)
# The first time, this will open a browser for authorization.
# It stores tokens locally (e.g., in token.json) for future use.
# credentials = authenticate(credentials_path='/path/to/client_secrets.json')

# Option 3: Use Service Account Key File
# credentials = authenticate(credentials_path='/path/to/service_account.json')

# The 'credentials' object can now be passed to tool functions (if needed),
# although the LangChain tools often handle this implicitly if setup correctly.
```

Refer to the [Debugging Common Issues](#debugging-common-serverapi-issues) section from Guide 1 if you encounter authentication problems, as the root causes (API enablement, scopes, quota project) are often the same.

### Direct Python Usage (Example)

```python
from google_slides_llm_tools import authenticate, create_presentation, add_slide

# Authenticate (choose one method from above)
credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')

# Create a presentation
presentation_info = create_presentation(credentials, title="My Python Presentation")
presentation_id = presentation_info['presentationId']
print(f"Created presentation: {presentation_id}")

# Add a slide
slide_info = add_slide(credentials, presentation_id=presentation_id, layout="TITLE_ONLY")
slide_id = slide_info['replies'][0]['createSlide']['objectId']
print(f"Added slide: {slide_id}")

# ... call other functions like add_text_to_slide, add_image_to_slide, etc.
# Remember to pass the 'credentials' object as the first argument.
```

### Usage with LangChain

The package provides a helper function to easily get LangChain-compatible tools.

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI # Or any other LangChain compatible LLM
from google_slides_llm_tools import get_langchain_tools, authenticate

# --- Authentication Setup ---
# Method 1: Ensure ADC is configured globally (gcloud login, set-quota-project)
# LangChain tools will often pick up ADC automatically.

# Method 2: Authenticate explicitly and potentially pass creds if needed
# (though get_langchain_tools is designed to work with ADC by default)
# credentials = authenticate(use_adc=True, project_id='YOUR_PROJECT_ID')

# --- LangChain Setup ---
# Get the Google Slides tools configured for LangChain
# It implicitly uses the underlying functions which expect ADC by default.
tools = get_langchain_tools() # Add arguments here if customization is needed

# Create an LLM instance
llm = ChatOpenAI(temperature=0, model_name="gpt-4") # Example

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS, # Or another suitable agent type
    verbose=True
)

# Run the agent
try:
    result = agent.run(
        "Create a new Google Slides presentation named 'AI Report Q3'. "
        "Add a title slide with that name. Then add a second slide with layout 'TITLE_AND_BODY', "
        "set its title to 'Key Findings', and add a bullet point saying 'Reached new markets'."
    )
    print("Agent finished successfully.")
    print("Result:", result) # Note: agent.run often returns final string answer
except Exception as e:
    print(f"Agent execution failed: {e}")

```

See the [LangChain example](examples/langchain_example.py) for a more complete example.

---

## Available Tools

The package provides tools covering these categories (usable via MCP or LangChain):

- **Slides Operations**: Create, read, update, and delete slides and presentations
- **Formatting**: Add and format text
- **Multimedia**: Add images, videos, and audio links
- **Data**: Integrate with Google Sheets (creating charts/tables - *if implemented*)
- **Templates**: Apply layouts, duplicate presentations
- **Collaboration**: Manage permissions and sharing
- **Animations**: Set slide transitions (*if implemented*)
- **Export**: Export presentations/slides to PDF or get thumbnails

*Refer to the source code docstrings or specific function signatures for detailed parameters.*

## Documentation

For more detailed documentation on each function/tool, refer to the docstrings in the source code.

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## Testing

This package includes tests using Python's `unittest` framework, primarily using mock objects.

To run the tests:

```bash
./run_tests.py # Or python -m unittest discover tests
```

For details, see the [Testing Guide](TESTING.md).

## License

MIT License 