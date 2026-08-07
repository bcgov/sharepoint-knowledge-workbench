# Phase 9 Retrospective

**Date:** 2026-08-07. **Source baseline:** `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` (read-only
throughout; no source file modified). Satisfies the `phase-9-retrospective` item in spec §18.

---

## 1. What the evidence overturned

The single most valuable output of this phase was **correcting the spec's own supporting data**.
The three-axis classification *framework* held up well; the numbers underneath it did not.

| Spec claim | Reality | Consequence |
|---|---|---|
| Skills are the extraction unit | Skills are 3-file shells (`SKILL.md` + `evals.json` + `results.tsv`) symlinking into a centralized 183-file `scripts/` tree | Extraction unit was wrong; §3c added |
| `sp-migrating-content` is "richest, 44 symlinks" | **29 LIVE** — 12 into `_deprecated/`, 3 dangling | `sharepoint-content-migration` justification collapsed |
| `sp-discovering-web-parts` "19 symlinks" | **13 LIVE** — 6 escape `plugins/` into project analysis data | Data, not capability |
| `sp-auditing-schema` "IMPLEMENTED (7 symlinks)" | 6 live, **1 broken** | Anchor survived, barely |
| `sp-converting-aspx-pages` "12 scripts + 5 symlinks" | **32 real files** | Undercounted |
| `sharepoint-schema` "weakest candidate" | 6 live scripts, genuinely deep | Justified |
| 9 agents | Not classified anywhere; §5 said "seven" | §8f added |

**17% of all source symlinks (22 of 128) were not extractable** — broken, deprecated-target, or
escaping the plugin boundary. A wholesale copy would have imported four broken links into a repo
whose symlink gate rejects them outright.

## 2. What worked

- **Resolve symlinks before classifying.** Task 2a existed only because the original plan validated
  symlinks *after* classifying with them. Every correction in §1 came from that reordering.
- **Executable genericity gates.** Making "no project literals" a *test* rather than a review
  checklist caught three real violations that human review would plausibly have missed — including
  one I introduced myself in a `pyproject.toml` comment. The gate having teeth mattered more than
  the gate existing.
- **Existing-plugin-first.** Two capabilities merged into existing plugins; no new plugin was
  created without a boundary justification surviving real evidence.
- **"Not justified" as an acceptable outcome.** Explicitly authorising subagents to reject a
  capability produced three well-evidenced rejections instead of three hollow plugins.
- **Committing per wave.** After the parallel failure (§3), commit-per-wave meant no work was ever
  lost again.

## 3. What went wrong

### 3.1 Parallel dispatch lost four waves at once (process failure, mine)

Five extraction agents were launched concurrently. A session limit terminated four mid-task, all
uncommitted. **Cost:** roughly an hour of agent work, and the user's confidence.

**Root cause:** optimising for throughput while every worker held uncommitted state in a shared
failure domain. **Fix, applied:** serial execution, one wave to completion, committed before the
next begins. **Rule for next time:** if a unit of work cannot survive the harness dying, it is too
big — commit or checkpoint before starting the next one.

### 3.2 An unverified claim relayed as fact

Wave 5 was reported as "near-complete" based on file counts, without running anything. It actually
had **27 failing tests, no `pyproject.toml`, and no `skills/`**. **Fix:** every subsequent claim in
this phase was backed by pasted command output. Several subagent reports were independently
re-verified and two were found materially wrong.

### 3.3 The spec cited a tool that does not exist

§9a mandated `audit_plugin_structure.py` as repo-local. It ships with the installed
`agent-scaffolders` marketplace plugin. Wave 2 lost time hunting for it. Corrected in the spec;
logged `OPEN`/`Repeat: YES` in `map-debt.md`.

### 3.4 Genericity gates failed on their own test data — four times

The same defect recurred in four plugins: a scan for forbidden literals that includes the test
declaring those literals, or `.pytest_cache` node IDs, or the ordinary English word "records"
(substring-matching `ORDS`).

**Fix:** scope the scan to the runtime tree, use word-boundary matching, and add **anti-vacuity
guards** so the narrowing cannot silently become a no-op. **Lesson:** every time a gate was
narrowed to remove a false positive, a test was added pinning that it still fires on the real case.
Narrowing a gate without that guard is indistinguishable from disabling it.

## 4. Judgement calls worth recording

- **Three capabilities rejected on evidence,** not skipped for convenience:
  `sp-synthesizing-discovery` (fabricates its headline metrics), `sp-discovering-site-structure`
  (live-tenant collector — wrong plugin scope), `sharepoint-content-migration` (mechanism unproven
  outside deprecated code).
- **One capability deliberately dropped:** the source's `-Cleanup` switch called `Remove-PnPField`,
  a destructive tenant write. Not extracted; a test enforces its absence.
- **One security improvement over the source:** layout rules are data, therefore untrusted input.
  Conditions now evaluate through a restricted AST evaluator rejecting all call expressions —
  verified that `__import__("os").system(...)` and `open("/etc/passwd").read()` are blocked.
- **Honest-outcome vocabulary added throughout.** The source frequently conflated "nothing found"
  with "could not read", and in one case **fabricated fallback data when its input was missing**,
  reporting clean success. Now `UNAVAILABLE`, with no output written.

## 5. Coverage — stated plainly

**~20 artifacts onboarded; roughly half of the 21 implemented source skills.** Four new plugins,
two existing plugins extended, 447+ tests passing, zero broken symlinks in Phase 9 work.

This is **not** complete coverage of the source's SharePoint engineering capability, and the branch
should not be described as such. §20's exit statement — "at least one proven generic capability
family extracted... every remaining capability classified" — is met. Full onboarding was never what
§20 required, but it *is* what the working goal asked for, and that gap is real.

## 6. Open items carried forward

1. **Not merged to `main`** — requires human review per the per-phase workflow.
2. **Phase 3's exit gate remains unmet**; the waiver used here was scoped to non-publication work.
   `sp-uploading-content` (Wave 1) is the one extraction genuinely exposed to it.
3. `sp-generating-migration-reports` remains `UNVERIFIED_ACTIVE_CLAIM` — not re-verified.
4. `audit_plugin_structure.py` availability — `map-debt.md`, `OPEN`, `Repeat: YES`.
5. Live-tenant collection is unowned and needs a design decision before extraction.
6. 24 pre-existing broken symlinks in the four original Phase 4.5 plugins (`docs/diagrams` gap) —
   untouched, out of scope, but real.
