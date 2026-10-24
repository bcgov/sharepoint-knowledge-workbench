# Repository Installation & Package Management Guide

This document defines the single, authoritative suite of installation methods for the **SharePoint Knowledge Workbench** (`@sharepoint/sharepoint-workbench`).

---

## 📦 Primary Installation: APM (Agent Package Manager)

The modern, cross-platform standard for installing agent plugins and skills is **APM**. APM distributes the unified `@sharepoint/sharepoint-workbench` package directly across your active agent harnesses without Python dependencies or complex bootstrap scripts.

```bash
# Install globally for all supported agent harnesses (Claude, Copilot, Codex, Antigravity)
apm install @sharepoint/sharepoint-workbench --global --target claude,copilot,codex,antigravity

# Or install locally in your current project repository
apm install @sharepoint/sharepoint-workbench --target claude,copilot,codex,antigravity

# Update installed package to latest version
apm update @sharepoint/sharepoint-workbench

# Check installed packages and active client skills
apm list
```

---

## 🔌 Alternative: Agent Plugin Marketplace (Claude Code / Copilot)

If you are using **Claude Code** or the **GitHub Copilot CLI**, you can install the workbench directly via native marketplace integration:

### Claude Code Syntax
```text
# Add this repository to your known marketplaces
/plugin marketplace add richfrem/sharepoint-knowledge-workbench

# Open the interactive TUI to browse, discover, and install plugins
/plugin

# Or install the unified plugin directly
/plugin install sharepoint-workbench@sharepoint-knowledge-workbench
```

### Copilot CLI Syntax
```bash
# Add this repository as a known marketplace
copilot plugin marketplace add richfrem/sharepoint-knowledge-workbench

# Browse, discover, and install plugins via TUI
copilot plugin

# Or install the unified plugin directly (slugified ID)
copilot plugin install sharepoint-workbench@richfrem-sharepoint-knowledge-workbench
```

---

## 🛠️ Local Development (For Contributors & Maintainers)

If you have cloned this repository locally to develop or contribute to workbench skills:

```bash
git clone https://github.com/richfrem/sharepoint-knowledge-workbench.git
cd sharepoint-knowledge-workbench

# Install the unified plugin in editable Python mode:
pip install -e plugins/sharepoint-workbench

# Run the test suite:
pytest plugins/sharepoint-workbench/tests/

# Audit skills and sub-agents against authoring standards:
for d in plugins/sharepoint-workbench/skills/*; do
  python3 <path-to-authoring-skills>/scripts/audit_skill.py "$d" --mode source
done

python3 <path-to-authoring-subagents>/scripts/audit_sub_agent.py plugins/sharepoint-workbench --all
```

---

## 🔄 Upgrading from Legacy Layouts

The repository has completed its architectural consolidation:
1. **From 7 Plugins & 108 Micro-Skills ➔ 1 Canonical Plugin & 11 Domain Hubs**:
   - Legacy plugin folders (`sharepoint-workbench-setup`, `sharepoint-document-conversion`, `sharepoint-site-assessment`, `sharepoint-site-build-and-publish`, `sharepoint-site-migration`, `sharepoint-copilot-agents-and-skills`, `sharepoint-spfx-development`) have been retired.
   - All capabilities are unified under `plugins/sharepoint-workbench` (`@sharepoint/sharepoint-workbench`).
2. **Zero Symlink Architecture**:
   - `symlinks.json` has been retired.
   - All 11 domain skills are self-contained hubs with inlined resources and modal dispatch (`references/modes/<mode>.md`).
3. **Transition Mapping**:
   - Consult [`docs/plans/master_migration_inventory.csv`](docs/plans/master_migration_inventory.csv) for the exact 1:1 trace of all 108 former micro-skills into the new modal commands.
   - For downstream consumer projects (such as `csb-intranet`), follow the step-by-step guidance in [`docs/plans/csb_intranet_sp_migration_refactor_plan.md`](docs/plans/csb_intranet_sp_migration_refactor_plan.md).
