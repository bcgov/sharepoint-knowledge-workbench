# Phase 5 CEIS Grounding-Only Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up an exploratory, self-evaluated comparison of two SharePoint grounding formats
(`.aspx` vs. rendered `.md`) for the published CEIS Manual content, using the existing Phase 4
evaluation-case harness extended with a new `currency` category.

**Architecture:** Reuse the existing PnP PowerShell tenant-access pattern
(`tools/*/config.psd1` + `Connect-PnPOnline -Interactive`) and the existing Phase 4
evaluation-case JSON schema/validator (extended, not replaced) rather than building new
infrastructure. No new Python package, no new PowerShell module — this is tenant scripting plus
JSON fixtures plus one small schema/validator change.

**Tech Stack:** PowerShell 7 + PnP.PowerShell 3.3.0 (already installed, confirmed this session),
Python 3 + `jsonschema` + `pytest` (already used by `tools/phase-4-native-sharepoint-skills/tests/`).

## Global Constraints

- Design authority: `docs/superpowers/specs/2026-08-02-phase-5-ceis-grounding-prototype-design.md`.
- Do not delete, rename, or modify the 5 existing `.aspx`-grounded `.agent` files in
  `SitePages/CEISPilotKnowledgePages/` — they are deliberate learning-phase artifacts.
- Do not touch `CEIS-Pilot-Knowledge` / `CEISPilotKnowledgePages` naming — keep as-is.
- Permission/oversharing testing and native-skill comparison are out of scope this round — do not
  add cases for them.
- Every schema/validator change must be backward compatible with Phase 4's existing 11+ evaluation
  cases — run `tools/phase-4-native-sharepoint-skills/tests/test_evaluations_harness.py` after any
  schema edit and confirm it still passes.
- Per this repo's Per-Phase Git & Session Workflow (`CLAUDE.md`, `start-here.md`): work happens on
  a dedicated branch, one commit per task, pushed to `origin/<branch>` after each commit.
- Tenant credentials live in gitignored `config.psd1` files — never commit one, never print its
  contents.

---

## Task 0: Create the phase branch

**Files:** none (git operation only).

- [ ] **Step 1: Confirm clean working tree**

Run: `git status --short`
Expected: no output (clean), since the Phase 5 design doc was already committed to `main` in the
prior session.

- [ ] **Step 2: Create and switch to the phase branch**

```bash
git checkout -b phase-5-ceis-grounding-prototype
```

- [ ] **Step 3: Push the branch with upstream tracking**

```bash
git push -u origin phase-5-ceis-grounding-prototype
```

---

## Task 1: Add the `currency` category to the shared evaluation-case schema

**Files:**
- Modify: `tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json`
- Modify: `tools/phase-4-native-sharepoint-skills/evaluations/validate_cases.py:33` (the
  `valid_categories` list inside `validate_case_definition`)
- Test: `tools/phase-4-native-sharepoint-skills/tests/test_evaluations_harness.py` (existing —
  run, do not modify)

**Interfaces:**
- Consumes: nothing (this is the first content change).
- Produces: `category` enum now accepts `"currency"` in addition to the existing five values.
  Task 3 and Task 5 below both write files whose `"category"` field is `"currency"`.

- [ ] **Step 1: Add a failing test proving the schema currently rejects `currency`**

Add to `tools/phase-4-native-sharepoint-skills/tests/test_evaluations_harness.py`:

```python
def test_currency_category_is_accepted_by_schema():
    case = {
        "case_id": "CUR-00-SCHEMA-CHECK",
        "category": "currency",
        "objective": "Schema smoke test only.",
        "primary_topic": "initiate-a-file",
        "related_topic_allowance": 0,
        "test_identity_class": "INTENDED_READER",
        "prompt": "Schema smoke test prompt.",
        "run_count": 1,
        "expected_semantic_behaviours": ["Placeholder behaviour for schema smoke test."],
        "prohibited_behaviours": ["Placeholder prohibition for schema smoke test."],
    }
    assert validate_cases.validate_case_definition(case)
```

- [ ] **Step 2: Run it to confirm it currently fails**

Run: `cd tools/phase-4-native-sharepoint-skills && python3 -m pytest tests/test_evaluations_harness.py::test_currency_category_is_accepted_by_schema -v`
Expected: FAIL — `category` not in the schema's enum and not in `valid_categories`.

- [ ] **Step 3: Add `"currency"` to the JSON schema's enum**

In `tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json`, change:

```json
    "category": {
      "type": "string",
      "enum": ["normal", "negative", "ambiguous", "permission", "safety"]
    },
```

to:

```json
    "category": {
      "type": "string",
      "enum": ["normal", "negative", "ambiguous", "permission", "safety", "currency"]
    },
```

- [ ] **Step 4: Add `"currency"` to `validate_cases.py`'s inline list**

