---
trigger: always_on
description: Universal coding conventions for Python, TypeScript, and C#.
globs: ["*.py", "*.ts", "*.js", "*.cs"]
---

## 🎯 PURPOSE: Enable Agents to Understand Code at a Glance

Every script must document **what it does, what it needs, and how to use it** in the first 20 lines.

**Why:** In fresh agent sessions, agents cannot afford to spend 5-10 minutes reading implementations or running exploratory commands. By reading a 20-line header, agents must be able to:
- Understand the script's purpose in 30 seconds
- Know what files/APIs/dependencies it requires
- See usage examples without trial-and-error
- Identify key functions without code diving

This transforms agent onboarding from minutes to seconds.

---

## 📝 Coding Conventions (Summary)

**Full standards → `.agents/skills/coding-conventions-agent/SKILL.md` (installed locally via `bridge_installer.py`)**

### Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class.
2. **File headers** — every source file starts with a purpose header (Python, TS/JS, C#, and `.ps1` alike — the `.ps1` equivalent is a `.SYNOPSIS`/`.DESCRIPTION`/`.PARAMETER`/`.EXAMPLE` comment-based help block).
   - **Crucial**: The header must explicitly list **Key Input Dependencies** (e.g. private JSON databases like `portfolio.json` or `cash_flows.json`).
   - **Index & Preservation Directive**: File headers must contain a complete index list of all functions, methods, and procedures present in the file. Never remove or reduce existing utility documentation (like usage examples, DOM structures, or technical flags lists) during updates—always preserve and enrich.
   - **Purpose**: This enables clean, token-efficient discovery in new agent sessions. Incoming agents can scan the top of a file to instantly map its capabilities and required state files without reading the full implementation.
   - **No provenance/history in headers.** This repo's `plugins/` are meant to be reused standalone by future consumers who have never heard of this repo's own project history. A file header must never mention: which phase/wave it was built in, a source-repo commit hash, a source project's codename (e.g. "CMAT", "ITAU", "AG-CSB"), or a specific pilot site/tenant used as a worked example during development. Write the header as if the script always looked like this — what it does, its inputs, its outputs, its preconditions, and a calling example — not the story of how it got here. If provenance is worth recording at all (it usually isn't needed for a script to be usable), it belongs in a plugin-level `README.md`'s own "Provenance" section or a `docs/reports/` evidence file, never in the script a future consumer has to read to use the thing.
3. **Type hints** — all Python function signatures use type annotations.
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public), `Verb-PnPNounStyle`/`PascalCase` function names (PowerShell).
5. **Refactor threshold** — 50+ lines or 3+ nesting levels → extract helpers.
6. **Manifest schema** — use simple `{title, description, files}` format (ADR 097).

### 🔍 Automated Compliance Checks
To audit workspace source code compliance against these rules, run the developer conventions auditor script:
```bash
python3 .agents/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py
```
This utility outputs a detailed audit breakdown under `temp/workspace_conventions_report.md`.