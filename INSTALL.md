# Repository Installation & Lifecycle — Central Authority

This document defines how to install, configure, update, and manage plugins and skills in the **SharePoint Knowledge Workbench** (`@sharepoint/sharepoint-workbench`), as well as how to pair it with governance extensions from the universal **Agent Plugins & Skills** monorepo (`agent-plugins-skills`).

All packages are managed with [APM](https://github.com/microsoft/apm) (Agent Package Manager). APM copies skills and subagents from `plugins/sharepoint-workbench/.apm/` into your agent harness folders (`.claude/`, `.agents/`, `~/.gemini/antigravity-cli/`), keeps a manifest and lockfile, and handles updates and removal on Windows, macOS and Linux with no symlinks and no build step.

## Dependencies and install order

The workbench is a **level 2** package. It sits on two level 1 sources, which have no dependencies of their own:

| Level | Package | Repository |
|---|---|---|
| 1 | `bc-gov-design-system` | [`richfrem/bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system) |
| 1 | the six `agent-plugins-skills` plugins | [`richfrem/agent-plugins-skills`](https://github.com/richfrem/agent-plugins-skills) |
| 2 | `sharepoint-workbench` (this repo) | this repo |

`plugins/sharepoint-workbench/apm.yml` declares no dependencies, so installing that package alone never pulls anything extra. The **root `apm.yml`** of this repo lists everything needed: the workbench plugin (`./plugins/sharepoint-workbench`) and the level 1 packages it builds on (from GitHub). Install according to the scope you choose:

- **Global (default):** install level 1 first (section 4), then the workbench (section 3). Both go into `~/.apm/apm.yml`. To install the workbench and everything in the root `apm.yml` with one command from the repo root: `apm install --global "$PWD" --target claude,copilot,codex,agy --parallel-downloads 0` (untested end to end; the level 1 packages come from GitHub, not from your local clones). Don't run a plain `apm install` for a global setup; it installs into the project.
- **Project:** run `apm install` at the repo root. It installs everything listed in the root `apm.yml` into the project, so no separate workbench step is needed. Don't also install any of them globally.

Check what is already global first:

```bash
apm deps list --global
```

---

## 📦 Option 1: APM Package Management (Recommended)

### 1. Install the APM CLI

Use APM 0.35.0 or newer; the `agy` (Antigravity) target needs it.

**macOS / Linux:**
```bash
curl -sSL https://aka.ms/apm-unix | sh -s -- @v0.35.0
```

**Windows (PowerShell):**
```powershell
irm https://aka.ms/apm-windows | iex
```

Verify the installation:
```bash
apm --version
```

---

### 2. Get the repository

```bash
git clone https://github.com/bcgov/sharepoint-knowledge-workbench.git
cd sharepoint-knowledge-workbench
git checkout <tag-or-commit>      # optional: pin a release
```

---

### 3. Install the SharePoint Knowledge Workbench

#### A. Global Install (Recommended for Workstations)
Make workbench skills and agents available in every project. Global installs need the **absolute path** to the plugin folder; a relative path such as `./plugins/sharepoint-workbench` is rejected.

**Windows (PowerShell):**
```powershell
apm install "$PWD\plugins\sharepoint-workbench" --global --target claude,copilot,codex,agy --parallel-downloads 0
```

**macOS / Linux:**
```bash
apm install "$PWD/plugins/sharepoint-workbench" --global --target claude,copilot,codex,agy
```

`--parallel-downloads 0` avoids an "Access denied" error on Windows when APM renames its staging folder. If a skill folder already exists that APM did not create, APM skips it; add `--force` to overwrite.

The global installation writes to your workstation profile directories:
```text
APM state & cache:           ~/.apm/                              (Windows: %USERPROFILE%\.apm\)
Claude Code skills:          ~/.claude/skills/
Copilot & Codex skills:      ~/.agents/skills/                    (shared)
Antigravity (agy) skills:    ~/.gemini/antigravity-cli/skills/
```

Global (user-scope) support differs by harness: `claude` supports every primitive; `copilot`, `codex` and `agy` support skills but only some other primitives (for `agy`, hooks and agents are not installed globally).

#### B. Project-Local Install (For Consumer Repositories & Pilots)
To install the workbench into one project (e.g. `jag-csb-intranet`), run from that project's root and point at your clone:

```bash
cd <path-to-consumer-repo>
apm install <path-to-clone>/plugins/sharepoint-workbench --target claude,copilot,codex,agy
```

This creates a local `apm.yml` and `apm.lock.yaml` in the project root and provisions skills to `.claude/skills/` and `.agents/skills/`. Commit `apm.yml` and `apm.lock.yaml` together. In CI, reproduce the exact install with `apm install --frozen`.

#### Windows vs macOS / Linux

| | Windows | macOS / Linux |
| :--- | :--- | :--- |
| Install APM | `irm https://aka.ms/apm-windows \| iex` | `curl -sSL https://aka.ms/apm-unix \| sh -s -- @v0.35.0` |
| Plugin path | Absolute, `"$PWD\plugins\sharepoint-workbench"` | Absolute, `"$PWD/plugins/sharepoint-workbench"` |
| Extra flag | `--parallel-downloads 0` | not needed |
| State folder | `%USERPROFILE%\.apm\` | `~/.apm/` |

---

### 4. Install the level 1 dependencies first (`agent-plugins-skills`, `bc-gov-design-system`)

Install these **before** the workbench when going global (see "Dependencies and install order"). Install the design system from its clone, with its absolute path, then the `agent-plugins-skills` plugins. Its plugins are installed the same way, from a clone, with absolute paths; there is no separate build step. See that repository's `INSTALL.md` for the full list and per-skill selection.

```bash
# Windows (PowerShell): the design system, from your clone of bc-gov-design-system
apm install "<path-to-clone>\bc-gov-design-system" --global --target claude,copilot,codex,agy --parallel-downloads 0

git clone https://github.com/richfrem/agent-plugins-skills.git
cd agent-plugins-skills

# Windows (PowerShell); on macOS / Linux use "$PWD/plugins/<name>" and drop --parallel-downloads 0
apm install "$PWD\plugins\agent-agentic-os" "$PWD\plugins\dev-utils" --global --target claude,copilot,codex,agy --parallel-downloads 0
```

To install every `agent-plugins-skills` plugin in one command, run this from your `agent-plugins-skills` clone (Windows, PowerShell):

```powershell
$plugins = Get-ChildItem plugins -Directory | Where-Object { Test-Path "$($_.FullName)\apm.yml" } | ForEach-Object { $_.FullName }
apm install @plugins --global --target claude,copilot,codex,agy --parallel-downloads 0
```

macOS / Linux:

```bash
apm install $(for d in "$PWD"/plugins/*/; do [ -f "$d/apm.yml" ] && echo "${d%/}"; done) --global --target claude,copilot,codex,agy
```

---

### 5. Updating & Managing Installed Packages

```bash
# List all installed APM packages and active client skills
apm list

# Update: pull the new release in your clone, then reinstall from it
git pull && apm install <absolute-path-to-clone>/plugins/sharepoint-workbench --global --target claude,copilot,codex,agy

# Uninstall the workbench package
apm uninstall <absolute-path-to-clone>/plugins/sharepoint-workbench --global
```

---

### 6. Troubleshooting on Windows

**`Failed to resolve transitive dep ... [WinError 3] The system cannot find the path specified`**, with paths under `%LOCALAPPDATA%\apm\cache\git\checkouts_v1\...`
- Cause: this happens when APM installs from a GitHub reference (for example `bcgov/sharepoint-knowledge-workbench`) instead of a local folder. Its git cache folder plus the workbench's deep skill paths go over Windows' 260-character path limit. In one failing log the source paths were 256 to 315 characters, so all 11 skills failed.
- Fix: install from a clone at a short path (for example `C:\src\sharepoint-knowledge-workbench`) using the absolute-path command in section 3. If you must install from GitHub, enable long paths first: run as administrator `New-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force`, run `git config --global core.longpaths true`, then restart your terminal. Long paths are not guaranteed to fix it; a short clone path is the reliable option.
- If another project's plugin lists this repository as a git dependency, that project's install hits the same limit. Point it at a local clone, or enable long paths.
- A failed install is safe to retry: APM restores `apm.yml` and commits nothing.

**`Access denied` on `.apm-resolution-staging`:** add `--parallel-downloads 0`. If an earlier install was interrupted, delete `%USERPROFILE%\.apm\apm_modules\.apm-resolution-staging` and `%USERPROFILE%\.apm\.apm-lifecycle.lock` and run it again.

**`N files skipped -- local files exist, not managed by APM`:** a skill folder already exists that APM did not create. Add `--force` to overwrite it.

**Relative path rejected on `--global`:** use the absolute path (section 3A).

---

## 🔌 Option 2: Native Agent Plugin Marketplace (Claude Code / Copilot)

If you are using **Claude Code** (2.1.81+) or the **GitHub Copilot CLI**, you can install directly via the marketplace:

### Claude Code Syntax
```text
# Add this repository as a marketplace
/plugin marketplace add richfrem/sharepoint-knowledge-workbench

# Install the unified plugin
/plugin install sharepoint-workbench@sharepoint-knowledge-workbench
```

### Copilot CLI Syntax
```bash
# Add this repository as a marketplace
copilot plugin marketplace add richfrem/sharepoint-knowledge-workbench

# Install the unified plugin
copilot plugin install sharepoint-workbench@richfrem-sharepoint-knowledge-workbench
```

---

## 🛠️ Local Development (Contributors & Maintainers)

For developers working directly on the workbench skills and scripts:

```bash
git clone https://github.com/richfrem/sharepoint-knowledge-workbench.git
cd sharepoint-knowledge-workbench

# Install in editable Python mode:
pip install -e plugins/sharepoint-workbench

# Run unit and integration tests:
pytest plugins/sharepoint-workbench/tests/

# Audit all skills against authoring standards:
for d in plugins/sharepoint-workbench/.apm/skills/*; do
  python3 <path-to-authoring-skills>/scripts/audit_skill.py "$d" --mode source
done

# Audit all 9 subagents:
python3 <path-to-authoring-subagents>/scripts/audit_sub_agent.py plugins/sharepoint-workbench --all
```

---

## 🔄 Upgrading from Legacy Layouts

The repository has completely retired the legacy 7-plugin and 108 micro-skill architecture:
1. **Unified Hub**: All 108 micro-skills are now consolidated into 11 domain hubs under `plugins/sharepoint-workbench/.apm/skills/` using modal execution (`references/modes/<mode>.md`).
2. **Zero Symlinks**: `symlinks.json`, `skills-lock.json`, `plugin-sources.json`, and `plugin-retention.json` have been retired. All skills are self-contained.
3. **Traceability**: See [`docs/plans/master_migration_inventory.csv`](docs/plans/master_migration_inventory.csv) for the complete 1:1 old-to-new mapping.
4. **Consumer Guidance**: See [`docs/plans/csb_intranet_sp_migration_refactor_plan.md`](docs/plans/csb_intranet_sp_migration_refactor_plan.md) for downstream migration steps.
