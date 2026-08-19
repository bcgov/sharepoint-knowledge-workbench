# SharePoint & Content Plugin Taxonomy Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize domain prefixes across all plugins (`content-*`, `sharepoint-*`, `workbench-*`) and skills, resolve misnamed/stranded executors (2 plugin renames, 1 merge, 1 split), fill 16 confirmed capability gaps (grep-verified against `main` + enterprise SharePoint provisioning scripts), harden safety purity tests, and fix all pre-existing defects (`marketplace.json`, stale docs/frontmatter).

**Architecture:** Every task is either (a) a pure rename/move of already-working, already-tested code — verified via git rename detection and re-running test suites, or (b) a new PnP.PowerShell executor script following the exact pattern already proven across sibling scripts (strict mode, dry-run by default, `-Execute` + operation-specific `-ConfirmToken`, `Get-WorkbenchConnectionConfig.ps1` for connection resolution, `Connect-PnPOnline -Interactive`, outcome status JSON).

**Tech Stack:** PowerShell 7 (`pwsh`) + PnP.PowerShell cmdlets, Python 3.10+/pytest, Markdown (`SKILL.md`/`plugin.yaml`/`plugin.json`), this repo's hub-and-spoke symlink convention via `.agents/skills/symlink-manager/scripts/symlink_manager.py`.

**Spec:** `docs/superpowers/specs/2026-08-18-sharepoint-plugin-taxonomy-redesign-spec.md` — read this first.

## Global Constraints & Mandatory Rules

- **Coding Conventions (`.agent/rules/coding-conventions.md`)**: Every `.ps1` script begins with a standard help header (`.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`). Python scripts use dual-layer docstrings and type hints.
- **TDD Requirement (`.agent/rules/test-driven-development.md`)**: New Python modules (`schema_scaffold.py`, `mapping_utils.py`) must have failing tests written before implementation.
- **Hub-and-Spoke Symlinks (`.agent/rules/plugin-architecture-policy.md`)**: Real scripts live in `plugins/<plugin>/scripts/`. Skill directories only contain file-level symlinks created via `.agents/skills/symlink-manager/scripts/symlink_manager.py`.
- **Git Rename Preservation (`.agent/rules/self-evolution-policy.md`)**: Perform moves using `git mv` and stage in batches so git tracks renames (`R`) rather than delete/create pairs.
- **Worktree Lifecycle (`.agent/rules/worktree-lifecycle-management.md`)**: When working in worktrees, progress must be reported using the exact 6-state vocabulary (`written in worktree`, `committed in worktree`, `pushed to origin`, `merged into origin/main`, `local branch ref updated`, `checked out on disk`).


---

## Task 1: Fix pre-existing defects independent of any rename

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `plugins/sharepoint-content-publication/skills/upload-content/SKILL.md`

**Interfaces:** none — prose/config-only fixes, no code interfaces.

- [ ] **Step 1: Read the current marketplace.json and find what's missing**

