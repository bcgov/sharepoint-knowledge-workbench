# SharePoint Engineering Plugin Set — how the pieces fit together

**Audience:** someone setting this repository up to do SharePoint site analysis, migration, or
modernization work. **Status:** as-built, 2026-08-07, on the Phase 9 branch.

Phase 9 added four plugins that turn this workbench from a document-conversion tool into a
SharePoint engineering toolkit. This document explains how they relate to each other, to the
existing `workbench-setup` configuration model, and — importantly — **where the seams currently
are**, so nobody assumes an integration that does not yet exist.

---

## The end-to-end flow

```text
 SETUP                    COLLECT                 ANALYSE / CONVERT              PUBLISH
 workbench-setup          [NOT OWNED]             sharepoint-discovery           sharepoint-
   setup-sharepoint-        ⚠ no plugin             analyze-page-inventory        content-
   connection               collects exports        analyze-webpart-code          publication
   validate-app-            from a live tenant.     analyze-site-navigation
   registration             You must export         analyze-custom-forms         sharepoint-
   initialize-document-     manually today.         analyze-permissions           agents-and-
   workflow                                                                       skills
   validate-workbench-    Produces the JSON       sharepoint-schema
   environment            exports every            audit-schema
                          analysis plugin          extract-choice-fields
                          consumes.
                                                  sharepoint-link-remediation
                                                    extract-links
                                                    remediate-links      ← only WRITE-capable
                                                    validate-link-integrity  skill in the set

                                                  sharepoint-page-modernization
                                                    analyze-aspx-pages
                                                    convert-aspx-pages
                                                    compose-page-preview
```

## The three contracts that hold the set together

### 1. Everything analytical is read-only and disk-only

`sharepoint-discovery`, `sharepoint-schema`, and `sharepoint-page-modernization` perform **zero
tenant I/O**. They read exports you already have and write artifacts to a directory you name. This
is enforced by tests, not just convention.

**Consequence:** they cannot fetch their own inputs. See the gap below.

### 2. Writes are gated, always

The only write-capable skill in the set is `remediate-links`, and it has three independent gates:
dry-run by default, an explicitly injected writer, and a plan-derived confirmation token that goes
stale if the underlying documents change. `workbench-setup`'s `test_connection` follows the same
shape — it requires an injected connector and raises `NotImplementedError` without one.

**If you add a tenant-writing capability later, match this pattern.** Do not introduce a default
live connection anywhere.

### 3. Honest outcomes are a shared vocabulary, not a per-plugin invention

Every plugin distinguishes the states a naive tool conflates:

| Status | Meaning |
|---|---|
| `OBSERVED` | Read successfully, content present |
| `EMPTY` | Read successfully, genuinely nothing there |
| `PARTIAL` | Some parts unreadable — recorded, never hidden |
| `UNAVAILABLE` | Input missing entirely. **No output directory is created.** |
| `FORBIDDEN` | Permission denied |
| `FAILED` | The operation failed |

`UNAVAILABLE` and `EMPTY` are never conflated. Several source scripts fabricated fallback data when
their input was missing and reported clean success; that behaviour was deliberately removed.

---

## Known seams — read before assuming integration

### ⚠ Seam 1: nothing collects the exports (the big one)

**No plugin in this repository connects to a live tenant to produce the exports the analysis
plugins consume.** The source repository's collectors (`Connect-PnPOnline`-based) were deliberately
not extracted — they would have violated the zero-tenant-I/O contract of every plugin that could
have hosted them.

**Today:** you produce exports by hand, or with your own scripts, in the shapes each plugin's
`SKILL.md` documents.

**The fix is a design decision, not a port:** a new collection plugin with an explicit
connection/write-safety boundary, built against `workbench-setup`'s connector-injection contract.
See `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/remaining-capability-roadmap.md`,
rank 1, and the concrete proposal in
`docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md` (Part A) —
**design only, not authorized to build**.

### ⚠ Seam 2: the new plugins do not read `workbench-setup`'s config

`workbench-setup` generates `config.psd1` (connection), `document-workflows/<Id>.workflow.psd1`,
and `publication-profiles/<Id>.publication.psd1`. **None of the four Phase 9 plugins read any of
them.** They take explicit paths as parameters instead.

This is **deliberate, not an oversight** — `plugin-architecture-policy.md` §1.3 requires each
plugin to install and run standalone, and the four are verified to do so via
`isolated_install_check.py`. A hard dependency on `workbench-setup` would break that.

**But it does mean there is no single "configure once, run everything" entry point yet.** If you
want one, the right shape is an orchestration layer that *reads* the config and *passes* explicit
paths down — not plugins reaching into a shared config themselves. That layer does not exist. A
concrete proposal is now written up in
`docs/superpowers/specs/2026-08-07-sharepoint-collection-and-orchestration-design.md` (Part B) —
**design only, not authorized to build**.

### ⚠ Seam 3: publication is gated on Phase 3

`sharepoint-content-publication` gained an `upload-content` skill in Phase 9, but Phase 3 — which
owns the destination library's metadata schema and source-of-truth lifecycle — has not reached its
exit gate. That skill is deliberately package-only (injected uploader required, no tenant-write
path). Treat its contract as provisional until Phase 3 closes.

---

## Installing

Each plugin installs independently:

```bash
pip install -e plugins/sharepoint-discovery
pip install -e plugins/sharepoint-schema
pip install -e plugins/sharepoint-link-remediation
pip install -e plugins/sharepoint-page-modernization
```

All four are registered in `.claude-plugin/marketplace.json`. Each has its own test suite; run any
of them with `python3 -m pytest plugins/<name>/tests/ -q`.

## Provenance

All four were extracted from a separate SharePoint migration repository under Phase 9, pinned to an
exact source commit, with every capability's origin, removed project coupling, and intentional
behaviour changes recorded in
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`. No extracted code
carries a runtime dependency on that repository — verified by test in every plugin.
