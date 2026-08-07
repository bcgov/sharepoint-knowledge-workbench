# Phase 9 Provenance Record — First Milestone Extraction

**Scope of this record:** the two skills identified in
`docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8c/§8d as
`PHASE_9_EXTRACT_TO_EXISTING_PLUGIN` / `PHASE_9_MERGE_WITH_EXISTING_SKILL` — `sp-uploading-content`
and `sp-validating-app-registration`. Fields follow spec §8b. No other CMAT capability was
extracted in this pass; the remaining 32 skills retain their existing §8d classification.

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

## Independence verification (both records)

- No import, symlink, or path reference to the CMAT repository exists in either destination
  module, test file, or SKILL.md.
- Neither module depends on ORDS configuration, CMAT schemas, or BC Government URLs/GUIDs.
- Both plugins (`sharepoint-content-publication`, `workbench-setup`) install and test standalone
  (`pip install -e plugins/<name>`, `python -m pytest tests/`) with the CMAT repository absent from
  the environment — confirmed by running both suites from this worktree, which has no dependency on
  the CMAT checkout at any path.

## Source-repository preservation

- No file in `/Users/richardfremmerlid/Projects/jag-csb-cmat-sharepoint-online` was read via any
  write-capable tool, moved, or modified during this extraction — read-only inspection only
  (`find`, `cat`, `readlink`/`ls -la` for symlink resolution).

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
