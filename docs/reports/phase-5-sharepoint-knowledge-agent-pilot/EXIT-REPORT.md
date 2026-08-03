# Phase 5 Exit Report — CEIS Grounding-Only Prototype

**Disposition: `PHASE_5_ACCEPTED_WITH_LIMITATIONS`** — confirmed by the user 2026-08-03, conditioned
on all findings being documented (verified below).

## 1. Branch and commits

- Branch: `phase-5-ceis-grounding-prototype`, based on `main`.
- 17 commits ahead of `main` (`e7d8fde` .. `e3e05d7`), plus the plan doc commit `1ccb18a`.
- Design-stream files (see Section 4) remain uncommitted and are **not** part of this branch's
  history — verified via `git status --short` immediately before this report.

Commit list (oldest first):
```
1ccb18a docs: plan for Phase 5 CEIS grounding prototype
e7d8fde feat(phase5): add currency category to shared evaluation-case schema
e6632fa feat(phase5): scaffold evaluations directory and validator
01c7f0b chore(phase5): gitignore the real config.psd1 before it can be created
8c3a453 feat(phase5): add normal/negative/ambiguous evaluation cases
eb38ebb feat(phase5): upload rendered-markdown content, add currency evaluation cases
2f9e5d6 docs(phase5): record unverified ready-made-Copilot agent-launch-by-name observation
d823e0e docs(phase5): confirm path-1 agent access + tightened instructions work correctly
063663b docs(phase5): record .aspx baseline agent selection (Task 4 complete)
ea0e3e8 docs: multi-document destination-configuration design (design only, not authorized)
bc9e420 docs: implementation plan for multi-document destination configuration (planning only, not authorized to execute)
98d76c5 docs: fix 12 design defects + coding-convention gaps (planning only, still not authorized)
4ef92d0 fix(phase5): idempotent/deterministic backups + reuse existing media on upload
921b68c docs: define SharePoint agents and skills plugin domain
3ec52a3 feat(phase5): create .md-grounded comparison agent (Task 6 complete)
540b22a docs(phase5): Task 7 — run all 7 evaluation cases against both agents
1d73fdd docs(phase5): Task 8 — consolidated findings (Phase 5 prototype work complete)
e3e05d7 docs(research): extract Phase 5 Task 7/8 findings with broader relevance
```

Note: commits `ea0e3e8`, `bc9e420`, `98d76c5`, `921b68c` are the **design-stream planning
documents** (multi-document destination configuration, `sharepoint-agents-and-skills` plugin) —
they were committed to this branch as planning-only artifacts (explicitly not authorized to
implement), interleaved chronologically with Phase 5 execution work but scoped and labeled
separately in their own commit messages and doc headers. They do not touch tenant state or Phase 5
evidence.

## 2. Tasks 0–8 completion

| Task | Status | Evidence |
|---|---|---|
| 0 — plan | Done | `docs/superpowers/plans/2026-08-02-phase-5-ceis-grounding-prototype.md` |
| 1 — currency category schema | Done | `e7d8fde` |
| 2 — evaluation harness scaffold | Done | `e6632fa` |
| 3 — evaluation cases (7 total) | Done | `8c3a453`, `eb38ebb` |
| 4 — `.aspx` baseline agent selection | Done | `results/task4-aspx-agent-selection.md` |
| 5 — rendered-Markdown upload | Done | `eb38ebb`, `4ef92d0` (idempotency fix) |
| 6 — `.md`-grounded comparison agent | Done | `results/task6-baseline-verification.md`, `task6-instruction-diff.md`, `task6-md-agent-creation.md` |
| 7 — run all 7 cases against both agents | Done | `results/task7-run-ledger.md`, 14 per-case evidence files |
| 8 — consolidated findings | Done | `results/task8-consolidated-findings.md` (10/10 required sections) |

## 3. Live tenant artifacts (retained, not rolled back)

