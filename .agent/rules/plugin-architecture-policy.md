---
description: Universal rules for plugin file duplication, symlinks, cross-plugin dependency bounds, and relative execution paths.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/*.py", "plugins/**/*.md"]
---

# Plugin Architecture & Coupling Policy

**Full ADR context → `ADRs/001_` through `005_`**

## 1. Separation of Concerns & Loose Coupling

1. **Transitional Architectures**: Heavy orchestration frameworks (e.g., `spec-kitty-plugin`, `agent-agentic-os`, `agent-loops`) are treated as *Transitional Architectures*. They exist only until native AI SDKs (like Claude or GitHub Copilot) build these operational features inherently. 
2. **Strict Decoupling (Skills are Apps)**: Functional skills and scripts must **NEVER** hard-code dependencies on transitional frameworks to execute.
3. **Pluggable Independence**: If a user runs `npx skills add <some-plugin>`, that plugin MUST function completely in isolation. It cannot crash or halt because `spec-kitty` or the `agent-agentic-os` memory manager happens to be missing.
4. **Agent Delegation over Code Interfaces**: If a plugin requires coordination with another plugin, it must do so via Natural Language agent instructions (e.g., *"Please invoke the `spec-kitty-agent` to..."*) rather than hardcoded Python imports, hidden filesystem state manipulations, or rigid cross-plugin bindings.

---

## 2. Zero Duplication & Self-Contained Skill Structure (Hub-and-Spoke)

1. **Hub Placement (Plugin Root)**: Shared scripts, assets, templates, and references within a plugin must live exactly *once* at the plugin's root (e.g., `plugins/<plugin>/scripts/`, `assets/`, `references/`). Do not author primary files directly inside a skill directory.
2. **Spoke Subdirectories (Skill Root)**: When authoring or adding any skill (`plugins/<plugin>/skills/<skill-name>/`), you must create matching subdirectories for every required resource category:
   - `skills/<skill-name>/scripts/`
   - `skills/<skill-name>/assets/` (if templates/assets are consumed)
   - `skills/<skill-name>/references/` (if documentation/reference guides are consumed)
3. **Mandatory `symlink-manager` Creation & Tracking**:
   - Every resource file needed by the skill must be symlinked into the skill's subfolder using `symlink_manager.py create --src <hub-file> --dst <spoke-file>`.
   - **File-Level Symlinks ONLY**: Directory-level symlinks are strictly forbidden because package managers and installer hooks drop them during deployment.
   - All symlinks must be tracked in the repository-wide [`symlinks.json`](file:///C:/Users/RICHFREM/source/repos/sharepoint-knowledge-workbench/symlinks.json) manifest so they can be audited (`symlink_manager.py audit`) and restored across Windows, macOS, and Linux (`symlink_manager.py restore`).
4. **Canonical Authority**: The copy of a file inside the skill's directory (the symlink target) is the authoritative version at runtime. The source at the plugin root is the origin — changes must propagate to the skill copies via the plugin installer or manual sync.

---

## 3. Strict Relative Path Execution

1. **Relative to Skill Root**: Inside `SKILL.md` workflows, path references must always be **relative to the skill root** (e.g., `../scripts/script.py` or `python3 scripts/script.py`). **Never use absolute paths or paths relative to the repository root.**
2. **Self-Contained Content**: Every file a skill references must be present inside the skill's directory — either as a hard copy or a symlink. A skill must be fully self-contained. Do not reference files outside the skill folder from within a command.

**Correct:**
```bash
../references/diagrams/workflows/discovery.mmd
../scripts/miner.py
python3 scripts/helper.py
```

**Incorrect:**
```bash
docs/diagrams/workflows/discovery.mmd
plugins/legacy-system/scripts/miner.py
C:\Users\...\miner.py
```

### Install Locations Reference
Skills are installed by installers into dynamic directories:
- `.agents/skills/<skill-name>/` (canonical)
- `.agent/skills/<skill-name>/`
- `.claude/skills/<skill-name>/`

After installation, relative paths inside commands resolve from the skill root at the installed location. Verify paths against the installed structure, not the source tree.