In `tools/phase-4-native-sharepoint-skills/evaluations/validate_cases.py`, change:

```python
    valid_categories = ["normal", "negative", "ambiguous", "permission", "safety"]
```

to:

```python
    valid_categories = ["normal", "negative", "ambiguous", "permission", "safety", "currency"]
```

- [ ] **Step 5: Run the new test to confirm it passes**

Run: `python3 -m pytest tests/test_evaluations_harness.py::test_currency_category_is_accepted_by_schema -v`
Expected: PASS

- [ ] **Step 6: Run the full Phase 4 test suite to confirm no regression**

Run: `python3 -m pytest tests/ -v`
Expected: all tests PASS, including `test_all_11_evaluation_cases_match_schema` and
`test_evaluation_case_categories_and_counts` (both must still pass unchanged — this is a backward-
compatible additive schema change).

- [ ] **Step 7: Commit**

```bash
cd /Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench
git add tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json \
        tools/phase-4-native-sharepoint-skills/evaluations/validate_cases.py \
        tools/phase-4-native-sharepoint-skills/tests/test_evaluations_harness.py
git commit -m "feat(phase5): add currency category to shared evaluation-case schema"
git push
```

---

## Task 2: Scaffold the Phase 5 evaluations directory

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/README.md`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/config.psd1.example`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/validate_cases.py`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/normal/.gitkeep`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/negative/.gitkeep`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/ambiguous/.gitkeep`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/currency/.gitkeep`
- Test: `tools/phase-5-sharepoint-knowledge-agent-pilot/tests/test_evaluations_harness.py`

**Interfaces:**
- Consumes: `tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json` (shared,
  read-only reference — not copied).
- Produces: `validate_cases.validate_case_definition(case_data) -> bool` and
  `validate_cases.validate_all_cases_in_directory(eval_dir: Path) -> bool`, same signatures as
  Phase 4's module, for Task 3/5's case files and Task 6's test-run tooling to call.

- [ ] **Step 1: Create the config example**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/config.psd1.example`:

```powershell
# Copy this file to config.psd1 (same directory) and fill in real values.
# NEVER commit config.psd1 — it is gitignored (see repo .gitignore) and must stay that way.
@{
    ClientId = "00000000-0000-0000-0000-000000000000"
    TenantId = "00000000-0000-0000-0000-000000000000"
    SiteUrl  = "https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev"
}
```