```bash
grep -n '"name"' .claude-plugin/marketplace.json
```
Confirm `sharepoint-provisioning-execution` is absent from the list (it should be, per the spec's
defect #2) and note the exact JSON shape of a neighboring entry (e.g.
`sharepoint-provisioning`'s) to copy.

- [ ] **Step 2: Add the missing marketplace entry**

Insert a new object into the `plugins` array (or wherever the existing entries live — match the
file's actual structure) for `sharepoint-provisioning-execution`, using the same field shape as its
neighbors (`name`, `source: "./plugins/sharepoint-provisioning-execution"`, and a `description`
copied from that plugin's own `.claude-plugin/plugin.json`).

- [ ] **Step 3: Update the stale top-level description**

Find the file's top-level `description` field (currently names only 7 plugins per the spec's defect
#2) and rewrite it to reflect the current plugin count and the 2026-08 SharePoint-domain expansion,
matching this repo's actual scope per `CLAUDE.md`'s own Purpose section.

- [ ] **Step 4: Fix the stale upload-content SKILL.md claim**

```bash
grep -n "not-yet-built" plugins/sharepoint-content-publication/skills/upload-content/SKILL.md
```
Find and replace the false claim (line ~46, "Raw file/asset upload to a document library... is a
separate, not-yet-built capability") with an accurate statement: this capability already exists via
`spo-publish-markdown-plan.ps1`'s `Add-PnPFile` call with checkout/checkin (cite the exact script
and line the spec's grep found).

- [ ] **Step 5: Verify marketplace.json is still valid JSON**

```bash
python -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"
```
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin/marketplace.json plugins/sharepoint-content-publication/skills/upload-content/SKILL.md
git commit -m "fix: add missing marketplace.json entry, correct stale upload-content capability claim"
```

---

## Task 2: Harden sharepoint-provisioning's zero-tenant-I/O purity test

**Files:**
- Modify: `plugins/sharepoint-provisioning/tests/test_plugin_independence.py` (this is the OLD,
  soon-to-be-renamed `sharepoint-provisioning` — do this task BEFORE Task 3's rename, so the rename
  in Task 3 carries the hardened test forward, not the weak one)

**Interfaces:**
- Consumes: `plugins/sharepoint-schema/tests/test_genericity_and_independence.py`'s pattern (the
  spec's Task 2 reference — read this file first for its exact `_shipped_files()`/forbidden-call-list
  structure before writing the replacement).

- [ ] **Step 1: Read the reference pattern**

```bash
cat plugins/sharepoint-schema/tests/test_genericity_and_independence.py
```
Note its file-scanning approach (scans every file, not just `.py`) and its forbidden-call list.

- [ ] **Step 2: Read the current weak test**

```bash
sed -n '124,141p' plugins/sharepoint-provisioning/tests/test_plugin_independence.py
```
This is `test_no_live_pnp_or_csom_or_network_transport_ships` — confirm it has `if path.suffix !=
".py": continue` (the `.ps1` blind spot) and a short forbidden-call list missing `Add-PnP*`/`New-PnP*`/
`Set-PnP*`/`Remove-PnP*`.

- [ ] **Step 3: Rewrite the test to scan every file type and ban every PnP write verb**

Replace the `.py`-only scan and short forbidden-call list with a version that scans all files (reuse
this file's own `_shipped_files()` helper, just drop its `.py`-only filtering for this specific
test) and bans, in addition to the existing list (`Connect-PnPOnline`, `Get-PnPContext`,
`New-ClientContext`, `requests.get`, `requests.post`, `urllib.request`, `http.client`,
`socket.socket`), every PnP write-verb prefix: `Add-PnP`, `New-PnP`, `Set-PnP`, `Remove-PnP`,
`Invoke-PnPSPRestMethod`. Use a substring/prefix match (not exact cmdlet names) so it catches every
current and future write cmdlet, not just an enumerated list that will go stale again.

```python
def test_no_live_pnp_or_csom_or_network_transport_ships():
    """Zero tenant I/O ships in this plugin (Phase 9 spec s13, task hard
    requirement #2): no PnP/CSOM call, no raw network call, anywhere in the
    runtime tree -- scans every shipped file type (not just .py), and bans
    every PnP write-verb prefix, not an enumerable cmdlet list that goes
    stale as new executors are written elsewhere in this ecosystem."""
    forbidden_exact = [
        "Connect-PnPOnline", "Get-PnPContext", "New-ClientContext",
        "requests.get", "requests.post", "urllib.request", "http.client",
        "socket.socket",
    ]
    forbidden_prefixes = ["Add-PnP", "New-PnP", "Set-PnP", "Remove-PnP", "Invoke-PnPSPRestMethod"]
    offenders = []
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(PLUGIN_ROOT).parts
        if "__pycache__" in parts or path.suffix in {".pyc"}:
            continue
        if ".pytest_cache" in parts or ".egg-info" in " ".join(parts):
            continue
        if "tests" in parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for call in forbidden_exact:
            if call in text:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {call}")
        for prefix in forbidden_prefixes:
            for match in re.finditer(re.escape(prefix) + r"[A-Za-z]+", text):
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {match.group()}")

    assert offenders == []
```

Add `import re` at the top of the file if not already present.

- [ ] **Step 4: Run the test and confirm it still passes against current content**

```bash
cd plugins/sharepoint-provisioning && python -m pytest tests/test_plugin_independence.py -v
```
Expected: all pass (the plugin genuinely ships zero PnP anywhere right now — this hardening should
not find anything, only close the gap for future drift).

- [ ] **Step 5: Commit**

```bash
git add plugins/sharepoint-provisioning/tests/test_plugin_independence.py
git commit -m "fix(sharepoint-provisioning): harden zero-tenant-I/O test to scan all file types, ban PnP write-verb prefixes"
```

---

## Task 3: Rename sharepoint-provisioning (old, zero-I/O) to sharepoint-schema-reconciliation

**Files:**
- Move: `plugins/sharepoint-provisioning/` → `plugins/sharepoint-schema-reconciliation/` (whole
  directory, via `git mv`)
- Modify: `plugins/sharepoint-schema-reconciliation/.claude-plugin/plugin.json` (name field)
- Modify: `plugins/sharepoint-schema-reconciliation/plugin.yaml` (name field, if this plugin has one
  — check first)
- Modify: `.claude-plugin/marketplace.json` (update the entry's `name`/`source`)
- Modify: `plugin-sources.json` (update the plugin name in its local-sources list)
- Modify: `skills-lock.json` (rename the 4 skill keys' plugin association if tracked there)

**Interfaces:**
- Produces: the plugin's public Python API (`list_provisioning.plan_provisioning`,
  `field_provisioning`, `content_type_provisioning`) is UNCHANGED — only the plugin's directory
  name, `plugin.json`/`plugin.yaml` `name` field, and every cross-reference to the old name change.
  Do not touch the Python module names or their internal logic.

- [ ] **Step 1: git mv the whole directory**

```bash
git mv plugins/sharepoint-provisioning plugins/sharepoint-schema-reconciliation
```

- [ ] **Step 2: Update the plugin's own manifest name fields**

```bash
grep -n '"name"' plugins/sharepoint-schema-reconciliation/.claude-plugin/plugin.json
```
Change `"name": "sharepoint-provisioning"` to `"name": "sharepoint-schema-reconciliation"`. Check
for a `plugin.yaml` in this directory too (`ls plugins/sharepoint-schema-reconciliation/plugin.yaml
2>/dev/null`) and update its `name:` field the same way if it exists.

- [ ] **Step 3: Update marketplace.json**

Find the marketplace entry for `sharepoint-provisioning` (the old one — be careful not to confuse it
with `sharepoint-provisioning-execution`'s entry, which Task 4 will separately rename) and update
its `name` and `source` fields to the new path.

- [ ] **Step 4: Update plugin-sources.json and skills-lock.json**

```bash
grep -n "sharepoint-provisioning\b" plugin-sources.json skills-lock.json
```
(The `\b` word boundary excludes `sharepoint-provisioning-execution` from this grep — confirm that
before editing.) Update the plugin name reference(s) found.

- [ ] **Step 5: Find and fix every cross-plugin reference to the old name**

```bash
grep -rln "sharepoint-provisioning\b" plugins/ docs/ *.md --include="*.md" --include="*.json" --include="*.yaml" 2>/dev/null | grep -v "sharepoint-provisioning-execution\|sharepoint-schema-reconciliation"
```
For every file found, read the matching line(s) and update the plugin name reference to
`sharepoint-schema-reconciliation`, preserving surrounding prose. Do NOT touch historical/dated log
files (`start-here.md`'s narrative history sections, `.agent/map-debt.md`) — those are a record of
what happened at the time, not current-state references; only fix files describing *current* state
(READMEs, SKILL.md files, CLAUDE.md's plugin list, docs/vision's authoritative table).

- [ ] **Step 6: Run this plugin's test suite from its new location**

```bash
cd plugins/sharepoint-schema-reconciliation && python -m pytest -q
```
Expected: same pass/fail counts as before the move (100 tests, 99 pass, 1 pre-existing unrelated
`evals.json` failure).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: rename sharepoint-provisioning to sharepoint-schema-reconciliation (was misnamed -- zero tenant I/O, plans only, never executes)"
```

---

## Task 4: Rename sharepoint-provisioning-execution to sharepoint-provisioning

**Files:**
- Move: `plugins/sharepoint-provisioning-execution/` → `plugins/sharepoint-provisioning/`
- Modify: `plugins/sharepoint-provisioning/.claude-plugin/plugin.json`, `plugin.yaml`
- Modify: `.claude-plugin/marketplace.json`, `plugin-sources.json`, `skills-lock.json`
- Modify: `plugins/sharepoint-schema-reconciliation/skills/*/SKILL.md` (4 files — these currently
  say "the real executor lives in sharepoint-provisioning-execution's apply-sharepoint-provisioning-plan
  skill"; update to the new name)

**Interfaces:** same principle as Task 3 — only naming changes, PnP script logic unchanged.

- [ ] **Step 1: git mv the whole directory**

```bash
git mv plugins/sharepoint-provisioning-execution plugins/sharepoint-provisioning
```

- [ ] **Step 2: Update manifest name fields**

Same pattern as Task 3 Step 2, for this plugin's `plugin.json`/`plugin.yaml`.

- [ ] **Step 3: Update marketplace.json entry added in Task 1**

Task 1 added a `sharepoint-provisioning-execution` entry to `marketplace.json` because it was
missing. Update that same entry's `name`/`source` to `sharepoint-provisioning` now (don't add a
second entry).

- [ ] **Step 4: Update plugin-sources.json, skills-lock.json**

Same grep-and-fix pattern as Task 3 Step 4, targeting `sharepoint-provisioning-execution` this time.

- [ ] **Step 5: Fix the 4 cross-references from sharepoint-schema-reconciliation and fix frontmatter**

```bash
grep -rln "sharepoint-migration-planning.*apply-sharepoint-provisioning-plan\|sharepoint-provisioning-execution" plugins/sharepoint-schema-reconciliation/
```
These 4 `SKILL.md` files (one per skill: list, content-types, fields, calendar) point at the
executor plugin by its old name (some may still say `sharepoint-migration-planning` from before the
2026-08-18 extraction — fix both stale forms in one pass). Update each to say
`sharepoint-provisioning`.

Also fix `plugins/sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/SKILL.md`: update line 3 frontmatter from `plugin: sharepoint-migration-planning` to `plugin: sharepoint-provisioning`.

- [ ] **Step 6: Run this plugin's test suite**

```bash
cd plugins/sharepoint-provisioning && python -m pytest -q
```
Expected: same pass count as before (this plugin ships `.ps1` only, likely no `pytest` suite of its
own to run — if `pytest -q` reports "no tests collected," that's expected, not a failure; confirm by
checking for a `tests/` directory first).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: rename sharepoint-provisioning-execution to sharepoint-provisioning (reclaims the name -- this is the plugin that actually provisions)"
```

---

## Task 5: Move spo-provision-calendar.ps1 into sharepoint-provisioning

**Files:**
- Move: `plugins/sharepoint-migration-planning/scripts/spo-provision-calendar.ps1` →
  `plugins/sharepoint-provisioning/scripts/spo-provision-calendar.ps1`
- Modify: `plugins/sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/SKILL.md` (add
  this script to its executor table)
- Modify: `plugins/sharepoint-schema-reconciliation/skills/provision-modern-calendar-list/SKILL.md`
  (fix its "not currently part of apply-sharepoint-provisioning-plan" caveat — it now is)
- Create symlink: `plugins/sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/scripts/spo-provision-calendar.ps1`

- [ ] **Step 1: git mv the script**

```bash
git mv plugins/sharepoint-migration-planning/scripts/spo-provision-calendar.ps1 plugins/sharepoint-provisioning/scripts/spo-provision-calendar.ps1
```

- [ ] **Step 2: Fix the script's own internal cross-references**

Read the moved file's docstring for any relative-path assumptions about its old location (it
previously referenced `sharepoint-provisioning`'s `calendar_provisioning.py` by name, not path, so
this is likely just a prose check, not a path fix — verify with `grep -n
"calendar_provisioning\|sharepoint-provisioning" plugins/sharepoint-provisioning/scripts/spo-provision-calendar.ps1`).

- [ ] **Step 3: Create the symlink into the skill folder**

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-provisioning/scripts/spo-provision-calendar.ps1 --dst plugins/sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/scripts/spo-provision-calendar.ps1 --description "apply-sharepoint-provisioning-plan skill's bundled copy of spo-provision-calendar.ps1"
```

- [ ] **Step 4: Update the skill's own SKILL.md table**

Add a row to `apply-sharepoint-provisioning-plan/SKILL.md`'s executor table for
`spo-provision-calendar.ps1`, matching the existing table's format (script name, plan input source,
PnP verb).

- [ ] **Step 5: Fix the stale caveat in provision-modern-calendar-list/SKILL.md**

That file currently says (per the prior session's Task 4) `spo-provision-calendar.ps1` is "not
currently part of `apply-sharepoint-provisioning-plan` and should be treated as a follow-up" — this
task IS that follow-up. Update the sentence to state it's now included.

- [ ] **Step 6: Verify and run both plugins' test suites**

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py audit
cd plugins/sharepoint-migration-planning && python -m pytest -q
cd ../sharepoint-provisioning && python -m pytest -q 2>&1 || echo "no tests, expected"
```
Expected: audit clean, migration-planning's test count unchanged minus nothing (the script wasn't
under test there), no new failures.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: move spo-provision-calendar.ps1 into sharepoint-provisioning (was stranded in migration-planning, a plugin whose contract is planning-only)"
```

---

## Task 6: Merge sharepoint-schema into sharepoint-discovery

**Files:**
- Move: `plugins/sharepoint-schema/scripts/*` → `plugins/sharepoint-discovery/scripts/`
- Move: `plugins/sharepoint-schema/skills/*` → `plugins/sharepoint-discovery/skills/`
- Modify: `plugins/sharepoint-discovery/plugin.yaml` (add the 5 absorbed skills to its `skills:`
  list, update description)
- Modify: `plugins/sharepoint-discovery/tests/` — merge `sharepoint-schema`'s
  `test_genericity_and_independence.py` in, rescoped to cover the merged plugin's full tree (do NOT
  delete or weaken it — see spec's explicit requirement)
- Delete: `plugins/sharepoint-schema/` (empty after the moves above)

**Interfaces:**
- Consumes: `sharepoint-schema`'s existing Python modules (`schema_export.py`, `calculated_columns.py`,
  `choice_fields.py`, `schema_definition.py`) — moved as-is, imports/module names unchanged.

- [ ] **Step 1: git mv scripts and skills**

```bash
git mv plugins/sharepoint-schema/scripts/schema_export.py plugins/sharepoint-discovery/scripts/schema_export.py
git mv plugins/sharepoint-schema/scripts/calculated_columns.py plugins/sharepoint-discovery/scripts/calculated_columns.py
git mv plugins/sharepoint-schema/scripts/choice_fields.py plugins/sharepoint-discovery/scripts/choice_fields.py
git mv plugins/sharepoint-schema/scripts/schema_definition.py plugins/sharepoint-discovery/scripts/schema_definition.py
```
(Adjust exact script filenames to what `ls plugins/sharepoint-schema/scripts/` actually shows —
this list is from the plugin's known skill set, verify before running.)

```bash
git mv plugins/sharepoint-schema/skills/audit-schema plugins/sharepoint-discovery/skills/audit-schema
git mv plugins/sharepoint-schema/skills/diff-sharepoint-schema plugins/sharepoint-discovery/skills/diff-sharepoint-schema
git mv plugins/sharepoint-schema/skills/extract-calculated-columns plugins/sharepoint-discovery/skills/extract-calculated-columns
git mv plugins/sharepoint-schema/skills/extract-choice-fields plugins/sharepoint-discovery/skills/extract-choice-fields
git mv plugins/sharepoint-schema/skills/generate-sharepoint-schema-from-export plugins/sharepoint-discovery/skills/generate-sharepoint-schema-from-export
```

- [ ] **Step 2: Fix the moved skills' symlinks**

Each moved skill folder's `scripts/` symlinks now point at the wrong relative path (they pointed
into `sharepoint-schema/scripts/`, need to point into `sharepoint-discovery/scripts/`). For each,
remove and recreate via the tool:

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py remove --dst plugins/sharepoint-discovery/skills/audit-schema/scripts/schema_export.py
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-discovery/scripts/schema_export.py --dst plugins/sharepoint-discovery/skills/audit-schema/scripts/schema_export.py --description "audit-schema skill's bundled copy of schema_export.py"
```
Repeat for every symlink in every one of the 5 moved skill folders (`diagnose` first to see the
full list of what needs fixing: `python .agents/skills/symlink-manager/scripts/symlink_manager.py
diagnose` — anything under `plugins/sharepoint-discovery/skills/{audit-schema,diff-sharepoint-schema,
extract-calculated-columns,extract-choice-fields,generate-sharepoint-schema-from-export}` showing
broken is one to fix this way).

- [ ] **Step 3: Merge the plugin.yaml skill lists**

Add the 5 moved skill names to `sharepoint-discovery/plugin.yaml`'s `skills:` list (alongside its
existing 9). Update its `description` field to mention schema auditing/diffing/extraction, not just
inventory collection.

- [ ] **Step 4: Merge the test suites, rescoping the strict one**

```bash
cp plugins/sharepoint-schema/tests/test_genericity_and_independence.py plugins/sharepoint-discovery/tests/test_genericity_and_independence.py
```
Read the copied file's `PLUGIN_ROOT`/`_shipped_files()` definitions — they should already resolve
relative to `Path(__file__).resolve().parents[1]`, which will now correctly point at
`sharepoint-discovery` once the file lives there, no path literal to fix. Run it:

```bash
cd plugins/sharepoint-discovery && python -m pytest tests/test_genericity_and_independence.py -v
```
This is the critical check the spec calls out: `sharepoint-discovery` currently has real PnP
read-cmdlet usage (`Get-PnP*`) in its OTHER scripts (the original 9 discovery skills, which do
connect to a live tenant for inventory collection) — but this test's forbidden-call list should only
ban WRITE cmdlets (`Add-PnP`, `New-PnP`, `Set-PnP`, `Remove-PnP`) and the always-forbidden
`Connect-PnPOnline`/network calls, same list as Task 2's hardened version. If discovery's existing
`Get-PnP*` collector scripts trip this test because it also bans `Get-PnP*`, that's a false failure —
read the copied test's exact forbidden list and confirm it only bans write verbs, not `Get-PnP*`
reads (which discovery's core job requires). Fix the forbidden list to exclude `Get-PnP` if it's
there.

- [ ] **Step 5: Remove the now-empty sharepoint-schema plugin directory**

```bash
ls plugins/sharepoint-schema/
```
Confirm only empty directories and manifest files remain (no scripts/skills left behind), then:
```bash
git rm -r plugins/sharepoint-schema/
```

- [ ] **Step 6: Fix cross-references to the old sharepoint-schema plugin name repo-wide**

```bash
grep -rln "sharepoint-schema\b" plugins/ docs/ *.md .claude-plugin/ --include="*.md" --include="*.json" --include="*.yaml" 2>/dev/null | grep -v "sharepoint-schema-reconciliation"
```
For each file, update the reference to point at `sharepoint-discovery` instead. Same historical-log
exclusion as Task 3 Step 5 — don't rewrite dated narrative logs.

- [ ] **Step 7: Run sharepoint-discovery's full test suite**

```bash
cd plugins/sharepoint-discovery && python -m pytest -q
```
Expected: all pass, including the newly-merged strict purity test.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: merge sharepoint-schema into sharepoint-discovery (both zero-I/O diagnostic, same lifecycle phase); rescope the strict purity test to the merged tree, not weaken it"
```

---

## Task 7: Add scaffold-schema-definition skill to sharepoint-discovery

**Files:**
- Create: `plugins/sharepoint-discovery/scripts/schema_scaffold.py`
- Create: `plugins/sharepoint-discovery/skills/scaffold-schema-definition/SKILL.md`
- Create symlink: `plugins/sharepoint-discovery/skills/scaffold-schema-definition/scripts/schema_scaffold.py`
- Create symlink: `plugins/sharepoint-discovery/skills/scaffold-schema-definition/scripts/schema_definition.py`
- Test: `plugins/sharepoint-discovery/tests/test_schema_scaffold.py`

**Interfaces:**
- Consumes: `schema_definition.py`'s existing `SiteSchemaDefinition`/`FieldDef`/`ContentTypeDef`/
  `ListDef` types (moved into this plugin by Task 6) — read these type definitions first
  (`cat plugins/sharepoint-discovery/scripts/schema_definition.py`) before writing this task's code,
  so field names match exactly.
- Produces: `scaffold_schema(name: str, fields: list[dict], content_types: list[dict], lists: list[dict])
  -> SiteSchemaDefinition` — a pure function building a `SiteSchemaDefinition` from caller-supplied
  minimal descriptions, filling in every required field the type needs with sensible defaults where
  the caller didn't specify one, never inventing field content the caller didn't ask for.

- [ ] **Step 1: Read the existing schema_definition.py types**

```bash
cat plugins/sharepoint-discovery/scripts/schema_definition.py
```
Note the exact dataclass/field names for `SiteSchemaDefinition`, `FieldDef`, `ContentTypeDef`,
`ListDef` (or equivalent — names may differ, use what's actually there).

- [ ] **Step 2: Write the failing test first**

```python
# plugins/sharepoint-discovery/tests/test_schema_scaffold.py
from schema_scaffold import scaffold_schema

def test_scaffold_minimal_schema_produces_valid_definition():
    result = scaffold_schema(
        name="Case Management",
        fields=[{"internal_name": "CaseNumber", "type": "Text", "display_name": "Case Number"}],
        content_types=[{"name": "Case File", "parent": "Item", "fields": ["CaseNumber"]}],
        lists=[{"title": "Case Files", "template": 100, "content_types": ["Case File"]}],
    )
    assert result.name == "Case Management"
    assert len(result.fields) == 1
    assert result.fields[0].internal_name == "CaseNumber"
    assert len(result.content_types) == 1
    assert result.content_types[0].name == "Case File"
    assert len(result.lists) == 1
    assert result.lists[0].title == "Case Files"

def test_scaffold_rejects_content_type_referencing_undeclared_field():
    import pytest
    with pytest.raises(ValueError, match="undeclared field"):
        scaffold_schema(
            name="X",
            fields=[],
            content_types=[{"name": "Y", "parent": "Item", "fields": ["NoSuchField"]}],
            lists=[],
        )

def test_scaffold_rejects_list_referencing_undeclared_content_type():
    import pytest
    with pytest.raises(ValueError, match="undeclared content type"):
        scaffold_schema(
            name="X",
            fields=[],
            content_types=[],
            lists=[{"title": "Y", "template": 100, "content_types": ["NoSuchContentType"]}],
        )
```

- [ ] **Step 3: Run to confirm it fails**

```bash
cd plugins/sharepoint-discovery && python -m pytest tests/test_schema_scaffold.py -v
```
Expected: `ModuleNotFoundError: No module named 'schema_scaffold'`.

- [ ] **Step 4: Write the implementation**

```python
# plugins/sharepoint-discovery/scripts/schema_scaffold.py
"""
schema_scaffold.py
===================

Purpose:
    Authors a SiteSchemaDefinition from scratch, from a caller-supplied
    minimal description -- fields, content types, lists. Every other schema
    tool in this plugin (audit, diff, extract) requires an existing schema
    export or definition as input; nothing authors one. This closes that
    gap deliberately, as a pure, deterministic construction function (no AI
    model call, no invented content) -- see wave_script_generation.py in
    sharepoint-migration-planning for the identical design rationale.

Layer: sharepoint-discovery / scripts
"""

from schema_definition import SiteSchemaDefinition, FieldDef, ContentTypeDef, ListDef


def scaffold_schema(
    name: str,
    fields: list[dict],
    content_types: list[dict],
    lists: list[dict],
) -> SiteSchemaDefinition:
    field_defs = [
        FieldDef(
            internal_name=f["internal_name"],
            type=f["type"],
            display_name=f.get("display_name", f["internal_name"]),
            required=f.get("required", False),
            choices=f.get("choices", []),
        )
        for f in fields
    ]
    known_field_names = {f.internal_name for f in field_defs}

    content_type_defs = []
    for ct in content_types:
        for field_name in ct.get("fields", []):
            if field_name not in known_field_names:
                raise ValueError(
                    f"Content type '{ct['name']}' references undeclared field '{field_name}' -- "
                    f"declare it in the 'fields' list first."
                )
        content_type_defs.append(
            ContentTypeDef(
                name=ct["name"],
                parent=ct.get("parent", "Item"),
                fields=ct.get("fields", []),
            )
        )
    known_content_type_names = {ct.name for ct in content_type_defs}

    list_defs = []
    for lst in lists:
        for ct_name in lst.get("content_types", []):
            if ct_name not in known_content_type_names:
                raise ValueError(
                    f"List '{lst['title']}' references undeclared content type '{ct_name}' -- "
                    f"declare it in the 'content_types' list first."
                )
        list_defs.append(
            ListDef(
                title=lst["title"],
                template=lst.get("template", 100),
                content_types=lst.get("content_types", []),
            )
        )

    return SiteSchemaDefinition(
        name=name,
        fields=field_defs,
        content_types=content_type_defs,
        lists=list_defs,
    )
```

Note: adjust the exact constructor keyword names (`internal_name`, `type`, etc.) to match whatever
`schema_definition.py` actually defines, found in Step 1 — this code assumes reasonable names but
the real file is the source of truth.

- [ ] **Step 5: Run tests, confirm they pass**

```bash
cd plugins/sharepoint-discovery && python -m pytest tests/test_schema_scaffold.py -v
```
Expected: 3 passed.

- [ ] **Step 6: Write the skill**

Create `plugins/sharepoint-discovery/skills/scaffold-schema-definition/SKILL.md`:

```markdown
---
name: scaffold-schema-definition
plugin: sharepoint-discovery
description: Authors a SiteSchemaDefinition from scratch (fields, content types, lists) given a minimal caller-supplied description -- validates every content-type/list reference against declared fields/content-types before construction. The only schema tool in this plugin's family that does not require an existing export as input.
allowed-tools: Bash, Read
examples:
  - "python -c \"from schema_scaffold import scaffold_schema; print(scaffold_schema('X', fields=[...], content_types=[...], lists=[...]))\""
---

# Scaffold Schema Definition

## Trigger and Purpose

Use this skill when starting a greenfield site-provisioning project (Track A) and there is no
existing schema export to diff against -- every other schema skill in this plugin
(`audit-schema`, `diff-sharepoint-schema`, `generate-sharepoint-schema-from-export`) requires one.
This skill authors a `SiteSchemaDefinition` from a minimal description, ready to hand to
`sharepoint-schema-reconciliation`'s reconcile skills as the target schema.

## Validation, not fabrication

`scaffold_schema` never invents field/content-type content beyond what the caller supplies. It
does validate structural consistency: a content type referencing an undeclared field, or a list
referencing an undeclared content type, raises `ValueError` immediately rather than producing a
schema that will fail downstream reconciliation with a confusing error.

## Usage

```bash
python3 scripts/schema_scaffold.py --help
```
(or import `scaffold_schema` directly per the example above)
```

- [ ] **Step 7: Create the symlinks**

```bash
mkdir -p plugins/sharepoint-discovery/skills/scaffold-schema-definition/scripts
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-discovery/scripts/schema_scaffold.py --dst plugins/sharepoint-discovery/skills/scaffold-schema-definition/scripts/schema_scaffold.py --description "scaffold-schema-definition skill's bundled copy of schema_scaffold.py"
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-discovery/scripts/schema_definition.py --dst plugins/sharepoint-discovery/skills/scaffold-schema-definition/scripts/schema_definition.py --description "scaffold-schema-definition skill's bundled copy of schema_definition.py"
```

- [ ] **Step 8: Add to plugin.yaml's skill list**

Add `scaffold-schema-definition` to `sharepoint-discovery/plugin.yaml`'s `skills:` list.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat(sharepoint-discovery): add scaffold-schema-definition skill (gap: nothing authored a target schema from scratch)"
```

---

## Task 8: Add gap-fill scripts to sharepoint-provisioning (Columns, Views, Items, Site/Locale, Branding, Security, Navigation, Taxonomy, Pages, Webparts, Hubs, Libraries, Formatting, Search)

**Files:**
- Create: `plugins/sharepoint-provisioning/scripts/spo-add-list-column.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-update-list-column.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-remove-list-column.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-provision-list-view.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-add-list-item.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-provision-site.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-provision-branding.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-manage-hub-site.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-create-modern-page.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-configure-webparts.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-configure-library-settings.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-provision-permissions.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-configure-item-permissions.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-configure-column-formatting.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-provision-navigation.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-provision-term-set.ps1`
- Create: `plugins/sharepoint-provisioning/scripts/spo-trigger-reindex.ps1`
- Modify: `plugins/sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/SKILL.md`
  (add all to the executor table)
- Create symlinks into the skill's `scripts/` folder

**Interfaces:** each script follows the exact pattern established in Task 1 of the prior session's
plan (`spo-update-site-column.ps1`) — dry-run/`-Execute`/`-ConfirmToken`/JSON-result shape.

- [ ] **Step 1: spo-add-list-column.ps1 (list-scoped field add)**

Create `spo-add-list-column.ps1` with `Add-PnPField -List $action.list_title`. Confirm token: `ADD-SPO-LIST-COLUMN`.

- [ ] **Step 2: spo-update-list-column.ps1, spo-remove-list-column.ps1, and spo-provision-list-view.ps1**

- `spo-update-list-column.ps1`: uses `Set-PnPField -List $action.list_title -Identity $action.internal_name`. Confirm token: `UPDATE-SPO-LIST-COLUMN`.
- `spo-remove-list-column.ps1`: uses `Remove-PnPField -List $action.list_title -Identity $action.internal_name -Force`. Confirm token: `REMOVE-SPO-LIST-COLUMN`.
- `spo-provision-list-view.ps1`: uses `Add-PnPView -List $action.list_title -Title $action.view_title -Fields $action.fields -SetAsDefault:$([bool]$action.set_as_default)`. Confirm token: `PROVISION-SPO-LIST-VIEW`.

- [ ] **Step 3: spo-add-list-item.ps1**

Create `spo-add-list-item.ps1` using `Add-PnPListItem -List $action.list_title -Values $valuesHash`. Confirm token: `ADD-SPO-LIST-ITEM`.

- [ ] **Step 4: spo-provision-site.ps1, spo-provision-branding.ps1, and spo-manage-hub-site.ps1**

- `spo-provision-site.ps1`: `New-PnPSite -Type TeamSite` / `-Type CommunicationSite`, optional regional locale/timezone `Set-PnPRegionalSettings`. Confirm token: `PROVISION-SPO-SITE`.
- `spo-provision-branding.ps1`: `Set-PnPWebTheme` / `Set-PnPSite -LogoFilePath`. Confirm token: `PROVISION-SPO-BRANDING`.
- `spo-manage-hub-site.ps1`: `Register-PnPHubSite` / `Add-PnPHubSiteAssociation`. Confirm token: `MANAGE-SPO-HUB-SITE`.

- [ ] **Step 5: spo-create-modern-page.ps1 and spo-configure-webparts.ps1**

- `spo-create-modern-page.ps1`: `Add-PnPPage -Name $action.page_name -LayoutType $action.layout_type`, `Add-PnPPageSection -Page $action.page_name -SectionTemplate $action.section_template`. Confirm token: `CREATE-SPO-MODERN-PAGE`.
- `spo-configure-webparts.ps1`: `Add-PnPPageWebPart -Page $action.page_name -DefaultWebPartType $action.webpart_type -Section $action.section -Column $action.column`. Confirm token: `CONFIGURE-SPO-WEBPARTS`.

- [ ] **Step 6: spo-configure-library-settings.ps1 and spo-configure-column-formatting.ps1**

- `spo-configure-library-settings.ps1`: `Set-PnPList -Identity $action.library_title -EnableVersioning -MajorVersions $action.major_versions -EnableMinorVersions:$([bool]$action.enable_minor_versions)`. Confirm token: `CONFIGURE-SPO-LIBRARY-SETTINGS`.
- `spo-configure-column-formatting.ps1`: `Set-PnPField -List $action.list_title -Identity $action.internal_name -Values @{ CustomFormatter = $action.formatter_json }`. Confirm token: `CONFIGURE-SPO-COLUMN-FORMATTING`.

- [ ] **Step 7: spo-provision-permissions.ps1 and spo-configure-item-permissions.ps1**

- `spo-provision-permissions.ps1`: `New-PnPGroup`, `Set-PnPGroupPermissions`, `Add-PnPUserToGroup`. Confirm token: `PROVISION-SPO-PERMISSIONS`.
- `spo-configure-item-permissions.ps1`: `Set-PnPListItemPermission -List $action.list_title -Identity $action.item_id -ClearExisting -Group $action.group_name -AddRole $action.permission_level`. Confirm token: `CONFIGURE-SPO-ITEM-PERMISSIONS`.

- [ ] **Step 8: spo-provision-navigation.ps1, spo-provision-term-set.ps1, and spo-trigger-reindex.ps1**

- `spo-provision-navigation.ps1`: `Add-PnPNavigationNode -Title $action.title -Url $action.url -Location $action.location`. Confirm token: `PROVISION-SPO-NAVIGATION`.
- `spo-provision-term-set.ps1`: `New-PnPTermGroup`, `New-PnPTermSet`, `New-PnPTerm`. Confirm token: `PROVISION-SPO-TERM-SET`.
- `spo-trigger-reindex.ps1`: `Request-PnPReIndexWeb` / `Request-PnPReIndexList -Identity $action.list_title`. Confirm token: `TRIGGER-SPO-REINDEX`.

- [ ] **Step 9: Parse-check all 17 new scripts**

```bash
for f in spo-add-list-column spo-update-list-column spo-remove-list-column spo-provision-list-view spo-add-list-item spo-provision-site spo-provision-branding spo-manage-hub-site spo-create-modern-page spo-configure-webparts spo-configure-library-settings spo-provision-permissions spo-configure-item-permissions spo-configure-column-formatting spo-provision-navigation spo-provision-term-set spo-trigger-reindex; do
  pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-provisioning/scripts/$f.ps1', [ref]\$null, [ref]\$null) | Out-Null; Write-Output '$f OK'"
done
```

- [ ] **Step 10: Create all symlinks**

```bash
for f in spo-add-list-column spo-update-list-column spo-remove-list-column spo-provision-list-view spo-add-list-item spo-provision-site spo-provision-branding spo-manage-hub-site spo-create-modern-page spo-configure-webparts spo-configure-library-settings spo-provision-permissions spo-configure-item-permissions spo-configure-column-formatting spo-provision-navigation spo-provision-term-set spo-trigger-reindex; do
  python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-provisioning/scripts/$f.ps1 --dst plugins/sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/scripts/$f.ps1 --description "apply-sharepoint-provisioning-plan skill's bundled copy of $f.ps1"
done
```

- [ ] **Step 11: Update the skill's SKILL.md table**

Add all rows to `apply-sharepoint-provisioning-plan/SKILL.md`'s executor table.

- [ ] **Step 12: Verify symlinks and commit**

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py audit
git add -A
git commit -m "feat(sharepoint-provisioning): add 17 gap-fill executors (columns, views, items, sites, branding, hubs, pages, webparts, libraries, formatting, security, navigation, taxonomy, reindex)"
```

---

## Task 9: Add document-library file migration & mapping helpers to sharepoint-content-migration

**Files:**
- Create: `plugins/sharepoint-content-migration/scripts/spo-migrate-library-files.ps1`
- Create: `plugins/sharepoint-content-migration/scripts/mapping_utils.py` (expands `id_mapping.py` with User/Group and Taxonomy Term GUID mapping support)
- Modify: `plugins/sharepoint-content-migration/skills/migrate-sharepoint-list-content/SKILL.md`
- Create symlinks into the skill's `scripts/` folder

- [ ] **Step 1: Read the existing item-migration script for the plugin's established pattern**

```bash
cat plugins/sharepoint-content-migration/scripts/spo-migrate-list-items.ps1
```

- [ ] **Step 2: Write spo-migrate-library-files.ps1**

Real cmdlets: `Get-PnPFile`/`Add-PnPFile` (download from source site, upload to target),
preserving metadata via `Set-PnPFileMetadata` or `Set-PnPListItem` on the uploaded file's list item.
Confirm token: `MIGRATE-SPO-LIBRARY-FILES`. Plan JSON carries `source_library`, `target_library`,
and either an explicit file list or a `migrate_all: true` flag.

- [ ] **Step 3: Write mapping_utils.py and unit tests**

Add helper functions to map source user UPNs/group names and taxonomy term GUIDs to target tenant equivalents, alongside existing lookup ID mapping. Add unit tests in `plugins/sharepoint-content-migration/tests/test_mapping_utils.py`.

- [ ] **Step 4: Parse-check, symlink, update SKILL.md, commit**

```bash
pwsh -NoProfile -Command "[System.Management.Automation.Language.Parser]::ParseFile('plugins/sharepoint-content-migration/scripts/spo-migrate-library-files.ps1', [ref]\$null, [ref]\$null) | Out-Null; Write-Output OK"
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-content-migration/scripts/spo-migrate-library-files.ps1 --dst plugins/sharepoint-content-migration/skills/migrate-sharepoint-list-content/scripts/spo-migrate-library-files.ps1 --description "migrate-sharepoint-list-content skill's bundled copy of spo-migrate-library-files.ps1"
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-content-migration/scripts/mapping_utils.py --dst plugins/sharepoint-content-migration/skills/migrate-sharepoint-list-content/scripts/mapping_utils.py --description "migrate-sharepoint-list-content skill's bundled copy of mapping_utils.py"
git add -A
git commit -m "feat(sharepoint-content-migration): add document-library file migration and principal/term mapping helpers"
```

---

## Task 10: Split sharepoint-page-modernization-execution out of sharepoint-content-publication

**Files:**
- Create: `plugins/sharepoint-page-modernization-execution/.claude-plugin/plugin.json`
- Create: `plugins/sharepoint-page-modernization-execution/plugin.yaml`
- Move 4 skills + their scripts from `sharepoint-content-publication` (following the exact same
  `git mv` + symlink-recreation pattern as the prior session's Task 3, which did this identical kind
  of extraction for `sharepoint-provisioning-execution`)

Skills/scripts moving: `convert-page-to-modern` (`spo-convert-page-to-modern.ps1`),
`execute-page-bulk-migration` → rename to `execute-bulk-page-conversion`
(`spo-convert-pages-bulk.ps1`), `validate-page-migration` → rename to `validate-page-conversion`
(`spo-validate-page-conversion.ps1`), `copy-spo-page-between-sites` → rename to
`copy-page-between-sites` (`spo-page-copy-plan.ps1`).

- [ ] **Step 1: Create the new plugin's manifest files**

```json
{
    "name": "sharepoint-page-modernization-execution",
    "version": "0.1.0-alpha.1",
    "description": "Real PnP.PowerShell executors for classic-to-modern page conversion, bulk conversion, cross-site page copy, and post-conversion validation. Consumes the layout/component-mapping manifest sharepoint-page-modernization's planning skills produce. Dry-run by default, gated behind -Execute plus an operation-specific -ConfirmToken. Extracted from sharepoint-content-publication 2026-08-18, mirroring the same plan/execute split already established for sharepoint-schema-reconciliation/sharepoint-provisioning.",
    "author": { "name": "Richard Fremmerlid" },
    "repository": "https://github.com/richfrem/sharepoint-knowledge-workbench",
    "license": "MIT",
    "keywords": ["sharepoint", "page-modernization", "pnp-powershell", "convert-to-modern"]
}
```
(save to `plugins/sharepoint-page-modernization-execution/.claude-plugin/plugin.json`)

```yaml
name: sharepoint-page-modernization-execution
version: 0.1.0-alpha.1
status: implemented
description: "Real PnP.PowerShell executors for classic-to-modern page conversion, bulk conversion, cross-site page copy, and post-conversion validation. Paired with sharepoint-page-modernization (plan only, zero I/O) the same way sharepoint-provisioning is paired with sharepoint-schema-reconciliation."
author: Richard Fremmerlid
kind: backend
platforms:
  - linux
  - macos
  - windows
skills:
  - convert-page-to-modern
  - execute-bulk-page-conversion
  - validate-page-conversion
  - copy-page-between-sites
```
(save to `plugins/sharepoint-page-modernization-execution/plugin.yaml`)

- [ ] **Step 2: git mv the canonical scripts**

```bash
mkdir -p plugins/sharepoint-page-modernization-execution/scripts
git mv plugins/sharepoint-content-publication/scripts/spo-convert-page-to-modern.ps1 plugins/sharepoint-page-modernization-execution/scripts/
git mv plugins/sharepoint-content-publication/scripts/spo-convert-pages-bulk.ps1 plugins/sharepoint-page-modernization-execution/scripts/
git mv plugins/sharepoint-content-publication/scripts/spo-validate-page-conversion.ps1 plugins/sharepoint-page-modernization-execution/scripts/
git mv plugins/sharepoint-content-publication/scripts/spo-page-copy-plan.ps1 plugins/sharepoint-page-modernization-execution/scripts/
git mv plugins/sharepoint-content-publication/scripts/Get-WorkbenchConnectionConfig.ps1 plugins/sharepoint-page-modernization-execution/scripts/Get-WorkbenchConnectionConfig.ps1
```
(the connection helper: check first whether `sharepoint-content-publication` has other skills still
needing it — per its shrunk skill list in the spec, `plan-aspx-publication`/`publish-markdown`/etc.
likely still need it, so this last `git mv` is probably wrong; instead symlink a NEW copy into the
new plugin from `workbench-setup` directly, the same way other plugins do, rather than moving
`content-publication`'s copy out from under its remaining skills — verify with `grep -rl
"Get-WorkbenchConnectionConfig" plugins/sharepoint-content-publication/skills/*/SKILL.md` before
deciding).

- [ ] **Step 3: git mv the 4 skill folders, dropping their old (now-broken) symlinks first**

```bash
find plugins/sharepoint-content-publication/skills/convert-page-to-modern -type l -delete
find plugins/sharepoint-content-publication/skills/execute-page-bulk-migration -type l -delete
find plugins/sharepoint-content-publication/skills/validate-page-migration -type l -delete
find plugins/sharepoint-content-publication/skills/copy-spo-page-between-sites -type l -delete
git add -A

git mv plugins/sharepoint-content-publication/skills/convert-page-to-modern plugins/sharepoint-page-modernization-execution/skills/convert-page-to-modern
git mv plugins/sharepoint-content-publication/skills/execute-page-bulk-migration plugins/sharepoint-page-modernization-execution/skills/execute-bulk-page-conversion
git mv plugins/sharepoint-content-publication/skills/validate-page-migration plugins/sharepoint-page-modernization-execution/skills/validate-page-conversion
git mv plugins/sharepoint-content-publication/skills/copy-spo-page-between-sites plugins/sharepoint-page-modernization-execution/skills/copy-page-between-sites
```

- [ ] **Step 4: Recreate all symlinks via the tool**

For each of the 4 moved skills, recreate its `scripts/` symlinks pointing at the new plugin-root
location:
```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py create --src plugins/sharepoint-page-modernization-execution/scripts/spo-convert-page-to-modern.ps1 --dst plugins/sharepoint-page-modernization-execution/skills/convert-page-to-modern/scripts/spo-convert-page-to-modern.ps1 --description "convert-page-to-modern skill's bundled copy"
```
Repeat for the other 3 skills' scripts, and for the connection helper into each of the 4 skill
folders that reference it (check each skill's SKILL.md for whether it dot-sources
`Get-WorkbenchConnectionConfig.ps1` directly — if so it needs its own symlinked copy too).

- [ ] **Step 5: Rename SKILL.md frontmatter to match new skill/plugin names**

For each of the 4 moved `SKILL.md` files, update the `name:` and `plugin:` frontmatter fields to the
new skill name and `sharepoint-page-modernization-execution`.

- [ ] **Step 6: Update sharepoint-content-publication's plugin.yaml**

Remove the 4 moved skill names from its `skills:` list.

- [ ] **Step 7: Update sharepoint-page-modernization's cross-reference**

Per the spec's defect #5, its `convert-aspx-pages`/`map-aspx-to-modern-layout` skill (see Task 11)
should reference the new executor plugin by its new name and skill names.

- [ ] **Step 8: Update marketplace.json, plugin-sources.json with the new plugin**

Same pattern as Task 1's addition — new entry for `sharepoint-page-modernization-execution`.

- [ ] **Step 9: Verify symlinks and run both plugins' test suites**

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py audit
cd plugins/sharepoint-content-publication && python -m pytest -q
cd ../sharepoint-page-modernization-execution && python -m pytest -q 2>&1 || echo "no tests, expected for .ps1-only plugin"
```

- [ ] **Step 10: Commit**

```bash
git add -A
git commit -m "refactor: split sharepoint-page-modernization-execution out of sharepoint-content-publication (mirrors the schema-reconciliation/provisioning plan-execute split)"
```

---

## Task 11: Rename convert-aspx-pages to map-aspx-to-modern-layout

**Files:**
- Move: `plugins/sharepoint-page-modernization/skills/convert-aspx-pages/` →
  `plugins/sharepoint-page-modernization/skills/map-aspx-to-modern-layout/`

- [ ] **Step 1: git mv, drop and recreate symlinks, update frontmatter**

```bash
find plugins/sharepoint-page-modernization/skills/convert-aspx-pages -type l -delete
git add -A
git mv plugins/sharepoint-page-modernization/skills/convert-aspx-pages plugins/sharepoint-page-modernization/skills/map-aspx-to-modern-layout
```
Recreate symlinks via `symlink_manager.py create` (same pattern as prior tasks). Update the
`SKILL.md`'s `name:` frontmatter field and update `plugin.yaml`'s skill list entry.

- [ ] **Step 2: Fix cross-references**

```bash
grep -rln "convert-aspx-pages" plugins/ docs/
```
Update every reference found to the new skill name.

- [ ] **Step 3: Verify and commit**

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py audit
git add -A
git commit -m "refactor(sharepoint-page-modernization): rename convert-aspx-pages to map-aspx-to-modern-layout (collided with content-publication's convert-page-to-modern -- one plans, one executes, both named 'convert')"
```

---

## Task 12: Resolve the stray dossier script in sharepoint-spfx-authoring

**Files:**
- Investigate: `plugins/sharepoint-spfx-authoring/scripts/provision-sample-dossier-schema.ps1`

- [ ] **Step 1: Read the script and its consuming skill to determine its real purpose**

```bash
cat plugins/sharepoint-spfx-authoring/scripts/provision-sample-dossier-schema.ps1
grep -rl "provision-sample-dossier-schema" plugins/sharepoint-spfx-authoring/skills/
```
Determine: is this a genuine reusable production capability (in which case relocate it into
`sharepoint-provisioning` alongside Task 8's new scripts, since it's real schema/item writes), or is
it specifically a dev-fixture that seeds a local/test tenant with sample data so an SPFx developer
has something to build a web part against (in which case it legitimately belongs in
`sharepoint-spfx-authoring`, just needs its role documented so it isn't mistaken for a stray
executor again)?

- [ ] **Step 2a (if relocating): git mv and update the consuming skill's reference**

```bash
git mv plugins/sharepoint-spfx-authoring/scripts/provision-sample-dossier-schema.ps1 plugins/sharepoint-provisioning/scripts/
```
Recreate its symlink into `sharepoint-spfx-authoring`'s consuming skill (it can still be referenced
cross-plugin, same pattern established elsewhere in this plan) or into
`sharepoint-provisioning/skills/apply-sharepoint-provisioning-plan/scripts/` if it becomes a general
executor.

- [ ] **Step 2b (if keeping, documenting instead): add an explicit header note**

Add a `.SYNOPSIS` clarification to the script itself and a note in
`sharepoint-spfx-authoring/README.md` stating explicitly: "this script writes real sample data to a
tenant for SPFx development/demo purposes — it is a dev fixture, not a general-purpose provisioning
capability; see `sharepoint-provisioning` for that."

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "docs/refactor(sharepoint-spfx-authoring): resolve provision-sample-dossier-schema.ps1's ambiguous role"
```

---

## Task 13: Rename 4 document conversion plugins to content-* prefix

**Files:**
- Move: `plugins/source-document-extraction/` → `plugins/content-extraction/`
- Move: `plugins/document-structure-analysis/` → `plugins/content-structure-analysis/`
- Move: `plugins/structured-content-assembly/` → `plugins/content-assembly/`
- Move: `plugins/structured-content-rendering/` → `plugins/content-rendering/`
- Modify: `pyproject.toml`, `.claude-plugin/plugin.json`, `plugin.yaml` across all 4 plugins
- Modify: `.claude-plugin/marketplace.json`, `plugin-sources.json`, `skills-lock.json`
- Update cross-references across active docs and test suites

- [ ] **Step 1: git mv the 4 plugin directories**

```bash
git mv plugins/source-document-extraction plugins/content-extraction
git mv plugins/document-structure-analysis plugins/content-structure-analysis
git mv plugins/structured-content-assembly plugins/content-assembly
git mv plugins/structured-content-rendering plugins/content-rendering
```

- [ ] **Step 2: Update plugin manifests & pyproject.toml files**

Update package names and source paths in `plugin.json`, `plugin.yaml`, and `pyproject.toml` in all 4 directories.

- [ ] **Step 3: Update central registers**

Update `.claude-plugin/marketplace.json`, `plugin-sources.json`, and `skills-lock.json`.

- [ ] **Step 4: Run test suites across all 4 renamed plugins**

```bash
for p in content-extraction content-structure-analysis content-assembly content-rendering; do
  cd "plugins/$p" && python -m pytest -q
  cd ../..
done
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: standardize document conversion plugins to content-* prefix"
```

---

## Task 14: Standardize skill names with domain prefixes (content-*, sharepoint-*, workbench-*)

**Files:**
- Rename skill folders and update `SKILL.md` frontmatter across `plugins/`
- Update symlinks via `symlink_manager.py`
- Update `plugin.yaml` skill arrays

- [ ] **Step 1: Rename skills to match standardized taxonomy**

Execute folder renames via `git mv` (e.g., `extract-docx` $\rightarrow$ `content-extract-docx`, `audit-schema` $\rightarrow$ `sharepoint-audit-schema`, `validate-environment` $\rightarrow$ `workbench-validate-environment`).

- [ ] **Step 2: Update SKILL.md name: frontmatter and recreate symlinks**

Update `name:` field in all `SKILL.md` files and run `python .agents/skills/symlink-manager/scripts/symlink_manager.py restore`.

- [ ] **Step 3: Update plugin.yaml manifests**

Ensure each plugin's `plugin.yaml` lists its new prefixed skill names.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "refactor: apply domain prefix standardization across all skills (content-*, sharepoint-*, workbench-*)"
```

---

## Task 15: Audit & wire all missing skill scripts, references, and symlinks

**Files:**
- Symlinks in `plugins/**/skills/*/scripts/`
- Symlinks in `plugins/**/skills/*/references/`
- Symlinks in `plugins/**/skills/*/assets/`
- Update `symlinks.json`

Several existing skills (`sharepoint-content-publication/publish-markdown`, `sharepoint-schema-reconciliation/provision-list`, etc.) have empty `scripts/` folders even though their implementing `.ps1` or `.py` files exist at the plugin root.

- [ ] **Step 1: Wire missing script symlinks for all skills**

For each skill, inspect its `SKILL.md` for referenced scripts/tools and create the necessary symlink via `symlink_manager.py create`:
- `sharepoint-content-publication/publish-markdown-to-sharepoint` $\rightarrow$ link `spo-publish-markdown-plan.ps1`, `sharepoint_publish_plan.py`, `Get-WorkbenchConnectionConfig.ps1`
- `sharepoint-content-publication/publish-aspx-to-sharepoint` $\rightarrow$ link `sharepoint_publish_plan.py`, `Get-WorkbenchConnectionConfig.ps1`
- `sharepoint-content-publication/reconcile-sharepoint-publication` $\rightarrow$ link `sharepoint_reconcile.py`, `Get-WorkbenchConnectionConfig.ps1`
- `sharepoint-content-publication/rollback-sharepoint-publication` $\rightarrow$ link `spo-rollback-publication.ps1`, `Get-WorkbenchConnectionConfig.ps1`
- `sharepoint-content-publication/validate-sharepoint-publication` $\rightarrow$ link `spo-validate-publication-deployment.ps1`, `Get-WorkbenchConnectionConfig.ps1`
- `sharepoint-schema-reconciliation/provision-list` $\rightarrow$ link `list_provisioning.py`, `provisioning_outcomes.py`
- `sharepoint-schema-reconciliation/provision-fields` $\rightarrow$ link `field_provisioning.py`, `provisioning_outcomes.py`
- `sharepoint-schema-reconciliation/provision-content-types` $\rightarrow$ link `content_type_provisioning.py`, `provisioning_outcomes.py`
- `sharepoint-spfx-authoring/request-site-collection-app-catalog` $\rightarrow$ link relevant setup references / `.ps1` helpers

- [ ] **Step 2: Re-audit all symlinks**

```bash
python .agents/skills/symlink-manager/scripts/symlink_manager.py audit
```
Expected: `All links OK.`

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "refactor: wire all missing skill scripts and reference symlinks across plugins"
```

---

## Task 16: Final repo-wide verification & central registry synchronization

**Files:**
- `.claude-plugin/marketplace.json`
- `plugin-sources.json`
- `skills-lock.json`
- `README.md`
- `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`

- [ ] **Step 1: Run workspace conventions auditor and plugin compliance audits**

```bash
python3 .agents/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py
for p in $(ls plugins/); do
  python3 .agents/skills/plugin-installer/scripts/audit_plugin_structure.py "plugins/$p" 2>/dev/null || true
done
```

- [ ] **Step 2: Sync and verify .claude-plugin/marketplace.json matches plugins/ on disk**

Ensure all 16 plugins are listed with accurate names, sources (`./plugins/<name>`), and descriptions.

- [ ] **Step 3: Update main project README.md and root agent instructions**

Update `README.md`, `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` to reflect the clean 16-plugin taxonomy:
- `content-*` (4 conversion plugins)
- `sharepoint-*` (11 SharePoint tenant plugins)
- `workbench-*` (1 environment setup plugin)

- [ ] **Step 4: Run full test suites across all 16 plugins**

```bash
for p in $(ls plugins/); do
  echo "=== $p ==="
  if [ -d "plugins/$p/tests" ]; then
    cd "plugins/$p" && python -m pytest -q 2>&1 | tail -3
    cd ../..
  fi
done
```

- [ ] **Step 5: Verify no orphaned plugin directories remain on disk**

```bash
ls plugins/sharepoint-schema 2>&1
ls plugins/sharepoint-provisioning-execution 2>&1
ls plugins/source-document-extraction 2>&1
ls plugins/document-structure-analysis 2>&1
ls plugins/structured-content-assembly 2>&1
ls plugins/structured-content-rendering 2>&1
```
Expected: all report "No such file or directory".

- [ ] **Step 6: Pre-Completion Gate Verification**

Output the mandatory Pre-Completion Self-Evolution Gate block verbatim and confirm all criteria are satisfied before closing.

- [ ] **Step 7: Final Commit**

```bash
git add -A
git commit -m "chore: synchronize central manifests, marketplace.json, symlinks.json, and root documentation"
```

