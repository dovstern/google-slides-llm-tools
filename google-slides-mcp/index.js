const { spawn } = require('child_process');

/**
 * Starts the Google Slides MCP server programmatically.
 * Note: This primarily executes the CLI script and might have limitations
 * compared to a native Node.js server implementation.
 *
 * @param {object} options Configuration options.
 * @param {number} [options.port=8000] Port to run the server on.
 * @param {string} [options.credentials] Path to Google OAuth credentials JSON file.
 * @param {boolean} [options.useAdc=false] Use Application Default Credentials.
 * @param {string} [options.project] Google Cloud project ID for ADC.
 * @returns {Promise<import('child_process').ChildProcess>} A promise that resolves with the spawned child process.
 */
function startServer(options = {}) {
  return new Promise((resolve, reject) => {
    const { port = 8000, credentials, useAdc = false, project } = options;

    if (!useAdc && !credentials) {
      return reject(new Error('Must provide either options.credentials or options.useAdc'));
    }

    const scriptPath = require.resolve('./bin/google-slides-llm-tools-mcp.js');
    const nodeArgs = [scriptPath];

    nodeArgs.push('--port', port.toString());

    if (useAdc) {
      nodeArgs.push('--use-adc');
      if (project) {
        nodeArgs.push('--project', project);
      }
    } else if (credentials) {
      nodeArgs.push('--credentials', credentials);
    }

    console.log(`Programmatically starting MCP server: node ${nodeArgs.join(' ')}`);

    const childProcess = spawn(process.execPath, nodeArgs, {
        stdio: ['ignore', 'pipe', 'pipe'] // Don't inherit, capture output
    });

    childProcess.stdout.on('data', (data) => {
      console.log(`[MCP Server stdout]: ${data.toString().trim()}`);
      // Potentially resolve once a specific startup message is seen
      if (data.toString().includes('Starting Google Slides MCP Server')) {
          // We might resolve earlier, but let's wait a tiny bit for the python process to potentially fail
          setTimeout(() => resolve(childProcess), 500);
      }
    });

    childProcess.stderr.on('data', (data) => {
      console.error(`[MCP Server stderr]: ${data.toString().trim()}`);
    });

    childProcess.on('error', (err) => {
      reject(new Error(`Failed to spawn server process: ${err.message}`));
    });

    childProcess.on('close', (code) => {
      if (code !== 0) {
        console.warn(`MCP server process exited with code ${code}`);
        // Potentially reject if it closes unexpectedly early
      }
    });

    // Handle parent process exit
    process.on('exit', () => {
      if (!childProcess.killed) {
        childProcess.kill();
      }
    });

  });
}

module.exports = {
  startServer
}; 