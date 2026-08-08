# Phase 9 Provenance Record — First Milestone Extraction

**Scope of this record:** the two skills identified in
`docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8c/§8d as
`PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` / `PHASE_9_MERGE_WITH_EXISTING_SKILL` — `sp-uploading-content`
and `sp-validating-app-registration`. Fields follow spec §8b. No other CMAT capability was
extracted in this pass; the remaining 32 skills retain their existing §8d classification.

**Appended 2026-08-07 — Wave 2 (agents):** Records 3–6 below cover the four zero-project-literal
agents classified `GENERIC_SHAREPOINT_AGENT` in
`task-2a-symlink-resolution-and-task-3a-agent-classification.md` (Task 3a). Same source baseline,
same field set. The remaining five agents (`sp-discovery-agent`, `sp-migration-agent`,
`sp-deployment-planner`, `sp-migration-orchestrator`, `sp-wave-orchestrator`) are **out of Wave 2
scope** and retain their Task 3a disposition.

## Common source baseline

- **Source repository:** `/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online` (CMAT)
- **Source commit:** `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` (2026-08-05 09:19:39 -0700)
- **Source plugin:** `sharepoint-migration`
- **CMAT repository disposition:** read-only reference only — not modified, not rebound, remains
  independently operable.

---

## Record 1 — `sp-uploading-content` → `sharepoint-content-publication/skills/upload-content`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-uploading-content/`
- **Source scripts (resolved through symlinks):**
  - `plugins/sharepoint-migration/scripts/upload/upload-modern-page.ps1`
  - `plugins/sharepoint-migration/scripts/upload/upload-modern-page-rest.ps1`
  - `plugins/sharepoint-migration/scripts/upload/migrate-site-assets.ps1` (not ported — CMAT-scale
    site-asset migration, out of scope for this narrow extraction)
  - `plugins/sharepoint-migration/scripts/upload/pnp-powershell-upload-script-example.ps1` (not
    ported — reference example only, no reusable logic beyond what's captured below)
- **Source tests:** none found (`sp-uploading-content/evals/` contains `evals.json`/`results.tsv`
  only; no `scripts/tests/` populated for `upload/` — a gap already noted in the spec's §8c table)
- **Source references:** none
- **Source implementation status:** `IMPLEMENTED` (4 symlinks, per spec §8d)
- **Destination plugin/skill:** `sharepoint-content-publication/skills/upload-content` (existing
  plugin, per spec §8d's `PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` disposition)
- **Destination files:**
  - `plugins/sharepoint-content-publication/scripts/sharepoint_upload.py` (new module)
  - `plugins/sharepoint-content-publication/tests/unit/test_sharepoint_upload.py` (new tests)
  - `plugins/sharepoint-content-publication/skills/upload-content/SKILL.md` (new skill)
- **Removed project coupling:** PnP-PowerShell cmdlet syntax replaced with a language-neutral
  `PublishAction`/`UploadResult`/`Uploader` contract (matches this plugin's existing
  `sharepoint_publish_plan.py` dataclasses); no site URLs, page names, or `AG-PSSG-*`/court-related
  literals retained; `Connect-PnPOnline -ClientId '1950a258-...'` (Microsoft's well-known PnP
  Management Shell client ID, present in the CMAT source) was **not** carried over — the
  destination module has no default client identity at all.
- **Intentional behavior changes:**
  1. Ported from PowerShell (CMAT) to Python, matching this repo's plugin language convention (all
     four Phase 4.5 domain plugins and `sharepoint-content-publication` are Python).
  2. CMAT's script performs the tenant write itself (`Connect-PnPOnline` + `Add-PnPPage` inline).
     The destination `upload_pages()` requires an **injected `uploader` callable** and raises
     `NotImplementedError` without one — this repo's `sharepoint-content-publication` plugin has an
     established Phase 3 "package-only" architecture (`sharepoint_publish_plan.py`,
     `sharepoint_package.py`) with real tenant writes gated behind Stage 3.4.3's not-yet-approved
     write-identity decision. This is a deliberate, documented behavior change, not a silent
     capability loss — the underlying page-creation contract (`Add-PnPPage`/`Add-PnPPageTextPart`/
     `Publish-PnPPage`) is preserved as the documented expectation for any real `uploader` a future
     authorized caller injects.
  3. Stops on first failed action (`UploadError`) rather than CMAT's fire-and-continue console
     output — matches this plugin's "honest partial results, not empty-success reports" requirement
     (spec §13).
- **New neutral fixtures:** `test_sharepoint_upload.py` uses synthetic `PublishAction`s
  (`page-0.html` → `page-0.aspx` under `SitePages/Demo`) — no real tenant URLs, GUIDs, or content.
- **Parity evidence:** the retained behavior is the `Add-PnPPage`/`Add-PnPPageTextPart`/
  `Publish-PnPPage` sequential page-creation contract (source input: an ordered list of upload
  actions; source expected result: each action either succeeds or the run stops; destination
  neutral fixture: a 2–3 action synthetic `PublishPlan`; destination result: `upload_pages()`
  returns per-action `UploadResult`s in order and raises on the first failure — verified by
  `test_upload_pages_succeeds_with_injected_uploader` and
  `test_upload_pages_stops_on_first_failure`). Byte identity not applicable (language change).

---

## Record 2 — `sp-validating-app-registration` → `workbench-setup/skills/validate-app-registration`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-validating-app-registration/`
- **Source scripts (resolved through symlinks):**
  - `plugins/sharepoint-migration/scripts/diagnostics/test-spo-auth.ps1` (primary logic ported)
  - `plugins/sharepoint-migration/scripts/lib/user-groups-lib.ps1` (not ported — group/permission
    enumeration is a distinct responsibility from auth validation, out of scope for this pass)
  - `plugins/sharepoint-migration/scripts/app-reg-tests/test-etl-app-registration.ps1`,
    `seed-sandbox.ps1`, `test-user-groups-lib.ps1` (not ported — ETL/ORDS-side test harness,
    explicitly excluded by the spec's ORDS boundary)
- **Source references (not ported — CMAT/BC-Gov service-request procedure docs, excluded by the
  genericity contract):** `references/overview.md`,
  `references/service-request-draft-application-registration.md`,
  `references/service-request-draft-interactive-app-registration.md`,
  `references/delegated-permission-boundary-test.md`
- **Source config example (not ported — CMAT-specific):** `config/config.psd1.example`
- **Source tests:** `scripts/app-reg-tests/test-etl-app-registration.ps1` and
  `test-user-groups-lib.ps1` target ETL/group-library code, not `test-spo-auth.ps1` itself — no
  direct source test exists for the ported logic (same gap noted in spec §8d).
- **Source implementation status:** `IMPLEMENTED` (7 symlinks, per spec §8d)
- **Destination plugin/skill:** `workbench-setup/skills/validate-app-registration` (existing
  plugin, per spec §8d's `PHASE_9_MERGE_WITH_EXISTING_SKILL` disposition), wired as an optional
  connector into `setup-sharepoint-connection`'s `-TestConnection` path.
- **Destination files:**
  - `plugins/workbench-setup/scripts/app_registration_validation.py` (new module)
  - `plugins/workbench-setup/tests/test_app_registration_validation.py` (new tests)
  - `plugins/workbench-setup/skills/validate-app-registration/SKILL.md` (new skill; script
    symlinked into the skill folder per this repo's hub-and-spoke convention, recorded in
    `symlinks.json`)
  - `plugins/workbench-setup/skills/setup-sharepoint-connection/SKILL.md` (updated: documents
    wiring `make_device_code_connector` into `test_connection(connection, connector=...)`)
- **Removed project coupling:** no BC Government tenant URLs/GUIDs, no `bcgov.sharepoint.com`,
  no service-request/procedure text, no CMAT app-registration values. `Write-Host`
  console-diagnostic formatting replaced with a structured `AppRegistrationValidationResult`
  dataclass.
- **Intentional behavior changes:**
  1. Ported from PowerShell to Python (language convention match, as above).
  2. CMAT's script performs the device-code flow and REST calls directly via
     `Invoke-RestMethod`, with an interactive `Read-Host` pause. The destination
     `validate_app_registration(connection, http_client)` requires an **injected `http_client`**
     (no interactive pause, no live default transport) — preserves `workbench-setup`'s existing
     `config_setup.test_connection()` contract of "zero tenant I/O unless the caller explicitly
     supplies a connector." `test_connection()`'s own `NotImplementedError` guard is **unchanged**
     — this extraction adds a real, working connector implementation
     (`make_device_code_connector`) that a caller *may* inject, it does not remove or weaken the
     opt-in requirement.
  3. Permission/auth failures (device-code failure, token failure, `_api/contextinfo` 403/failure,
     missing digest) are returned as `AppRegistrationValidationResult(success=False, detail=...)`
     rather than CMAT's `Write-Host -ForegroundColor Red` console output — same information,
     structured for programmatic honest-partial-result handling (spec §13).
- **New neutral fixtures:** `test_app_registration_validation.py`'s `FakeHttpClient` and
  `CONNECTION` dict use `https://example.sharepoint.com/sites/Demo`, `example-tenant-id`,
  `example-client-id` — no real tenant identifiers.
- **Parity evidence:** the retained behavior is CMAT's three-step sequence (device-code request →
  token poll → `_api/contextinfo` digest check, with JWT claim decoding for diagnostics) — source
  input: `SiteUrl`/`TenantId`/`ClientId`; source expected result: a `FormDigestValue` on success or
  a clear failure reason; destination neutral fixture: `CONNECTION` + `FakeHttpClient`; destination
  result: `validate_app_registration()` returns `success=True` with `signed_in_as`/`app_id`
  populated on the happy path, and an honest `success=False` with a specific `detail` on each of
  four independently-tested failure modes (device-code failure, token failure, permission denial,
  missing digest) — verified by
  `test_validate_app_registration_success`,
  `test_validate_app_registration_device_code_failure_is_honest_partial_result`,
  `test_validate_app_registration_token_failure_is_honest_partial_result`,
  `test_validate_app_registration_permission_denial_reports_failure_not_empty_success`, and
  `test_validate_app_registration_missing_digest_is_failure`. Byte identity not applicable
  (language change).

---

## Records 3–6 (Wave 2, 2026-08-07) — four generic agents → `sharepoint-agents-and-skills/agents/`

All four share the common source baseline above (`sharepoint-migration` @ `78d6bb9`), the same
source directory (`plugins/sharepoint-migration/agents/`), and the same destination directory
(`plugins/sharepoint-agents-and-skills/agents/` — an **existing** plugin, per spec §8c's
destination-matching rule; no new plugin was created). Shared facts are stated once here and not
repeated per record.

- **Source scripts / references / tests:** none. Each source agent is a single self-contained
  Markdown file (17–18 lines) with no symlinks, no backing script, and no `agents/` test harness in
  the source. Nothing was omitted from the port for these four.
- **Source implementation status:** `IMPLEMENTED` (agent definitions, complete as authored).
- **Orchestration coupling (spec §8f vocabulary):** `GENERIC_SHAREPOINT_AGENT` for all four —
  independently re-verified by full content read, not just the Task 3a literal scan. The scan
  result held: zero occurrences of `JUSTIN`, `CEIS`, `ORDS`, `courthouse`, `appearance`, `AG-CSB`,
  `ITAU`, `PIO`, `ICM`, or `wave` in any of the four.
- **Hidden environment assumptions found on read (none blocking):** no tenant URLs, no GUIDs, no
  app registrations, no list/field/content-type names, no assumed directory layout, no dependency
  on the source `CLAUDE.md` or any runbook. **The one real coupling is a routing-table coupling:**
  every one of the four is a *pure router* whose entire body names source-plugin skills
  (`sp-extracting-links`, `sp-auditing-schema`, …). Those names are not project literals, but they
  are dangling references in this repository. This is the substantive genericization work in Wave 2
  and it is recorded per record below.
- **Removed project coupling (all four):** the `plugin:` frontmatter value `sharepoint-migration`
  replaced with `sharepoint-agents-and-skills`; the `sp-` source-repository naming prefix replaced
  with this repo's unprefixed convention (`sp-link-agent` → `sharepoint-link-agent`, etc.); every
  source-skill routing target replaced with either a real capability in this repository or an
  explicit `## Not available in this workbench` declaration. No source-repository path, relative
  traversal, or symlink survived — none existed to begin with.
- **Intentional structural changes (all four):**
  1. **Routing tables rewritten against this repository's actual capability inventory.** A verbatim
     copy would have produced four agents pointing at fifteen nonexistent skills. Preserving the
     *decision logic* while re-targeting the *routing table* is the extraction; copying the file
     would not have been.
  2. **A mandatory `## Not available in this workbench` section was added to every agent**, and is
     enforced by test. The source agents already practised honest gap-reporting in prose ("planned,
     no script yet"); this promotes that practice from prose to an asserted structural contract,
     matching spec §13's honest-partial-results requirement.
  3. **`agents/` established as a plugin component directory in this repo for the first time.** Real
     files at the plugin root — no symlinks were created, and none are appropriate: agents are
     top-level plugin components (peers of `skills/`), not files consumed from inside a skill
     directory, so the hub-and-spoke rule is satisfied by construction. Verified end to end:
     `plugin_add.py` reports the destination as `.agents/ (skills + agents + commands + hooks)` and
     installs all four.
  4. **Registered in `plugin.yaml` under a new `agents:` key** (test-asserted).
- **New neutral fixtures:** none required — the contract test reads the real artifacts. No tenant
  data, URLs, or GUIDs appear anywhere in the four files or the test.
- **Parity evidence (all four):** byte identity is not applicable and not claimed — the routing
  table is the file. The retained behavior is each agent's **decision rule**, which is preserved
  verbatim in substance and verified per record below. Genericity is verified mechanically by
  `plugins/sharepoint-agents-and-skills/tests/unit/test_agent_definitions.py` (22 assertions across
  6 contracts: frontmatter schema, name↔filename, forbidden-literal scan, source-path/GUID/tenant-URL
  scan, dangling-capability-reference resolution against every real skill/plugin/agent name in
  `plugins/`, mandatory unavailability section, and manifest registration). Written first, observed
  failing on the absent `agents/` directory and the absent `agents:` manifest key, then made to pass.

### Record 3 — `sp-link-agent.md` → `agents/sharepoint-link-agent.md`

- **Retained decision rule:** the strict `extract → remediate → validate` ordering, with the source's
  stated justification preserved (validation is meaningless before remediation; remediation needs
  the extraction scan's output).
- **Re-targeted routing:** validation now routes to `assemble-structured-content` (canonical-package
  `broken_local_link` failure), `validate-rendered-output` (broken links/media, orphan pages, path
  traversal; PASS or FAIL, never WARN), and `validate-sharepoint-publication` (pre-upload, offline).
- **Declared unavailable:** link extraction and link remediation against live published pages, and
  link rewriting inside Office/PDF binaries — the last of which corresponds to the source's own
  `sp-remediating-document-content-links` "planned, no script" note, carried across as a gap rather
  than as a dangling skill name.

### Record 4 — `sp-modernization-agent.md` → `agents/sharepoint-modernization-agent.md`

- **Retained decision rule:** distinguish a full pipeline route from a lighter/targeted route, and
  flag unbuilt remediation paths as manual.
- **Re-targeted routing:** `render-sharepoint-aspx` for modern-page artifact production (including
  its confirmed constraint that raw `.aspx` upload fails with Access denied),
  `create-aspx-rendering-template`/`validate-rendering-template` when the request is really about
  page shape, and `publish-aspx-to-sharepoint` named explicitly as a *different* domain.
- **Declared unavailable:** classic-page conversion, wiki-page conversion, web-part remediation,
  page-layout remediation. **Scope note:** this repository renders modern-page artifacts *from
  structured content it owns*; it does not read an existing classic page and rebuild it. The agent
  states that distinction explicitly and is instructed not to silently reinterpret one as the other
  — this is the single largest semantic gap between source and destination for these four agents.

### Record 5 — `sp-schema-agent.md` → `agents/sharepoint-schema-agent.md`

- **Retained decision rule:** read-only audit first, always; mapping is the expensive second
  question; report unscripted mapping as unscripted rather than performing it silently.
- **Re-targeted routing:** `validate-sharepoint-publication` (offline pre-upload schema conformance
  against the target library schema) as the read-only-first route, plus the publication mapping
  emitted by `assemble-structured-content`.
- **Declared unavailable:** live environment-to-environment schema diff, content-type mapping, list
  mapping, taxonomy mapping (the source's four `sp-mapping-*`/`sp-auditing-schema` targets).

### Record 6 — `sp-validation-agent.md` → `agents/sharepoint-validation-agent.md`

- **Retained decision rule:** validation runs *after* other domains' work, never before; produce the
  final summary report; never claim automated coverage that does not exist.
- **Re-targeted routing — the one agent whose coverage materially improved:** in the source, all
  three validation skills were `planned` with no backing script, so the agent could only report a
  gap. This repository has real, implemented validators, and the agent now routes by *artifact under
  test*: `assemble-structured-content`, `validate-rendered-output`, `compare-rendered-output`,
  `validate-sharepoint-publication`, `reconcile-sharepoint-publication`,
  `verify-sharepoint-native-skill`, `inventory-and-validate-agentassets`, and
  `validate-workbench-environment`.
- **Declared unavailable:** post-deployment validation that files/pages/metadata/links/media are
  actually present after upload (a limit `validate-sharepoint-publication` states about itself),
  permission validation, and automated cross-stage report generation. The agent is explicitly
  instructed not to infer post-upload success from a passing pre-upload validation.

### Agents deliberately NOT extracted in Wave 2

`sp-discovery-agent` (3 literals), `sp-migration-agent` (3), `sp-deployment-planner` (14),
`sp-migration-orchestrator` (36), `sp-wave-orchestrator` (161) — out of scope for this wave, no
content read performed, Task 3a dispositions unchanged. No judgment about their extractability is
made or implied here.

## Independence verification (both records)

- No import, symlink, or path reference to the CMAT repository exists in either destination
  module, test file, or SKILL.md.
- Neither module depends on ORDS configuration, CMAT schemas, or BC Government URLs/GUIDs.
- **Wave 2 (Records 3–6):** the four agent files contain no import, symlink, or path reference to
  the CMAT repository, and no runtime dependency of any kind — they are Markdown routing
  definitions. `plugins/sharepoint-agents-and-skills` tests pass standalone with the CMAT checkout
  absent from the environment (68 passed, up from 46 passed + 5 empty-parametrization skips before
  this change; zero pre-existing tests changed). `symlink_manager.py diagnose` reports 24 broken
  links before and 24 after — the pre-existing `docs/diagrams/` gap, unchanged; Wave 2 added zero
  symlinks and zero broken links. `audit.py --path plugins/sharepoint-agents-and-skills` reports
  `AUDIT PASSED`, with only the plugin's pre-existing `references/`-directory warnings.
- Both plugins (`sharepoint-content-publication`, `workbench-setup`) install and test standalone
  (`pip install -e plugins/<name>`, `python -m pytest tests/`) with the CMAT repository absent from
  the environment — confirmed by running both suites from this worktree, which has no dependency on
  the CMAT checkout at any path.

## Source-repository preservation

- No file in `/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online` was read via any
  write-capable tool, moved, or modified during this extraction — read-only inspection only
  (`find`, `cat`, `readlink`/`ls -la` for symlink resolution).

---

# Wave 5 — `sharepoint-link-remediation` (new plugin)

**Source repository:** `jag-csb-cmat-sharepoint-online` (local checkout, read-only).
**Source commit (pinned):** `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` (2026-08-05 09:19:39 -0700).
**Source plugin:** `sharepoint-migration`.
**Destination plugin:** `plugins/sharepoint-link-remediation` (new — §8e "provisionally justified",
confirmed by Task 2a's live-symlink recount: 3 of 4 candidate skills have real backing).

## Record 7 — `sp-extracting-links` → `extract-links`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-extracting-links/` (5 LIVE symlinks,
  0 broken/deprecated/escaping — Task 2a).
- **Source scripts:** resolved into `scripts/link-conversion/` and `scripts/lib/`.
- **Source implementation status:** `IMPLEMENTED`.
- **Destination:** `skills/extract-links/SKILL.md` + `scripts/link_extraction.py`,
  `scripts/link_outcomes.py`.
- **Removed project coupling:** all source host/tenant literals; the source's implicit
  single-tenant assumption is gone — callers pass content or paths.
- **Intentional behavior changes:** PowerShell → Python (Wave 1 precedent). Added the explicit
  `Outcome` vocabulary: `EMPTY` (read fine, no links) is now distinguishable from `FAILED`
  (nothing could be read), which the source conflated. `sources_attempted` drives an
  all-sources-failed run to `FAILED` rather than an empty success (spec §13).
- **New neutral fixtures:** `tests/fixtures/legacy-page.aspx` — synthetic, no live identifiers.
- **Parity evidence:** link classification (`absolute`, `server_relative`, `protocol_relative`,
  `mailto`, `anchor`, `malformed`) preserved semantically; verified by
  `tests/test_link_extraction.py`. Byte identity not applicable (language change).

## Record 8 — `sp-remediating-links` → `remediate-links`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-remediating-links/` (3 LIVE symlinks).
- **Source implementation status:** `IMPLEMENTED` (generic regex URL-rewrite).
- **Destination:** `skills/remediate-links/SKILL.md` + `scripts/link_remediation.py`,
  `scripts/link_rules.py`.
- **Removed project coupling:** **this is the most significant genericization in the wave.** The
  source embedded its own source/target tenant hosts directly in the rewrite logic. The
  destination has no built-in host, tenant, or project URL at all — every rewrite is supplied by a
  caller-provided declarative ruleset (`load_ruleset`), and a malformed ruleset raises
  `RulesetError` rather than silently matching nothing.
- **Intentional behavior changes:** write safety hardened well beyond the source, per spec §13 —
  dry-run is the default, a writer must be explicitly injected (`WriterRequired`), and applying
  additionally requires a plan-derived confirmation token (`ConfirmationRequired`) that goes stale
  if the documents change. `rollback_remediation` added. Partial/forbidden/failed outcomes are
  reported distinctly; a partly-failed run is never reported as success.
- **Parity evidence:** rewrite semantics verified by `tests/test_link_remediation.py` (33 tests).

## Record 9 — `sp-validating-link-integrity` → `validate-link-integrity`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-validating-link-integrity/` (1 LIVE
  symlink — thin; Task 2a flagged "verify real depth before claiming implemented", and the real
  backing was confirmed thin, so the destination is a deliberate reimplementation of the
  *technique* rather than a port of substantial source logic).
- **Source implementation status:** `IMPLEMENTED` (thin).
- **Destination:** `skills/validate-link-integrity/SKILL.md` + `scripts/link_integrity.py`.
- **Removed project coupling:** no tenant transport ships at all; resolution is injected.
- **Intentional behavior changes:** `UNRESOLVABLE` is a first-class status distinct from
  `BROKEN` — "could not be checked" is never reported as "verified good". An empty inventory
  reports `EMPTY`, never a pass.
- **Parity evidence:** `tests/test_link_integrity.py`.

## Not extracted, and why

- `sp-remediating-document-content-links` — `PLANNED_WITH_NO_IMPLEMENTATION` in the source
  (SKILL.md claims `planned`, zero backing scripts). Recorded as a gap; no empty skill created.

## Independence verification

- `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py --plugin
  sharepoint-link-remediation --import-package link_rules` → **PASS, 113 tests** at the time of the
  packaging commit (121 after the skills/SKILL.md addition).
- `test_plugin_independence.py` enforces, as executable gates: no project literal in any runtime
  file, no source-repository marker, no GUID-shaped identifier, every module imports with no
  third-party dependency, and no module living only inside a skill directory (hub-and-spoke).
- Two anti-vacuity guards protect those gates:
  `test_runtime_tree_is_literal_free_scan_is_not_vacuous` (the scan set can never become empty) and
  `test_literal_matching_flags_real_literals_and_not_ordinary_words` (the word-boundary rule stays
  strict on real identifiers while not firing on ordinary English).

## Source-repository preservation

No file in the source repository was modified. Symlink resolution used `readlink`/`ls -la` only.
The 4 `BROKEN`, 12 `DEPRECATED_TARGET`, and 6 `ESCAPES_PLUGIN` links recorded in Task 2a were
**not** extracted and were **not** repaired in the source (§17 forbids source modification).

---

# Wave 3 — `sharepoint-discovery` (new plugin, PARTIAL COVERAGE)

**Source repository:** `jag-csb-cmat-sharepoint-online` (local checkout, read-only).
**Source commit (pinned):** `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f`.
**Source plugin:** `sharepoint-migration`.
**Destination plugin:** `plugins/sharepoint-discovery` (new).

> **Coverage warning — read before treating this plugin as complete.** Task 2a identified **7**
> implemented discovery capabilities. This wave delivers **2 skills over 3 modules**, covering the
> page-inventory and web-part-code analysis capabilities only. The remaining implemented
> capabilities (`sp-discovering-site-structure`, `sp-discovering-navigation`,
> `sp-discovering-forms`, `sp-discovering-permissions`, `sp-synthesizing-discovery`) are **NOT
> extracted**. This plugin is genuinely useful as-is but is not a complete port of the source's
> discovery family.

## Record 10 — page inventory analysis → `analyze-page-inventory`

- **Source:** `sp-discovering-pages` / `sp-analysing-aspx-pages` (3 and 5 LIVE symlinks
  respectively), resolving into `scripts/page-migration/analyse_aspx_content.py`.
- **Source implementation status:** `IMPLEMENTED`.
- **Destination:** `skills/analyze-page-inventory/SKILL.md` + `scripts/page_inventory_analysis.py`.
- **Removed project coupling:** the source embedded one organisation's complexity thresholds and
  disposition rules directly. All are now caller-supplied via `load_rules(path)`; no migration
  judgement ships as a live default.
- **Intentional behavior changes:** PowerShell/Python → Python (Wave 1 precedent). Added the
  `DiscoveryStatus` vocabulary — the source printed to console and, on a missing input, silently
  substituted fabricated defaults. A missing input is now `UNAVAILABLE` and creates no output
  directory at all (spec §13).
- **Parity evidence:** `tests/test_page_inventory_analysis.py`.

## Record 11 — web-part code analysis → `analyze-webpart-code`

- **Source:** `sp-discovering-web-parts` — 19 raw symlinks, but Task 2a recomputed this to **13
  LIVE**: 6 pointed outside the plugin boundary at `01_source_sharepoint/analysis/` project
  analysis documents. **Those 6 were not extracted** — they are project data, not capability, and
  fail the genericity contract by definition.
- **Source implementation status:** `IMPLEMENTED` (richest discovery skill).
- **Destination:** `skills/analyze-webpart-code/SKILL.md` + `scripts/webpart_code_analysis.py`.
- **Removed project coupling:** the source hardcoded a ~30-entry helper-script table and named
  business-rule heuristics — site-specific institutional knowledge. All removed and replaced by the
  caller-supplied `KnowledgeBase` / `InlineLogicRule`; `DEFAULT_KNOWLEDGE_BASE` is generic.
- **Intentional behavior changes:** `ScriptEditorMissing` is preserved as a first-class category
  distinct from `Empty` — an unretrievable web part is an unknown, not an empty one — and any run
  containing one reports `PARTIAL` with a count rather than `OBSERVED`. This was enforced by
  correcting a test that had asserted `OBSERVED` on a fixture legitimately yielding `PARTIAL`.
- **Parity evidence:** `tests/test_webpart_code_analysis.py`, including
  `test_run_with_fully_retrievable_input_is_observed` covering the clean-input path.

## Record 12 — `discovery_inputs.py` (new, no source counterpart)

Shared status vocabulary and input loading. **New in this repository** — the source scripts had no
shared outcome vocabulary and silently fabricated defaults on missing input. This module exists to
make "not checked" impossible to confuse with "checked and fine".

## Not extracted, and why

- `sp-discovering-lists`, `sp-discovering-content-types`, `sp-discovering-workflows` —
  `PLANNED_WITH_NO_IMPLEMENTATION` in the source. Gaps, not skills.
- `sp-discovering-site-structure`, `sp-discovering-navigation`, `sp-discovering-forms`,
  `sp-discovering-permissions`, `sp-synthesizing-discovery` — implemented in the source but **not
  yet extracted**; deferred, not rejected. Note `sp-discovering-site-structure` is backed by the
  two most literal-saturated files in the entire source (178 and 147 hits — spec §8h), so its
  extraction cost is high despite being read-only.
- The 6 `ESCAPES_PLUGIN` symlinks under `sp-discovering-web-parts/references/` — project analysis
  documents outside the plugin boundary.

## Independence verification

- `isolated_install_check.py --plugin sharepoint-discovery --import-package discovery_inputs` →
  **PASS, 41 tests**.
- Runtime tree contains zero project literals (verified by grep and by
  `test_module_source_contains_no_project_literals`). Provenance docstrings that originally named
  the source project were reworded — provenance belongs in this file, not in shipped modules.

## Source-repository preservation

No file in the source repository was modified; symlink resolution was read-only.

---

# Wave 6 — `sharepoint-schema` (new plugin)

**Source repository:** `jag-csb-cmat-sharepoint-online` (read-only). **Pinned commit:**
`78d6bb91a6c3c01208208a8c2a06f241fef9ce9f`. **Source plugin:** `sharepoint-migration`.
**Destination:** `plugins/sharepoint-schema` (new).

## Justification verdict

Spec §8e rated this the **weakest** of the five provisionally-justified candidates ("only 2 of 5
implemented, both thin... provisionally justified on `sp-auditing-schema` alone"). Direct
inspection at the pinned commit revised that upward: `sp-auditing-schema` resolves to **6 live
scripts** (schema comparison, site parity, duplicate auditing, missing-field detection), not a thin
shell. **Verdict: justified as a standalone plugin.** Distinct domain (schema variance), cohesive
responsibility, independent installation value, no existing workbench plugin owns it.

## Record 13 — `sp-auditing-schema` → `audit-schema`

- **Source:** 7 symlinks, of which **6 LIVE and 1 BROKEN** (`compare-live-schema-test-vs-spo.ps1`
  → nonexistent target). The broken link was **not** extracted and **not** repaired in the source
  (§17). Live targets resolved into `scripts/schema-audit/` and `scripts/utilities/`.
- **Destination:** `skills/audit-schema/SKILL.md` + `scripts/schema_export.py`,
  `scripts/schema_diff.py`, `scripts/duplicate_fields.py`.
- **Removed project coupling:** the source hardcoded its own environment pair and a project path
  segment in the export layout. Both removed — environment labels and the scope segment are
  explicit caller parameters, and a test asserts the default layout assumes no project scope
  segment. Compared properties and the builtin-column exclusion list are likewise caller-supplied.
- **Intentional behavior changes:** PowerShell → Python (Wave 1 precedent). Added the
  `SectionStatus` vocabulary (`OBSERVED`/`EMPTY`/`PARTIAL`/`UNAVAILABLE`) — a missing export is
  `UNAVAILABLE`, never a clean pass; an unreadable list yields `PARTIAL`; a list present on one
  side only is reported, never dropped; duplicate keys surface as ambiguity rather than being
  resolved by guessing. `render_markdown` is deterministic and emits no timestamp or host
  identifier so successive reports diff cleanly.
- **Deliberate capability REMOVAL:** the source's duplicate-field script carried a `-Cleanup`
  switch that called `Remove-PnPField` — a destructive tenant write. **That capability was not
  extracted.** `test_module_exposes_no_remediation_or_write_capability` enforces its absence. This
  is an intentional narrowing consistent with spec §13's read-only-default posture, not an
  oversight.
- **Parity evidence:** `tests/test_schema_export.py` (13), `tests/test_schema_diff.py` (10),
  `tests/test_duplicate_fields.py` (9).

## Record 14 — `sp-extracting-choices` → `extract-choice-fields`

- **Source:** 1 LIVE symlink → `scripts/utilities/extract-choices.ps1`. Task 2a flagged this as
  thin and required verifying real depth; confirmed thin, so the destination reimplements the
  technique rather than porting substantial logic.
- **Destination:** `skills/extract-choice-fields/SKILL.md` + `scripts/choice_fields.py`.
- **Intentional behavior changes:** "no options defined" (`EMPTY`) and "options unknown"
  (`UNKNOWN`, no `Choices` property in the export) are distinguished and never conflated;
  `to_overrides_mapping` omits unknown option sets rather than emitting an empty list, so a
  consumer cannot mistake "we don't know" for "there are none". Both the plain-array and OData
  `{"results": [...]}` envelope forms are supported. The group filter is opt-in with no default —
  nothing is silently excluded.
- **Parity evidence:** `tests/test_choice_fields.py` (9).

## Not extracted, and why

- `sp-mapping-content-types`, `sp-mapping-lists`, `sp-mapping-taxonomy` —
  `PLANNED_WITH_NO_IMPLEMENTATION` in the source. Gaps, not skills; no empty skills created.
- `sp-synthesizing-deployment-matrix` — spec §8d flagged this `UNVERIFIED_ACTIVE_CLAIM`
  (`SKILL.md` claims `active`, zero scripts and zero symlinks). **Direct inspection at the pinned
  commit confirms the claim is unfounded: it has no backing implementation.** This resolves that
  open `REQUIRES_HUMAN_DECISION` item — reclassify as `PLANNED_WITH_NO_IMPLEMENTATION`.
- The source's field-deletion (`-Cleanup`) capability — deliberately dropped, see Record 13.

## Independence verification

- `isolated_install_check.py --plugin sharepoint-schema --import-package schema_export` → PASS.
- All 4 runtime modules: zero project literals, zero GUIDs/tenant URLs, standard library only, no
  tenant connection or write path — each enforced by a test in
  `tests/test_genericity_and_independence.py`, guarded against vacuity by
  `test_runtime_scan_is_not_vacuous`.

## Source-repository preservation

No source file was modified. The broken symlink was recorded, not repaired.

---

# Wave 4 — `sharepoint-page-modernization` (new plugin)

**Source repository:** `jag-csb-cmat-sharepoint-online` (read-only). **Pinned commit:**
`78d6bb91a6c3c01208208a8c2a06f241fef9ce9f`. **Source plugin:** `sharepoint-migration`.
**Destination:** `plugins/sharepoint-page-modernization` (new).

Spec §8e: "the single richest implementation in the entire audit... the strongest single Phase 9
pilot candidate." Confirmed — `sp-converting-aspx-pages` holds 32 real files plus 5 LIVE symlinks,
more than any other source artifact.

## Record 15 — `sp-analysing-aspx-pages` + `sp-converting-aspx-pages` → `analyze-aspx-pages`, `convert-aspx-pages`

- **Source skills:** `sp-analysing-aspx-pages` (5 LIVE symlinks), `sp-converting-aspx-pages`
  (32 real files + 5 LIVE symlinks). Shared scripts resolve into `scripts/page-migration/` — the
  most-symlinked directory in the source (28 inbound links).
- **Source implementation status:** `IMPLEMENTED`, richest in repo.
- **Destination:** two skills over five modules —
  `outcomes.py` (shared status vocabulary), `aspx_inventory.py` (stage 1),
  `component_classification.py` (stage 2), `layout_selection.py` (stage 3),
  `component_mapping.py` (stage 4) — plus packaged assets `layout-rules.json`,
  `webpart-mapping.json`, `webpart-migration-rules.json`, `manifest-schema.json`,
  `preview-template.html`, `gap-notice.template.html`.
- **Removed project coupling:** the source's organisation-specific layout thresholds and web-part
  mapping entries were institutional knowledge. They are now packaged, caller-overridable **data**
  files; no migration judgement is hardcoded in Python. Zero project literals in shipped code.
- **Intentional behavior changes:**
  - PowerShell/Python → Python throughout (Wave 1 precedent).
  - Added the shared honest-outcome vocabulary: missing input `UNAVAILABLE` (never a clean pass),
    no components `EMPTY`, partially-parseable input `PARTIAL` with unreadable parts recorded.
    Malformed markup is handled, not crashed on (`malformed-page` fixture).
  - `Unknown` is a first-class classification variant — a component the classifier cannot place is
    reported as unknown rather than forced into a plausible category.
  - **Security hardening not present in the source:** layout-rule conditions are evaluated by a
    restricted AST evaluator (`safe_eval_condition`) permitting only names, constants, comparisons,
    boolean operators and arithmetic. **Any call expression is rejected** — `__import__(...)`,
    `open(...)` etc. raise `UnsafeConditionError` and the rule is recorded in `skippedRules` rather
    than executed. Rule files are data and are therefore treated as untrusted input. Verified
    independently: both `__import__("os").system(...)` and `open("/etc/passwd").read()` are
    blocked while `zoneCount > 2` evaluates normally.
  - **Gaps are named, not hidden:** connected-consumer web parts cannot be reproduced on modern
    pages. Rather than dropping them silently or substituting something plausible, a gap notice is
    rendered from the packaged template **naming the specific lists that were not migrated**.
    Unsupported web-part types are surfaced explicitly.
- **No tenant writes:** the pipeline produces a conversion *manifest* conforming to
  `assets/manifest-schema.json`. It does not create, publish, or modify anything in SharePoint.
- **Parity evidence:** 54 tests across `test_outcomes.py`, `test_aspx_inventory.py`,
  `test_component_classification.py`, `test_component_mapping.py`, `test_layout_selection.py`.
  Several invoke the stage CLIs through real `subprocess`, with real file parsing and real path
  resolution — unmocked, per `.agent/rules/test-driven-development.md`'s critical-runtime-paths
  rule, since parsing files off disk is this plugin's entire job.

## Boundary vs `structured-content-rendering` (spec §4a)

`structured-content-rendering` **renders new** pages from structured content this workbench owns.
This plugin **analyses and converts existing** legacy pages it did not create. Different inputs,
different responsibility. Neither was modified by this extraction and no code is shared between
them.

## Not extracted, and why

- `sp-converting-wiki-pages` (2 LIVE symlinks, resolved and read in full) — **rejected, not
  deferred.** Both symlinks (`scripts/page-migration/convert-wiki-page.ps1` and its dot-sourced
  dependency `scripts/lib/sp-extract-lib.ps1`) resolve to a **live-tenant collector**, not an
  analyser of already-exported content:
  - `convert-wiki-page.ps1` takes a live `-SourceSiteUrl` and authenticates via
    `New-ClientContextSafe` (a real CSOM `ClientContext` against that URL), falling back to
    `Invoke-SpWebRequest` (a thin wrapper over `Invoke-WebRequest`) against the same live site
    when CSOM/IWA auth fails.
  - Its SKILL.md lists prerequisites of "VPN connected to on-premises SharePoint network" and
    "IDIR credentials for IWA" — i.e. it requires a live network path and live credentials to run
    at all. It downloads the raw `.aspx`, rendered HTML, web parts, and image assets directly
    from the tenant over that connection; there is no exported-content input path.
  - This is the exact same shape already rejected once in this phase for a different capability
    (the one that called `Connect-PnPOnline`) — live tenant I/O is out of scope for
    `sharepoint-page-modernization`, which is contractually a no-tenant-I/O plugin that only
    analyses/converts content already sitting on disk.
  - The companion reference doc (`references/aspx-to-spo-migration-strategy.md`, 379 lines) was
    considered for extraction on its own — its core finding ("classic pages cannot be directly
    converted; reconstruct, not convert") is generic and this workbench independently
    corroborated it. It was **not extracted**: the document is pervasively coupled to the source
    project throughout (specific page names, page-count tiers, and organisation-specific
    interaction-model analysis run through Sections 1, 3, 6, and 8, not confined to an isolable
    subsection), so a compliant scrub would amount to writing new generic guidance from the one
    corroborated sentence rather than extracting existing content — out of scope for an
    extraction pass.
- `sp-remediating-page-layouts`, `sp-remediating-web-parts` —
  `PLANNED_WITH_NO_IMPLEMENTATION` in the source. Gaps, not skills.

## Independence verification

`isolated_install_check.py --plugin sharepoint-page-modernization --import-package outcomes` →
**PASS, 54 tests against the wheel-installed package.** This specifically confirms
`scripts/assets/` is packaged correctly — the exact class of defect Phase 6 caught, where assets
outside the `package-dir` boundary work under editable install but break a real wheel build.

## Source-repository preservation

No source file was modified; reference reading only.

---

# Consolidation record (2026-08-07)

All five wave branches merged into `phase-9-reusable-sharepoint-plugin-extraction`. Three registry
files conflicted on every wave after the first (`symlinks.json`, `.claude-plugin/marketplace.json`,
`provenance.md`) because each wave appends to all three. **Every conflict was resolved by union —
no wave's entries were dropped in favour of another's.**

## Post-consolidation verification (whole branch, not per-wave)

| Plugin | Tests |
|---|---|
| `sharepoint-link-remediation` | 121 passed |
| `sharepoint-discovery` | 41 passed |
| `sharepoint-schema` | 50 passed |
| `sharepoint-page-modernization` | 54 passed |
| `sharepoint-agents-and-skills` | 68 passed |
| `sharepoint-content-publication` | 31 passed |
| `workbench-setup` | 52 passed |
| **Total** | **417 passed, 0 failed** |

- All 11 plugins present in `.claude-plugin/marketplace.json`; `claude plugin validate .` passes
  (one pre-existing unrelated warning on an older plugin's `capabilities` field).
- Symlink integrity: 24 broken links repo-wide, **all pre-existing** in the four original Phase 4.5
  plugins (`docs/diagrams` gap, 6 each). **Zero** broken links in any plugin Phase 9 created or
  touched.

## Coverage — what this phase did and did not onboard

**Onboarded (17 artifacts):** 2 skills into existing plugins (Wave 1), 4 agents into
`sharepoint-agents-and-skills` (Wave 2), and 4 new plugins — `sharepoint-discovery` (2 skills),
`sharepoint-link-remediation` (3), `sharepoint-schema` (2), `sharepoint-page-modernization` (2).

**Deliberately NOT onboarded — deferred, not rejected:**

- Five implemented discovery capabilities: `sp-discovering-site-structure`, `sp-discovering-navigation`,
  `sp-discovering-forms`, `sp-discovering-permissions`, `sp-synthesizing-discovery`. Note
  `sp-discovering-site-structure` is backed by the two most literal-saturated files in the source
  (178 and 147 hits, §8h) — read-only but expensive to genericize.
- `sp-converting-wiki-pages` (2 LIVE symlinks, implemented).
- `sp-running-sharegate-jobs` — depends on an external commercial tool; dependency must be
  documented before extraction, per §8d.
- `sp-uploading-content`'s broader dual-mechanism upload capability beyond Wave 1's scope.

**Excluded on evidence, not deferred:**

- `sharepoint-content-migration` as a plugin. Task 2a recomputed `sp-migrating-content` from 44 raw
  symlinks to **29 LIVE** (12 resolve into `scripts/_deprecated/`, 3 dangle). Its reusable
  wave-execution *mechanism* is unproven outside deprecated code, so §8e's provisional
  justification does not survive the corrected evidence. Extracting it would mean building on
  `_deprecated/`.
- `sp-provisioning-modern-calendars` — `KEEP_CMAT_SPECIFIC`.
- The whole `ords-integration-migration` plugin — verified read of all 4 skills confirms they are
  entirely court-system/Oracle-specific. `ORDS_SPECIFIC_OUT_OF_SCOPE` stands.
- The source's field-deletion (`-Cleanup`) capability — deliberately dropped (Record 13).
- 11 `PLANNED_WITH_NO_IMPLEMENTATION` source skills — gaps, not capabilities. No empty skills were
  created for any of them.

**Roughly half of the 21 implemented source skills are now onboarded.** This branch is not a
complete port of the source's SharePoint engineering capability and should not be described as one.

## Merge status

**NOT merged to `main`.** Per this repository's per-phase workflow, `main` integration requires
human review and approval; the agent does not merge. Phase 9's own exit criteria (§20) also remain
partially unmet — notably the full remaining-capability roadmap and the phase retrospective.

---

## Appended 2026-08-07 — Wave 3: `sharepoint-discovery` extension (navigation, forms, permissions)

Extends the existing `plugins/sharepoint-discovery/` plugin (2 skills, 3 modules, 41 tests before
this wave) with three more read-only analysis capabilities, following the same
`discovery_inputs.py` `DiscoveryStatus`/`DiscoveryOutcome` vocabulary and flat-`scripts/` house
style as the plugin's existing `page_inventory_analysis.py`/`webpart_code_analysis.py`. Same
source repository/commit/plugin baseline as above.

### Record 7 — `sp-discovering-navigation` → `sharepoint-discovery/skills/analyze-site-navigation`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-discovering-navigation/`
- **Source scripts (resolved through symlinks, 2 LIVE):**
  - `plugins/sharepoint-migration/scripts/page-migration/generate-deep-nav-analysis.py` (ported)
  - `plugins/sharepoint-migration/scripts/page-migration/extract-site-navigation.ps1` (not ported —
    a live tenant collector, out of scope for a read-only analysis plugin that consumes exports)
- **Source tests:** none found for either script.
- **Source implementation status:** `IMPLEMENTED`.
- **Destination files:**
  - `plugins/sharepoint-discovery/scripts/navigation_analysis.py` (new module)
  - `plugins/sharepoint-discovery/tests/test_navigation_analysis.py` (new tests, 10 cases)
  - `plugins/sharepoint-discovery/tests/fixtures/navigation.json` (new neutral fixture)
  - `plugins/sharepoint-discovery/skills/analyze-site-navigation/SKILL.md` (new skill; script and
    `discovery_inputs.py` symlinked into the skill's `scripts/` folder per `symlinks.json`)
- **Removed project coupling:** the hardcoded `total_webs: 6`, the fixed `site_url =
  "https://csb.jag.gov.bc.ca"` default, the `--site-name` CLI default `"CSB Intranet Prod"`, the
  `config.psd1` `ExportBase`/`StructureSourceUrl` regex-scraping path resolution, and the Markdown
  template-file substitution (`SITE-NAVIGATION-CHROME-SUMMARY-template.md`) are all removed. The
  destination module takes one caller-supplied export path and one caller-supplied output
  directory; it has no default site identity and no tenant-specific path convention.
- **Intentional behavior changes:**
  1. The source printed a fixed `"SPO Hub Global Navigation"` mapping label per row regardless of
     input; the destination reports structural facts only (title, url, depth, child count) and
     leaves migration-target labeling to the caller/reviewer — no per-row judgement is fabricated.
  2. The source's `total_webs` field was a hardcoded constant (6) never derived from any input;
     dropped entirely rather than carried forward as a fake statistic.
  3. Added recursive max-depth computation across arbitrarily nested `children` — the source only
     handled a single level of children for the row's sub-node count and never computed how deep
     the tree actually went.
  4. Honest outcomes added: a missing export is `UNAVAILABLE` (source silently built an empty
     `nav_data = {}` and reported "0 nodes" as if that were a successful survey); an export with no
     nodes at all is `EMPTY`; a non-object export is `FAILED`.
- **New neutral fixtures:** `tests/fixtures/navigation.json` — a synthetic 2-level tree (`Home`,
  `Departments > Finance/HR > Benefits`) and a flat `quickLaunch` list. No real tenant URLs.
- **Parity evidence:** retained behavior is the flatten-with-depth/child-count structural read of a
  `{topNav, quickLaunch}` export — source input: `TopNav`/`QuickLaunch` JSON arrays with optional
  `Children`; source output: a row per top-level node with a child count; destination fixture: the
  2-level synthetic tree above; destination result: `analyse()` returns 2 top-nav top-level nodes,
  4 nodes total, max depth 2, and per-node `depth`/`childCount` matching the tree shape — verified
  by `test_max_depth_reflects_deepest_child_chain` and `test_flattened_nodes_carry_depth_and_child_count`.

### Record 8 — `sp-discovering-forms` → `sharepoint-discovery/skills/analyze-custom-forms`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-discovering-forms/`
- **Source scripts (resolved through symlinks, 2 LIVE):**
  - `plugins/sharepoint-migration/scripts/page-migration/generate-deep-forms-analysis.py` (ported)
  - `plugins/sharepoint-migration/scripts/page-migration/download-custom-forms.ps1` (not ported — a
    live tenant collector, same read-only-analysis-plugin boundary as Record 7)
- **Source tests:** none found for either script.
- **Source implementation status:** `IMPLEMENTED`.
- **Destination files:**
  - `plugins/sharepoint-discovery/scripts/forms_analysis.py` (new module)
  - `plugins/sharepoint-discovery/assets/form-classification-rules.json` (new neutral default
    rules asset, packaged copy symlinked into `scripts/assets/` per `symlinks.json`, matching the
    existing `webpart-migration-rules.json` hub-and-spoke pattern)
  - `plugins/sharepoint-discovery/tests/test_forms_analysis.py` (new tests, 11 cases)
  - `plugins/sharepoint-discovery/tests/fixtures/forms.json` (new neutral fixture)
  - `plugins/sharepoint-discovery/skills/analyze-custom-forms/SKILL.md` (new skill; script and
    `discovery_inputs.py` symlinked into the skill's `scripts/` folder)
- **Removed project coupling:** the fixed `site_url`/`"CSB Intranet Prod"` defaults, the
  `config.psd1` scraping path, and the hardcoded `"Custom Power Apps / React Form"` modernization
  strategy string (baked into the source regardless of what kind of custom form was found) are all
  removed. The destination reads the modernization strategy per classification from a
  caller-supplied rules file (`load_rules`), following the same "rules are data, not code" pattern
  already established by `page_inventory_analysis.py`'s `webpart-migration-rules.json`.
- **Intentional behavior changes:**
  1. Strategy text is now caller-owned data (`assets/form-classification-rules.json`), not a single
     hardcoded string applied to every custom form regardless of kind.
  2. Honest outcomes added: a missing forms export or rules file is `UNAVAILABLE` (the source
     silently fell back to an empty `forms_data = []` list and reported a clean "0 custom forms"
     summary if neither `--input` nor the default manifest path existed); an empty export is
     `EMPTY`; a non-array export is `FAILED`.
- **New neutral fixtures:** `tests/fixtures/forms.json` — three synthetic list forms (a scripted
  custom form, an InfoPath/layout-only custom form, an out-of-box form). No real tenant data.
- **Parity evidence:** retained behavior is the three-way classification (out-of-box / script /
  InfoPath-layout-only) — source input: a `ListName`/`IsCustomized`/`HasScript` array; source
  output: `oob_forms`/`script_count`/`infopath_count` tallies plus a custom-forms row list;
  destination fixture: the 3-entry synthetic array above; destination result: `analyse()` reports
  1 out-of-box, 1 script, 1 InfoPath form, with `customItems` excluding the out-of-box entry and
  each custom item carrying the caller-supplied strategy string for its `formKind` — verified by
  `test_classifies_script_infopath_and_out_of_box` and
  `test_custom_items_carry_a_caller_supplied_strategy`.

### Record 9 — `sp-discovering-permissions` → `sharepoint-discovery/skills/analyze-permissions`

- **Source skill:** `plugins/sharepoint-migration/skills/sp-discovering-permissions/`
- **Source script (resolved through symlink, 1 LIVE):**
  - `plugins/sharepoint-migration/scripts/page-migration/generate-deep-permissions-analysis.py`
    (ported)
- **Depth correction:** the Phase 9 dispatch brief flagged this skill as "1 LIVE — thin, verify
  real depth before claiming it's implemented." On read, the single script is 242 lines with real
  branching logic — it accepts *two* distinct export shapes (a flat per-(principal, object) row
  array, or a structured `{Groups, Objects}` document with an explicit
  `HasUniqueRoleAssignments` flag), derives groups/objects from either, and generates two separate
  reports (a group provisioning checklist and a broken-inheritance exception report). This is not
  thin; it was extracted in full.
- **Source tests:** none found.
- **Source implementation status:** `IMPLEMENTED`.
- **Destination files:**
  - `plugins/sharepoint-discovery/scripts/permissions_analysis.py` (new module)
  - `plugins/sharepoint-discovery/tests/test_permissions_analysis.py` (new tests, 9 cases,
    covering both accepted input shapes)
  - `plugins/sharepoint-discovery/tests/fixtures/permissions-flat.json`,
    `tests/fixtures/permissions-structured.json` (new neutral fixtures)
  - `plugins/sharepoint-discovery/skills/analyze-permissions/SKILL.md` (new skill; script and
    `discovery_inputs.py` symlinked into the skill's `scripts/` folder)
- **Removed project coupling:** the fixed `"https://csb.jag.gov.bc.ca"` default site URL, the
  `--site-name "CSB Intranet Prod"` default, the `config.psd1` scraping path, the
  `.replace('CSB_', '').replace('CMAT_', '')` group-name transformation (a project-specific prefix
  strip applied to every group name), and — most significantly — the **fabricated fallback data**
  the source wrote when its input file did not exist (`{"SiteUrl": "https://csb.jag.gov.bc.ca",
  "Groups": [{"Name": "Owners", ...}, {"Name": "Members", ...}], "Objects": []}`, which let the
  source report a clean-looking two-group checklist even when no real export was ever read) are
  all removed.
- **Intentional behavior changes:**
  1. A missing permissions export is now `UNAVAILABLE` with **no output written** — the source's
     synthetic-fallback behavior above is exactly the kind of "empty success" this plugin's honest-
     outcomes contract (spec §13) forbids, so it was not carried over as a default; it is recorded
     here for transparency, not silently dropped.
  2. Group-name normalization (stripping org-specific prefixes) is removed as project-specific
     display logic, not reusable analysis.
  3. The two source reports (checklist + exception report) are consolidated into one
     `permissions-plan.{json,md}` pair with two sections, matching this plugin's one-plan-per-run
     convention (`page-inventory-plan`, `navigation-plan`, `forms-plan`) rather than the source's
     two-separate-files convention.
- **New neutral fixtures:** `permissions-flat.json` (3 flat rows across 3 objects) and
  `permissions-structured.json` (2 groups, 2 objects, 1 with broken inheritance) — no real tenant
  URLs or GUIDs.
- **Parity evidence:** retained behavior is dual-shape group/object derivation plus broken-
  inheritance filtering — source input (structured shape): `Groups`/`Objects` with
  `HasUniqueRoleAssignments`; source output: `unique_objects` filtered to `HasUniqueRoleAssignments
  == True`; destination fixture: `permissions-structured.json`'s 2 objects, 1 flagged unique;
  destination result: `analyse()` returns `uniqueObjectsCount == 1` and names the correct object —
  verified by `test_structured_shape_flags_unique_role_assignments_only`. Flat-shape parity:
  source derives one row per unique `ObjectTitle`/`ListName` across repeated principal rows;
  destination fixture: `permissions-flat.json`'s 3 rows across `Site`/`Policies`/`Forms`;
  destination result: `analyse()` derives exactly 3 objects and groups the 2 `Forms`/`Policies`
  rows sharing `HR Reviewers` correctly — verified by `test_flat_shape_derives_groups_and_objects`
  and `test_flat_shape_groups_multiple_role_assignments_under_one_object`.

### Not extracted, and why

- **`sp-synthesizing-discovery`** (`generate-master-discovery-meta-review.py`, 1 LIVE symlink, 129
  lines) — read in full and judged **too thin to extract as a real capability**. Its only actual
  data-driven step is reading one manifest file's array length for `total_pages`; every other
  metric it reports (`total_wps`, `unique_wp_groups`, `flagged_links`, `total_groups`,
  `custom_forms`, `total_nav_nodes`) is a **hardcoded literal fallback**
  (`{"total_pages": 654, "total_wps": 193, "unique_wp_groups": 181, "flagged_links": 4792,
  "total_groups": 53, "custom_forms": 0, "total_nav_nodes": 109}`) that is never reconciled against
  any of the other 12 discovery domains' real output files — despite the module's own docstring
  describing it as reading "all discovery outputs across the 13 discovery domains." The
  "complexity rating" and page-disposition percentages (`oob_pages = total_pages * 0.7`,
  `custom_pages = total_pages * 0.25`) it derives are arithmetic on those same mostly-fabricated
  numbers, not analysis of real data. A synthesis/meta-review capability worth extracting would
  need to genuinely read the sibling `navigation-plan.json`/`forms-plan.json`/
  `permissions-plan.json`/`page-inventory-plan.json` artifacts this wave's three modules (plus the
  existing two) now produce and roll them up — that is a real, separate design task, not a port of
  this script. Deferred, not built as a hollow shell.
- **`sp-discovering-site-structure`** (3 LIVE symlinks) — not read in detail this wave, consistent
  with the dispatch brief's budget warning: its two backing scripts,
  `scripts/inventory/export-sharepoint-inventory.ps1` and
  `export-sharepoint-inventory-custom.ps1`, are PowerShell **collectors** (they connect to a live
  tenant to build the inventory export), not analysis of an already-collected export — out of
  scope for this read-only-analysis plugin regardless of their reported 147/178 project-literal
  saturation. The third symlink, `diagnose-page.ps1`, is also a live-tenant diagnostic script, not
  an analysis-of-export capability. No PowerShell collector from this skill fits this plugin's
  contract; a site-structure *analysis* module (consuming whatever JSON these collectors produce)
  remains a legitimate future candidate but was not attempted this wave.

### Verification (Wave 3)

- `python3 -m pytest -q plugins/sharepoint-discovery` — **71 passed** (41 pre-existing + 30 new:
  10 navigation + 11 forms + 9 permissions).
- `python3 tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py --plugin
  sharepoint-discovery --import-package discovery_inputs` — passed (exit 0), all 71 tests green
  inside a clean, isolated venv built from the plugin's own wheel.
- `symlink_manager.py restore` — 7 new symlinks created (1 asset, 6 script copies across the 3 new
  skills), 0 new failures (24 pre-existing broken links elsewhere in the repo, unchanged).
- No project literal (`justin`, `ceis`, `ords`, `courthouse`, `ag-csb`, `ag-bcps`, `ag-pssg`,
  `itau`, `pio`, `icm`, `crownnet`, `mediainfo`, `jag.gov.bc.ca`, `bcgov.sharepoint.com`, `cmat`,
  `csb`) found in any new script, asset, skill doc, test, or fixture (grep-verified).

---

# Verification of the two "not extracted" judgements (2026-08-07, independent re-check)

Both skip decisions in the discovery-extension round were re-verified against the pinned source
rather than accepted on assertion. **Both hold.**

## `sp-synthesizing-discovery` — correctly NOT extracted

Backing script `scripts/page-migration/generate-master-discovery-meta-review.py` (129 lines):

- Lines 102-106 define a **hardcoded metrics dictionary** (`total_pages: 654`, `total_wps: 193`,
  `flagged_links: 4792`, ...). Only `total_pages` is ever replaced with real data, from a single
  manifest's array length (line 116). Every other headline figure in the generated "meta review"
  is a constant baked into the script.
- Lines 40-42 **fabricate** further figures from arbitrary ratios:
  `oob_pages = int(total_pages * 0.7)`, `custom_pages = int(total_pages * 0.25)`,
  `spfx_candidates = int(unique_groups * 0.1)`. These are invented estimates presented as
  discovery output.
- Thresholds (`> 100`, `> 500`, `> 1000`) are hardcoded organisation-specific judgement.

Extracting this would have shipped fabricated numbers wearing the appearance of measurement —
precisely the "silent false confidence" failure mode this phase's honest-outcome vocabulary exists
to prevent. A genuine synthesis capability would need to actually roll up the sibling `*-plan.json`
outputs; that is a **new design task**, not an extraction. Recorded as a real capability gap.

## `sp-discovering-site-structure` — correctly NOT extracted (scope, not cost)

Its backing scripts are **live-tenant collectors**, not analysers of an already-collected export:
`export-sharepoint-inventory.ps1` calls `Connect-PnPOnline` and queries a live tenant directly.

`plugins/sharepoint-discovery` is deliberately a **read-only analysis plugin operating on exports
you already have** — it performs no tenant I/O at all. A live collector does not belong in it
regardless of literal density. The 147/178 literal saturation (§8h) is a real additional cost, but
the **scope mismatch is the decisive reason**, and it would remain decisive even if the scripts
were perfectly generic.

Live-tenant collection remains unowned in this workbench. If it is ever wanted it needs its own
plugin with an explicit connection/write-safety boundary, designed against `workbench-setup`'s
connector-injection contract — not folded into the analysis plugin.

---

## Appended 2026-08-07 — Record 16: `combine-preview.ps1` (from `sp-running-sharegate-jobs`) → `compose-page-preview`

### Independence verification (why this one component, out of a ShareGate-dependent skill)

`sp-running-sharegate-jobs` is filed under 3 LIVE symlinks and was previously ranked as blocked on
a commercial-tool dependency decision (Rank 2, roadmap §2). Read individually, one of the three,
`combine-preview.ps1` (458 lines), is not ShareGate-dependent at all:

- **Zero ShareGate calls** — no `Import-Module ShareGate`, no `Connect-Site`, no `Copy-Content`, no
  ShareGate cmdlet of any kind.
- **Zero live-tenant I/O** — no `Connect-PnPOnline`/`Get-PnP*`/`New-ClientContext`/
  `Invoke-WebRequest`/`Invoke-RestMethod` anywhere in the file.
- **Zero project literals** — no organisation, site, or tenant name; its only `.EXAMPLE` block
  references a project-specific path (`courts-intranet\...`), which was **not** carried into the
  destination (see below).

The script is a purely offline, disk-only merge: it reads a chrome folder's `site-chrome.json`
(navigation, header, logo, ancestors) and a page folder's `modern-preview.html` +
`metadata.json`, and writes one combined offline preview HTML file. It was simply co-located with
two genuinely ShareGate-dependent upload scripts inside the same source skill folder.

### Record

- **Source skill:** `plugins/sharepoint-migration/skills/sp-running-sharegate-jobs/`
- **Source script:** `plugins/sharepoint-migration/scripts/page-migration/combine-preview.ps1`
  (ported in full; the two remaining ShareGate upload scripts in the same skill were **not**
  ported — they remain blocked on the commercial-dependency decision, see roadmap §2 Rank 2).
- **Source tests:** none found.
- **Source implementation status:** `IMPLEMENTED`.
- **Destination files:**
  - `plugins/sharepoint-page-modernization/scripts/preview_composition.py` (new module)
  - `plugins/sharepoint-page-modernization/tests/test_preview_composition.py` (new tests, 9 cases)
  - `plugins/sharepoint-page-modernization/skills/compose-page-preview/SKILL.md` (new skill;
    `preview_composition.py` and `outcomes.py` symlinked into the skill's `scripts/` folder)
- **Why this plugin:** `sharepoint-page-modernization` already converts classic pages and ships a
  `preview-template.html` asset for its own webpart-mapping preview stage. A reviewer confirming a
  page conversion needs to see the result in the site's actual navigation/header/logo/breadcrumb
  context — this closes that loop, and reuses the plugin's existing `outcomes.py` vocabulary
  rather than introducing a second one.
- **Removed project coupling:** the `.EXAMPLE` block's `courts-intranet\...` sample path was
  dropped, not carried into any docstring, comment, or SKILL.md.
- **Intentional behavior changes:**
  1. Honest outcomes per this plugin's vocabulary: a missing `metadata.json`, `modern-preview.html`,
     or `site-chrome.json` is `Unavailable` and writes no output (the source `throw`s but leaves no
     structured signal); empty page content is `Empty` (source had no such check and would have
     merged an empty fragment silently); missing logo/ancestors/navigation is `Partial`, with the
     specific missing part(s) named in the outcome detail (source silently rendered blank
     nav/breadcrumb/logo regions with no signal that anything was missing); full chrome and content
     is `Observed`.
  2. Never fabricates a substitute logo, breadcrumb entry, or nav item when chrome data is absent —
     verified by `test_partial_reason_never_fabricates_a_substitute_logo`.
  3. `--output` is an explicit CLI option (defaults to `full-preview.html` inside the page folder,
     matching the source's default), rather than a PowerShell parameter.
- **New neutral fixtures:** synthetic `site-chrome.json` (built inline in the test module — a
  generic `"Example Site"` web title, `/home` nav link, `/` ancestor), `modern-preview.html`, and
  `metadata.json`. No real tenant URLs, GUIDs, or organisation names.
- **Parity evidence:** retained behavior is chrome+content merge, logo-file portability (local logo
  copied into the page folder's `assets/` subfolder), top-nav overflow grouped under a "More" entry
  beyond 5 visible items, and pill-styled breadcrumb rendering with the current page title appended
  — verified by `test_full_chrome_and_content_reports_observed`,
  `test_top_nav_beyond_five_entries_grouped_under_more`, and
  `test_breadcrumb_includes_current_page_title`.

### Verification (Record 16)

- `python3 -m pytest -q plugins/sharepoint-page-modernization` — **63 passed** (54 pre-existing + 9
  new).
- `python3 tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py --plugin
  sharepoint-page-modernization --import-package outcomes` — passed (exit 0), all 63 tests green
  inside a clean, isolated venv built from the plugin's own wheel.
- `symlink_manager.py restore` — 2 new symlinks created (`preview_composition.py`, `outcomes.py`
  into `compose-page-preview/scripts/`), 0 new failures (24 pre-existing broken links elsewhere in
  the repo, unchanged — confirmed via `diagnose`).
- No project literal (`justin`, `ceis`, `ords`, `courthouse`, `ag-csb`, `ag-bcps`, `ag-pssg`,
  `itau`, `pio`, `icm`, `crownnet`, `mediainfo`, `jag.gov.bc.ca`, `bcgov.sharepoint.com`, `cmat`,
  `courts-intranet`) found in the new module, skill doc, or test (grep-verified).

---

# `sharepoint-provisioning` (new plugin, 2026-08-07)

**Source repository:** `jag-csb-cmat-sharepoint-online` (local checkout, read-only).
**Source commit (pinned):** `78d6bb91a6c3c01208208a8c2a06f241fef9ce9f` (2026-08-05 09:19:39 -0700).
**Destination plugin:** `plugins/sharepoint-provisioning` (new).

## Disposition history

`remaining-capability-roadmap.md` §4a records that spec §8e's original verdict on a provisioning
plugin ("not justified — no confirmed generic implemented skill exists here at all") was based on
scanning only `sharepoint-migration`'s 34 skills. A direct read of
`plugins/ords-integration-migration/scripts/ag-tenant/reset-and-provision-etl-target-schema.ps1`
and its dependency `plugins/sharepoint-migration/scripts/lib/content-type-lib.ps1` found a real,
generic, already-zero-literal pattern hiding there. §4a overturned the exclusion and ranked this
work alongside Rank 1 (live-tenant collection) as design-gated, not effort-gated — this record is
that design pass, executed once the write-safety gate design (mirroring `remediate-links`) was
decided.

## Record — content-type-lib.ps1 / field-helpers.ps1 / list-helpers.ps1 → `sharepoint-provisioning`

- **Source scripts (read in full, not just symlink-resolved):**
  - `plugins/sharepoint-migration/scripts/lib/content-type-lib.ps1` (138 lines, 6 functions,
    zero project literals in the source itself) — `New-SiteContentTypeSafe`,
    `Add-FieldToContentTypeSafe`, `Hide-FieldOnContentTypeSafe`, `Show-FieldOnContentTypeSafe`,
    `Unlink-FieldFromContentTypeSafe`, `Add-ContentTypeToListSafe`.
  - `plugins/sharepoint-migration/scripts/lib/field-helpers.ps1` (250 lines, 2 literals in the
    source: a `CMAT replatform` naming-normalisation comment and a `Court_Room` field rename —
    both stripped, neither ported) — `Get-DeployableFields`, `Repair-FieldType`, `Add-FieldSafe`,
    `Invoke-FieldsForList`.
  - `plugins/sharepoint-migration/scripts/lib/list-helpers.ps1` (43 lines, 0 literals) —
    `Invoke-WithRetry`, `New-ListSafe`, `New-LibrarySafe`.
- **Source implementation status:** `IMPLEMENTED` (all three files, live production helper
  libraries dot-sourced by multiple wave scripts).
- **Source pattern only (explicitly not ported as content):**
  `plugins/ords-integration-migration/scripts/ag-tenant/reset-and-provision-etl-target-schema.ps1`
  (351 lines). Read in full. The declarative-schema-driven provisioning shape, reconcile-not-
  recreate semantics (create-if-missing content types/columns, display-name drift detection and
  reconciliation, explicit unlink of undeclared fields), the `Add-PnPField` `-Formula`-parameter
  limitation and its raw-Field-XML workaround (for Calculated columns; generalised here to also
  cover Lookup/LookupMulti and User/UserMulti, which the same script's field-helpers dependency
  also renders via raw XML for the same typed-API-limitation reason), the duplicate-title
  detection before any delete (`Get-PnPList | Where-Object Title -eq`, never a single identity
  lookup — a real incident: a stray duplicate-titled list caused auth to silently resolve to the
  wrong list), and the fail-loud "still exists after delete" check were all read and are reflected
  in this plugin's design. **No CMAT content was ported from this file**: not the 52-list
  inventory, not `Modern_Manual_Appearances`/`Modern_Scheduled_Appearances`, not the calendar/
  court-appearance provisioning logic (`New-ModernCalendarList`, `Set-AppearanceFormLayouts`), not
  any list/field/content-type name, not any BC Government/JAG/ORDS/ITAU literal.
- **Destination files:**
  - `plugins/sharepoint-provisioning/scripts/provisioning_outcomes.py` (new — shared `Outcome`
    vocabulary, same shape as `sharepoint-link-remediation`'s `link_outcomes.py`)
  - `plugins/sharepoint-provisioning/scripts/field_provisioning.py` (new — ports
    `Get-DeployableFields`/`Repair-FieldType` as `filter_deployable_fields`/
    `field_needs_type_repair`; ports the calculated/lookup/user raw-XML technique as
    `build_calculated_field_xml`/`build_lookup_field_xml`/`build_user_field_xml`; per-field
    planning as `plan_field_action`)
  - `plugins/sharepoint-provisioning/scripts/content_type_provisioning.py` (new — ports all six
    `content-type-lib.ps1` functions as pure planning: `plan_content_type`,
    `plan_add_content_type_to_list`)
  - `plugins/sharepoint-provisioning/scripts/list_provisioning.py` (new — ports
    `Invoke-WithRetry`'s retry *intent* as an executor-boundary concern left to the caller's
    injected executor, not reimplemented as a sleep loop in planning code; ports
    `New-ListSafe`/`New-LibrarySafe` as create-if-missing list planning; ports the reconcile-
    schema/duplicate-detection/fail-loud pattern as `plan_provisioning`, `detect_duplicate_lists`,
    `apply_provisioning`, `verify_deletion_complete`)
  - `plugins/sharepoint-provisioning/tests/test_field_provisioning.py` (30 tests)
  - `plugins/sharepoint-provisioning/tests/test_content_type_provisioning.py` (10 tests)
  - `plugins/sharepoint-provisioning/tests/test_list_provisioning.py` (20 tests, including the
    explicit four-state write-safety gate proof: dry-run writes nothing, missing executor raises,
    missing/stale confirmation token raises, a real executor with a valid token executes)
  - `plugins/sharepoint-provisioning/tests/test_plugin_independence.py` (27 tests — genericity,
    source-repo-marker, GUID-shape, and zero-tenant-transport gates)
  - `plugins/sharepoint-provisioning/skills/provision-content-types/SKILL.md`,
    `skills/provision-fields/SKILL.md`, `skills/provision-list/SKILL.md` (new)
- **Removed project coupling:** every source/tenant/project literal from all four source files —
  no `bcgov.sharepoint.com`, no `AG-CSB-ITAU-CMAT-*` site names, no `Modern_Manual_Appearances`/
  `Modern_Scheduled_Appearances` content-type names, no `Court_Room`/`ITAU_Cal_*`/
  `All_Appearances`/`Appearance_City_to_be_Verified` field or list names, no `CMAT Columns`
  group name (destination default group is `Custom Columns`, matching the generic default already
  used by `content-type-lib.ps1` itself, not the CMAT-specific override used only in the reset
  script's site-column loop), no wave-dependency-matrix/target-list-inventory JSON schema shape
  tied to the 52-list CMAT inventory. Every column, content type, and target list this plugin
  provisions is 100% caller-supplied via `ProvisioningSchema`.
- **Intentional behavior changes:**
  1. PowerShell → Python (Wave 1 precedent, matches this repo's plugin-language convention).
  2. **The whole plugin is planning-only; no PnP/CSOM call, no raw network call, ships anywhere in
     it** (task hard requirement #2, enforced by
     `test_no_live_pnp_or_csom_or_network_transport_ships`). The source scripts performed live
     `Get-PnPContentType`/`Add-PnPField`/`Remove-PnPList`/etc. calls inline; every one of those
     call sites is replaced here by either a pure comparison against caller-supplied
     `CurrentState`/observed-type input, or a step in `ProvisioningPlan._write_items()` that is
     only ever invoked through a caller-injected `executor(step, detail)` callable.
  3. **Three-gate write safety, exactly matching `remediate-links`** (task hard requirement #1):
     dry-run by default (`apply_provisioning(plan)` with no arguments changes nothing),
     `ExecutorRequired` raised without an injected executor, `ConfirmationRequired` raised without
     `confirm=plan.confirmation_token` (a token derived from the plan's own write-item content via
     SHA-256, so it goes stale the instant the schema or observed state changes — proven directly
     by `test_apply_provisioning_token_goes_stale_when_plan_source_data_changes`). **This is a
     real, significant improvement over the source**: the source script had a `-DryRun` switch but
     no confirmation-token concept at all — a live run with `-DryRun` unset executed immediately.
  4. **A fourth, unconditional gate** not present in the three-gate pattern this plugin otherwise
     mirrors: `DuplicateListsBlockProvisioning` refuses execution of any plan carrying a duplicate-
     title finding, even with an otherwise-valid confirmation token — direct response to the
     source's own documented incident (`reset-and-provision-etl-target-schema.ps1`'s Stage 1
     comment: "a stray duplicate-titled 'Persons' list on PROD caused app-only auth to silently
     resolve to the wrong list"). `detect_duplicate_lists` compares a caller-supplied
     `matching_count` (never a single identity lookup) against every `recreate=True` list target.
  5. **Reconcile, not recreate, preserved and made explicit** (task hard requirement #3): fields
     and content types are create-if-missing by default; an existing content type's field-link
     hidden-flag drift against the schema is reported in the plan's `detail` text
     (`"... (drift: was ...)"`) rather than silently corrected without being named — proven by
     `test_plan_content_type_detects_hidden_flag_drift_and_reports_not_silently_fixes`; fields no
     longer declared on a content type are explicitly unlinked via
     `ContentTypeDef.unlink_fields`, mirroring the source's explicit
     `Unlink-FieldFromContentTypeSafe` calls for `Appearance_Description`/`Full_URL`. Lists are
     untouched unless explicitly declared `recreate=True` — the source always deleted its full 52-
     list inventory unconditionally; this plugin narrows that to an explicit per-list opt-in.
  6. **The calculated-column XML-construction technique preserved and generalised, with escaping
     verified and hardened** (task hard requirement #4): `build_calculated_field_xml` reproduces
     the source's `Add-PnPFieldFromXml` workaround for the fact that no typed field-creation API
     accepts a formula. The source's escaping was inconsistent across call sites — the field-
     helpers `Lookup`/`User` XML builders escaped only `&` and `"`, while the reset script's
     Calculated-column builder separately escaped `&`/`<`/`>` for the formula and `&`/`"`/`'` for
     the display name, with no escaping applied to `StaticName`/`Name`/`Group` at all (those are
     always internal identifiers in the source, never literal user text, so this was safe in
     context but not defensively correct). The destination applies the full XML attribute-escaping
     set (`&` `<` `>` `"` `'`) to **every** attribute value and the text-escaping subset (`&` `<`
     `>`) to the formula's element-text body, consistently across `build_calculated_field_xml`,
     `build_lookup_field_xml`, and `build_user_field_xml` — verified directly by
     `test_build_calculated_field_xml_escapes_ampersand_lt_gt_in_display_name` and
     `test_build_calculated_field_xml_escapes_formula_body`, which assert the raw unescaped
     characters never survive into the rendered XML.
  7. **Field/tenant-identifier resolution is deliberately left to the caller.** The source's
     `Invoke-FieldsForList` resolved a lookup field's target list id via a live `Get-PnPList` call
     against a `GuidMap`; a `field_id`/`lookup_list_id` in this plugin's XML builders is always a
     caller-supplied value (a real GUID the caller has already resolved via whatever collection
     mechanism it uses) — this module never resolves a `lookup_list_key` to a live id itself, since
     doing so would itself be tenant I/O.
  8. **Honest outcomes** (task hard requirement #6): a plan with nothing to do is `EMPTY`; a plan
     with real changes is `OBSERVED`; a plan carrying a blocking duplicate finding is `FAILED` and
     `list_deletions` for the blocked title is deliberately left empty (not silently populated then
     ignored); an `apply_provisioning` call where some steps succeed and some fail is `PARTIAL`
     with both lists populated; an executor raising `PermissionError` yields `FORBIDDEN`, never a
     generic `FAILED`.
- **Fail-loud verification (task hard requirement #5, second half):** `verify_deletion_complete`
  ports the source's `if (-not $check) { throw "... verification failed ..." }` post-creation
  check (from `New-ListSafe`) generalised to the delete side per the reset script's own Stage 3
  guard ("SKIPPING creation ... Stage 1 deletion did not fully clear it. Investigate before
  re-running.") — it raises `DeletionVerificationFailed` if a caller's fresh post-delete
  observation shows the object still present, rather than assuming a delete call succeeding means
  the object is gone.
- **New neutral fixtures:** every test uses synthetic names (`Demo_Item`, `Demo_List`,
  `Widget_Count`, `Full_Label`) — no real tenant URLs, GUIDs (test GUIDs are placeholder-shaped,
  e.g. `11111111-2222-3333-4444-555555555555`, and live only in `tests/`, which is excluded from
  the genericity scan by the same rationale documented in `sharepoint-link-remediation`'s
  `test_plugin_independence.py`), or CMAT domain concepts.
- **Parity evidence:** the retained behavior per source function is: `New-SiteContentTypeSafe` →
  `plan_content_type`'s `create_content_type` step (create-if-missing, `already_correct` when
  present); `Add-FieldToContentTypeSafe`/`Hide-FieldOnContentTypeSafe`/
  `Show-FieldOnContentTypeSafe` → `plan_content_type`'s `link_field`/`hide_field`/`show_field`
  steps with drift detection; `Unlink-FieldFromContentTypeSafe` → `plan_content_type`'s
  `unlink_field` step, only emitted when the field is actually linked (matching the source's own
  "nothing to do" branch); `Add-ContentTypeToListSafe` → `plan_add_content_type_to_list`;
  `Get-DeployableFields` → `filter_deployable_fields` (verified by
  `test_filter_deployable_fields_*`, covering group/type/Title/hidden/readonly/force-include/
  explicit-exclude, matching every predicate in the source `Where-Object` clause);
  `Repair-FieldType` → `field_needs_type_repair`; the Calculated/Lookup/User raw-XML branches of
  `Add-FieldSafe` → `build_calculated_field_xml`/`build_lookup_field_xml`/`build_user_field_xml`;
  `New-ListSafe`/`New-LibrarySafe` → `plan_provisioning`'s list-creation planning; the reset
  script's Stage 1 duplicate-title check → `detect_duplicate_lists`. Verified by 87 tests total
  (30 field, 10 content-type, 20 list/gate, 27 independence).

## Not extracted, and why

- **`New-ModernCalendarList`, `Set-AppearanceFormLayouts`, `Set-NewButtonContentTypes`** (called by
  the reset script but defined in `plugins/sharepoint-migration/scripts/calendars/
  modern-calendar-lib.ps1`, not read in this pass) — calendar/court-appearance-domain
  provisioning logic, `KEEP_PROJECT_SPECIFIC` per the roadmap's existing disposition for
  `sp-provisioning-modern-calendars`. Not read, not ported.
- **The 52-list CMAT target inventory, `wave-dependency-matrix.json`, `site-columns.json`,
  `Modern_Manual_Appearances.json`/`Modern_Scheduled_Appearances.json` templates** — CMAT-specific
  data files, not a reusable mechanism. `ProvisioningSchema` replaces the *shape* these files
  played (declarative columns/content-types/lists) but ships with zero pre-populated content.
- **The reset script's site-column loop's `Add-PnPField`/`Set-PnPField` calls for non-Calculated
  columns** — folded into the generic `plan_field_action`/`field_needs_type_repair` path rather
  than ported as a separate site-columns-specific function; the source's distinction between
  "site column" and "list column" provisioning is a scope parameter to the caller
  (`FieldDef` with no `ListTitle` vs. one bound to a list), not a separate code path here.
- **`Auth-helpers.ps1`'s `Connect-Spo`** — tenant connection/authentication, explicitly out of
  scope (task hard requirement #2: zero tenant I/O).
- **The reset script's `Write-Log`/`Write-Host` console formatting** — replaced entirely by the
  structured `ProvisioningPlan`/`ProvisioningResult` dataclasses and the `Outcome` vocabulary,
  matching this repo's honest-outcomes convention.

## Independence verification

- `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py --plugin
  sharepoint-provisioning --import-package list_provisioning` → **PASS, 87 tests against the
  wheel-installed package.**
- `test_plugin_independence.py` enforces, as executable gates: no project literal, no source-
  repository marker, no GUID-shaped identifier, every module importing with no third-party
  dependency, no module living only inside a skill directory (hub-and-spoke — moot here since no
  symlinks were created; every skill's only file is a real `SKILL.md`, matching
  `sharepoint-schema`'s and `sharepoint-link-remediation`'s precedent of skills with no bundled
  scripts/references), and zero live PnP/CSOM/network transport calls anywhere in the runtime
  tree.
- No symlink was created for this plugin — none of its three skills reference a shared script or
  reference file from inside the skill directory (each `SKILL.md` is the skill directory's only
  file), the same shape as `sharepoint-schema`'s and `sharepoint-link-remediation`'s skills.
  `symlink_manager.py` was not run because there was nothing to symlink; this plugin adds zero
  entries to `symlinks.json` and zero new broken links by construction.

## Source-repository preservation

No file in either `jag-csb-cmat-sharepoint-online` or its sibling checkouts was modified, moved,
or written to by any write-capable tool during this extraction — read-only inspection only.

## Merge status

**NOT merged to `main`.** Per this repository's per-phase workflow, `main` integration requires
human review and approval; the agent does not merge.
