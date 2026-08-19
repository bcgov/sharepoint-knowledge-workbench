# AGENTS.md / CLAUDE.md / GEMINI.md

Behavioral guidelines to reduce common LLM coding mistakes, plus project-specific context for this repository.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code/content that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use scripts.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent content, comments, or formatting.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead content, mention it — don't delete it.
- Every changed line/file should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Verify before claiming done.**

For multi-step tasks, state a brief plan and verify each step before saying it's complete.

---

## Project-Specific Context: SharePoint Knowledge Workbench

### Purpose & Architecture

This repository is the central public toolkit for the **AI-Assisted Structured Knowledge Workbench**, moving document-centric manuals (Word/PDF) into a content-centric model (**Content + Template + Renderer = Published Output**), and providing complete SharePoint discovery, schema reconciliation, tenant provisioning, and migration tooling.

The ecosystem is composed of **16 independently-installable domain plugins** located under `plugins/`:
- **Content Conversion (4 plugins):** `content-extraction`, `content-structure-analysis`, `content-assembly`, `content-rendering`
- **SharePoint Engineering (11 plugins):** `sharepoint-discovery`, `sharepoint-schema-reconciliation`, `sharepoint-provisioning`, `sharepoint-page-modernization`, `sharepoint-page-modernization-execution`, `sharepoint-link-remediation`, `sharepoint-content-migration`, `sharepoint-migration-planning`, `sharepoint-content-publication`, `sharepoint-spfx-authoring`, `sharepoint-agents-and-skills`
- **Environment & Setup:** `workbench-setup`

Each plugin is self-contained with its own tests, packaging, and skill definitions.

### Repository Layout

```
plugins/                 ← The 16 domain plugins & skill packages
docs/                    ← Initiative architecture, design specs, and reference catalog
.agent/rules/            ← Authoritative engineering rules and policies
.claude-plugin/          ← Marketplace definition (marketplace.json)
INSTALL.md               ← Complete installation and bootstrapping guide
```

Consumer documents, intake files, run outputs, and project-specific tests are managed in separate consumer repositories (e.g. project POC repositories).

### Sub-agent usage
Use the cheapest models possible where possible. If the job doesn't require spawning sub-agents, don't do so.

### Scratch Output
Write temporary files and intermediate analysis output to a `temp/` directory (git-ignored) — never to the project root directly.