- `SitePages/CEISPilotKnowledgePages/` — 25 `.aspx` pages + 5 pre-existing `.agent` files (unchanged,
  none deleted/renamed per the design's explicit instruction).
- `CEIS-Pilot-Knowledge/pages/*.md` + `index.md` — rendered Markdown uploaded for this prototype,
  reusing the library's existing `media/` (no duplication).
- New agent: `CEIS-Markdown-Comparison-Agent.agent`, created via hand-authored JSON + `Add-PnPFile`,
  mirroring `CEIS-ASPX-Only-Test`'s live baseline instructions with only the source binding swapped.
- Selected `.aspx` baseline: `CEIS-ASPX-Only-Test` (unchanged).
- No tenant rollback was performed and none is required — nothing was deleted, and both new
  agent/content additions are intentional, retained prototype evidence.

## 4. Design-stream separation (uncommitted, NOT part of Phase 5 closure)

Confirmed via `git status --short` immediately before writing this report — still modified,
uncommitted, and untouched by this closure:

```
 M CLAUDE.md
 M docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md
 M docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md
 M docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md
```

These are architecture-drift corrective design documents (Section 0 of `CLAUDE.md`, the
`sharepoint-agents-and-skills` plugin design, the multi-document destination-configuration design,
and the vision doc's current-state banner) — **design-complete, implementation/migration not
authorized**, per `.agent/map-debt.md`'s 2026-08-02 entry. They require their own review/commit
decision, separate from Phase 5. Not lost, not silently folded into this closure.

## 5. Evaluation-case inventory and evidence counts

- 7 cases: NORM-01, NORM-02, NEG-01, NEG-02, AMB-01, CUR-01, CUR-02 (normal/negative/ambiguous/
  currency categories), schema-validated against `tools/phase-4-native-sharepoint-skills/schemas/
  evaluation-case-schema.json` (extended with the `currency` category, backward compatible).
- 20 live runs total (7 cases × 2 agents × 1–2 runs each, per each case's `run_count`).
- 14 final evidence files (`results/<CASE-ID>-{aspx,md}.md`) — the 20-vs-14 discrepancy is fully
  accounted for in `results/task7-run-ledger.md`, including the AMB-01 mislabeling correction
  (a pasted response headed with the wrong agent name was caught immediately, clarified with the
  user, and correctly filed with an explicit provenance note rather than discarded).

## 6. Consolidated findings (summary — full detail in `task8-consolidated-findings.md`)

1. **Currency-as-timestamp-proxy** (both agents, reproduced independently): asked which of two
   topics was reviewed more recently, both agents inferred an answer from SharePoint file-upload
   timestamps — an artifact of the researcher's batch-upload process, not real review metadata —
   and answered confidently with no caveat, rather than reporting `UNKNOWN`.
2. **Cross-run relationship-answer instability** (both agents, reproduced independently): a
   cross-topic-relationship question produced a hedged first-run answer and a confident,
   *mutually contradictory* second-run answer across the two agents.
3. **Ambiguity-handling — single-case, format-level difference**: on the one ambiguity case, the
   `.md`-grounded agent cleanly met the requirement on both runs; the `.aspx`-grounded agent only
   partially met it both times. Weakest finding — not confirmed at scale.
4. **Direct/negative-case quality was comparable across both formats** — no material gap.

Findings 1 and 2 were also extracted into `docs/research/field-note-aspx-vs-markdown-grounding-comparison.md`
(cross-referenced from `docs/research/README.md` index entry #8 and
`docs/vision/key-unanswered-questions.md` question #16) as part of the newly established protocol
of pulling generalizable findings into `docs/research/` after each applicable task — see
`docs/research/README.md` for the full extraction.

## 7. Citation-verification status

**Not verified.** No cited source was opened and checked against the claim it supposedly supports,
in any of the 20 runs. All findings rest on response text/structure only. Recorded explicitly as
`CITATION_SUPPORT_NOT_VERIFIED` per the evidence-discipline rule established at the start of this
work — this is the primary reason the disposition is `_WITH_LIMITATIONS` rather than an
unqualified accept.

## 8. Limitations and deferred work (per the design's own Section 6 non-goals)

- No native-skill comparison (`GROUNDING_PLUS_NATIVE_SKILL`) this round.
- No multi-identity permission/oversharing testing (only one licensed test identity available).
- No production deployment governance, lifecycle ownership, or enterprise exit-gate evidence — this
  prototype deliberately does not attempt to satisfy the governed
  `phase-5-sharepoint-knowledge-agent-pilot-spec.md`.
- No canonical-chunk editing / agent-assisted republishing (Phase 6.5 territory).
- Citation accuracy not verified (Section 7 above).
- Sample size (7 cases, 1–2 runs) is too small for statistical claims — findings 1/2 above are
  reproduced-and-strong, finding 3 is single-case and weak.
- `POSSIBLE_CONTENT_GAP` items flagged in `task8-consolidated-findings.md` Section 7 remain
  unaddressed (content authoring is out of scope for this prototype).

## 9. Final bounded conclusion (verbatim, per the design's Section 1)

> This prototype evaluates grounded answer behavior for a selected set of researcher-created CEIS
> questions across two content representations (`.aspx` and rendered `.md`). It does not certify
> production readiness, complete permission safety, or suitability for legal decision-making.

## 10. Test / evidence completeness check

- `evaluations/validate_cases.py` — all 7 case files pass schema validation.
- `tests/test_evaluations_harness.py` — passes (harness-level tests, not tenant-dependent).
- All 10 required sections present in `task8-consolidated-findings.md` (verified by section-header
  scan immediately before this report: Prototype scope, Test design, Per-case comparison ×7,
  Cross-case findings, Citation limitation, Representation conclusion, Content gaps, Prototype
  limitations, Recommended next steps, Final bounded conclusion).

## 11. Reviewer findings

No external/subagent review was run against Task 8 specifically in this closure step — findings
were self-authored/self-judged per the design's own Section 4 ("no real CEIS SME review this
round"). The disposition above was confirmed directly by the user after reviewing this summary.

## 12. Recommended next steps (from `task8-consolidated-findings.md` Section 9)

Classified `NOW` / `NEXT` / `LATER` / `DEFERRED` — see that document for the full list; highest
priority is adding an explicit "no real currency metadata → report `UNKNOWN`" test case to any
future formal Phase 3/5 currency-handling policy work, given finding 1's clean reproduction.
