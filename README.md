# Google Slides LLM Tools

A Python package providing tools for LLMs to interact with Google Slides, supporting both LangChain tools and MCP (Model Context Protocol) server functionality for integration with various LLM clients and agents.

## Features

- Create and manipulate Google Slides presentations
- Format text and add multimedia content
- Apply templates and layouts
- Manage collaboration and sharing
- Set animations and transitions
- Export presentations to various formats
- Integration with both LangChain and MCP server

---

## Guide 1: Using the MCP Server

This guide explains how to set up and run the MCP (Model Context Protocol) server using `npx`, allowing LLM clients like Claude or Cursor to interact with Google Slides.

### Prerequisites

* Node.js and npm (Node Package Manager) installed
* A Google Cloud project with the Google Slides API and Google Drive API enabled. Go to the [Google Cloud Console](https://console.cloud.google.com/) to enable them for your project if needed.
* Google Cloud authentication credentials (either OAuth credentials or service account key)

### Installation & Setup

No installation required - you'll run the server directly with `npx`.

### Authentication Setup

Before running the server, you need to set up authentication with Google Cloud to access the Slides and Drive APIs:

**Method 1: Using OAuth Credentials**

1. **Create OAuth Credentials:**
   * Go to the [Google Cloud Console](https://console.cloud.google.com/)
   * Navigate to "APIs & Services" → "Credentials"
   * Create an OAuth 2.0 Client ID (Desktop application type)
   * Download the credentials JSON file to a secure location on your computer

**Method 2: Using Service Account**

1. **Create Service Account Key:**
   * Go to the [Google Cloud Console](https://console.cloud.google.com/)
   * Navigate to "IAM & Admin" → "Service Accounts"
   * Create a service account or use an existing one
   * Create a new key (JSON format) and download it to a secure location
   * Ensure the service account has appropriate roles for Google Slides and Drive

### Running the Server

Run the MCP server using `npx` and point it to your credentials file:

```bash
npx google-slides-llm-tools-mcp --credentials /path/to/your/credentials.json
```

Replace `/path/to/your/credentials.json` with the actual path to your OAuth credentials or service account key file.

#### Additional Options

* **Specify port:** By default, the server runs on port 8000. To use a different port:
  ```bash
  npx google-slides-llm-tools-mcp --credentials /path/to/your/credentials.json --port 8001
  ```

* **Using ADC (Application Default Credentials):** If you've configured ADC using the Google Cloud SDK:
  ```bash
  npx google-slides-llm-tools-mcp --use-adc
  ```

### Connecting Clients

Once the server is running, connect your LLM client:

#### Connecting Cursor (and similar Generic Clients)

1. Note the URL and port the server is running on (e.g., `http://localhost:8000` if running locally on the default port)
2. In your LLM client (like Cursor), provide this URL when prompted for an MCP server address or tool provider endpoint
3. The LLM assistant should then be able to discover and utilize the Google Slides tools exposed by the server

#### Connecting Claude Desktop

Claude Desktop can also use the MCP server through its configuration:

1. **Locate the Claude Desktop configuration file:**
   * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   * Windows: `C:\Users\USERNAME\AppData\Roaming\Claude\claude_desktop_config.json`

2. **Edit the configuration file:**
   ```json
   {
     "mcpServers": {
       "google-slides": {
         "command": "npx",
         "args": [
           "google-slides-llm-tools-mcp",
           "--credentials",
           "/path/to/your/google_credentials.json"
         ]
       }
     }
   }
   ```
   Replace `/path/to/your/google_credentials.json` with the actual path to your credentials file. You can also use `--use-adc` instead of `--credentials` if you prefer using Application Default Credentials.

3. **Restart Claude Desktop.**

### Debugging Common Server/API Issues

If you encounter errors, especially `403 Forbidden` errors when the server tries to call Google APIs:

1. **APIs Enabled:** Double-check that both the Google Slides API and Google Drive API are enabled for your Google Cloud Project in the [Cloud Console](https://console.developers.google.com/apis/dashboard).

2. **Credentials:**
   * Verify the path to your credentials file is correct
   * Ensure the credentials have the necessary scopes:
     * `https://www.googleapis.com/auth/presentations`
     * `https://www.googleapis.com/auth/drive` 
   * If using a service account, ensure it has appropriate permissions

3. **Project ID:** If using `--use-adc`, you might need to explicitly set the project ID:
   ```bash
   npx google-slides-llm-tools-mcp --use-adc --project YOUR_PROJECT_ID
   ```

### Advanced: Programmatic Usage

For advanced users who want to use the MCP server programmatically (e.g., from Node.js):

```javascript
const { startServer } = require('google-slides-llm-tools-mcp');

startServer({
  port: 8000,
  credentials: '/path/to/your/credentials.json',
  // Or useAdc: true
}).then(() => {
  console.log('Server started successfully');
}).catch(error => {
  console.error('Failed to start server:', error);
});
```

*Note: This advanced usage requires installing the package with npm: `npm install google-slides-llm-tools-mcp`*

---

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