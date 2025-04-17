#!/usr/bin/env node

/**
 * This script synchronizes version numbers between package.json and setup.py
 */

const fs = require('fs');
const path = require('path');

// Read package.json version
const packageJsonPath = path.resolve(__dirname, '../package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const version = packageJson.version;

console.log(`Current version from package.json: ${version}`);

// Update setup.py
const setupPyPath = path.resolve(__dirname, '../setup.py');
let setupPyContent = fs.readFileSync(setupPyPath, 'utf8');

// Replace version in setup.py using regex
const versionRegex = /(version\s*=\s*['"])[\d.]+(['"])/;
const newSetupPyContent = setupPyContent.replace(versionRegex, `$1${version}$2`);

if (setupPyContent !== newSetupPyContent) {
    fs.writeFileSync(setupPyPath, newSetupPyContent);
    console.log(`Updated setup.py with version ${version}`);
} else {
    console.log('setup.py already has the correct version.');
} 