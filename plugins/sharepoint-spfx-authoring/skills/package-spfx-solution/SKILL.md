---
name: package-spfx-solution
plugin: sharepoint-spfx-authoring
description: Automates production SPFx solution builds using Heft/Webpack and verifies .sppkg package integrity.
allowed-tools: Bash, Read, Write
---

# package-spfx-solution

## Overview

This skill provides step-by-step instructions for compiling, testing, and packaging an SPFx web part solution into a production `.sppkg` package ready for deployment to a SharePoint App Catalog.

## Prerequisites

- **Node.js**: v18 or v22 LTS
- **Terminal Pathing**: Ensure Node.js v22/v18 is active in your terminal session (`nvm use 22`).

## Core Workflow

### Step 1: Navigate to the SPFx Project Directory

```bash
cd path/to/spfx-solution-root
```

### Step 2: Execute Production Build & Package Command

For modern SPFx solutions using Heft (version 1.20+):

```powershell
$env:Path = "C:\Users\RICHFREM\AppData\Local\nvm\v22.23.2;" + $env:Path; npx heft test --clean --production && npx heft package-solution --production
```

*(Or via npm script defined in package.json):*
```bash
npm run build
```

### Step 3: Verify Output Artifacts

Confirm the command completed with exit code 0 and generated the final `.sppkg` file at:

```text
sharepoint/solution/<solution-name>.sppkg
```

Check that the generated package size is >0 KB and contains no build or linting errors.
