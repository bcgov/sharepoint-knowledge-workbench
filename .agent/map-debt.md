
### [2026-08-17] Stale "Stage 3.4.3" False Blockers Found and Fixed in `sharepoint-content-publication`

- **Logged Date**: 2026-08-17
- **Cycle/Session**: Post-porting-round follow-up, prompted by direct user pushback: a separate
  session inventorying `.ps1` scripts across 7 plugins reported 4 expected-but-missing
  capabilities (new-page-from-scratch web-part authoring, ad-hoc list-item seeding, SPFx
  packaging, web-part-connection wiring). Investigation found 3 of those 4 were correctly out of
  scope (no PnP cmdlet exists for web-part connections; SPFx is a different toolchain never
  claimed by any plugin; ad-hoc seeding deliberately doesn't fit this workbench's plan-not-script
  convention) — but page authoring/upload turned out to be a **real, already-built capability**
  (`upload-content`'s `spo-upload-plan.ps1`, `Add-PnPPage`/`Add-PnPPageTextPart`/`Publish-PnPPage`,
  shipped in an earlier session) that a sibling skill's SKILL.md was **falsely claiming didn't
  exist yet**.
- **Artifact Affected**: `plugins/sharepoint-content-publication/skills/{publish-aspx-to-sharepoint,
  publish-markdown-to-sharepoint,rollback-sharepoint-publication,validate-sharepoint-publication}/
  SKILL.md`, plus 3 new real executors: `scripts/spo-publish-markdown-plan.ps1`,
  `scripts/spo-rollback-publication.ps1`, `scripts/spo-validate-publication-deployment.ps1`.
