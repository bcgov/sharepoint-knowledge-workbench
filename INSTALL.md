# Repository Installation & Lifecycle — Central Authority

This document defines how to install, configure, update, and manage plugins and skills in the **SharePoint Knowledge Workbench** (`@sharepoint/sharepoint-workbench`), as well as how to pair it with governance extensions from the universal **Agent Plugins & Skills** monorepo (`agent-plugins-skills`).

All packages are managed with [APM](https://github.com/microsoft/apm) (Agent Package Manager). APM copies skills and subagents from `plugins/sharepoint-workbench/.apm/` into your agent harness folders (`.claude/`, `.agents/`, `~/.gemini/antigravity-cli/`), keeps a manifest and lockfile, and handles updates and removal on Windows, macOS and Linux with no symlinks and no build step.

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

### 4. Install Companion Governance Skills (`agent-plugins-skills`)

For repository governance, issue tracking, and agent lifecycle tooling, install packages from the sibling [`agent-plugins-skills`](https://github.com/richfrem/agent-plugins-skills) repository. Its plugins are installed the same way, from a clone, with absolute paths; there is no separate build step. See that repository's `INSTALL.md` for the full list and per-skill selection.

```bash
git clone https://github.com/richfrem/agent-plugins-skills.git
cd agent-plugins-skills

# Windows (PowerShell); on macOS / Linux use "$PWD/plugins/<name>" and drop --parallel-downloads 0
apm install "$PWD\plugins\agent-agentic-os" "$PWD\plugins\dev-utils" --global --target claude,copilot,codex,agy --parallel-downloads 0
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
