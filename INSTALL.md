# Repository Installation — Central Authority

This document defines the single, authoritative suite of installation methods for all domain plugins, skills, and agents in the **SharePoint Knowledge Workbench** ecosystem (`richfrem/sharepoint-knowledge-workbench`).

---

## Consumer Installation (Bootstrapping)

These commands are for consumers and project repositories (e.g. migration pilots, document conversion runs) who want to add plugins seamlessly *without* cloning the workbench repo. The single `.agents/` environment directory is **not committed** to your repo. It will be empty by default. Run one of the installers below to deploy plugins.

### Option 1: `uvx` — Modern Python Standard (Recommended)

If you have [uv](https://docs.astral.sh/uv/) installed, you get instantaneous, isolated installations natively cross-platform without Node.js.

```bash
# Interactive picker
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/sharepoint-knowledge-workbench

# Install everything non-interactively (no prompts)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/sharepoint-knowledge-workbench --all -y

# Install a specific domain plugin directly (e.g., content-assembly or sharepoint-discovery)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/sharepoint-knowledge-workbench/plugins/content-assembly -y
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/sharepoint-knowledge-workbench/plugins/sharepoint-discovery -y

# Preview what will be installed without writing any files
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/sharepoint-knowledge-workbench --dry-run
```

### Option 2: Fallback Bootstrap (Zero Tooling Assumptions)

If you don't use `uv`, you can install purely using standard Python tooling without cloning the repo.

**Mac / Linux:**
```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python - richfrem/sharepoint-knowledge-workbench
```

**Windows (PowerShell):**
```powershell
Invoke-RestMethod https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python - richfrem/sharepoint-knowledge-workbench
```

### Subsequent Installations

Because `uvx` and `bootstrap.py` execute ephemerally, you simply repeat the same command to add new plugins later. There is no local state to manage outside of your `.agents/` folder.

---

## Alternative: Agent Plugin Marketplace (Claude Code / Copilot)

If you are using **Claude Code** (2.1.81+) or the **Copilot Plugin CLI**, you can add this repository as a native marketplace and install plugins without leaving your terminal session:

### Claude Code Syntax
```text
# Add this repository to your known marketplaces
/plugin marketplace add richfrem/sharepoint-knowledge-workbench

# Open the interactive TUI to browse, discover, and install plugins
/plugin

# Or install a specific domain plugin directly
/plugin install content-extraction@sharepoint-knowledge-workbench
/plugin install sharepoint-discovery@sharepoint-knowledge-workbench
/plugin install sharepoint-provisioning@sharepoint-knowledge-workbench
```

### Copilot CLI Syntax
```bash
# Add this repository as a known marketplace
copilot plugin marketplace add richfrem/sharepoint-knowledge-workbench

# Browse, discover, and install plugins via TUI
copilot plugin

# Install a specific plugin directly (slugified marketplace ID)
copilot plugin install content-assembly@richfrem-sharepoint-knowledge-workbench
```

> [!NOTE]
> **Gemini CLI**: The `gemini extensions install` command installs the entire repository as a raw context bundle, not as discrete addressable plugins. For Gemini CLI, use **`uvx`** (Option 1 above) which correctly deploys individual plugins and skills into your `.agents/` folder.

---

## Alternative: npx skills CLI (Mac / Linux only)

> [!NOTE]
> **`npx skills add` installs skills only** — no commands, agents, or hooks. It also only works correctly on Mac/Linux (Git symlinks check out as plain-text files on Windows). For full plugin deployment on any platform, use `uvx` or `bootstrap.py`.

### Standard Commands
```bash
# Install a specific skill collection from this workbench
npx skills add richfrem/sharepoint-knowledge-workbench

# Install a specific plugin from the repository
npx skills add richfrem/sharepoint-knowledge-workbench/plugins/content-rendering

# Update all installed skills across all agents
npx skills update
```

> [!CAUTION] 
> **Broken Symlinks on Windows:** `npx skills add` fails on Windows because it fails to dereference Git symlinks correctly. Use `uvx` or `bootstrap.py` for full platform-agnostic deployment.

---

## Installer Comparison

| Method | Platform | Full Plugin | GitHub source | Notes |
|---|---|---|---|---|
| `uvx` ★ | **All** (Win/Mac/Linux) | ✅ skills + agents + commands + hooks | ✅ `owner/repo` | Recommended default |
| `bootstrap.py` | **All** (Win/Mac/Linux) | ✅ full | ✅ `owner/repo` | Zero-dependency fallback |
| Marketplace CLI ★ | **Claude / Copilot** | ✅ skills + agents + commands + hooks | ✅ | Native TUI / Marketplace |
| `npx skills add` | Mac/Linux only | ❌ skills only | ✅ | No Python required |

---

## Local Development (For Developers & Contributors)

If you have cloned this repository locally to develop or contribute to plugins:

```bash
git clone https://github.com/richfrem/sharepoint-knowledge-workbench.git
cd sharepoint-knowledge-workbench

# Install local plugin-installer skill into your environment if needed
python .agents/skills/plugin-installer/scripts/plugin_add.py ./plugins --all -y

# Or install individual plugins in editable Python mode:
pip install -e plugins/content-extraction
pip install -e plugins/content-structure-analysis
pip install -e plugins/content-assembly
pip install -e plugins/content-rendering

# Alternatively, you can use uvx locally against the repository:
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add ./plugins --all -y
```