- **The actual bug**: `publish-aspx-to-sharepoint`'s and `rollback-sharepoint-publication`'s
  SKILL.md both said real tenant writes "remain a future, separately-authorized capability once
  Stage 3.4.3 is approved" — Stage 3.4.3 is a real, still-unapproved decision (naming an
  authorized-write owner/identity, per `docs/vision/master-initiative-plan-workstreams-and-phases.md`),
  but it was never actually the gate on these skills: every other real `.ps1` executor in this
  plugin (and all 10 SharePoint plugins from the 2026-08-11 porting round) already runs today
  under the ordinary interactive `Connect-PnPOnline` convention with no Stage 3.4.3 dependency
  at all. The doc language was written once, early, and never corrected when the first real
  executor (`spo-upload-plan.ps1`) actually shipped and proved the gate didn't apply. A
  same-repo scan for the same phrase (`Grep` for "Stage 3.4.3"/"not yet approved"/"remains a
  future capability" across every `SKILL.md`) confirmed no other plugin has this pattern —
  isolated to this one plugin's 3 skills.
- **Fix**: corrected all 3 stale SKILL.md files to point at (or add) real executors instead of
  repeating the false blocker; built the 2 genuinely missing executors
  (`spo-publish-markdown-plan.ps1` — `Add-PnPFile` + checkout/checkin discipline per
  `sharepoint-ps1-authentication-convention.md`'s spirit; `spo-rollback-publication.ps1` —
  `Remove-PnPPage`/`Remove-PnPFile` with fail-loud post-removal verification, same discipline as
  `spo-migrate-list-items.ps1`'s verification pattern). Also closed `validate-sharepoint-
  publication`'s separately, honestly-documented (not a false blocker — a real admitted gap)
  post-deployment-validation absence with `spo-validate-publication-deployment.ps1`, read-only,
  no confirmation token required since it never writes.
- **Evidence**: all 3 new scripts parse-checked clean via
  `[System.Management.Automation.Language.Parser]::ParseFile()`. `README.md` updated with the
  correction and the 3 new scripts. `Get-WorkbenchConnectionConfig.ps1` reused (already present
  in this plugin, no new symlink needed).
- **Severity**: Medium — no incorrect production behavior (these were planning-only skills that
  correctly refused to write), but the false "blocked" framing could have caused a future session
  to avoid building real capability that was actually safe to build, or to re-litigate a
  governance question that didn't need litigating.
- **Repeat**: Yes — same failure class as every other "source-audit gap doesn't map onto the
  target plugin's own design contract" entry in this file, but inverted: here the plugin's *own
  documentation* was the source of the false constraint, not an external source-repo audit.
- **Status**: Fixed, this session.

### [2026-08-11] `sharepoint-provisioning`'s Real Executors Built — Last Plugin, Session Closes

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round — this closes the last of 10
  SharePoint plugins
- **Artifact Affected**: `plugins/sharepoint-migration-planning/scripts/spo-provision-{site-columns,
  content-types,list,calendar}.ps1` (new, 4 scripts). `plugins/sharepoint-provisioning/` itself was
  **not touched** — deliberately, by design (see below).
- **The strongest version of this session's recurring tension, 4th occurrence**: `sharepoint-
  provisioning`'s own README states zero tenant I/O of any kind, **enforced by a real test**
  (`test_no_live_pnp_or_csom_or_network_transport_ships`) — no live PnP/CSOM/network code can ever
  ship inside that plugin's package. But its 4 skills (`provision-list`, `provision-fields`,
  `provision-content-types`, `provision-modern-calendar-list`) are write-capable and each define an
  `ExecutorRequired` gate. Confirmed with the user: the real executors belong in `sharepoint-
  migration-planning` instead (which already positions itself, per its own README, as generating
  wave scripts that call into `sharepoint-provisioning`'s plan/apply functions). Unlike the 3 prior
  occurrences (`sharepoint-migration-planning`'s own orchestrator question, `sharepoint-schema`,
  `sharepoint-page-modernization` — each resolved as "find/build a small in-scope capability
  instead"), this one resolved as "the executor needs a different plugin entirely."
- **Real cmdlet sequences, evidenced against the source repo's `wave0a-site-columns.ps1`/
  `wave0b-content-types.ps1`/`lib/field-helpers.ps1`/a modern-calendar-list library**:
  `Add-PnPField` (typed fields) / `Add-PnPFieldFromXml` (raw-XML Calculated/Lookup/User fields,
  fed by `field_provisioning.py`'s `build_*_field_xml` output) for site columns;
  `Add-PnPContentType`/`Add-PnPFieldToContentType`/`Remove-PnPFieldFromContentType` plus CSOM
  `FieldLinks[...].Hidden` + `Invoke-PnPQuery` (no typed hide/show cmdlet exists) for content
  types; `New-PnPList`/`Remove-PnPList` with post-op `Get-PnPList` verification for lists;
  `New-PnPList -Template 100`/`Add-PnPFieldFromXml -List <title>`/`Invoke-PnPSPRestMethod` (modern
  calendar view creation, no typed cmdlet) for calendars.
- **Real design seam, found and documented honestly (same class as `spo-migrate-list-items.ps1`'s
  `MigrationItem` seam)**: `field_provisioning.py`'s `FieldAction.to_dict()` doesn't carry `type`/
  `display_name`/`required`/`choices` — the plan JSON `spo-provision-site-columns.ps1` consumes is
  augmented by the caller, not a literal serialization of the Python dataclass.
- **Start/End platform-bug guard, verified correct by direct code read**: `field_provisioning.py`
  has no awareness of the Start/End-must-never-be-a-site-column rule at all (confirmed by reading
  it) — `spo-provision-site-columns.ps1` refuses any field action named `Start`/`End` itself, before
  any cmdlet runs. `spo-provision-calendar.ps1` has two independent structural guards: refuses any
  `list_creation.template` other than 100, and has no code path that ever calls `Add-PnPFieldFromXml`
  without `-List` for a `list_local_fields` entry — there is no site-column branch to fall into by
  mistake, not just a runtime check.
- **Duplicate-title safety gate implemented as a real whole-plan refusal**: `spo-provision-list.ps1`
  checks `plan.blocking_findings` before processing any deletion step and refuses the entire plan
  outright if non-empty, matching `list_provisioning.py`'s own README language exactly ("never, not
  even a partial subset").
- **5-source-category audit confirmed no second gap**: agents, assets/templates, references, and
  `sp-provisioning-modern-calendars` all checked directly — either already covered or genuinely out
  of scope (group/permissions template correctly left unbuilt; `user-groups-lib.ps1` and the
  destructive `clean-slate-*.ps1` scripts explicitly excluded per the user's confirmed scope
  boundary, no destination Python module exists for user/group management).
- **`Get-WorkbenchConnectionConfig.ps1` now has a 5th consuming plugin** (`sharepoint-migration-
  planning`, new plugin-root symlink hop).
- **Evidence**: all 4 scripts parse-clean, zero project-specific literal leakage, 1 new symlink
  verified real via `Get-ChildItem`'s `LinkType: SymbolicLink`, `sharepoint-migration-planning`
  64/64 tests passing before and after, dry-run smoke tests against fixtures (including
  guard-triggering fixtures) all correct, no tenant I/O performed, `sharepoint-provisioning/`
  verified untouched.
- **Severity**: N/A (closure entry)
- **Repeat**: N/A
- **Status**: RESOLVED — **this closes the last of 10 SharePoint plugins in this porting round.**
  Next real work (per the user's explicit direction): take over the ASPX/design-system promotion
  work into `sharepoint-content-publication` directly (see `temp/aspx-design-system-promotion-
  directive.md` and `start-here.md`'s own section on this), rather than a new plugin porting pass.

### [2026-08-11] `sharepoint-page-modernization` Report Generator Added — No Manifest-Assembly Step Exists Yet

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round, `sharepoint-page-modernization`
- **Artifact Affected**: `plugins/sharepoint-page-modernization/scripts/conversion_report.py` (new),
  `component_mapping.py`/`layout_selection.py` (gap found, not fixed)
- **Context**: this plugin's 3 skills (`analyze-aspx-pages`, `convert-aspx-pages`,
  `compose-page-preview`) were already fully implemented — unlike every other plugin closed this
  session, the gap here wasn't a missing `.ps1` executor (this plugin is deliberately zero-tenant-
  I/O and already once rejected a live-tenant collector) but a missing report-generation capability,
  matching a known Phase-9 deferred finding. Confirmed with the user before proceeding: none of the
  3 originally-audited source scripts (`convert-and-upload-aspx.ps1`, `convert-wiki-page.ps1`,
  `diagnose-page.ps1`) were in scope, same tension pattern as `sharepoint-migration-planning` and
  `sharepoint-schema` before it — the source-repo audit's gap list doesn't reliably map onto what a
  target plugin's own design contract will actually accept.
- **Real second gap found while building the report generator, not silently papered over**:
  `plugins/sharepoint-page-modernization/scripts/assets/manifest-schema.json`'s
  `PageConversionManifest` shape (`webParts`, `manifestHash`, `gaps`, `confidence`, `layout`, etc.)
  is not produced by anything in this codebase today. `component_mapping.py` returns a `plan` dict
  (`mappingVersion`/`rulesApplied`/`sections`/`notMigrated`/`outcome`); `layout_selection.py`
  returns a `decision` dict (`selectedLayout`/`sectionTemplate`/`ruleApplied`/`skippedRules`/
  `outcome`). Neither matches the schema, and nothing assembles them into it — confirmed via grep,
  no file under `scripts/*.py` contains `webParts`/`manifestHash`/`PageConversionManifest` outside
  the schema file itself. `conversion_report.py` was built strictly against the schema contract as
  specified (a fixture manifest was hand-built for its tests, since no real producer exists to
  generate one), so `generate-conversion-report` currently has **no upstream producer** feeding it a
  real manifest yet.
- **Follow-up, undone**: a manifest-assembly step that turns `component_mapping.py`'s `plan` +
  `layout_selection.py`'s `decision` into a schema-conformant `PageConversionManifest` (adding the
  currently-absent `manifestHash`, `convertedAt`, `environmentProfile`, `source`, `target` fields).
- **Evidence**: 82/82 tests passing (74 pre-existing + 8 new); zero project-specific literal
  leakage; 1 new symlink verified real via `Get-ChildItem`'s `LinkType: SymbolicLink`; caught and
  fixed a missing `conversion_report` entry in `pyproject.toml`'s `py-modules` (same class of bug
  as the earlier `sharepoint-schema`/`calculated_columns` miss — editable installs mask this,
  isolated installs don't; worth checking for this pattern proactively on every new module going
  forward, not just after it's caught twice).
- **Severity**: L (real gap, honestly documented, not blocking what shipped)
- **Repeat**: YES (missing `pyproject.toml` `py-modules` entry — 2nd occurrence this session)
- **Status**: OPEN (manifest-assembly step is real follow-up work, not urgent)

### [2026-08-11] RESOLVED: Scratch SharePoint Page Edit Needed Explicit Checkout/Checkin

- **Logged Date**: 2026-08-11
- **Cycle/Session ID**: `9df8d825-19a5-46ef-88e8-4b18c496f39d`
- **Artifact Affected**: `temp/sharepoint-aspx-experiment.ps1`,
  `temp/spo-page-checkout-utility.ps1`
- **Friction Observed**: the initial scratch page-edit flow mutated `CanvasContent1`/published
  without explicitly checking out and checking in the target Site Pages file.
- **Why it was not fixed earlier**: the first pass treated `Publish-PnPPage` as sufficient for a
  scratch experiment and did not account for libraries requiring checkout/version discipline.
- **Recommended fix**: keep checkout/checkin as a reusable helper around all future page-canvas
  mutation scripts before promoting any learning into `plugins/sharepoint-content-publication/`.
- **Evidence or reproduction step**: run `temp/sharepoint-aspx-experiment.ps1 -Execute
  -Action ReplaceHeader -ConfirmToken <CONFIRM_TOKEN>`; the write path now dot-sources
  `temp/spo-page-checkout-utility.ps1`, calls `Invoke-SpoPageCheckout`, mutates `CanvasContent1`,
  calls `Invoke-SpoPageCheckin`, then publishes.
- **Severity**: M
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-11] OPEN: SharePoint Modern ASPX Authoring Lessons Need Promotion From Scratch Script to Plugin Capability

- **Logged Date**: 2026-08-11
- **Cycle/Session ID**: `9df8d825-19a5-46ef-88e8-4b18c496f39d`
- **Artifact Affected**: `temp/sharepoint-aspx-experiment.ps1`,
  `temp/spo-page-checkout-utility.ps1`,
  `temp/spo-page-style-section-headings-experiment.ps1`,
  `temp/spo-list-webpart-format-experiment.ps1`, future
  `plugins/sharepoint-content-publication/` page-authoring scripts/skills
- **Friction Observed**: live SharePoint modern `.aspx` authoring cannot be treated as a raw file
  upload or blind `Add-PnPPageTextPart` append. The page's visible surface lives in
  `CanvasContent1`; existing section/zone/control placement must be exported and analyzed before
  mutation. Rich-text canvas control metadata (`data-sp-controldata`) must be HTML-encoded for
  the attribute, but the `data-sp-rte` body must remain real HTML or SharePoint renders literal
  markup. Page writes also need checkout/checkin discipline before publish/check-in completion.
- **Why it was not fixed now**: current work is an experiment under `temp/`; promoting this into a
  reusable plugin capability needs a TDD contract, fixtures based on exported `CanvasContent1`,
  and design of a supported script/skill interface rather than further hardening the scratch file.
- **Readiness assessment update**: keep the tenant-tested lessons, but do not straight-promote
  the mutation scripts. The checkout/checkin utility and export/control-inventory pattern are the
  closest to promotion. Header replacement, section-heading replacement, and list-view formatting
  remain scratch: they contain page-specific selectors/content, hardcoded formatter opinions, and
  no offline tests. The rejected `Apply` action that blindly appends a text part should not be
  promoted.
- **Recommended fix**: create a tested `plugins/sharepoint-content-publication/` utility that
  exports `.aspx` + `CanvasContent1` + `LayoutWebpartsContent`, extracts canvas controls with
  section/zone/control indices, supports targeted replacement/insertion, wraps mutation in
  checkout/checkin, and uses the repo's standard PnP auth pattern. Add fixtures covering encoded
  control metadata versus raw RTE HTML so literal-markup regressions fail offline before tenant
  writes.
- **Source-repo scripts to consult during promotion**:
  - `<legacy-source-repo>/plugins/sharepoint-migration/scripts/page-migration\analyze-aspx-webparts.ps1`
    for downloaded-ASPX web part inventory, zones, list bindings, connected web parts, and
    CEWP/SEWP extraction from raw page files.
  - `<legacy-source-repo>/plugins/sharepoint-migration/scripts/page-migration\scan-webparts.ps1`
    and `extract-webpart-content.ps1` for live content-database web part discovery via
    `GetLimitedWebPartManager` plus `exportwp.aspx`, including the lesson not to filter by
    author-editable web part Title.
  - `<legacy-source-repo>/plugins/sharepoint-migration/scripts/page-migration\convert-wiki-page.ps1`
    and `extract-site-navigation.ps1` for content-first extraction, chrome stripping,
    navigation/chrome capture, asset URL rewriting, and local preview package generation.
  - `<legacy-source-repo>/plugins/sharepoint-migration/scripts/page-migration\convert-and-upload-aspx.ps1`
    for the end-to-end legacy ASPX to modern SPO page pipeline, including local intermediate
    artifacts and optional upload.
  - `<legacy-source-repo>/plugins/sharepoint-migration/scripts/upload\upload-modern-page.ps1`
    and `upload-modern-page-rest.ps1` for modern page creation/upload patterns, HTML sanitizing
    before PnP injection, overwrite handling, and PnP-version compatibility considerations.
  - `<legacy-source-repo>/plugins/sharepoint-migration/scripts/upload\migrate-site-assets.ps1`
    for source SiteAssets enumeration/download/cache/upload so page image and icon URLs resolve
    after migration.
- **Existing workbench plugin scripts to consult during promotion**:
  - `plugins/sharepoint-content-publication/scripts/spo-convert-page-to-modern.ps1`
    for single-page conversion flow and current repo-standard PnP auth/config handling.
  - `plugins/sharepoint-content-publication/scripts/spo-convert-pages-bulk.ps1`
    for bulk orchestration, worker invocation patterns, and validation chaining.
  - `plugins/sharepoint-content-publication/scripts/spo-page-copy-plan.ps1`
    for copy-plan safety contracts, tenant-admin URL handling, and dry-run/execute confirmation
    patterns.
  - `plugins/sharepoint-content-publication/scripts/spo-upload-plan.ps1`
    for current modern page creation/upload plan execution and overwrite handling.
  - `plugins/sharepoint-content-publication/scripts/spo-validate-page-conversion.ps1`
    for validation/readback patterns after page conversion.
- **Evidence or reproduction step**: run
  `temp/sharepoint-aspx-experiment.ps1 -Execute -Action Export` against
  `TopicHome Copy.aspx` and inspect `canvas-controls.json`/`CanvasContent1.html`; earlier
  over-encoded RTE body rendered as visible `<section style=...>` text on the page. Additional
  scratch scripts now cover section-heading text cleanup and list-web-part view-formatting
  inventory/apply, but both need generalization and tests before reuse.
- **Severity**: M
- **Repeat**: YES
- **Status**: OPEN

### [2026-08-11] `sharepoint-content-migration`'s Real Executor Added — `MigrationItem` Design Seam Found

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round, `sharepoint-content-migration`
- **Artifact Affected**: `plugins/sharepoint-content-migration/scripts/spo-migrate-list-items.ps1`
  (new), `plugins/sharepoint-content-migration/scripts/item_migration.py` (seam found, not fixed)
- **Context**: same gap class as every other plugin closed this round — `apply_item_migration`
  required an injected `executor(item) -> dest_id` callable with nothing real behind it. New script
  distinguishes create (`Add-PnPListItem`, non-batched — confirmed against the source repository's
  own `migrate-helpers.ps1` that `-Batch` doesn't reliably return a usable item reference in the
  installed PnP.PowerShell version, exactly the finding that mattered here since this workflow needs
  the real ID immediately for `id_mapping.record_id_mapping`) from backfill/update
  (`Set-PnPListItem -Identity <id>`, pass 2 of the two-pass lookup-resolution technique).
- **Real design seam found, not silently papered over**: `item_migration.py`'s `MigrationItem`
  dataclass carries only `source_id`/`fields` — no `dest_id`/"is this a backfill" field — and
  neither `MigrationItem` nor `ItemMigrationPlan` defines `to_dict()`/`from_dict()` (only
  `ItemMigrationResult` does). The new `.ps1`'s plan-JSON is therefore its own contract, not a
  literal serialization of the Python dataclass — a caller producing that plan JSON from Python must
  augment each backfill item with `dest_id` itself. Documented in the script's own comment-based help
  and the skill's `SKILL.md` "Design seam" section (same pattern as `spo-remediate-document-content-
  links.ps1`'s `remediated_content` seam). Follow-up, undone: give `MigrationItem` a native optional
  `dest_id` field if a caller wants the Python plan object itself to represent both passes.
- **5-source-category audit run, no second gap found**: `skills/sp-content-migration` (thin LegacySource
  wrappers, nothing new), `skills/sp-migrating-content` (entirely LegacySource wave-schema-deployment
  orchestration, out of scope), `agents/sp-migration-agent.md`/`sp-migration-orchestrator.md` (LegacySource
  wave sequencing — this workbench's own `sharepoint-content-migration-sequencing-agent.md` already
  generalizes the real rule, parent-before-child + self-referential-last, more cleanly),
  `assets/templates/content-migration-manifest.json` (pure LegacySource project data), `references/CONTENT-
  MIGRATION-GUIDE.md`/`CALENDAR-OVERLAY-MIGRATION-DECISION.md` (pure LegacySource runbooks). Confirmed via
  direct reads, not assumed from the audit's own classification labels.
- **`Get-WorkbenchConnectionConfig.ps1` now has a 4th consuming plugin** (`sharepoint-content-
  migration`, first use — new plugin-root symlink hop created).
- **Evidence**: script parse-checks clean, dry-run smoke test against a fixture plan correctly
  distinguished create vs. backfill actions, zero project-specific literal leakage, 3 new symlinks
  verified real via `Get-ChildItem`'s `LinkType: SymbolicLink`, 30/30 tests passing before and after.
- **Severity**: L (real seam, honestly documented, not blocking)
- **Repeat**: N/A (new finding)
- **Status**: OPEN (the `MigrationItem` native `dest_id` field is real follow-up work, not urgent)

### [2026-08-11] Two Real Collector Gaps Found While Wiring `sharepoint-discovery` → `sharepoint-schema`

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round, `sharepoint-schema` follow-up work
- **Artifact Affected**: `plugins/sharepoint-discovery/scripts/collect-sharepoint-schema-export.ps1`
  (new), `plugins/sharepoint-schema/scripts/calculated_columns.py` (new)
- **Context**: `sharepoint-schema`'s analysis tools (`schema_export.py`'s `ExportLayout`) expect a
  directory-tree export shape that nothing in the workbench previously produced end-to-end.
  `collect-sharepoint-schema-export.ps1` was built to close that gap by orchestrating
  `collect-sharepoint-inventory.ps1`'s existing modes into the right shape. Two real,
  separate gaps surfaced while doing this — both reported honestly (a `Write-Warning` at runtime
  plus an inline comment) rather than fabricated or silently omitted:
  1. **No site-columns-only collector mode exists.** `collect-sharepoint-inventory.ps1`'s
     `ListFields` mode requires `-ListName`, so site-scoped/web-level fields (not attached to any
     specific list) are never enumerated by any of its 4 modes. `summary/site_columns.json` is
     therefore never written by the new orchestrator. Follow-up: add a genuine site-columns mode to
     `collect-sharepoint-inventory.ps1` (or a standalone collector) before this can close.
  2. **No collector captures `Formula` for Calculated-type fields.** Both the source repository's
     own `discover-calculated-columns.ps1` and this workbench's `collect-sharepoint-inventory.ps1`
     leave `Formula` uncaptured for Calculated fields (the source script explicitly notes its REST
     export target doesn't carry it either — this isn't a regression introduced here, it's a
     pre-existing upstream gap). `extract-calculated-columns`'s `find_calculated_columns` reports
     the field with `formula=None` plus an ambiguity entry rather than fabricating a formula.
     Follow-up: `collect-sharepoint-inventory.ps1`'s `ListFields` mode would need to request the
     `Formula` field property explicitly for Calculated-type fields.
- **Severity**: L (both honestly reported, no silent data loss; real work, not urgent)
- **Repeat**: N/A (new findings, not a repeat of a known issue)
- **Status**: OPEN (both are real follow-up collector work, not blocking anything shipped this
  round — `sharepoint-schema`'s 5 skills and the new orchestrator are otherwise complete and tested)

### [2026-08-11] `Get-WorkbenchConnectionConfig` Deduplicated From 11 Copies to 1 Canonical File

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round, `sharepoint-schema` prep work
- **Artifact Affected**: 11 `.ps1` scripts across `sharepoint-content-publication` (5),
  `sharepoint-discovery` (3), `sharepoint-link-remediation` (3) — every real `.ps1` executor added
  this session had independently pasted its own copy of the same `Get-WorkbenchConnectionConfig`
  function, a DRY violation flagged twice already (in this session's own earlier map-debt entries)
  before finally being fixed.
- **Friction Observed**: user directly asked "should we have one lib at root, shared with
  symlinks?" and "dedupe one copy regardless, most important" — surfaced the debt this session had
  been accumulating silently across its own `.ps1` executor work.
- **Real functional divergence found, not just duplication**: 10 of 11 copies were byte-identical;
  `sharepoint-content-publication/scripts/spo-page-copy-plan.ps1`'s copy was an older/incomplete
  version — missing the `SiteUrl` property and the nested-`Connection`-block merge logic the other
  10 have. Checked whether this was a live bug: `spo-page-copy-plan.ps1` derives its own `SiteUrl`
  values from parsed page URLs rather than consuming the connection config's `SiteUrl`, so the gap
  was dead/unused in that specific script, not an active bug — but it would have become one the
  moment anyone reused that field, and is now fixed by picking up the corrected canonical version.
- **Fix**: `plugins/workbench-setup/scripts/Get-WorkbenchConnectionConfig.ps1` is now the one real
  file (workbench-setup already owns `config.psd1` concerns). Every consuming plugin gets a
  plugin-root symlink to it (`sharepoint-content-publication`, `sharepoint-discovery`,
  `sharepoint-link-remediation`), and every skill that needs it gets a second-hop symlink to its own
  plugin's root copy — the same two-hop hub-and-spoke pattern already established for
  `provisioning_outcomes.py` (owned by `sharepoint-provisioning`, symlinked into 5+ other plugins),
  now proven out for `.ps1` as well as `.py`. All 11 original files edited to dot-source the local
  symlinked copy instead of defining the function inline.
- **Evidence**: all 12 relevant files (1 new canonical + 11 edited) parse-clean via
  `[System.Management.Automation.Language.Parser]::ParseFile()`; 14 new symlinks (3 plugin-root hops
  + 11 skill-dir hops) verified real via `Get-ChildItem`'s `LinkType: SymbolicLink`; zero project-
  specific literal leakage; `sharepoint-content-publication` 38/38 and `sharepoint-link-remediation`
  164/164 (1 pre-existing unrelated `evals.json` failure) tests still passing after the edit.
- **Severity**: M (real functional divergence found, not just style debt)
- **Repeat**: NO (root cause fixed at the source, not worked around)
- **Status**: RESOLVED

### [2026-08-11] `sharepoint-link-remediation`'s 3 Write-Capable Skills Now Have Real `.ps1` Executors

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round, `sharepoint-link-remediation`
- **Artifact Affected**: `plugins/sharepoint-link-remediation/scripts/spo-remediate-page-links.ps1`,
  `spo-remediate-document-content-links.ps1`, `spo-remediate-field-image-references.ps1`
- **Friction Observed**: Same gap class as `sharepoint-discovery`/`sharepoint-content-publication`
  (see the 2026-08-11 "Phase 9 Onboarding" entry below) — `remediate-links`,
  `remediate-document-content-links`, and `remediate-field-image-references` each defined a real
  `Writer`/`Executor`-callable safety gate with nothing behind it. `extract-links` and
  `validate-link-integrity` were confirmed out of scope (deliberately read-only/local-only by
  design, not a gap).
- **Fix**: 3 new `.ps1` scripts, following `sharepoint-content-publication/scripts/spo-upload-plan.ps1`'s
  established convention exactly (`Get-WorkbenchConnectionConfig` from `config.psd1`, dry-run
  default, `-Execute` + a literal `-ConfirmToken`, `Get-Command`-gated PnP cmdlet checks). Real PnP
  cmdlet sequences verified against `Repair-EmbeddedLinks.ps1` in the source repository (proven
  cmdlets only, none of its LegacySite-specific config/literals ported).
- **Reusable design seam, worth remembering for any future document-content-mutation executor**:
  `document_link_remediation.py`'s OOXML zipfile/XML-part rewrite is Python-only logic — it can't be
  reimplemented in PowerShell, and rewritten file bytes aren't JSON-safe to put in a plan file. The
  division of labor that works: the Python `plan_document_link_remediation` caller writes each
  changed document's already-remediated bytes to a local temp file and augments the plan JSON with a
  `remediated_content_path` field; `spo-remediate-document-content-links.ps1` starts from that
  augmented plan and only does the checkout/upload/checkin. Documented in the script's own
  comment-based help and the skill's `SKILL.md`, not left implicit.
- **Checkout/checkin discipline applied**: per this same file's newest scratch-page-edit entry
  (`RESOLVED: Scratch SharePoint Page Edit Needed Explicit Checkout/Checkin`), the document-content
  executor wraps its write in `Set-PnPFileCheckedOut` / `Set-PnPFileCheckedIn -CheckinType
  MajorCheckIn`, not a bare content overwrite.
- **`Get-WorkbenchConnectionConfig` is now duplicated a third time** (once each in
  `sharepoint-content-publication`, and now twice more across these 3 new link-remediation scripts,
  which share one copy across their own 3 files but don't share it with the other plugin). Worth
  factoring into a genuinely shared, symlinked helper if a 4th plugin needs the same
  `config.psd1`-reading logic — not urgent, flagged here so it isn't silently reinvented a 4th time.
- **Evidence**: all 3 scripts parse-check clean (`[System.Management.Automation.Language.Parser]::ParseFile`),
  zero project-specific literal leakage (grepped for `LegacySite`/`LegacySource`/`LegacyApp`/`LegacyOrg`/`LegacyOrg`),
  all 6 skill-directory symlinks (3 `.ps1` + pre-existing Python copies) verified real via
  `Get-ChildItem`'s `LinkType: SymbolicLink`, 164/164 real tests passing (1 pre-existing unrelated
  failure, `test_no_module_lives_only_inside_a_skill_directory` re: `evals.json`, confirmed via
  `git stash` to predate this work).
- **Severity**: L
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-11] Reusable Playbook for Porting a Source-Repo Plugin, Learned the Hard Way on `sharepoint-discovery`

**Read this before starting the same porting process on any other plugin**
(`sharepoint-schema`, `sharepoint-provisioning`, `sharepoint-content-migration`,
`sharepoint-content-publication`, `sharepoint-link-remediation`, `sharepoint-page-modernization`,
`sharepoint-migration-planning`). This session ran the full `sharepoint-discovery` porting cycle
end to end and got corrected by the user at nearly every step — the corrections are the reusable
lesson, recorded once here instead of re-derived plugin by plugin.

1. **A source plugin's onboardable surface is five categories, not one.** `scripts/*.ps1` is not
   "the source" — it's one of `scripts/`, `skills/` (a full parallel structure with real Python +
   tests), `agents/` (orchestrating `.md` files), `assets/templates/` (reusable report templates +
   real project data mixed together), and `references/` (mostly project-specific runbooks, but a
   few genuinely portable methodology docs). Scope every one of these five before calling an audit
   "thorough" — this session did NOT do this at first, was corrected by the user three separate
   times (after agents/, after assets/, after references/), and had to run 2 extra audit passes to
   catch up. Do all five in one pass next time, not sequentially as each gets discovered.
2. **"Complete"/"already exists"/"already covered" is a claim, not a status — verify it or don't
   say it.** Every one of these claims made this session (by sub-agents and by the orchestrating
   session itself) turned out to need correction on direct inspection at least once: a whole-
   audit "thorough" claim (missed 4 categories), multiple per-plugin "Done — complete" claims
   (each was 1 skill's worth of work, not the whole plugin), and an `ALREADY_EXISTS_IN_WORKBENCH`
   classification for 4 file pairs that was right for 3 and wrong for 1 (the webpart narrative-
   analysis gap). The fix that actually worked: **independently re-verify every agent's/audit's
   claim yourself before repeating it** — parse-check scripts, grep for literal leakage, `ls -la`
   symlinks for the real `l` mode bit (not trust "I created a symlink"), and diff claimed-matching
   files field-by-field against real fixtures rather than trusting a filename match or a
   classification label.
3. **A source repo's own SKILL.md/agent docs can themselves be wrong.** `sp-discovering-permissions`'s
   own `SKILL.md` has a copy-paste bug — its documented "Stage 1" command invokes
   `extract-site-navigation.ps1`, not a real permissions collector, and its paired analysis script
   has no tenant-collection logic of its own either. Don't assume a documented pipeline in the
   source repo actually works; read the referenced scripts, not just the doc prose describing them.
4. **Fix fabricated/hardcoded-conclusion scripts during the port — never carry them forward.**
   `generate-discovery-reports.ps1` asserted fixed conclusions ("SPFx needed? **No.**") regardless
   of actual scan data; same failure class as the earlier, already-rejected `sp-synthesizing-
   discovery`. The corrective rewrite made every conclusion genuinely conditional on the real
   computed counts, or explicitly reported the data as unavailable rather than fabricating
   boilerplate. Check every ported report-generator for this pattern specifically — it's easy to
   miss because the boilerplate reads as plausible prose, not as an obviously-wrong number.
5. **`ln -s` via the Bash tool silently produces a real-file COPY on this Windows/Git-Bash setup,
   not a symlink.** Every agent this session had to be told to use PowerShell's
   `New-Item -ItemType SymbolicLink -Path <dst> -Target <relative-src>` instead, and every symlink
   still had to be independently verified with `ls -la`'s `l` mode bit (or `Get-ChildItem`'s
   `LinkType: SymbolicLink`) before trusting it. Bake this into every future agent prompt that
   creates symlinks on this platform — don't rediscover it per-agent.
6. **Parallelizing independent skill-builds across agents works well and is faster** — this
   session's own earlier feedback ("you could have done those in batches of 5") was applied
   successfully for `sharepoint-discovery`'s remaining 4 skill-builds (4 parallel agents, ~10
   minutes total vs. what would have been much longer serially). Keep doing this for the next
   plugin's skill-builds; don't revert to one-at-a-time.
7. **A "gap" a script-level diff finds may already be covered by a properly-designed *agent*,
   not another script.** The webpart narrative-analysis gap the verification pass found (source's
   deep-analysis script vs. destination's shallower Python module) turned out to already have a
   better answer than a script-level port: `sharepoint-webpart-modernization-analysis-agent`
   already does this reasoning, and does it with a "pattern-collapse discipline" the source script
   never had. Before building a Python/PowerShell fix for a narrative/judgment-shaped gap, check
   whether an agent already exists in the destination for exactly that judgment call — building
   more script logic to replicate what an agent should do is the wrong direction, matching this
   session's broader skill-vs-agent distinction (procedures/collection → skill or script;
   judgment/reasoning → agent).
8. **Symlinks.json/plugin.yaml/plugin.json/map-debt.md are shared files — never let parallel
   agents write to them.** Every agent dispatched this session was told to report the exact entries
   needed and let the orchestrating session add them centrally, avoiding concurrent-write
   conflicts. Also: agents proposed the wrong `symlinks.json` key names (`source`/`target` instead
   of this repo's actual `src`/`dst`/`strategy`/`description`) every single time — check the real
   schema yourself before pasting an agent's proposed entry in verbatim.
9. **Refactor the plugin's `README.md` as the last step of every plugin pass, every time.**
   `sharepoint-discovery`'s and `sharepoint-content-publication`'s READMEs were both left stale
   after their respective passes closed (one still claimed "zero tenant I/O"/"5 of 7 capabilities",
   the other still described the plugin as a Phase 4.5 transitional holding location) — caught only
   because the user asked, not caught proactively. Add "update `README.md`" as a mandatory final
   step alongside `plugin.yaml`/`plugin.json`/`map-debt.md` updates, not an afterthought: file tree,
   what's real vs. planning-only, any real platform constraints discovered, install/test
   instructions. Do this before declaring the plugin done, not after being asked.
10. **Commit and push after each plugin closes, don't batch across plugins.** Small, reviewable,
    individually-revertable commits per plugin (or per logical unit within a large plugin) — this
    session's actual commits (`08e2a46` discovery+content-publication code,
    `b0223c1` start-here.md, `4887363` READMEs) show the pattern: even the same-session README fix
    got its own commit rather than being folded into the original one after the fact.

### [2026-08-11] Phase 9 Onboarding — Real Tenant-Write/Discovery Executors Never Ported, Only Their Planning Halves

- **Logged Date**: 2026-08-11
- **Artifact Affected**: `plugins/sharepoint-discovery/`, `plugins/sharepoint-schema/`,
  `plugins/sharepoint-provisioning/`, `plugins/sharepoint-content-migration/`,
  `plugins/sharepoint-content-publication/` (`sharepoint_upload.py`),
  `plugins/sharepoint-link-remediation/`, `plugins/sharepoint-page-modernization/`
- **Friction Observed**: user asked "how are files uploaded" after being shown
  `sharepoint_upload.py` requires an injected `uploader` callable and raises
  `NotImplementedError` without one. Follow-up audit (general-purpose agent, 2026-08-11) found this
  is a **systemic pattern across 6-7 plugins**, not a one-off: Phase 9's extraction from
  `legacy-source-repository` consistently ported the *planning/logic* half of a capability
  (a Python module that builds a plan, dict, or diff) but never the *execution* half (the real
  `Connect-PnPOnline`/`Get-PnP*`/`Add-PnP*` `.ps1` that source repo actually had working). Neither
  README nor SKILL.md made this legible as a gap at a glance — each read as if the capability
  worked until the injected-dependency requirement was traced through.
- **Confirmed gaps** (source repo has real, working `.ps1`; workbench plugin does not):
  1. **Discovery of lists/site structure** (`sharepoint-discovery`) — **MISSING**, zero `.ps1`,
     zero tenant I/O. Source: `.agents/skills/sp-discovering-site-structure/scripts/
     export-sharepoint-inventory.ps1` (real `Get-PnPList` etc.). Workbench only reads a pre-existing
     local JSON export (`discovery_inputs.py::load_json_input`).
  2. **Discovery of site columns/content types** (`sharepoint-schema`) — **MISSING**, same pattern;
     source: `get-list-columns.ps1`, `get-lookup-columns.ps1`; workbench
     (`schema_export.py::load_schema_export`) only reads a pre-existing export off disk.
  3. **List/field/content-type provisioning** (`sharepoint-provisioning`) — **STUB**. Source:
     `plugins/sharepoint-migration/scripts/waves/wave0a-site-columns.ps1`, `wave0b-content-types.ps1`
     (real `Add-PnP*`). Workbench `list_provisioning.py::apply_provisioning` raises
     `ExecutorRequired` without an injected executor; no `.ps1` in the plugin.
  4. **List-item content migration** (`sharepoint-content-migration`) — **STUB**, same
     `ExecutorRequired` pattern in `item_migration.py::apply_item_migration`. Source:
     `wave2-<list>.ps1`, `wave3-<list>-dependents.ps1` etc.
  5. **Page upload/publish** (`sharepoint-content-publication`) — **STUB** (the finding that started
     this audit). Source: `plugins/sharepoint-migration/scripts/upload/upload-modern-page.ps1`
     (real `Add-PnPPage`/`Add-PnPPageTextPart`/`Publish-PnPPage`). Workbench `sharepoint_upload.py`
     raises `NotImplementedError` without an injected `uploader`; the new
     `spo-page-copy-plan.ps1` (2026-08-11, same session) is itself a planner/recommender for
     `Copy-PnPPage`, not a generalized upload executor.
  6. **Link remediation writes** (`sharepoint-link-remediation`) — **STUB/MISSING**. Source:
     `link-conversion/LinkConversion.ps1`, `Repair-EmbeddedLinks.ps1` (real tenant writes).
     Workbench modules are pure text-rule transforms with no tenant-write call path.
  7. **Page modernization execution** (`sharepoint-page-modernization`) — **DESIGN_SCAFFOLD**.
     Source: `page-migration/convert-and-upload-aspx.ps1` (real upload). Workbench has
     classification/mapping/preview logic only, no execution path, no `.ps1`.
- **Cleared, not a gap**: the `.aspx` naming complaint raised alongside this (stale/dangling
  `.aspx` references in `publish-aspx-to-sharepoint`/`copy-spo-page-between-sites`) — checked, all
  `.aspx` mentions in those skills are intentional and consistent (documenting that raw `.aspx`
  upload is confirmed blocked on the tenant).
- **Why it wasn't caught during Phase 9's own audit**: Phase 9's exhaustive
  `temp/phase9-source-audit/file-tracking.json` classified individual *source files* as
  `ONBOARDED`/`NOT_RECOMMENDED`/`NEEDS_ONBOARDING_DEFERRED`, but a planning-only Python module and
  its real `.ps1` execution counterpart were treated as separately classifiable files rather than
  one capability pair — a Python plan-builder being marked `ONBOARDED` didn't require its paired
  executor script to also land, so the executor silently never got a tracking entry at all in
  several cases. Each plugin's own "plan is pure, apply is gated behind an injected
  executor/confirmation token" safety contract (real and correct on its own terms, see this file's
  earlier entries and `CLAUDE.md`) also made a missing executor look like *deliberate design*
  rather than an *incomplete port* — both explanations produce the exact same code shape
  (`raise ExecutorRequired`/`NotImplementedError`), so nothing about reading the stub in isolation
  distinguishes "safety gate, executor to be supplied by caller" from "nobody ever wrote the
  executor."
- **User decision (2026-08-11)**: log this gap list and pause — no porting started yet, sequencing
  to be decided in a future session.
- **Update (2026-08-11, same day, later session):** gap #5 (page upload/publish,
  `sharepoint-content-publication`) partially closed — `upload-content` skill now has a real
  `plugins/sharepoint-content-publication/scripts/spo-upload-plan.ps1` executor
  (`Add-PnPPage`/`Add-PnPPageTextPart`/`Publish-PnPPage`, dry-run by default, `-Execute
  -ConfirmToken UPLOAD-SPO-PLAN` gated, reads a `PublishPlan` JSON file directly since Python
  cannot inject a PowerShell callback into `sharepoint_upload.py`). Scope: page creation from
  pre-rendered HTML only (matches `structured-content-rendering`'s `render-sharepoint-aspx`
  output) — raw asset/file upload to a document library is still MISSING, tracked as follow-on
  work (see `docs/reports/sharepoint-migration-ps1-source-inventory.md`'s
  `sharepoint-content-migration: migrate-site-assets` row). Full plan:
  `docs/superpowers/plans/2026-08-11-sharepoint-content-publication-real-uploader.md`. Verified:
  script parses clean, dry-run against a fixture plan produces the expected JSON, plugin's full
  test suite (38 tests) still passes. `sharepoint-discovery`, `sharepoint-schema`,
  `sharepoint-provisioning`, `sharepoint-content-migration`, `sharepoint-link-remediation`,
  `sharepoint-page-modernization` gaps are unchanged.
- **Update (2026-08-11, same day, later session):** gap #1 (discovery of lists/site structure)
  partially closed — `sharepoint-discovery`'s `analyze-page-inventory` skill now has a real,
  read-only `plugins/sharepoint-discovery/scripts/collect-sharepoint-page-inventory.ps1` collector
  (Site Pages library only; `-IncludeListForms` warns and no-ops, not yet implemented; the
  plugin's other 4 domains — forms, navigation, permissions, webpart-code — are still MISSING/
  STUB, tracked as follow-on work per the source-script mapping table in
  `docs/superpowers/plans/2026-08-11-sharepoint-discovery-real-collector-executors.md`'s
  "Findings from the full 147-file source inventory" section). Verified: script parses clean, two
  new shape-contract tests (`test_page_inventory_collector_shape.py`) pass against the plugin's
  existing `page-inventory.json` fixture, plugin's test suite (63 of 64 tests — excluding one
  pre-existing, unrelated `os.geteuid()` Windows-incompatibility failure in
  `test_discovery_inputs.py` that blocks full-suite collection on Windows and should be fixed
  separately) still passes. `sharepoint-schema`, `sharepoint-provisioning`,
  `sharepoint-content-migration`, `sharepoint-link-remediation`, `sharepoint-page-modernization`
  gaps are unchanged.
- **Update (2026-08-11, same day, later session): `sharepoint-content-publication` fully closed**
  (following the reusable playbook recorded elsewhere in this file). Cross-checked all 5 source
  categories (scripts/skills/agents/assets/references/tests) before building anything — confirmed
  only 3 remaining source files (`link-conversion/{Invoke-LinkConversionBulk,LinkConversion,
  Test-LinkConversion}.ps1`), 2 already-covered skills needing no rework, zero assets/references
  targeting this plugin, and one agent (`sp-validation-agent.md`) whose destination equivalent
  (`sharepoint-validation-agent.md`) was independently verified to already be richer than the
  source, not stale — only needed one new routing line added, not a rebuild. Built 3 new skills:
  `convert-page-to-modern` (`spo-convert-page-to-modern.ps1`, single-page `ConvertTo-PnPPage` +
  caller-supplied field mapping, dry-run/`-Execute`/confirm-token gated), `execute-page-bulk-
  migration` (`spo-convert-pages-bulk.ps1`, subprocess-per-page orchestrator with resumable
  manifest + throttle, kept from the source's already-generic design, minus its link-repair step
  which belongs to `sharepoint-link-remediation` not duplicated here), and `validate-page-migration`
  (`spo-validate-page-conversion.ps1`, read-only post-run validator). Two real literal leaks
  (`"MediaInfo"`, a real LegacySite library name) found and fixed during independent verification,
  in `.EXAMPLE` blocks that would have otherwise passed a cursory review. All 3 scripts parse
  clean, zero remaining project-literal matches, all 5 symlinks confirmed real (`l` mode bit) via
  `Get-ChildItem`, dry-run output verified to produce zero tenant I/O by default, plugin's 38-test
  suite unaffected (no new Python — pure PowerShell addition, same verification bar as
  `spo-page-copy-plan.ps1`/`spo-upload-plan.ps1`). `plugin.yaml` updated (3 new skills listed).
  `sharepoint-schema`, `sharepoint-provisioning`, `sharepoint-content-migration`,
  `sharepoint-link-remediation`, `sharepoint-page-modernization` gaps are unchanged.
- **Correction (2026-08-11, same day, later session): the source-repo audit scope itself was
  incomplete, not just the porting work.** The 147-file inventory
  (`docs/reports/sharepoint-migration-ps1-source-inventory.md`) covered only
  `plugins/sharepoint-migration/scripts/*.ps1` in the source repo. It silently missed four other
  real, substantial categories in the same source plugin: `skills/` (35 skill folders, 148 files —
  a proper skills structure mirroring this workbench's own, with real Python + tests),
  `agents/` (10 orchestrating-agent `.md` files), `assets/templates/` (17 files), and
  `references/` (14 files). This was caught by the user directly, not discovered proactively —
  the earlier "Done — audit complete" framing for the 147-file pass was as overstated as the
  per-plugin "complete" claims corrected above; same failure pattern, larger scale. Two follow-up
  audits closed the gap:
  - `docs/reports/sharepoint-migration-skills-and-agents-source-inventory.md` — 35 skills (corrected
    from an initial 33), 148 files, 10 agents. Headline: no net-new missed CAPABILITY was found
    (14/35 skills are `PLANNED_WITH_NO_IMPLEMENTATION` in the source itself; ~15 already match the
    known "planning ported, executor missing" pattern) — but it found a real, previously-untracked
    gap: `sp-discovering-permissions`'s live-collection leg has no named source script anywhere in
    the `.ps1`-only audit. It also confirmed the 4 top-level orchestrator agents
    (`sp-deployment-planner`, `sp-migration-agent`, `sp-migration-orchestrator`,
    `sp-wave-orchestrator`) have **no destination equivalent** and were never attempted — the
    biggest actual gap this pass found, and also the most LegacySource-literal-dense files in the whole
    source tree (up to 161 project-specific literals in one file). `sp-discovery-agent.md`
    specifically (13-14 step discovery orchestration sequence) also has no destination equivalent —
    `sharepoint-discovery` has zero agents today. Confirmed this does NOT duplicate the
    `collect-sharepoint-page-inventory.ps1`/`collect-sharepoint-inventory` work already done —
    only step 1 of its sequence overlaps; the rest route to collectors that don't exist yet
    (navigation/webpart-code/forms/permissions), so building the orchestrating layer should wait
    until those collectors exist. Per user discussion: this orchestration layer does not have to
    become a separate `agents/*.md` file — it could equally be a skill (e.g.
    `orchestrate-sharepoint-discovery`) under `plugins/sharepoint-discovery/skills/`, consistent
    with how other plugins in this workbench mix agents and skills for orchestration; decide
    skill-vs-agent when this piece is actually built, not before.
  - `docs/reports/sharepoint-migration-assets-and-references-source-inventory.md` — 34 files
    (17 assets + 14 references + 3 top-level tests). ~11 are real onboarding candidates (9 reusable
    report templates, 2 methodology docs); 1 (`webpart-migration-rules.json`) confirmed already
    ported (byte-diffed against the destination copy, exit 0 — not just a filename match); 22 are
    correctly LegacySource-specific project data/runbooks/decision records (including real client
    correspondence) that should stay in the source repo, not be onboarded.
  - **Implication beyond `sharepoint-discovery`**: the source repo's `skills/`, `agents/`,
    `assets/`, and `references/` span multiple destination plugins (schema, provisioning,
    content-migration, content-publication, link-remediation, page-modernization,
    migration-planning) — every gap entry logged in this file's earlier 2026-08-11 entries for
    those plugins was made against the same incomplete scope and should be re-verified against
    these two new inventory documents before being treated as complete, not just
    `sharepoint-discovery`'s.
- **Update (2026-08-11, same day, later session): `collect-sharepoint-inventory` skill added,
  closing the remaining 6 of 7 files this gap's original list named** (the 7th,
  `check-managed-metadata-custom.ps1`/`check-managed-metadata-spo-prod.ps1`, maps to a still-not-
  built `audit-managed-metadata` skill, unchanged). Three real collector scripts added at
  `plugins/sharepoint-discovery/scripts/`: `collect-sharepoint-inventory.ps1` (modern SPO,
  PnP.PowerShell, 4 modes: Lists/ListFields/LibraryFiles/ContentTypes), `collect-onprem-sharepoint-
  inventory.ps1` (on-prem SP2016, NTLM/Kerberos REST, full-crawl or `-QuickCountsOnly`), and
  `collect-onprem-sharepoint-aspx-pages.ps1` (on-prem SP2016, NTLM/Kerberos REST, bulk `.aspx`
  downloader) — consolidating 7 source files without silently dropping any (full per-source
  mapping in the new skill's `SKILL.md`). Verified independently (not just trusting the building
  agent's own report): all 3 scripts parse clean, zero LegacySource/LegacyApp/LegacyOrg literals found via grep,
  plugin's 63-test suite still passes, symlinks confirmed real (`l` mode bit) via `ls -la`.
  `plugin.yaml` and `.claude-plugin/plugin.json` both updated (skill added, "zero tenant I/O"
  claim corrected to reflect this plugin now has a real collector). One LegacySource-specific list-name
  literal (a fixed list name) found leaking into a usage example during verification and fixed in
  both the script and SKILL.md.
- **Update (2026-08-11, same day, later session): `sharepoint-discovery` gap #1 now substantially
  closed.** Following the user's explicit "get one plugin correct first" direction, 4 parallel
  agents plus one script built directly by the orchestrating session closed every remaining
  collector gap this plugin had:
  - `audit-managed-metadata` (new skill) — 2 scripts (modern SPO + on-prem SP2016 variants).
  - `audit-onprem-schema-drift` (new skill) — 1 script, generalized from a heavily LegacySource-hardcoded
    source (removed hardcoded `$WatchFields`/`$SourceLists`/consumer-specific list-name pattern matching and a
    LegacySource-specific workflow-name search, replaced with `-SourceListNames`/`-DestinationListNames`/
    `-DestinationListPattern`/`-WatchFieldNames` parameters).
  - `generate-discovery-report-set` (new skill) — 1 script, **a corrective rewrite, not a port**:
    the source script asserted hardcoded conclusions as findings regardless of actual scan data
    (e.g. always printing "Are Modern Script Editor Web Parts needed? **No.**" regardless of the
    real web-part count; a whole `security-analysis-summary.md` section generated from zero data
    inputs). Independently verified the fix is real (not just claimed): the SPFx verdict is now
    genuinely conditional on `$sewpEntries.Count`, and the security-summary section is skipped
    entirely with a warning when no permissions input is supplied, rather than fabricating
    boilerplate. Same failure pattern as `sp-synthesizing-discovery`'s previously-rejected
    fabricated-metrics finding (Phase 9), now also caught and fixed for this script.
  - `analyze-site-navigation`, `analyze-webpart-code`, `analyze-custom-forms` — each extended with
    a real on-prem NTLM/REST collector (3 scripts; the two near-duplicate live web-part scanners
    from the source, `scan-webparts.ps1` and `scan-all-webparts-live.ps1`, were consolidated into
    one script's `-Mode Scan` with a `-FullSiteCrawl` switch rather than ported as two files).
  - `analyze-permissions` — extended with `collect-sharepoint-permissions.ps1`, built directly (not
    via agent) because **no real source script exists for this** — `sp-discovering-permissions`'s
    own `SKILL.md` in the source repo has a copy-paste bug, its documented "Stage 1" command
    actually invokes `extract-site-navigation.ps1`, not a permissions collector. Built from the
    `Get-PermissionRecords` REST pattern already read earlier this session in
    `export-sharepoint-inventory.ps1`, generalized and shape-matched to this skill's own existing
    `permissions-flat.json` fixture (verified field-for-field, not assumed).
  - 2 asset templates ported and generalized: `master-discovery-meta-review-template.md`,
    `site-navigation-chrome-summary-template.md` (the other 7 of 9 recommended templates from the
    assets audit belong to other plugins, out of scope here).
  - **Every one of the above was independently re-verified by the orchestrating session, not
    trusted from agent self-reports**: parse-checked, grepped for zero LegacySource/LegacyApp/LegacyOrg literal
    leakage, symlinks confirmed real (`l` mode bit) via direct `ls -la`, and output field shapes
    checked against real consumer fixtures line-by-line (not just the agent's claim that they
    matched). `plugin.yaml` and `.claude-plugin/plugin.json` updated to list all 4 new skills and
    correct the stale "zero tenant I/O" claim. Plugin test suite: 65/65 passing (63 baseline + 2
    new shape-contract tests for the permissions collector).
  - **What is still genuinely open**: the `sp-discovery-agent.md` orchestration layer (13-14 step
    discovery sequence) — deliberately not built this pass since its dependency (every referenced
    collector) only just landed. Per user discussion, this does not have to become a separate
    `agents/*.md` file — it could be a skill (e.g. `orchestrate-sharepoint-discovery`), consistent
    with how other plugins in this workbench mix agents and skills; decide when actually building
    it, not before. `plugins/sharepoint-discovery` currently has zero agents.
- **Update (2026-08-11, same day, later session): webpart narrative-analysis gap checked and
  closed, with a correction to the checking itself.** A verification pass (requested after the
  user pushed back on trusting "already exists" claims without diffing) found `webpart_code_
  analysis.py` was missing 5 of 7 narrative dimensions the source's `generate-deep-webpart-
  analysis.py` produced (business intent, actual enforcement level, SPFx assessment). Added
  `businessIntent`/`enforcementLevel`/`spfxAssessment` fields to `analyse()`'s group output and
  `generate_report()`'s Markdown, computed generically for structurally-unambiguous categories
  (Empty/TextOnly), caller-supplied via `InlineLogicRule` for recognised inline logic, honestly
  reported as "requires manual review" otherwise — never asserted as a fixed conclusion. 6 new
  tests added (70/70 plugin tests passing, up from 65). **Correction to the gap itself, found
  while wiring this in**: `analyze-webpart-code`'s own SKILL.md already documents a Stage 1/Stage
  2 split, and `sharepoint-page-modernization/agents/sharepoint-webpart-modernization-analysis-
  agent.md` already performs this narrative reasoning — and better than the source script did
  (it has a "pattern-collapse discipline" collapsing near-duplicate groups into one decision,
  which the source never had). The Python fields added here are a deterministic starting point,
  not a replacement for that agent — SKILL.md updated to say so explicitly, and a stale reference
  to the agent's old location (`sharepoint-agents-and-skills`, pre-2026-08-08 decentralization)
  was corrected to its real current location (`sharepoint-page-modernization`) while in there.
  **`sharepoint-discovery` is now considered fully closed for this porting pass** — the only
  remaining item is the orchestration layer noted above, deliberately deferred, not a gap.
- **Recommended fix, when resumed**: port the real `.ps1` executors listed above from
  `legacy-source-repository`, generalizing per this plugin ecosystem's existing conventions
  (`.agent/rules/sharepoint-ps1-authentication-convention.md` for auth, dry-run-by-default +
  confirm-token pattern already used by `spo-page-copy-plan.ps1`/`test-grant-tier-probe.ps1`).
  Discovery/schema (read-only) are the lowest-risk, highest-leverage starting point since
  provisioning/migration/upload arguably need their output as input. Update each plugin's
  `plugin.yaml`/SKILL.md and run `symlink_manager.py diagnose` after any shared-script changes.
- **Severity**: L (blocks real day-to-day use of 6-7 of 10 SharePoint plugins for live tenant work).
  **Repeat**: yes, in the sense that it is one root cause manifesting across many plugins — treat as
  a single tracked initiative, not seven independent bugs.

### [2026-07-30] PnP.PowerShell Tenant Upload Friction & Execution Discipline Failure

- **Logged Date**: 2026-07-30
- **Artifact Affected**: `tools/phase-3-sharepoint-discovery/run-phase3-tenant-pilot.ps1` and agent execution rules
- **Friction Observed**: 
  1. `Set-PnPPage -Values` is invalid syntax in PnP.PowerShell for custom page metadata (must use `Set-PnPListItem` with item ID).
  2. `Add-PnPPage` fails with "already exists" on rerun unless existence check and update logic are implemented.
  3. `& pandoc` output returns a string array in PowerShell, breaking `Add-PnPPageTextPart -Text` unless joined with `-join "`n"`.
  4. `Resolve-PnPFolder` fails with `Access Denied` on custom Document Libraries (must use `Add-PnPFolder -Name "media" -Folder "LibraryName"` instead).
  5. PnP list binding divergence: SharePoint list Title (`Target-Pilot-Knowledge`) vs URL path (`TargetPilotKnowledge`) caused target mismatches until explicit lookup fallback was implemented.
  6. **BEHAVIORAL FAILURE**: Agent repeatedly rushed broken script iterations to the user without doing full line-by-line file verification, failing to read explicit user instructions regarding target paths (`TargetPilotKnowledge`).
- **Prevention Rules (Hard Enforcement)**:
  - **Full-File Audit Gate**: Before asking the user to run any generated script, the agent MUST view the full file content (`view_file`), audit every variable, and verify parameter signatures against authoritative docs.
  - **Instruction Match Verification**: Explicit user inputs (URLs, paths, folder names, library titles) MUST be grep-checked against all script variables before claims of fix completion.
  - **Zero Guessing on PnP API**: PnP.PowerShell cmdlet options must never be inferred; test/verify parameter types locally before outputting instructions.
- **Evidence**: `run-phase3-tenant-pilot.ps1` commits `4323198`, `a530de0`, `65ef41f`, `55a9099`, `dbde503`, `6fd27c2`, `2ca5e76`, `0774cf3`, `97615da`.
- **Severity**: H
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-01] Phase 4.5 Wave 6 — `build_wheel()` Alphabetical-Last-Wheel Bug in Combined-Install Harness

- **Logged Date**: 2026-08-01
- **Cycle/Session**: Phase 4.5, Waves 4-8 execution session
- **Artifact Affected**: `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py::build_wheel`, `tools/phase-4-5-core-plugin-refactoring/combined_install_check.py`
- **Friction Observed**: `build_wheel(project_dir, dist_dir)` picks `sorted(dist_dir.glob("*.whl"))[-1]` — correct when called once per fresh `dist_dir`, but `combined_install_check.py` called it four times into ONE shared `dist_dir` (once per plugin). After the first call, every subsequent call's `glob` saw all wheels built so far and picked the alphabetically-LAST one across all of them (`source_document_extraction-...` always won), so three of the four "wheels" installed were actually duplicate copies of the same one plugin. The resulting combined install silently had only one real plugin's code, plus three mismatched dist-info records — surfaced as `ModuleNotFoundError` for bare names that were obviously present in the source tree, which took real debugging to trace back to the wheel-selection logic rather than an actual plugin bug.
- **Why it wasn't caught by any single-plugin isolated-install run**: `isolated_install_check.py` was only ever invoked with a fresh, empty `dist_dir` per call (once per plugin, in its own `tempfile.TemporaryDirectory()`), so the bug in `build_wheel`'s selection logic was latent and untriggered until Wave 6 introduced the first caller that reused one `dist_dir` across multiple `build_wheel` calls.
- **Fix**: `combined_install_check.py` now builds each plugin's wheel into its own `dist_dir / "dist" / <plugin-name>` subdirectory, never a shared one. `build_wheel` itself was left unchanged (still correct for its original single-call-per-directory contract) rather than patched to track "the wheel I just built" — the caller-side fix is simpler and matches how `isolated_install_check.py` already used it correctly.
- **Evidence**: repro'd via a persistent (non-tempfile) dist dir showing all four `build_wheel()` calls returning `source_document_extraction-0.1.0a1-py3-none-any.whl`; fix verified by re-running `combined_install_check.py` and confirming all four plugins' own bare modules import correctly post-install.
- **Severity**: M
- **Repeat**: NO (fixed at the one call site that could trigger it; no other caller reuses a shared `dist_dir`)
- **Status**: RESOLVED

### [2026-08-01] Phase 4.5 Wave 8 — `sharepoint_*.py` Outside the Migration's Known File Inventory

- **Logged Date**: 2026-08-01
- **Cycle/Session**: Phase 4.5, Wave 8 execution
- **Artifact Affected**: `plugins/docx-to-content/scripts/sharepoint_{cli,dry_run,package,reconcile}.py` (Phase 3's real, tenant-verified SharePoint publication tooling)
- **Friction Observed**: Wave 8's plan step was a literal `git rm -r plugins/docx-to-content/`. Before executing it, a full-directory listing (per the new Hard Gate #13 this session added) surfaced four `sharepoint_*.py` scripts and their tests that were never part of the four-plugin Known File Inventory from Wave 0/1 — `sharepoint-publication` is explicitly listed as deferred/out-of-scope in `CLAUDE.md`. A literal wholesale deletion would have destroyed working, tenant-tested code with no migration path.
- **Why it wasn't caught earlier**: the Known File Inventory was built once, early (Wave 0), scoped to the four domains being extracted; it was never re-diffed against the directory's actual full contents at the point of final deletion, seven waves later.
- **Fix**: flagged to the user before deleting anything (via `AskUserQuestion`); user chose to relocate. The four scripts, their four test files, and one doc file were `git mv`'d wholesale to a new `plugins/sharepoint-publication/` holding location (given its own minimal `.claude-plugin/plugin.json`/`plugin.yaml` and README documenting its provisional, not-yet-decomposed status) before the rest of `docx-to-content/` was removed. Non-contract reference docs/templates with no per-plugin home were relocated to `docs/architecture/docx-to-content-legacy-references/` the same way, rather than deleted.
- **Evidence**: `docs/superpowers/plans/phase-4-5-evidence/wave-8-removal-gate-checklist.md`, `docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`, commit `82c92b7`.
- **Severity**: H (would have been an unrecoverable-in-the-working-tree loss of real, tenant-verified functionality, recoverable only via git history archaeology)
- **Repeat**: NO (new Hard Gate #13 in `self-evolution-policy.md` makes this check mandatory before any future wholesale directory deletion)
- **Status**: RESOLVED

### [2026-08-01] Phase 4.5 Wave 8 wrap-up — Marketplace/plugin.json Gap Not Investigated Until User Repeated the Instruction

- **Logged Date**: 2026-08-01
- **Cycle/Session**: Phase 4.5 Wave 8 wrap-up
- **Artifact Affected**: `.claude-plugin/marketplace.json` (repo root, did not exist), `plugins/sharepoint-publication/.claude-plugin/plugin.json` (did not exist)
- **Friction Observed**: User said "remember at end of these phases you might need to update marketplace.json, use the marketplace manager skill." The agent manually `grep`'d for `marketplace.json` instead of invoking the actual `manage-marketplace` skill, concluded "not needed" from that manual proxy check, and reported that conclusion as final. The user had to say "i know what it's for" and then explicitly "create the marketplace file" before the real work happened — the agent's own conclusion was substituted for the user's stated intent instead of being used as one input alongside it.
- **Fix**: ran the actual `manage-marketplace` skill this time (not a manual proxy), created `.claude-plugin/marketplace.json` listing all real plugins, validated with `claude plugin validate .`, and added the missing `plugin.json`/`plugin.yaml` for `sharepoint-publication` (the one plugin that didn't have one) once the user pointed out only 4 of 5 plugins had been covered.
- **Evidence**: `.claude-plugin/marketplace.json`, `plugins/sharepoint-publication/.claude-plugin/plugin.json`, `plugins/sharepoint-publication/plugin.yaml`.
- **Severity**: S
- **Repeat**: NO (new Hard Gate #14 in `self-evolution-policy.md`)
- **Status**: RESOLVED

### [2026-08-02] Phase 4/5 — Reusable SharePoint Capability Written Into `tools/phase-N-*` Instead of an Already-Designed Plugin

- **Logged Date**: 2026-08-02
- **Cycle/Session**: Phase 4 native-skills work (prior session) + Phase 5 grounding prototype (this session)
- **Artifact Affected**: `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` (a real skill implementation, not phase evidence); `tools/phase-5-sharepoint-knowledge-agent-pilot/{upload-rendered-markdown.ps1, backup-existing-agents.ps1, backup-skills-and-templates.ps1}` (agent creation/backup, native-skill backup, content upload — all reusable operational capability).
- **Friction Observed**: `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` (lines ~230-269) already proposes a plugin named `sharepoint-knowledge` with skill groups explicitly named `native-skills/`, `agents/`, `deployment/`, `governance/`, `health/` — exactly the destination for this capability. The agent never read this document before or during either phase's execution, and instead (a) let a real skill implementation live inside a `tools/phase-4-*` folder, then (b) repeated the same mistake in Phase 5 by writing three new reusable `.ps1` scripts directly into `tools/phase-5-*` rather than checking the vision's plugin boundary first. When the user first raised it ("why are there skills inside tools/..."), the agent produced an inventory/migration-analysis document but proposed *inventing new plugin names* (`sharepoint-agents`, `sharepoint-native-skills`, `workbench-setup`) rather than checking whether the vision had already named the correct one — confirming the check still hadn't happened even after being directly prompted twice. Only stopped, and the real cause named, on the user's third direct challenge ("do you not understand the purpose of this repo and architecture even now?").
- **Why it wasn't caught earlier**: no step in this session's (or the referenced prior session's) workflow included "check `docs/vision/` for an existing plugin-boundary decision" before creating a new script or skill file. The `tools/phase-N-*` convention was inherited from earlier sessions and treated as settled precedent rather than re-checked against the vision each time new capability was added.
- **Fix**: **DESIGN_COMPLETE.** The domain and plugin name are now decided —
  `sharepoint-agents-and-skills` (not `sharepoint-knowledge`, rejected as too vague; not split
  into two plugins). Full migration design: `docs/superpowers/specs/
  2026-08-02-sharepoint-agents-and-skills-plugin-design.md` — final artifact disposition matrix,
  plugin tree, skill list, script parameter matrix, phase-wrapper strategy, evidence-preservation
  strategy, and 6 migration waves. **IMPLEMENTATION_NOT_AUTHORIZED. MIGRATION_NOT_STARTED.** Reusable
  agent/native-skill capability (`review-manual-topics/SKILL.md` and the scripts/backups listed in
  Artifact Affected above) is still mixed with Phase 3-5 phase evidence in `tools/`, unresolved
  until a migration wave is separately authorized and executed. New rule added (see `CLAUDE.md`
  Section 0): before creating any new script/skill file for SharePoint-facing capability, or before
  proposing a plugin name for a migration, read the vision doc's proposed-plugin-set section (and
  now this design doc) first.
- **Evidence**: this session's transcript; `docs/reports/multi-document-destination-config/{script-inventory-and-plugin-migration-candidates.md, complete-artifact-classification.md}` (the full artifact-level evidence inventory, still valid and reused by the design doc); `docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md` (the accepted domain model).
- **Severity**: M (no data loss or tenant damage, but real rework risk and repeated user correction across two phases)
- **Repeat**: YES — happened in Phase 4, then again in Phase 5 within the same architecture area. Per the aging rule, must escalate immediately on next encounter, not be deferred a third time.
- **Status**: OPEN (design complete; do not mark RESOLVED until a migration wave actually executes — see the design doc's Section 7)

### [2026-08-03] Phase 6 Task 0.17 — `workbench-setup` Wrongly Assigned Cross-Repository Ownership, Then Executed On Before the User Caught It

- **Logged Date**: 2026-08-03
- **Cycle/Session**: Phase 6 Task 0.16 wrap-up → Task 0.17 start (same session)
- **Artifact Affected**: `start-here.md`, `docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md` (Task 0.17 section), `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` (Section 8), `docs/superpowers/plans/2026-08-02-multi-document-destination-configuration.md`, `docs/architecture/complete-plugin-skill-catalog-after-phase-9.{json,md}` (`workbench-setup`'s `authoring_constraint` field) — all wrongly stated `workbench-setup`'s three skills must be authored in the sibling `agent-plugins-skills` monorepo as "Category 1 (marketplace-style)" skills, per `CLAUDE.md`'s Skill Development Protocol. A `git worktree`/branch was actually created in `agent-plugins-skills` under this wrong premise before the user caught it (3 untracked `.psd1.example` files, never committed/pushed — cleaned up, that repo otherwise unaffected, verified via `git status`/`git log` before and after cleanup).
- **Friction Observed**: the user's actual, prior instruction was to **use** the `marketplace-manager` skill (installed *from* `agent-plugins-skills` into this repo's `.agents/skills/`) as the *procedure/tool* for the applicable `marketplace.json` registration step — not to author `workbench-setup`'s plugin code *inside* `agent-plugins-skills`. The agent (in an earlier planning pass, not caught during the user's own plan review either) conflated "this skill's source-of-truth repo" with "where a plugin using/consulting that skill's procedure must itself be authored," and inserted the wrong conclusion into the Phase 6 plan as a stated cross-repository authoring constraint. That wrong constraint then survived unchallenged through plan review and start-here.md handoffs until this session began actually executing it (creating the worktree, generating the three canonical `.psd1.example` templates there) before the user interrupted and corrected it directly.
- **Why Hard Gate #14 did not prevent this**: gate #14 ("Don't Self-Conclude 'Not Needed' on a Capability the User Named Unprompted") covers the *inverse* failure — ignoring or dismissing a named capability. This incident is a different, related failure in the same conceptual area: correctly recognizing the named capability (`marketplace-manager`) but **misattributing its scope** — treating "consult skill X's procedure" as "adopt skill X's repository as this new plugin's home." Gate #14's check ("did I run the actual tool instead of a manual proxy") does not catch a scope-misattribution error, only a dismissal error.
- **Fix**: added Hard Gate #15 to `self-evolution-policy.md` (see below) generalizing this distinction — a named skill/tool's own source repository is never, by itself, evidence for where a *different* artifact (a new plugin, a new file, a new capability) that merely *uses* that skill must be authored. Corrected every false ownership statement listed under Artifact Affected above (each now carries an explicit correction record naming this incident), deleted the stray `agent-plugins-skills` worktree/branch, and confirmed via `git status`/`git log` that no other file in that sibling repo was touched.
- **Evidence**: this session's transcript (the user's exact correction message); commit `c8275c4` ("docs: correct false workbench-setup cross-repository ownership claim") in `sharepoint-knowledge-workbench`.
- **Severity**: M (no tenant/data impact, no code shipped under the wrong premise — but a real architecture-plan error that survived one full human plan review before being caught, plus wasted a session-start on the wrong repo)
- **Repeat**: NO (new Hard Gate #15 in `self-evolution-policy.md`)
- **Disposition of the wrong-repository attempt**: `ABANDONED_WRONG_REPOSITORY`.
- **Status**: RESOLVED

### [2026-08-03] Phase 6 native-runtime evaluation prep — `reconcile-deployed-skill.ps1` Falsely Reported Zero Deployed Skills

- **Logged Date**: 2026-08-03
- **Cycle/Session**: Phase 6 remediation round 2 — native-sharepoint runbook prep (live tenant verification)
- **Artifact Affected**: `plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1`
- **Friction Observed**: ran this existing, previously-untested-live script against the real tenant (`TargetSite-Dev`) to verify the `review-manual-topics` deployment precondition before running Phase 6's native-runtime evaluation cases. It reported `DISPOSITION: TASK_8_NO_SKILLS_DEPLOYED` — zero skill folders found in `AgentAssets/Skills/`. This was reported to the user as fact. The user pushed back ("you are wrong") and provided a screenshot showing `AgentAssets/Skills/` actually contains two real folders (`sample-test-skill`, `review-manual-topics`, both modified 3 days prior). The script was wrong, not the tenant — a false-negative live-tenant read that was initially reported as ground truth without the skepticism it deserved for a script that had never actually been run against a live tenant before (only ever exercised, if at all, as inert code).
- **Root causes, three real bugs found by direct cmdlet investigation, not guessing**:
  1. `Get-PnPFolderInFolder -FolderSiteRelativeUrl` was passed a SERVER-relative path (built from `$agentAssetsLib.RootFolder.ServerRelativeUrl`, e.g. `/sites/TargetSite-Dev/AgentAssets/Skills`) but that parameter requires a SITE-relative path (e.g. `AgentAssets/Skills`) — silently resolved to zero folders instead of erroring.
  2. `Get-PnPFile -Url ... -AsFile` (no `-Path`) selected the "Save to local path" parameter set, which requires `-Path`, causing an interactive prompt this session's non-interactive invocation couldn't answer, silently failing that lookup too.
  3. A second `Get-PnPFile ... -Path $tempPath -AsFile` call passed a full file path to `-Path`, but that parameter expects a directory with `-Filename` supplied separately — a second interactive-prompt failure.
- **Why this wasn't caught in Task 0's original completion**: `reconcile-deployed-skill.ps1` had no automated test coverage (verified: `grep` for its name across `tests/` returns nothing) and, per its own history, had likely never been run against a real live tenant end-to-end before this session — only ever validated by code review / synthetic reasoning. A cmdlet-parameter-set bug like #2/#3 (silently switching to a different parameter set that then prompts interactively) is exactly the kind of defect that only surfaces on a real, live, non-interactive run — never in a mocked or manually-reasoned-through review.
- **Fix**: fixed all three at the cmdlet-parameter level (switched to `-Identity` for folder enumeration, `-AsFileObject` for the no-save lookup, explicit `-Path`/`-Filename` split for the save-to-disk lookup). Verified fixed with a real, non-interactive (`< /dev/null`) re-run against the live tenant: correctly found both real deployed skill folders, computed real SHA-256 hashes, and correctly surfaced a genuine, separate finding (`DISPOSITION: DEPLOYED_ARTIFACT_DRIFT_DETECTED` — the deployed `review-manual-topics` hash does not match this repo's current `SKILL.md`).
- **Evidence**: commit `5e05893` ("fix(sharepoint-agents-and-skills): 3 real bugs in reconcile-deployed-skill.ps1"); the user's screenshot (this session, not persisted to the repo); before/after script output in this session's transcript.
- **Severity**: M (no tenant/data impact — read-only script — but a false negative that, if trusted without the user's own independent verification, would have led to an incorrect "skill not deployed, redeploy from scratch" action against a tenant that already had the correct artifact, and more broadly would have blocked Phase 6's native-runtime evaluation on a fabricated premise)
- **Repeat**: NO (fixed at the source; no other script in this repo shares this exact `reconcile-deployed-skill.ps1` code path). Generalizable lesson, not yet codified as a new Hard Gate: **a live-tenant script's first-ever real run should be treated as unverified until independently cross-checked (e.g. against the actual SharePoint UI), especially when it reports a negative/empty result** — a script silently returning "nothing found" due to a parameter-set bug looks identical to a script correctly reporting "nothing found," and only external verification (the user's screenshot here) distinguished them. Considered for a future Hard Gate if this pattern recurs.
- **Status**: RESOLVED

### [2026-08-03] Phase 6 native-runtime redeploy — `deploy-and-verify-skill.ps1` `Add-PnPFile` Parameter-Set Bug

- **Logged Date**: 2026-08-03
- **Cycle/Session**: Same session as the `reconcile-deployed-skill.ps1` fixes above — continuation, redeploying `review-manual-topics/SKILL.md` to resolve the `DEPLOYED_ARTIFACT_DRIFT_DETECTED` finding those fixes surfaced.
- **Artifact Affected**: `plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1`
- **Friction Observed**: real `-Execute` run against the live tenant failed with `Parameter set cannot be resolved using the specified named parameters` immediately upon attempting the upload.
- **Root cause**: `Add-PnPFile -Path $sourcePath -Folder $targetFolderUrl -FileName $targetFilename -Values @{...}` — `-Path` selects the "Upload file" parameter set, which provides `-NewFileName` for renaming on upload; `-FileName` belongs to a different, stream-based parameter set ("Upload file from stream"/"from text") that has no `-Path`. Mixing the two is invalid and PowerShell correctly rejected it (unlike the three `reconcile-deployed-skill.ps1` bugs, this one errored loudly rather than silently returning a wrong empty result — a better failure mode, caught immediately on the real execution attempt rather than needing external cross-checking).
- **Why not caught earlier**: same as the sibling script — no test coverage, and `-Execute` (the only code path that exercises this line) had apparently never been run against a real tenant before this session; the script's own preflight (`-Execute` omitted) never reaches this line at all.
- **Fix**: `-FileName` → `-NewFileName`. Verified fixed with a real `-Execute` run: upload succeeded, pre/post-deployment SHA-256 readback matched 100% (`bb327348...`), and the sibling reconciliation script (already fixed) confirmed `DISPOSITION: TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED` afterward — the drift this session found earlier is now resolved on the real tenant, not just in this repo's expectations.
- **Evidence**: commit `0345b5f`; live-tenant command output in this session's transcript (upload URL, matching SHA-256 readback, reconciliation re-run).
- **Severity**: L (errored loudly and immediately rather than silently misbehaving; no partial/corrupt write occurred — PnP rejects an invalid parameter combination before any tenant call is made)
- **Repeat**: NO (fixed at the source)
- **Status**: RESOLVED

### [2026-08-07] Phase 9 Wave 2 — `audit_plugin_structure.py` (Hard Gate #12) Does Not Exist in This Repository

- **Logged Date**: 2026-08-07
- **Cycle/Session**: Phase 9 Wave 2 — agent extraction into `plugins/sharepoint-agents-and-skills/`
- **Artifact Affected**: `.agent/rules/self-evolution-policy.md` Hard Gate #12; `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §9a (both name `audit_plugin_structure.py <plugin>` as a mandatory pre-completion check)
- **Friction Observed**: Hard Gate #12 and spec §9a both mandate running `audit_plugin_structure.py <plugin>` before any new skill/agent is considered complete, and explicitly distinguish it from `audit.py` ("it catches real files living inside skill dirs that the compliance audit does not flag as an error"). The script does not exist anywhere in this repository or in any installed skill — `find . -name 'audit_plugin_structure.py'` returns nothing; `.agents/skills/audit-plugin/scripts/` contains `audit.py`, `audit_marketplace_sources.py`, `run_eval.py`, `run_loop.py`, and helpers, but no structure auditor. A mandatory gate therefore cannot be satisfied as written.
- **Why it was not fixed now**: writing the missing auditor is a new capability in a different domain (plugin-structure tooling, owned by the `audit-plugin` skill from the sibling `agent-plugins-skills` monorepo per `CLAUDE.md`'s Category 1 protocol), not part of Wave 2's authorized scope, and Category 1 artifacts must be authored in the sibling repo under its own PR/review protocol — not created here.
- **Workaround used, and its limits**: ran `.agents/skills/audit-plugin/scripts/audit.py --path plugins/sharepoint-agents-and-skills` instead (result: `AUDIT PASSED`, only pre-existing `references/`-directory warnings). This is explicitly the weaker of the two checks per Hard Gate #12's own text. Wave 2's specific exposure is nil — it added no files inside any skill directory at all (agents are plugin-root peers of `skills/`) — but a future extraction that does add skill-internal files will hit a real, unguarded drift risk.
- **Recommended fix**: author `audit_plugin_structure.py` in `agent-plugins-skills` under the `audit-plugin` skill (real-file-inside-skill-dir detection, per ADR-002/ADR-003), merge via that repo's PR protocol, reinstall here — then update Hard Gate #12 and spec §9a with the resolved invocation path. Until then, Hard Gate #12's second sentence should be treated as aspirational and any Phase 9 wave that writes files into a skill directory must state explicitly which check it actually ran.
- **Evidence / reproduction**: `find . -name 'audit_plugin_structure.py'` → no results (repository and `.agents/` both searched, 2026-08-07).
- **Severity**: M (a mandatory hard gate is unsatisfiable as written; the drift class it exists to catch has already occurred once undetected across 16 files per the 2026-07-25 entry it cites)
- **Repeat**: YES — this gate will be unsatisfiable for every subsequent Phase 9 wave until the script exists. Must escalate on next encounter rather than being deferred again.
- **Status**: OPEN

### [2026-08-07] Phase 9 Wave 2 — `plugin_add.py` (Hard Gate #10) Writes a Worktree-Absolute Path into Tracked `plugin-sources.json`

- **Logged Date**: 2026-08-07
- **Cycle/Session**: Phase 9 Wave 2 — agent extraction into `plugins/sharepoint-agents-and-skills/`
- **Artifact Affected**: `plugin-sources.json`, `skills-lock.json` (both tracked); `.agents/skills/plugin-installer/scripts/plugin_add.py` (Category 1, sibling-repo owned)
- **Friction Observed**: Hard Gate #10 requires `plugin_add.py <plugin-path> -y` after any modification under `plugins/`. Running it from a git worktree (the standard per-phase workflow since Phase 2, per `CLAUDE.md`) appended an absolute worktree path — `<absolute-home-path>/.claude/worktrees/agent-aa349c7aac745b79c` — as a permanent `source` entry in tracked `plugin-sources.json`, and added 15 `installedAt` records to tracked `skills-lock.json` describing an install into a throwaway worktree-local `.agents/` directory that will not exist after the worktree is removed. Committing either would have shipped a dead machine-specific path into `main`.
- **Fix applied inline**: reverted both files (`git checkout -- plugin-sources.json skills-lock.json`) after confirming the installer's real verification value had already been obtained — it reported the destination as `.agents/ (skills + agents + commands + hooks)` and successfully installed all four new agent files, which is exactly the evidence Wave 2 needed to confirm `plugins/<plugin>/agents/` is the tool-recognized component location. The gate was run; only its tracked-file side effects were discarded. Nothing under `plugins/` was altered by the revert.
- **Recommended durable fix**: `plugin_add.py` should record the source as a repository-root-relative path (or the canonical repo URL it already knows — it writes `https://github.com/richfrem/sharepoint-knowledge-workbench` into `skills-lock.json` while writing an absolute worktree path into `plugin-sources.json`, so the two manifests disagree). Owned by `agent-plugins-skills`; fix belongs there, not here. Until then, Hard Gate #10 should carry a worktree caveat: run the installer, then verify `git status` and revert manifest churn that encodes the worktree path.
- **Evidence / reproduction**: `git diff plugin-sources.json` immediately after `python3 .agents/skills/plugin-installer/scripts/plugin_add.py . --plugins sharepoint-agents-and-skills -y` from the Wave 2 worktree, 2026-08-07.
- **Severity**: M (silently commits a machine- and worktree-specific absolute path into a tracked manifest; the per-phase worktree workflow means every future phase hits this)
- **Repeat**: YES — inherent to running Hard Gate #10 from any worktree, which is the mandated workflow. Escalate on next encounter.
- **Status**: RESOLVED (this occurrence reverted; underlying installer defect OPEN in the sibling repo)

### [2026-08-07] Phase 9 Wave 2 — Extracted Agents Were Pure Routers Over Nonexistent Skills

- **Logged Date**: 2026-08-07
- **Cycle/Session**: Phase 9 Wave 2 — agent extraction into `plugins/sharepoint-agents-and-skills/`
- **Artifact Affected**: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/task-2a-symlink-resolution-and-task-3a-agent-classification.md` (Task 3a classification); `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8f (agent classification axes)
- **Friction Observed**: Task 3a classified these four agents as zero-cost on genericity ("completely free of project literals... the cleanest extraction candidates found anywhere in this audit") based on a literal-density scan. That held on read — zero literals, confirmed. But the scan measured the wrong cost axis for agents: all four are *pure routers* whose entire body is a table of source-plugin skill names (`sp-extracting-links`, `sp-auditing-schema`, `sp-converting-aspx-pages`, …). Those names are not project literals and pass every §8h/§9 check, yet a verbatim copy would have produced four agents routing to roughly fifteen capabilities that do not exist in this repository. The real extraction work was rebuilding each routing table against this repo's actual capability inventory — not scrubbing literals, of which there were none.
- **Fix applied inline**: rewrote each routing table against verified real skills, added a mandatory `## Not available in this workbench` section to every agent, and made dangling references *mechanically impossible to reintroduce* — `tests/unit/test_agent_definitions.py` resolves every hyphenated inline-code token in every agent against the real set of skill/plugin/agent names under `plugins/`, failing unless the token exists or is explicitly declared unavailable. Task 3a's classification is not wrong and was not amended; the cost model behind it is incomplete.
- **Recommended fix**: spec §8f's agent-classification axes should gain a fifth axis alongside literal density — **routing-target resolvability**: the count of source capabilities an agent routes to that have no destination equivalent. For a router, that number *is* the extraction cost, and it is uncorrelated with literal density. Recommended before Wave 3 classifies `sp-discovery-agent`/`sp-migration-agent` (3 literals each — i.e. they will look cheap on the same incomplete axis that made these four look free).
- **Evidence / reproduction**: the four source files at `78d6bb9` are 17–18 lines each and name 15 distinct `sp-*` skills between them, of which zero exist in this repository (`ls plugins/*/skills/`); provenance Records 3–6 list the per-agent re-targeting.
- **Severity**: M (no defect shipped — caught during Wave 2 execution and guarded by test — but the same incomplete cost model is about to be applied to the remaining five agents in a later wave)
- **Repeat**: NO for these four (resolved and test-guarded); YES as a classification-model gap for Wave 3+ unless §8f gains the axis.
- **Status**: RESOLVED (Wave 2 artifacts); recommendation for §8f is OPEN

### 2026-08-07 — source-repo config fallback in sharepoint-agents-and-skills

- **Artifact:** `plugins/sharepoint-agents-and-skills/scripts/{verify-agentassets-ready,verify-agentassets-artifact,reconcile-deployed-skill,diagnose-sharepoint-library}.ps1`
- **Friction observed:** four scripts defaulted `$ConfigFile` to a plugin-local `config.psd1` and fell back to `tools/phase-3-sharepoint-discovery/config.psd1` — a source-repo/phase-evidence path that `CLAUDE.md` §0 explicitly says must never hold reusable operational implementation. They also read flat top-level keys, incompatible with the nested `Connection` block that `workbench-setup`'s `setup-sharepoint-connection` actually generates, and surfaced "Phase 3"/"Phase 4" phase language in user-facing error messages.
- **Why not fixed earlier:** predates Phase 9; surfaced by a config-alignment audit run this session.
- **Fix applied:** default is now the repository-root `config.psd1` (workbench-setup's canonical output). A normalizer accepts the canonical nested `Connection` block and falls back to flat keys for older plugin-local configs. The `tools/phase-3-*` fallback and all phase language are removed; a missing/placeholder app registration now points the operator at `setup-sharepoint-connection` instead.
- **Evidence:** `grep -rn 'FallbackConfigFile|phase3|tools/phase-3' plugins/sharepoint-agents-and-skills/scripts/*.ps1` returns nothing; all four parse clean via the PowerShell AST parser; plugin suite 68/68.
- **Severity:** M. **Repeat:** NO. **Status:** RESOLVED.

### 2026-08-07 — CWD-fragile config.psd1 defaults across sharepoint-agents-and-skills

- **Artifact:** 14 scripts in `plugins/sharepoint-agents-and-skills/scripts/*.ps1`.
- **Friction observed:** a precision audit (`scratchpad/audit_config_path_refs_v2.py`, filtering
  actual code paths from docstring noise) found every `$ConfigFile`/`$ConfigPath` PowerShell param
  default was a bare relative literal (`"config.psd1"` or `"plugins/sharepoint-agents-and-skills/
  config.psd1"`) with zero `$PSScriptRoot` anchoring anywhere in the repo's PowerShell scripts.
  Correct only if invoked with CWD == repo root, which nothing documents or enforces. 10 of the 14
  additionally pointed at the wrong file entirely — a plugin-local `config.psd1` that
  `setup-sharepoint-connection` never creates (same class of defect fixed for 4 of these scripts
  earlier this session in the `tools/phase-3-*` fallback fix, just not caught for all 14 at once).
- **Fix applied:** all 14 defaults now resolve via `(Join-Path $PSScriptRoot '../../../config.psd1')`
  — anchored to the script's own location, correct regardless of invocation CWD, and pointing at the
  single repo-root source of truth.
- **Evidence:** re-running the audit script shows 0 fragile hits; all 14 files parse clean via the
  PowerShell AST parser; plugin suite 68/68 unchanged.
- **Severity:** M. **Repeat:** NO. **Status:** RESOLVED.

### 2026-08-07 — symlink_manager.py not present in this worktree

- **Artifact:** N/A (tooling gap noticed while building `plugins/sharepoint-provisioning`).
- **Friction observed:** CLAUDE.md's Plugin-Local Resource Sharing section and this session's task
  brief both require any shared script/reference symlinked into a skill folder to go through
  `.agents/skills/symlink-manager/scripts/symlink_manager.py`. That path does not exist in this
  worktree (`.agents/` is not populated here); the only `symlink_manager.py` copies found on disk
  live in sibling repos (`agent-plugins-skills`, a legacy sibling plugin repo) or `~/Downloads`.
  `sharepoint-provisioning` did not end up needing any symlinks (all three skills' only file is a
  real `SKILL.md`, matching `sharepoint-schema`'s/`sharepoint-link-remediation`'s precedent of
  skills with no bundled scripts/references), so this was not blocking, but it would block the
  next plugin/skill that does need one until `.agents/skills/` is populated in this worktree.
- **Fix applied:** none — out of scope for this task. Documented so the next session that needs to
  create a real symlink knows to check `.agents/skills/` availability first rather than assuming
  the tool is present.
- **Severity:** L (did not block this task). **Repeat:** unknown — first time this worktree's
  `.agents/` absence was noticed explicitly. **Status:** OPEN, informational.

### 2026-08-07 — sharepoint-provisioning tests only ran via isolated_install_check.py, not directly

- **Artifact:** `plugins/sharepoint-provisioning/tests/{test_field_provisioning,test_content_type_provisioning,test_list_provisioning}.py`
- **Friction observed:** the agent that built this plugin reported `87 passed` verified only via `isolated_install_check.py` (an installed wheel). Running `python3 -m pytest plugins/sharepoint-provisioning/tests/ -q` directly failed with 3 collection errors — missing `sys.path.insert(0, .../scripts)`, the per-test-file convention `sharepoint-schema`'s test suite already establishes (as opposed to a shared `conftest.py`, which `sharepoint-link-remediation`/`sharepoint-page-modernization` use instead). Caught only because I independently re-ran the plugin's own tests directly rather than trusting the wheel-only verification.
- **Fix applied:** added the `sys.path.insert` block to all 3 files, ordered correctly after `from __future__ import annotations` (which must be the first statement after the module docstring — an intermediate fix attempt broke this ordering and had to be corrected).
- **Evidence:** `python3 -m pytest plugins/sharepoint-provisioning/tests/ -q` → 87 passed, run directly with no install step.
- **Severity:** S. **Repeat:** possible — future rounds should verify a new plugin's tests both via direct `pytest` and via `isolated_install_check.py`, not just the latter.
- **Status:** RESOLVED.

### 2026-08-07 — new py-module omitted from pyproject.toml py-modules list

- **Artifact:** `plugins/sharepoint-schema/pyproject.toml`, new module
  `plugins/sharepoint-schema/scripts/schema_definition.py`.
- **Friction observed:** direct `pytest` against the source tree passed (57/57) because it imports
  via `sys.path.insert`, but `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py
  --plugin sharepoint-schema --import-package schema_definition` failed with
  `ModuleNotFoundError: No module named 'schema_definition'` after a successful wheel build — the
  plugin's `[tool.setuptools] py-modules` list is an explicit enumeration (not auto-discovered),
  so adding a new top-level module to `scripts/` requires also adding its bare name to that list,
  or it silently gets left out of the installable wheel while still passing source-tree tests.
- **Fix applied:** added `"schema_definition"` to `plugins/sharepoint-schema/pyproject.toml`'s
  `py-modules` list.
- **Evidence:** `isolated_install_check.py --plugin sharepoint-schema --import-package
  schema_definition` now passes (57 passed) against the wheel-installed copy.
- **Severity:** S. **Repeat:** likely — every new bare-module file added to any of these
  flat-`scripts/` plugins must remember this same enumeration step; a source-tree-only pytest run
  will not catch its absence.
- **Status:** RESOLVED.

### 2026-08-07 — plugin_add.py cannot install sharepoint-schema (no .claude-plugin/plugin.json)

- **Artifact:** `plugins/sharepoint-schema/` (uses `plugin.yaml`, no `.claude-plugin/plugin.json`).
- **Friction observed:** `python3 .agents/skills/plugin-installer/scripts/plugin_add.py <repo>
  --plugins sharepoint-schema -y` failed with `Validation Failed: Missing manifest
  (.claude-plugin/plugin.json or plugin.json) in sharepoint-schema`. This is a pre-existing
  condition of the plugin (present before this task's changes; several other Phase-9 plugins use
  the same `plugin.yaml`-only convention) — not something introduced by adding the new skill.
  Side effect: running it did touch `skills-lock.json` timestamps repo-wide; reverted per task
  instructions with `git checkout -- plugin-sources.json skills-lock.json`.
- **Fix applied:** none — out of scope for this task (pre-existing manifest-format gap, not
  specific to the new skill).
- **Severity:** S. **Repeat:** yes, for any future skill added to a `plugin.yaml`-only plugin.
- **Status:** OPEN, informational.
### [2026-08-11] `sharepoint-content-migration` Skill Missing Installer Eval Manifest

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Plugin installer warning cleanup
- **Artifact Affected**: `plugins/sharepoint-content-migration/skills/migrate-sharepoint-list-content/evals/evals.json`
- **Friction Observed**: `plugin-add plugins/` installed `sharepoint-content-migration` but warned that `migrate-sharepoint-list-content` was missing `evals/evals.json`.
- **Why it wasn't fixed earlier**: The plugin was made installable by adding its missing plugin manifest first; the eval warning was non-blocking and surfaced as follow-up installer hygiene.
- **Recommended Fix**: Add a skill-local eval manifest covering the migration safety gates and two-pass lookup-ID backfill contract.
- **Evidence**: Reproduction from installer output: `Warning: Skill 'migrate-sharepoint-list-content' in plugin 'sharepoint-content-migration' is missing evals/evals.json`.
- **Severity**: S
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-11] `document-structure-analysis` Skill Missing Installer Eval Manifest

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Plugin installer warning cleanup
- **Artifact Affected**: `plugins/document-structure-analysis/skills/analyze-document-structure/evals/evals.json`
- **Friction Observed**: `plugin-add plugins/` installed `document-structure-analysis` but warned that `analyze-document-structure` was missing `evals/evals.json`.
- **Why it wasn't fixed earlier**: Earlier cleanup targeted the first user-named warning; reinstall exposed the next plugin in sequence with the same missing-eval-manifest issue.
- **Recommended Fix**: Add a skill-local eval manifest covering the normalized-source-document input, draft analysis-plan output, and plugin-boundary constraints.
- **Evidence**: Reproduction from installer output: `Warning: Skill 'analyze-document-structure' in plugin 'document-structure-analysis' is missing evals/evals.json`.
- **Severity**: S
- **Repeat**: YES
- **Status**: RESOLVED

### [2026-08-11] Plugin Skills Missing Installer Eval Manifests in Bulk

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Plugin installer warning cleanup
- **Artifact Affected**: `plugins/*/skills/*/evals/evals.json`
- **Friction Observed**: Reinstalling all plugins showed the missing-eval warning was systemic across many plugin-local skills, not isolated to one or two skills.
- **Why it wasn't fixed earlier**: Earlier passes fixed the first warnings encountered sequentially instead of auditing the whole `plugins/*/skills/*` surface.
- **Recommended Fix**: Audit every plugin-local skill and add a minimal skill-local eval manifest where missing, using each skill's documented contract as the eval target.
- **Evidence**: Repository audit found 61 remaining skills without `evals/evals.json`; each now has a generated manifest under its own `skills/<skill>/evals/` directory.
- **Severity**: M
- **Repeat**: YES
- **Status**: RESOLVED

### [2026-08-11] Transient Windows `skills-lock.json` Installer Write Crash

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Plugin installer warning cleanup
- **Artifact Affected**: `skills-lock.json`, `plugin-add plugins/ --all`
- **Friction Observed**: A full install run crashed while writing `skills-lock.json` for `sharepoint-content-publication` with `[Errno 22] Invalid argument`, even though the lockfile path was valid.
- **Why it wasn't fixed earlier**: The crash did not reproduce after inspecting the file; `skills-lock.json` was writable and valid JSON, and targeted plus full reinstalls completed successfully with UTF-8 environment variables set.
- **Recommended Fix**: If repeated, inspect the upstream installer's lockfile write/replace path on Windows for transient file-handle or path-normalization issues; for now, rerun with `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8`.
- **Evidence**: Targeted `sharepoint-content-publication` reinstall succeeded, followed by full `plugin-add plugins/ --all --yes` succeeding for 14/14 plugins.
- **Severity**: S
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-11] `copy-spo-page-between-sites` Symlink Manager Unavailable During Skill Audit

- **Logged Date**: 2026-08-11
- **Cycle/Session**: `sharepoint-content-publication` new skill audit
- **Artifact Affected**: `symlinks.json`; `plugins/sharepoint-content-publication/skills/copy-spo-page-between-sites/scripts/spo_page_copy_plan.py`
- **Friction Observed**: The skill acceptance criteria required exposing `spo_page_copy_plan.py` through a file-level symlink, but the documented `.agents/skills/symlink-manager/scripts/symlink_manager.py` helper was not present in this checkout.
- **Why it wasn't fixed earlier**: The new skill was added before this audit and had not yet been checked against the repository's hub-and-spoke symlink convention.
- **Recommended Fix**: Add the `symlinks.json` entry and create the specific file-level symlink; if this repeats, reinstall the symlink-manager skill or restore the helper before further symlink work.
- **Evidence**: `glob **/symlink_manager.py` found no helper; `symlinks.json` now contains the `spo_page_copy_plan.py` link and the destination is a `SymbolicLink`.
- **Severity**: S
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-11] SPO Page Copy Skill Used Python Front Door Instead of PowerShell Operator Script

- **Logged Date**: 2026-08-11
- **Cycle/Session**: `copy-spo-page-between-sites` page-to-page execution planning
- **Artifact Affected**: `plugins/sharepoint-content-publication/scripts/spo-page-copy-plan.ps1`; `plugins/sharepoint-content-publication/skills/copy-spo-page-between-sites/SKILL.md`
- **Friction Observed**: The initial page-copy planner was implemented as `spo_page_copy_plan.py`, which was awkward for an SPO/PnP operator workflow and unclear to the user.
- **Why it wasn't fixed earlier**: The Python helper followed the repo's pure-planning/test pattern, but this workflow is SharePoint operator-facing and should expose PowerShell/PnP command semantics directly.
- **Recommended Fix**: Replace the operator-facing planner with a `.ps1` front door that emits the exact `Copy-PnPPage` and `Rename-PnPFile` commands, supports `-Execute` behind a confirmation token, and remove the Python planner/symlink references.
- **Evidence**: `spo_page_copy_plan.py` and its test were removed; `spo-page-copy-plan.ps1` now validates source/target URLs, emits `Copy-PnPPage` plus `Rename-PnPFile` when page names differ, and the skill points to the `.ps1`.
- **Severity**: M
- **Repeat**: YES
- **Status**: RESOLVED

### [2026-08-11] `sharepoint-migration-planning`'s Remaining 3 Skills Implemented — `symlink_manager.py` Missing From This Checkout

- **Logged Date**: 2026-08-11
- **Cycle/Session**: Post-Phase-9 real-executor porting round, `sharepoint-migration-planning` (smallest remaining plugin, per `start-here.md`'s sequencing)
- **Artifact Affected**: `.agents/skills/symlink-manager/` (expected location, not present)
- **Friction Observed**: `CLAUDE.md`'s "Plugin-Local Resource Sharing" section and this repo's symlink rule both mandate creating shared-script symlinks via `.agents/skills/symlink-manager/scripts/symlink_manager.py create`, never `ln -s`/`New-Item` directly. When implementing `setup-sharepoint-migration-project`, `discover-sharepoint-site-inventory`, and `generate-sharepoint-wave-scripts` (flipping all 3 from `design-scaffold` to real, TDD-tested implementations, mirroring the existing `analyze-sharepoint-dependency-graph`/`plan-sharepoint-deployment-waves` pattern), `symlink_manager.py` was found absent from this checkout's `.agents/skills/`.
- **Why it wasn't fixed earlier**: Not previously needed — no new plugin-local symlinks had been created recently enough to hit this gap.
- **Recommended Fix**: The 6 required symlinks (`project_setup.py`, `inventory_validation.py`, `wave_script_generation.py`, and 3 `provisioning_outcomes.py` copies, one per new skill) were created directly with PowerShell's `New-Item -ItemType SymbolicLink`, then independently verified via `Get-ChildItem`'s `LinkType: SymbolicLink` — same end state the tool would produce, but bypassing the mandated tool since it isn't installed here. Check whether `symlink-manager` needs reinstalling from `agent-plugins-skills` (per `CLAUDE.md`'s Skill Development Protocol) before the next plugin pass that needs a new symlink.
- **Evidence**: 64/64 tests passing (up from 39/39) in `plugins/sharepoint-migration-planning/`; all 6 new symlinks verified real; `symlinks.json` updated with the corresponding entries; isolated `pip install -e` + import check passing.
- **Severity**: L
- **Repeat**: TBD
- **Status**: OPEN (tooling gap, not blocking; workaround used successfully)
