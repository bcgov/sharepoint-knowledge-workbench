# Phase 5 Design — CEIS Grounding-Only Prototype

**Status:** APPROVED (brainstorming complete, 2026-08-02). This is an exploratory prototype, not a
governed Phase 5 exit-gate pilot — see `docs/superpowers/specs/
phase-5-sharepoint-knowledge-agent-pilot-spec.md` for the full governed-pilot spec this prototype
deliberately does not attempt to satisfy.

## 1. Scope and framing

**Audience:** the user and this assistant, experimenting directly — not a real CEIS subject-matter
expert or external stakeholder. **Primary scenario:** `GROUNDING_ONLY` (per the governed spec's
Section 4 scenario-selection decision) — one or more SharePoint Copilot agents grounded only on
already-published CEIS content, no native skill required. `GROUNDING_PLUS_NATIVE_SKILL` (using the
existing `review-manual-topics` skill) is an optional future comparison, explicitly deferred.

**Bounded conclusion this prototype is allowed to produce:** "This prototype evaluates grounded
answer behavior for a selected set of researcher-created CEIS questions across two content
representations (`.aspx` and rendered `.md`). It does not certify production readiness, complete
permission safety, or suitability for legal decision-making."

**Explicitly deferred (not "passed," not "unnecessary"):** multi-identity permission/oversharing
testing (only one licensed test identity — `AG-CSB-INTRANET-DEV`, confirmed M365 E5 + Copilot
Premium — is available), production deployment governance, lifecycle ownership assignment,
native-skill comparison, enterprise exit-gate evidence per the governed spec's Sections 10-12.

## 2. Real tenant state this prototype builds on (verified, not assumed)

Verified live via PnP PowerShell against `AG-CSB-INTRANET-DEV` on 2026-08-02 (see
[[project_phase3_phase4_tenant_test_harness]] memory and `docs/research/
research-summary-phase3-sharepoint-write-capability-discovery.md`):

- **`SitePages/CEISPilotKnowledgePages/`** — 25 real `.aspx` topic pages (pandoc-converted from the
  CEIS Manual, matching its 25 topics) plus **5 existing `.agent` files**, all uploaded in the same
  minute (2026-08-01 02:26) as a deliberate batch of learning-phase agent variants — not accidental
  duplicates, do not delete:
  - `CEIS-Pilot-Knowledge-Agent.agent` / `CEIS-Pilot-Knowledge-Agent-Corrected.agent` — byte-
    identical instructions to each other; generic `.aspx`-prioritizing agent.
  - `CEIS-ASPX-Only-Test.agent` — strictest variant: `.aspx`-only, explicit images exclusion,
    explicit refusal-if-not-found behavior.
  - `CEIS-Topic-Reviewer-with-Skills.agent` — the only one also binding `AgentAssets` (the
    `review-manual-topics`/`ceis-test-skill` skills + `ceis-procedure-review-template.md`).
  - `CEISPilotKnowledgePages-manuallycreated.agent` — minimal/generic instructions, looks like a
    UI-created baseline.
  - `Get-PnPCopilotAgent` returns 0 for this site even though these files are real, working agents
    per Phase 3.0's confirmed finding that hand-authored `.agent` JSON uploaded via `Add-PnPFile`
    functions end-to-end without a UI wizard — that cmdlet just doesn't reliably enumerate this
    deployment path. Which of the 5 actually appear as selectable in the SharePoint chat pane must
    be checked directly in the browser (Task 1 below), not assumed from file existence.
- **`CEIS-Pilot-Knowledge`** (document library) — 319 media files only (images). **The rendered
  `.md` pages (`pages/*.md`, `index.md`) were never uploaded** — confirmed gap, and the reason
  this prototype's `.md` grounding source must be uploaded fresh (Task 2 below).
- Naming decision: keep `CEIS-Pilot-Knowledge` / `CEISPilotKnowledgePages` as-is. They are already
  reasonably named and already wired into 5 real agents; renaming would require redoing those
  agents' source bindings for no real benefit.

## 3. Grounding sources — two parallel comparison targets

1. **`.aspx` target** (existing): `SitePages/CEISPilotKnowledgePages/`, 25 pages, already grounds
   the 5 existing agents.
2. **`.md` target** (new upload needed): the rendered, consumption-oriented Markdown output —
   `runs/ceis-manual-v2/render/rendered-output/` (25 pages + media, publication-map ordered) —
   uploaded to a new, comparable location on the same site. This is the real peer to `.aspx` for a
   grounding/citation-quality comparison; it is **not** the canonical-content chunks (`runs/
   ceis-manual-v2/canonical-content/`), which are an editing-oriented format out of scope here —
   see `docs/vision/resolved-question-ongoing-editing-and-agent-assisted-rendering-phase-placement.md`
   for that distinct, deferred future capability (Phase 6.5).

## 4. Evaluation design

Full functional evaluation, self-authored and self-judged by the user and this assistant (no real
CEIS SME review this round). Reuses the existing, schema-validated Phase 4 evaluation-case pattern
(`tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json` +
`evaluations/validate_cases.py`) rather than inventing a new format — see
[[project_phase3_phase4_tenant_test_harness]].

**Schema change required:** add `"currency"` to the `category` enum (currently `normal`,
`negative`, `ambiguous`, `permission`, `safety`) — backward compatible, existing Phase 4 cases
still validate unchanged.

**Category mapping for this prototype:**
| Governed-spec eval type (Section 9) | Schema `category` | In scope this round? |
|---|---|---|
| Answerable | `normal` | Yes |
| Unanswerable | `negative` | Yes |
| Boundary/ambiguity | `ambiguous` | Yes |
| Currency (current/stale/superseded) | `currency` (new) | Yes |
| Permission/oversharing | `permission` | **Deferred** — only one licensed identity |

New case files live under a new `tools/phase-5-sharepoint-knowledge-agent-pilot/evaluations/`
directory, mirroring Phase 4's folder-per-category structure. Every case is run against **both**
the `.aspx`-grounded agent and the new `.md`-grounded agent, so results are directly comparable
per case, not just per format in aggregate.

## 5. Agent plan

- **Task 1:** manually check the SharePoint chat pane to confirm which of the 5 existing `.aspx`
  agents actually appear as selectable (not assumed from `Get-PnPCopilotAgent` returning 0). Pick
  one as the `.aspx` baseline — likely `CEIS-ASPX-Only-Test` (strictest, most testable refusal
  behavior) or `CEIS-Pilot-Knowledge-Agent`, decided after seeing what's actually selectable.
- **Task 2:** upload `runs/ceis-manual-v2/render/rendered-output/` to a new library/folder on the
  same site, then create one new agent grounded on it (hand-authored `.agent` JSON via
  `Add-PnPFile`, per the confirmed-working Phase 3.0 pattern), instructions mirroring the chosen
  `.aspx` baseline's instructions as closely as possible (same prioritization/refusal language,
  swapped source binding) so the comparison isolates format, not instruction wording.
- Do not delete, rename, or "clean up" any of the 5 existing `.aspx` agents.

## 6. Non-goals for this prototype

- No native-skill comparison (`GROUNDING_PLUS_NATIVE_SKILL`) this round.
- No multi-identity permission/oversharing testing.
- No production deployment governance, lifecycle ownership, or enterprise exit-gate evidence.
- No canonical-chunk editing or agent-assisted republishing (Phase 6.5 territory, not triggered).
