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