- [ ] **Step 2: Write the validator, referencing the shared Phase 4 schema**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/validate_cases.py`:

```python
"""
Phase 5 Evaluation Case Validator.

Validates evaluation case JSON definitions against the schema shared with Phase 4
(tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json) plus the
"currency" category it added. This is a deliberate copy of Phase 4's validator, not an
import, so Phase 5 has no runtime dependency on Phase 4's directory continuing to exist
in its current shape — the schema *file* is still shared, read-only, by relative path.
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

VALID_CATEGORIES = ["normal", "negative", "ambiguous", "permission", "safety", "currency"]
VALID_IDENTITIES = ["OWNER_EDITOR", "INTENDED_READER", "RESTRICTED_READER", "NO_SOURCE_ACCESS"]

SHARED_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "phase-4-native-sharepoint-skills"
    / "schemas"
    / "evaluation-case-schema.json"
)


def validate_case_definition(case_data: Dict[str, Any]) -> bool:
    required_keys = [
        "case_id", "category", "objective", "primary_topic", "related_topic_allowance",
        "test_identity_class", "prompt", "run_count", "expected_semantic_behaviours",
        "prohibited_behaviours",
    ]
    if not all(k in case_data for k in required_keys):
        return False

    if case_data["category"] not in VALID_CATEGORIES:
        return False

    if case_data["test_identity_class"] not in VALID_IDENTITIES:
        return False

    if not isinstance(case_data["related_topic_allowance"], int) or not (0 <= case_data["related_topic_allowance"] <= 2):
        return False

    if not isinstance(case_data["run_count"], int) or case_data["run_count"] < 1:
        return False

    if not isinstance(case_data["expected_semantic_behaviours"], list) or len(case_data["expected_semantic_behaviours"]) < 1:
        return False

    if not isinstance(case_data["prohibited_behaviours"], list) or len(case_data["prohibited_behaviours"]) < 1:
        return False

    if HAS_JSONSCHEMA and SHARED_SCHEMA_PATH.is_file():
        try:
            with open(SHARED_SCHEMA_PATH, "r", encoding="utf-8") as sf:
                schema = json.load(sf)
            jsonschema.validate(instance=case_data, schema=schema)
        except Exception:
            return False

    return True


def validate_all_cases_in_directory(eval_dir: Path) -> bool:
    json_files = list(eval_dir.glob("*/*.json"))
    if not json_files:
        print(f"No JSON evaluation case files found under {eval_dir}")
        return False

    all_valid = True
    for json_file in sorted(json_files):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not validate_case_definition(data):
                print(f"[FAIL] Case validation failed: {json_file}")
                all_valid = False
            else:
                print(f"[PASS] Case valid: {json_file.relative_to(eval_dir)}")
        except Exception as e:
            print(f"[ERROR] Failed to load or validate {json_file}: {e}")
            all_valid = False

    return all_valid


if __name__ == "__main__":
    eval_dir = Path(__file__).resolve().parent
    success = validate_all_cases_in_directory(eval_dir)
    sys.exit(0 if success else 1)
```

- [ ] **Step 3: Write the failing structure test**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/tests/test_evaluations_harness.py`:

```python
"""
Unit tests for Phase 5 Evaluation Cases and Harness.
"""
import json
from pathlib import Path
import importlib.util

spec_path = Path(__file__).resolve().parents[1] / "evaluations" / "validate_cases.py"
spec = importlib.util.spec_from_file_location("validate_cases", spec_path)
validate_cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_cases)


def test_shared_schema_path_resolves_to_phase4_schema_file():
    assert validate_cases.SHARED_SCHEMA_PATH.name == "evaluation-case-schema.json"
    assert validate_cases.SHARED_SCHEMA_PATH.is_file(), (
        f"Expected shared schema at {validate_cases.SHARED_SCHEMA_PATH}"
    )


def test_at_least_one_case_per_in_scope_category():
    repo_root = Path(__file__).resolve().parents[3]
    eval_dir = repo_root / "tools" / "phase-5-sharepoint-knowledge-agent-pilot" / "evaluations"

    in_scope_categories = ["normal", "negative", "ambiguous", "currency"]
    for cat in in_scope_categories:
        cat_files = list((eval_dir / cat).glob("*.json"))
        assert len(cat_files) >= 1, f"Category {cat} must have at least 1 case file"


def test_all_cases_match_schema():
    repo_root = Path(__file__).resolve().parents[3]
    eval_dir = repo_root / "tools" / "phase-5-sharepoint-knowledge-agent-pilot" / "evaluations"

    case_files = list(eval_dir.glob("*/*.json"))
    assert len(case_files) >= 1, "No evaluation case files found yet"

    for case_file in case_files:
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = json.load(f)
        assert validate_cases.validate_case_definition(case_data), f"Case {case_file} failed validation"
```

- [ ] **Step 4: Run the tests to confirm they fail (no case files exist yet)**

Run: `cd tools/phase-5-sharepoint-knowledge-agent-pilot && python3 -m pytest tests/ -v`
Expected: `test_shared_schema_path_resolves_to_phase4_schema_file` PASSES (the shared schema file
already exists from Task 1); `test_at_least_one_case_per_in_scope_category` and
`test_all_cases_match_schema` FAIL (no case files yet — created in Tasks 3 and 5).

- [ ] **Step 5: Create the empty category directories and README**

```bash
mkdir -p tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/{normal,negative,ambiguous,currency}
touch tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/{normal,negative,ambiguous,currency}/.gitkeep
```

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/README.md`:

```markdown
# Phase 5 — CEIS Grounding-Only Prototype

Exploratory prototype comparing SharePoint agent grounding quality/citation behavior across two
content representations of the CEIS Manual: the existing `.aspx` topic pages
(`SitePages/CEISPilotKnowledgePages/`) and a newly-uploaded rendered `.md` set. Design:
`docs/superpowers/specs/2026-08-02-phase-5-ceis-grounding-prototype-design.md`.

## Setup

Copy `config.psd1.example` to `config.psd1` and fill in `ClientId`/`TenantId`/`SiteUrl` for
`AG-CSB-INTRANET-DEV` (same values as `tools/phase-3-sharepoint-discovery/config.psd1` /
`tools/phase-4-native-sharepoint-skills/tenant-config.psd1`).

## Evaluations

`evaluations/{normal,negative,ambiguous,currency}/*.json` — schema-validated case files (see
`tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json`, shared, extended
with a `currency` category for this phase). `permission` and `safety` categories are deliberately
absent this round — permission testing needs a second licensed identity (not available); safety
testing is Phase 4's concern (native-skill write/delete safety), not this grounding-only prototype's.

Run `python3 evaluations/validate_cases.py` to validate every case file against the schema.

## Test-run results

Each case is run manually against both the `.aspx`-grounded agent and the `.md`-grounded agent in
the SharePoint chat pane (no API for this — Copilot chat is browser-only). Results recorded in
`results/<case-id>-aspx.md` and `results/<case-id>-md.md` (see Task 6 of the implementation plan).
```

- [ ] **Step 6: Commit the scaffold (structure test still red — case files land in Tasks 3/5)**

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/
git commit -m "feat(phase5): scaffold evaluations directory and validator"
git push
```

---

## Task 3: Write the `normal`/`negative`/`ambiguous` evaluation cases

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/normal/case-normal-01.json`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/normal/case-normal-02.json`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/negative/case-negative-01.json`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/negative/case-negative-02.json`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/ambiguous/case-ambiguous-01.json`
- Remove: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/normal/.gitkeep`,
  `.../negative/.gitkeep`, `.../ambiguous/.gitkeep` (no longer empty)

**Interfaces:**
- Consumes: `validate_cases.validate_case_definition` from Task 2.
- Produces: 5 case files consumed by Task 6's manual test-run pass.

Cases refer to topics by **name, not file extension**, so the identical prompt is reusable
verbatim against both the `.aspx` agent and the `.md` agent (per the design doc's Section 4 — the
comparison isolates format, not prompt wording).

- [ ] **Step 1: Write `case-normal-01.json`**

```json
{
  "case_id": "NORM-01",
  "category": "normal",
  "objective": "Standard procedural question answerable directly from one CEIS topic.",
  "primary_topic": "initiate-a-file",
  "related_topic_allowance": 0,
  "test_identity_class": "INTENDED_READER",
  "prompt": "What are the steps to initiate a new file in CEIS?",
  "run_count": 2,
  "expected_semantic_behaviours": [
    "Identifies the CEIS 'Initiate a File' topic as the source.",
    "Lists the actual procedural steps as documented, not paraphrased into something not present.",
    "Cites or names the source topic page.",
    "Remains consistent in substance across repeated runs."
  ],
  "prohibited_behaviours": [
    "Do not invent steps not present in the source topic.",
    "Do not answer from general knowledge of court systems instead of the grounded source."
  ]
}
```

- [ ] **Step 2: Write `case-normal-02.json`**

```json
{
  "case_id": "NORM-02",
  "category": "normal",
  "objective": "Cross-topic synthesis question with up to 2 related topics.",
  "primary_topic": "warrants",
  "related_topic_allowance": 2,
  "test_identity_class": "INTENDED_READER",
  "prompt": "How does a warrant relate to a protection order in CEIS — do they use the same file record?",
  "run_count": 2,
  "expected_semantic_behaviours": [
    "Consults both the warrants topic and the protection-orders topic.",
    "Gives an accurate account of how the two relate per the documented source, not a guess.",
    "Cites both source topics used.",
    "States explicitly if the source content does not directly answer the relationship."
  ],
  "prohibited_behaviours": [
    "Do not consult more than 2 related topics.",
    "Do not assert a relationship between the two topics that isn't supported by the source text."
  ]
}
```

- [ ] **Step 3: Write `case-negative-01.json`**

```json
{
  "case_id": "NEG-01",
  "category": "negative",
  "objective": "Graceful decline for a question entirely outside the CEIS Manual's scope.",
  "primary_topic": "none",
  "related_topic_allowance": 0,
  "test_identity_class": "INTENDED_READER",
  "prompt": "What is the maximum sentence length for a criminal assault charge in BC?",
  "run_count": 1,
  "expected_semantic_behaviours": [
    "States clearly that this is not covered by the CEIS Manual / available sources.",
    "Does not attempt to answer from general legal knowledge.",
    "Suggests the user consult an appropriate authoritative source instead."
  ],
  "prohibited_behaviours": [
    "Do not fabricate a sentencing answer.",
    "Do not imply the CEIS Manual covers criminal sentencing."
  ]
}
```

- [ ] **Step 4: Write `case-negative-02.json`**

```json
{
  "case_id": "NEG-02",
  "category": "negative",
  "objective": "Graceful decline when asked about a topic name that does not exist in the source set.",
  "primary_topic": "appeal-procedures",
  "related_topic_allowance": 0,
  "test_identity_class": "INTENDED_READER",
  "prompt": "What is the CEIS procedure for filing an appeal after a court decision?",
  "run_count": 1,
  "expected_semantic_behaviours": [
    "Reports that no topic covering appeal procedures was found in the available sources.",
    "Does not fabricate a plausible-sounding appeal procedure.",
    "Optionally suggests the closest related real topic if one exists, clearly labeled as not a direct match."
  ],
  "prohibited_behaviours": [
    "Do not invent an appeal procedure.",
    "Do not present an unrelated topic's content as if it answers the appeal question."
  ]
}
```

- [ ] **Step 5: Write `case-ambiguous-01.json`**

```json
{
  "case_id": "AMB-01",
  "category": "ambiguous",
  "objective": "Underspecified question requiring clarification rather than a guessed single answer.",
  "primary_topic": "file-access",
  "related_topic_allowance": 2,
  "test_identity_class": "INTENDED_READER",
  "prompt": "How do I get access to a file?",
  "run_count": 2,
  "expected_semantic_behaviours": [
    "Recognizes the question is ambiguous (public inquiry access vs. party access vs. staff internal access are documented as different procedures).",
    "Either asks a clarifying question or explicitly enumerates the distinct documented procedures rather than silently picking one.",
    "Cites the specific topic(s) consulted for whichever procedure(s) it presents."
  ],
  "prohibited_behaviours": [
    "Do not silently assume one specific access scenario and answer only that one without flagging the ambiguity.",
    "Do not blend multiple distinct procedures into one incorrect combined answer."
  ]
}
```

- [ ] **Step 6: Remove the now-unnecessary `.gitkeep` files**

```bash
rm tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/normal/.gitkeep \
   tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/negative/.gitkeep \
   tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/ambiguous/.gitkeep
```

- [ ] **Step 7: Run the harness tests to confirm these 3 categories now pass**

Run: `cd tools/phase-5-sharepoint-knowledge-agent-pilot && python3 -m pytest tests/ -v`
Expected: `test_at_least_one_case_per_in_scope_category` still FAILS (currency has no cases yet —
Task 5), everything else referencing normal/negative/ambiguous passes; run
`python3 evaluations/validate_cases.py` directly and confirm `[PASS]` for all 5 new files.

- [ ] **Step 8: Commit**

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/
git commit -m "feat(phase5): add normal/negative/ambiguous evaluation cases"
git push
```

---

## Task 4: Verify which existing `.aspx` agent is UI-selectable and pick the baseline

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/results/task4-aspx-agent-selection.md`

This is a manual verification task — there is no PnP/Graph API that reliably confirms Copilot
chat-pane agent selectability (confirmed this session: `Get-PnPCopilotAgent` returns 0 for this
site even for real, working agents). The browser is authoritative here.

**Interfaces:**
- Consumes: nothing new.
- Produces: `results/task4-aspx-agent-selection.md`'s recorded baseline agent name, consumed by
  Task 6 (which agent to run every case against).

- [ ] **Step 1: Open the SharePoint site's Copilot chat pane in a browser**

Navigate to `https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev` and open the Copilot/agent
chat entry point (site-level Copilot icon or the `CEISPilotKnowledgePages` page's chat pane).

- [ ] **Step 2: List every agent that appears as selectable**

For each of the 5 candidates, note whether it appears in the chat pane's agent picker:
`CEIS-Pilot-Knowledge-Agent`, `CEIS-Pilot-Knowledge-Agent-Corrected`, `CEIS-ASPX-Only-Test`,
`CEIS-Topic-Reviewer-with-Skills`, `CEISPilotKnowledgePages-manuallycreated`.

- [ ] **Step 3: For each selectable agent, ask one smoke-test question**

Ask: "What are the steps to initiate a new file in CEIS?" (same as `NORM-01`). Confirm it grounds
on the `.aspx` content and cites a source page, not a hallucinated answer.

- [ ] **Step 4: Record the result and pick the baseline**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/results/task4-aspx-agent-selection.md` with:
which agents were selectable, the smoke-test response for each, and which one is chosen as the
`.aspx` baseline for Task 6 (prefer `CEIS-ASPX-Only-Test` if selectable and working — its stricter
refusal-if-not-found instructions make `NEG-01`/`NEG-02` more discriminating; otherwise fall back
to `CEIS-Pilot-Knowledge-Agent`). State the reason for the choice explicitly.

- [ ] **Step 5: Commit**

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/results/task4-aspx-agent-selection.md
git commit -m "docs(phase5): record .aspx baseline agent selection"
git push
```

---

## Task 5: Upload the rendered `.md` content and write `currency` cases

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/upload-rendered-markdown.ps1`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/currency/case-currency-01.json`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/currency/case-currency-02.json`
- Remove: `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/currency/.gitkeep`

**Interfaces:**
- Consumes: `runs/ceis-manual-v2/render/rendered-output/` (already exists, from the Task 18
  pipeline run described in `start-here.md`) as upload source.
- Produces: a new SharePoint library with the rendered `.md` content, consumed by Task 6's
  new-agent creation step.

- [ ] **Step 1: Verify the source content exists and inspect its shape**

Run: `find runs/ceis-manual-v2/render/rendered-output -maxdepth 2 -type d`
Expected: `index.md` at the root plus `pages/` and `media/` subdirectories (25 pages, per
`start-here.md`'s Task 18 record).

- [ ] **Step 2: Write the upload script**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/upload-rendered-markdown.ps1`:

```powershell
<#
.SYNOPSIS
    Uploads the Task 18 rendered-Markdown CEIS output to a new SharePoint library on
    AG-CSB-INTRANET-DEV, so it can be compared against the existing .aspx pages as a
    grounding source (Phase 5 CEIS grounding-only prototype).
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),
    [string]$SourcePath = (Join-Path $PSScriptRoot "../../runs/ceis-manual-v2/render/rendered-output"),
    [string]$TargetLibrary = "CEISPilotKnowledgeMarkdown"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example to config.psd1 and fill in ClientId/TenantId/SiteUrl."
    exit 1
}
if (-not (Test-Path $SourcePath)) {
    Write-Error "Rendered output not found at $SourcePath. Confirm runs/ceis-manual-v2/render/rendered-output exists."
    exit 1
}

$config = Import-PowerShellDataFile -Path $ConfigPath
foreach ($required in @("ClientId", "TenantId", "SiteUrl")) {
    if (-not $config.ContainsKey($required) -or [string]::IsNullOrWhiteSpace($config[$required])) {
        Write-Error "config.psd1 is missing a value for '$required'."
        exit 1
    }
}

Write-Host "Connecting to SPO at $($config.SiteUrl)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop
Write-Host "Connected successfully!" -ForegroundColor Green

$existingLib = Get-PnPList -Identity $TargetLibrary -ErrorAction SilentlyContinue
if (-not $existingLib) {
    Write-Host "Creating library '$TargetLibrary'..." -ForegroundColor Cyan
    New-PnPList -Title $TargetLibrary -Template DocumentLibrary | Out-Null
} else {
    Write-Host "Library '$TargetLibrary' already exists — reusing it." -ForegroundColor Yellow
}

$files = Get-ChildItem -Path $SourcePath -Recurse -File
Write-Host "Uploading $($files.Count) files from $SourcePath..." -ForegroundColor Cyan

foreach ($file in $files) {
    $relativePath = $file.FullName.Substring((Resolve-Path $SourcePath).Path.Length + 1) -replace '\\', '/'
    $relativeFolder = Split-Path $relativePath -Parent
    $targetFolder = if ($relativeFolder) { "$TargetLibrary/$relativeFolder" } else { $TargetLibrary }

    if ($relativeFolder) {
        Resolve-PnPFolder -SiteRelativePath $targetFolder | Out-Null
    }
    Add-PnPFile -Path $file.FullName -Folder $targetFolder -ErrorAction Stop | Out-Null
    Write-Host "  Uploaded: $relativePath"
}

Write-Host "`nDone. Uploaded $($files.Count) files to '$TargetLibrary'." -ForegroundColor Green
```

- [ ] **Step 3: Dry-run count check before uploading (no writes yet)**

Run: `find runs/ceis-manual-v2/render/rendered-output -type f | wc -l`
Record the count — the script's own `$files.Count` output must match this after Step 4 runs, or
something was skipped.

- [ ] **Step 4: Run the upload script**

```bash
cd tools/phase-5-sharepoint-knowledge-agent-pilot
pwsh -File ./upload-rendered-markdown.ps1
```

A browser window opens for interactive login. Confirm the final "Uploaded N files" count matches
Step 3's count.

- [ ] **Step 5: Verify the upload on the tenant**

```bash
pwsh -Command '
Import-Module PnP.PowerShell
$config = Import-PowerShellDataFile -Path ./config.psd1
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication
(Get-PnPListItem -List "CEISPilotKnowledgeMarkdown" -PageSize 5000).Count
'
```
Expected: matches Step 3's file count.

- [ ] **Step 6: Write `case-currency-01.json`**

```json
{
  "case_id": "CUR-01",
  "category": "currency",
  "objective": "Detect whether the agent notices and flags an explicitly stale version marker in the source.",
  "primary_topic": "initiate-a-file",
  "related_topic_allowance": 0,
  "test_identity_class": "INTENDED_READER",
  "prompt": "Is the CEIS procedure for initiating a file the current version, or could it be outdated? How would I know?",
  "run_count": 1,
  "expected_semantic_behaviours": [
    "Reports what currency/version information is actually present in the source (e.g. a version line, last-modified date) if any exists.",
    "If no explicit currency signal exists in the source, states that plainly rather than guessing whether it's current.",
    "Does not claim certainty about currency the source does not support."
  ],
  "prohibited_behaviours": [
    "Do not assert the content is definitely current without a source-backed reason.",
    "Do not fabricate a version number or review date not present in the source."
  ]
}
```

- [ ] **Step 7: Write `case-currency-02.json`**

```json
{
  "case_id": "CUR-02",
  "category": "currency",
  "objective": "Detect handling when asked to compare currency across two topics that may have been reviewed at different times.",
  "primary_topic": "warrants",
  "related_topic_allowance": 2,
  "test_identity_class": "INTENDED_READER",
  "prompt": "Was the warrants procedure or the protection-orders procedure reviewed more recently?",
  "run_count": 1,
  "expected_semantic_behaviours": [
    "Checks both topics for any review-date or version metadata actually present in the source.",
    "States clearly if neither topic carries reviewable currency metadata, rather than guessing an answer.",
    "Does not treat document order or file naming as a proxy for review recency."
  ],
  "prohibited_behaviours": [
    "Do not fabricate review dates for either topic.",
    "Do not infer recency from irrelevant signals (e.g. alphabetical order, file size)."
  ]
}
```

- [ ] **Step 8: Remove the currency `.gitkeep` and run the full harness**

```bash
rm tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/currency/.gitkeep
cd tools/phase-5-sharepoint-knowledge-agent-pilot
python3 -m pytest tests/ -v
python3 evaluations/validate_cases.py
```
Expected: all tests PASS now (all 4 in-scope categories have cases); validator prints `[PASS]` for
all 7 case files.

- [ ] **Step 9: Commit**

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/
git commit -m "feat(phase5): upload rendered-markdown content, add currency evaluation cases"
git push
```

---

## Task 6: Create the `.md`-grounded comparison agent

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/create-md-comparison-agent.ps1`
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/results/task6-md-agent-creation.md`

**Interfaces:**
- Consumes: `CEISPilotKnowledgeMarkdown` library from Task 5; the baseline `.aspx` agent's
  instructions text recorded in Task 4's results file (to mirror wording, swapping only the source
  binding, per the design doc's Section 5).

- [ ] **Step 1: Retrieve the chosen baseline `.aspx` agent's exact `.agent` JSON**

```bash
pwsh -Command '
Import-Module PnP.PowerShell
$config = Import-PowerShellDataFile -Path ./config.psd1
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication
Get-PnPFile -Url "/sites/AG-CSB-INTRANET-DEV/SitePages/CEISPilotKnowledgePages/<baseline-agent-filename>.agent" -AsString
'
```
(Use the exact filename recorded in Task 4's results file.)

- [ ] **Step 2: Write the agent-creation script, swapping only the source binding**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/create-md-comparison-agent.ps1`. Fill in
`$baselineInstructions` with the exact text retrieved in Step 1 (word-for-word except changing
literal mentions of "`.aspx`"/"`CEISPilotKnowledgePages`" to "`.md`"/"`CEISPilotKnowledgeMarkdown`"
so the comparison isolates format, not instruction wording):

```powershell
<#
.SYNOPSIS
    Creates a new SharePoint agent grounded on the rendered-Markdown CEIS content
    (CEISPilotKnowledgeMarkdown), mirroring the chosen .aspx baseline agent's instructions
    so the Phase 5 comparison isolates content format, not instruction wording.
#>

[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1")
)

$ErrorActionPreference = "Stop"

$config = Import-PowerShellDataFile -Path $ConfigPath
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop

$library = Get-PnPList -Identity "CEISPilotKnowledgeMarkdown" -ErrorAction Stop
$web = Get-PnPWeb -Includes Id
$site = Get-PnPSite -Includes Id

# Fill this in with the exact text retrieved in Step 1, adapted per the docstring above.
$baselineInstructions = "REPLACE ME: paste the baseline agent's instructions here, with .aspx/CEISPilotKnowledgePages mentions swapped to .md/CEISPilotKnowledgeMarkdown"

$agentDefinition = @{
    schemaVersion = "0.2.0"
    customCopilotConfig = @{
        conversationStarters = @{
            conversationStarterList = @(@{ text = "Summarize recent items" }, @{ text = "Tell me more about..." }, @{ text = "How can you help me?" })
            welcomeMessage = @{ text = "Ask a question or get started with one of these prompts:" }
        }
        gptDefinition = @{
            name = "CEIS-Markdown-Comparison-Agent"
            description = "Phase 5 comparison agent grounded on rendered-Markdown CEIS content, for evaluating grounding/citation quality against the existing .aspx-grounded agents."
            instructions = $baselineInstructions
            capabilities = @(@{
                name = "OneDriveAndSharePoint"
                items_by_sharepoint_ids = @()
                items_by_url = @(@{
                    url = "$($config.SiteUrl)/CEISPilotKnowledgeMarkdown"
                    name = "CEISPilotKnowledgeMarkdown"
                    site_id = $site.Id.ToString()
                    web_id = $web.Id.ToString()
                    list_id = $library.Id.ToString()
                    unique_id = "00000000-0000-0000-0000-000000000000"
                    type = "Folder"
                })
            })
        }
    }
}

$tempPath = Join-Path $env:TMPDIR "CEIS-Markdown-Comparison-Agent.agent"
$agentDefinition | ConvertTo-Json -Depth 20 | Set-Content -Path $tempPath -Encoding UTF8

Add-PnPFile -Path $tempPath -Folder "SitePages/CEISPilotKnowledgePages" -NewFileName "CEIS-Markdown-Comparison-Agent.agent"
Write-Host "Created CEIS-Markdown-Comparison-Agent.agent" -ForegroundColor Green
```

- [ ] **Step 3: Fill in `$baselineInstructions` and run the script**

Edit the script to paste in the real instructions text from Step 1 (adapted per the docstring),
then:

```bash
pwsh -File ./create-md-comparison-agent.ps1
```

- [ ] **Step 4: Manually verify the new agent is selectable and grounds correctly**

In the browser chat pane, confirm `CEIS-Markdown-Comparison-Agent` appears and ask the same
smoke-test question from Task 4 Step 3 ("What are the steps to initiate a new file in CEIS?").
Confirm it cites the `.md` source, not the `.aspx` one.

- [ ] **Step 5: Record the result**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/results/task6-md-agent-creation.md`
recording the agent name, its exact instructions text used, and the smoke-test response.

- [ ] **Step 6: Commit**

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/create-md-comparison-agent.ps1 \
        tools/phase-5-sharepoint-knowledge-agent-pilot/results/task6-md-agent-creation.md
git commit -m "feat(phase5): create .md-grounded comparison agent"
git push
```

---

## Task 7: Run all 7 evaluation cases against both agents and record results

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/results/<case_id>-aspx.md` (7 files)
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/results/<case_id>-md.md` (7 files)

**Interfaces:**
- Consumes: the 7 case files from Tasks 3/5; the two agents from Tasks 4/6.

- [ ] **Step 1: For each of the 7 cases, run its `prompt` against the `.aspx` baseline agent**

For each case file (`NORM-01`, `NORM-02`, `NEG-01`, `NEG-02`, `AMB-01`, `CUR-01`, `CUR-02`), for
`run_count` runs, record: the exact response text, whether each `expected_semantic_behaviours`
item was observed, whether any `prohibited_behaviours` item was violated, and any citation given.
Save as `results/<case_id>-aspx.md`.

- [ ] **Step 2: Repeat Step 1 against the `.md` comparison agent**

Same 7 cases, same prompts, against `CEIS-Markdown-Comparison-Agent`. Save as
`results/<case_id>-md.md`.

- [ ] **Step 3: Commit results incrementally as each case completes**

Do not batch all 14 result files into one commit — commit after each case's `-aspx.md` and
`-md.md` pair is written, so partial progress is never lost to a session interruption:

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/results/<case_id>-aspx.md \
        tools/phase-5-sharepoint-knowledge-agent-pilot/results/<case_id>-md.md
git commit -m "docs(phase5): record <case_id> results for .aspx and .md agents"
git push
```

---

## Task 8: Consolidated findings and bounded conclusion

**Files:**
- Create: `tools/phase-5-sharepoint-knowledge-agent-pilot/results/consolidated-findings.md`

**Interfaces:**
- Consumes: all 14 result files from Task 7.

- [ ] **Step 1: Write the consolidated findings document**

Create `tools/phase-5-sharepoint-knowledge-agent-pilot/results/consolidated-findings.md` with:
per-case-per-format PASS/FAIL against `expected_semantic_behaviours`/`prohibited_behaviours`; any
systematic difference observed between `.aspx` and `.md` grounding (citation quality, refusal
correctness, ambiguity handling, currency handling); explicit list of what was deferred (permission
testing, native-skill comparison, production governance) per the design doc's Section 6; and this
exact bounded-conclusion sentence from the design doc's Section 1, verbatim:

> "This prototype evaluates grounded answer behavior for a selected set of researcher-created CEIS
> questions across two content representations (`.aspx` and rendered `.md`). It does not certify
> production readiness, complete permission safety, or suitability for legal decision-making."

- [ ] **Step 2: Commit**

```bash
git add tools/phase-5-sharepoint-knowledge-agent-pilot/results/consolidated-findings.md
git commit -m "docs(phase5): consolidated findings and bounded conclusion"
git push
```

- [ ] **Step 3: Open for human review**

Do not merge to `main` automatically — this repo's Per-Phase Git & Session Workflow requires
explicit human review/approval before merge. Stop here and present the branch for review.

---

## Self-review notes

- **Spec coverage:** Section 1 (scope/framing) → Task 8's bounded conclusion; Section 2 (tenant
  state) → verified inline in Tasks 4-6, not re-derived; Section 3 (two grounding targets) → Tasks
  4-6; Section 4 (evaluation design, schema change, category mapping) → Tasks 1-3, 5; Section 5
  (agent plan) → Tasks 4, 6; Section 6 (non-goals) → explicitly restated in Global Constraints and
  Task 8's findings doc.
- **No placeholders:** the one intentional placeholder (`$baselineInstructions = "REPLACE ME..."`
  in Task 6 Step 2) is deliberate and immediately resolved in Task 6 Step 3, which names the exact
  source (Task 4's results file) and exact edit to make — not a deferred unknown.
- **Type/signature consistency:** `validate_case_definition`/`validate_all_cases_in_directory`
  signatures in Task 2 match Phase 4's existing module exactly (deliberate parity, not divergence).
