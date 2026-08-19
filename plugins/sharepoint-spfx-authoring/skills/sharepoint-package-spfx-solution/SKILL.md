---
name: sharepoint-package-spfx-solution
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


> [!WARNING]
> **Do NOT run `npm audit fix --force`**: SPFx projects use strictly pinned toolchain packages (`@rushstack/heft`, `@microsoft/spfx-web-build-rig`). Running forced dependency upgrades will break the Heft build toolchain.

### Step 2: Execute Production Build, Package & Verify

Run the bundled helper script, pointing it at the SPFx solution root:

```powershell
pwsh -File scripts/package-spfx-solution.ps1 -SolutionPath path/to/spfx-solution-root
```

This runs `npx heft test --clean --production` followed by
`npx heft package-solution --production`, then confirms a non-empty `.sppkg` file exists under
`sharepoint/solution/`, printing PASS/FAIL for each stage.

*(Equivalently, if you prefer to run the underlying commands directly instead of the script):*
```powershell
$env:Path = "C:\Users\RICHFREM\AppData\Local\nvm\v22.23.2;" + $env:Path; npx heft test --clean --production && npx heft package-solution --production
```

*(Or via npm script defined in package.json):*
```bash
npm run build
```

### Step 3: Verify Output Artifacts

The helper script in Step 2 already verifies the package; if running the commands manually instead,
confirm the command completed with exit code 0 and generated the final `.sppkg` file at:

```text
sharepoint/solution/<solution-name>.sppkg
```

Check that the generated package size is >0 KB and contains no build or linting errors.

