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

### 2. Install from GitHub or get a local clone

A clone is optional. From the consuming project's root, install the workbench directly from GitHub:

```bash
apm install https://github.com/bcgov/sharepoint-knowledge-workbench --target claude,copilot,codex,agy
```

The root `apm.yml` includes the unified `plugins/sharepoint-workbench` package. To select that
plugin directly, use APM's `owner/repo/subdirectory` shorthand:

```bash
apm install bcgov/sharepoint-knowledge-workbench/plugins/sharepoint-workbench --target codex,copilot
```

Use the shorthand for plugin subdirectories: APM 0.33.0 treats extra path segments in an HTTPS URL
as part of the repository name rather than a plugin path. For user-wide availability, add `--global`:

```bash
apm install https://github.com/bcgov/sharepoint-knowledge-workbench --global --target claude,copilot,codex,agy
```

Unpinned commands select the default branch when initially resolved. For reproducible installs,
append an existing tag or commit SHA after the complete package path (replace the placeholder):

```bash
apm install "https://github.com/bcgov/sharepoint-knowledge-workbench#<tag-or-commit>" --target claude,copilot,codex,agy
apm install "bcgov/sharepoint-knowledge-workbench/plugins/sharepoint-workbench#<tag-or-commit>" --target codex,copilot
```

Select multiple harnesses with commas; repeating `--target` retains only its last value. Other targets
include `gemini`, `cursor`, `opencode` and `windsurf`; use `apm install --help` for the full list.
On Windows, add `--parallel-downloads 0`. If GitHub cache paths exceed Windows' path limit, use the
short-clone fallback in [Troubleshooting on Windows](#6-troubleshooting-on-windows).
Do not install the same workbench package from both GitHub and a local clone in the same scope.

#### Clone-based alternative

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

For repository governance, issue tracking, and agent lifecycle tooling, install packages from the sibling [`agent-plugins-skills`](https://github.com/richfrem/agent-plugins-skills) repository. Its plugins can also be installed directly from GitHub, without a clone or separate build step:

```bash
apm install https://github.com/richfrem/agent-plugins-skills --global --target claude,copilot,codex,agy
```

For selected companion plugins, use `richfrem/agent-plugins-skills/plugins/<plugin-name>` instead.
Append `#<tag-or-commit>` for a reproducible pin. See that repository's
[INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for the full list
and per-skill selection. Alternatively, install from a local clone with absolute paths:

```bash
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

For a GitHub installation, reinstall the same package path with the desired new or previous pin to
update or roll back. Replace the placeholder with an existing ref; omit `--global` for project scope:

```bash
apm install "https://github.com/bcgov/sharepoint-knowledge-workbench#<new-or-previous-tag-or-commit>" --global --target claude,copilot,codex,agy
```

For a clone-based installation, use the existing commands below:

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
