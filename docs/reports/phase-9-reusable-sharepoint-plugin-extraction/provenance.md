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
