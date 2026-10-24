# Repository Installation & Lifecycle — Central Authority

This document defines how to install, configure, update, and manage plugins and skills in the **SharePoint Knowledge Workbench** (`@sharepoint/sharepoint-workbench`), as well as how to pair it with governance extensions from the universal **Agent Plugins & Skills** monorepo (`agent-plugins-skills`).

All packages are managed with [APM](https://github.com/microsoft/apm) (Agent Package Manager). APM copies skills, subagents, and tools directly into your active agent harness directories (`.claude/`, `.agents/`, `~/.gemini/antigravity-cli/`), maintains manifests and lockfiles, and handles updates and rollbacks natively across Windows, macOS, and Linux with zero symlinks.

---

## 📦 Option 1: APM Package Management (Recommended)

### 1. Install the APM CLI

If APM is not already installed on your workstation:

**macOS / Linux:**
```bash
curl -sSL https://aka.ms/apm-unix | sh -s -- @v0.33.0
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

### 2. Install the SharePoint Knowledge Workbench

#### A. Global Install (Recommended for Workstations)
Make workbench skills and agents available across all your coding projects:

```bash
# Install globally for all supported agent harnesses (Claude, Copilot, Codex, Antigravity)
apm install @sharepoint/sharepoint-workbench --global --target claude,copilot,codex,antigravity

# Or install directly from a local clone of this repository:
apm install ./plugins/sharepoint-workbench --global --target claude,copilot,codex,antigravity
```

The global installation writes directly to your workstation profile directories:
```text
APM state & cache:           ~/.apm/                              (Windows: %USERPROFILE%\.apm\)
Claude Code skills:          ~/.claude/skills/
Copilot & Codex skills:      ~/.agents/skills/                    (shared)
Antigravity (agy) skills:    ~/.gemini/antigravity-cli/skills/
```

#### B. Project-Local Install (For Consumer Repositories & Pilots)
To install the workbench into a specific migration pilot or project repository (e.g. `jag-csb-intranet`):

```bash
cd <path-to-consumer-repo>

# Install the unified workbench package
apm install @sharepoint/sharepoint-workbench --target claude,copilot,codex,antigravity
```

This creates a local `apm.yml` and `apm.lock.yaml` in the project root, and provisions skills to `.claude/skills/` and `.agents/skills/`.

---

### 3. Install Companion Governance Skills (`agent-plugins-skills`)

For repository governance, issue tracking, and agent lifecycle tooling, install companion packages from the sibling `agent-plugins-skills` repository:

```bash
# Clone and materialize the companion monorepo if needed
git clone https://github.com/richfrem/agent-plugins-skills.git
cd agent-plugins-skills
python3 plugins/agent-extension-authoring/skills/packaging-with-apm/scripts/materialize_copies.py

# Install core developer utilities and agent OS globally
apm install ./plugins/agent-agentic-os --global --target claude,copilot,codex,antigravity
apm install ./plugins/dev-utils --global --target claude,copilot,codex,antigravity
apm install ./plugins/cli-agents --global --target claude,copilot,codex,antigravity
```

---

### 4. Updating & Managing Installed Packages

```bash
# List all installed APM packages and active client skills
apm list

# Update the workbench package to the latest version
apm update @sharepoint/sharepoint-workbench

# Uninstall the workbench package
apm uninstall @sharepoint/sharepoint-workbench --global
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
