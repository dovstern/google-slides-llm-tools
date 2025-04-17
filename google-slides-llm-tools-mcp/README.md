# Google Slides LLM Tools - MCP Server (npx runner)

[![npm version](https://badge.fury.io/js/google-slides-mcp.svg)](https://badge.fury.io/js/google-slides-mcp)

This package provides a convenient command-line interface (CLI) wrapper to run the [google-slides-llm-tools](https://github.com/YOUR_USERNAME/google-slides-llm-tools) Python package's MCP server. It allows you to easily start the server using `npx` without needing to manage a Python environment directly for the server process itself (though Python and the underlying package are still required).

This enables tools like Claude Desktop, Cursor, or other MCP clients to interact with Google Slides.

## Prerequisites

Before using this package, ensure you have the following installed:

1.  **Node.js and npm:** Required to run `npx`. Download from [nodejs.org](https://nodejs.org/).
2.  **Python:** Version 3.8 or higher. Required by the underlying `google-slides-llm-tools` package. Download from [python.org](https://www.python.org/).
3.  **google-slides-llm-tools Python Package:** The core Python package must be installed in an accessible Python environment. Install it using pip:
    ```bash
    pip install google-slides-llm-tools
    ```
4.  **Google Cloud Credentials:** You need credentials to allow the server to access the Google Slides and Drive APIs. See the Authentication Setup section below.

## Quick Start

Once the prerequisites are met, you can run the server directly using `npx`:

```bash
# Using Application Default Credentials (ADC) - Recommended
# Make sure you've run `gcloud auth application-default login` and `gcloud auth application-default set-quota-project YOUR_PROJECT_ID`
npx google-slides-mcp --use-adc --project YOUR_PROJECT_ID

# OR Using a Credentials File (OAuth or Service Account JSON)
npx google-slides-mcp --credentials /path/to/your/credentials.json
```

Replace `YOUR_PROJECT_ID` and `/path/to/your/credentials.json` accordingly.

The server will start, using the specified authentication method and listening on the default port (8000). You can then connect your MCP client (e.g., Cursor, Claude) to `http://localhost:8000`.

## Authentication Setup

The server needs to authenticate with Google Cloud. Choose one method:

**Method 1: Application Default Credentials (ADC) - Recommended**

1.  **Install Google Cloud SDK:** If you haven't already, [install `gcloud`](https://cloud.google.com/sdk/docs/install).
2.  **Login via `gcloud`:**
    ```bash
    gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive
    ```
3.  **Set Quota Project:**
    ```bash
    gcloud auth application-default set-quota-project YOUR_PROJECT_ID
    ```
    Replace `YOUR_PROJECT_ID`.
4.  **Run with `npx`:** Use the `--use-adc` and `--project YOUR_PROJECT_ID` flags.

**Method 2: Credentials File (OAuth or Service Account)**

1.  **Create/Download Credentials:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/) -> APIs & Services -> Credentials.
    *   Create either an "OAuth 2.0 Client ID" (Desktop app type) or a "Service Account Key" (JSON format).
    *   Download the JSON file securely.
    *   Ensure the credentials have scopes/permissions for Slides and Drive.
2.  **Run with `npx`:** Use the `--credentials /path/to/your/credentials.json` flag.

## Command-Line Options

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

## Usage with Clients

### Cursor / Generic Clients

1.  Start the server using `npx` as described above.
2.  Note the URL and port (e.g., `http://localhost:8000`).
3.  Provide this URL to your client when configuring the MCP endpoint.

### Claude Desktop

1.  Locate the Claude Desktop configuration file (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`).
2.  Edit the `mcpServers` section:
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
        // ... other servers
      }
    }
    ```
3.  Replace the arguments as needed for your authentication method.
4.  Restart Claude Desktop.

## Programmatic Usage (Advanced)

While primarily a CLI tool, you can technically start the server programmatically (this mainly spawns the CLI process):

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

## Publishing Guide (For Maintainers)

This package is configured for automated publishing to npm via GitHub Actions.

**Prerequisites:**

*   You need an account on [npmjs.com](https://www.npmjs.com/).
*   You must have permissions to publish this specific package on npm.
*   An npm automation token must be generated and stored as a repository secret named `NPM_TOKEN` in the GitHub repository settings (Settings > Secrets and variables > Actions).

**Steps to Publish:**

1.  **Update Code:** Make any necessary changes to the wrapper code (`bin/google-slides-mcp.js`, `index.js`, `README.md`, etc.).
2.  **Update Version:** Increment the `version` number in `package.json` according to [Semantic Versioning (SemVer)](https://semver.org/).
    *   Patch release (e.g., `0.1.1`): Bug fixes.
    *   Minor release (e.g., `0.2.0`): New features, backward-compatible.
    *   Major release (e.g., `1.0.0`): Breaking changes.
3.  **Commit Changes:** Commit your changes to version control (e.g., Git).
    ```bash
    git add .
    git commit -m "feat: Add new option X (v0.2.0)" # Or fix:, chore:, etc.
    ```
4.  **Create and Push Tag:** Create a git tag matching the version in `package.json` (prefixed with `v`) and push it to the repository.
    ```bash
    # Example for version 0.2.0
    git tag v0.2.0 
    git push origin v0.2.0 
    ```
    *(Alternatively, create the tag via the GitHub UI when creating a Release)*.

5.  **Monitor Action:** Pushing the tag will automatically trigger the "Publish NPM Package" GitHub Action defined in `.github/workflows/publish-npm.yml`. Monitor its progress in the "Actions" tab of the GitHub repository.

6.  **Verify:** Once the action completes successfully, check the package page on [npmjs.com](https://www.npmjs.com/package/google-slides-mcp) to ensure the new version is live.

**Manual Publishing (Fallback):**

If the GitHub Action fails or you need to publish manually:

1. Ensure you are logged in: `npm login`
2. Run from the package directory: `npm publish`

**Important Considerations:**

*   **Test Thoroughly:** Before creating a release tag, test the package locally using `npm link` or by installing it from a local tarball (`npm pack && npm install ./google-slides-mcp-*.tgz`).
*   **Dependencies:** Ensure the `dependencies` in `package.json` are correct.
*   **Python Dependency:** Remember this package *wraps* the Python package. Updates to the Python package might require updates (or at least testing) of this wrapper. Clearly document the compatible version(s) of `google-slides-llm-tools` if necessary.

## License

MIT 