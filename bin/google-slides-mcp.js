#!/usr/bin/env node

const { spawn } = require('child_process');
const { Command } = require('commander');
const fs = require('fs');
const path = require('path');

// Read version from package.json
const packageJsonPath = path.resolve(__dirname, '../package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const version = packageJson.version;

const program = new Command();

program
  .version(version)
  .option('--credentials <path>', 'Path to Google OAuth credentials JSON file')
  .option('--use-adc', 'Use Application Default Credentials (gcloud auth application-default login)')
  .option('--project <id>', 'Google Cloud project ID to use for ADC')
  .option('-p, --port <number>', 'Port to run the server on', '8000')
  .parse(process.argv);

const options = program.opts();

// Validate arguments
if (!options.useAdc && !options.credentials) {
  console.error('\x1b[31mError: Must provide either --credentials <path> or --use-adc\x1b[0m');
  program.help({ error: true }); // Show help and exit
}

if (options.useAdc && options.credentials) {
  console.warn('\x1b[33mWarning: Both --use-adc and --credentials provided. Using --use-adc.\x1b[0m');
  delete options.credentials; // Prioritize ADC
}

// Build the command to run the Python server
// We assume 'python' is in the PATH and the google_slides_llm_tools package is installed
const pythonExecutable = process.platform === 'win32' ? 'python.exe' : 'python';
const pythonArgs = [
  '-m', 'google_slides_llm_tools.mcp_server',
  '--port', options.port
];

if (options.useAdc) {
  pythonArgs.push('--use-adc');
  if (options.project) {
    pythonArgs.push('--project', options.project);
  }
} else if (options.credentials) {
  // Make sure the path exists (basic check)
  try {
    require('fs').accessSync(options.credentials);
  } catch (err) {
    console.error(`\x1b[31mError: Credentials file not found at ${options.credentials}\x1b[0m`);
    process.exit(1);
  }
  pythonArgs.push('--credentials', options.credentials);
}

console.log('\x1b[34mStarting Google Slides MCP Server via Python backend...\x1b[0m');
console.log(` -> Authentication: ${options.useAdc ? 'Application Default Credentials' + (options.project ? ` (Project: ${options.project})` : '') : 'Credentials file (' + options.credentials + ')'}`);
console.log(` -> Server Port: ${options.port}`);
console.log(` -> Executing: ${pythonExecutable} ${pythonArgs.join(' ')}`);

// Launch the Python process
const pythonProcess = spawn(pythonExecutable, pythonArgs, {
  stdio: 'inherit' // Pass stdin, stdout, stderr directly
});

// Handle process events
pythonProcess.on('error', (err) => {
  console.error('\x1b[31mFailed to start Python server process:\x1b[0m', err);
  console.error('\n\x1b[33mTroubleshooting:\x1b[0m'); // Explicitly reset color
  console.error(`  - Ensure Python 3.8+ is installed and accessible via the '${pythonExecutable}' command.`);
  console.error("  - Ensure the 'google-slides-llm-tools' Python package is installed in the environment where Python runs (`pip install google-slides-llm-tools`).");
  process.exit(1);
});

pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.log(`\x1b[31mPython server process exited with code ${code}\x1b[0m`);
  }
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n\x1b[34mReceived SIGINT. Shutting down Python server...\x1b[0m');
  if (pythonProcess && !pythonProcess.killed) {
      pythonProcess.kill('SIGINT');
  }
});

process.on('SIGTERM', () => {
  console.log('\n\x1b[34mReceived SIGTERM. Shutting down Python server...\x1b[0m');
  if (pythonProcess && !pythonProcess.killed) {
      pythonProcess.kill('SIGTERM');
  }
}); 