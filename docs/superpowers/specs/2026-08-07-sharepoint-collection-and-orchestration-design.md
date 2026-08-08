# Design — SharePoint Collection Plugin and Configuration Orchestration

> **Planning status:** `DESIGN_ONLY`, `NOT_IMPLEMENTATION_AUTHORIZATION`, `REQUIRES_HUMAN_DECISION`.
> Written 2026-08-07 to close the two architectural seams Phase 9 exposed but deliberately did not
> implement. Nothing here is authorized to build. It exists so the decision can be made against a
> concrete proposal rather than a blank page — the same convention as
> `2026-08-02-multi-document-destination-configuration-design.md`.

## Why this exists

Phase 9 delivered four SharePoint engineering plugins (discovery, schema, link-remediation, page
modernization — 456 tests, all independently installable). Two seams remain, documented in
`docs/architecture/sharepoint-engineering-plugin-set.md`:

1. **Nothing collects the exports** those plugins consume. A human produces them by hand.
2. **No unified configuration entry point.** The four plugins take explicit paths and read none of
   `workbench-setup`'s `config.psd1` / workflow / publication profiles.

Both were left open deliberately — seam 1 because extracting the source's `Connect-PnPOnline`
collectors would have violated every candidate plugin's zero-tenant-I/O contract, seam 2 because
`plugin-architecture-policy.md` §1.3 requires standalone installability. Neither is an oversight,
but together they are why the workbench is not yet turnkey.

---

## Part A — `sharepoint-collection` (new plugin)

### Responsibility

Connect to a live SharePoint tenant **read-only** and produce the export shapes the Phase 9
analysis plugins already consume. Nothing else. It analyses nothing and writes nothing to a tenant.

```text
sharepoint-collection  →  exports on disk  →  sharepoint-discovery
                                              sharepoint-schema
                                              sharepoint-page-modernization
```

### Why a new plugin rather than folding into `sharepoint-discovery`

Per the §8c destination-matching rule, an existing owner is preferred — but every Phase 9 analysis
plugin is **contractually zero-tenant-I/O**, enforced by tests
(`test_no_tenant_connection_or_write_path_exists_in_any_script`). Adding live collection to one of
them would break the property that makes it safe to run unsupervised. Collection has a genuinely
different trust boundary, lifecycle, and failure mode. It earns its own plugin.

### The safety contract (non-negotiable, mirrors `workbench-setup`)

1. **Read-only by construction.** Every cmdlet classified; no write, permission-management, or
   tenant-admin operation may be reachable. A test must prove no write path exists — the same
   pattern `sharepoint-schema` uses to prove the deleted `-Cleanup` capability is absent.
2. **Connector injection, no default connection.** Mirror
   `config_setup.test_connection(connection, connector=...)`: the module ships **no** live PnP/SDK
   transport and raises `NotImplementedError` without an injected connector. Importing the plugin
   must never be capable of touching a tenant.
3. **Honest partial results.** Permission denials produce `FORBIDDEN` on the affected section and
   `PARTIAL` overall — never a truncated export presented as complete. This is the single most
   important requirement: a silently-incomplete export poisons every downstream analysis.
4. **No credentials, tenant URLs, GUIDs, or group identities in committed fixtures.**

### Proposed skills

| Skill | Produces | Consumed by |
|---|---|---|
| `collect-site-structure` | site/web/list inventory | `sharepoint-discovery` |
| `collect-schema-export` | `summary/` + `lists/<n>/` field & content-type JSON | `sharepoint-schema` |
| `collect-page-content` | rendered page HTML + views + web-part content | `sharepoint-page-modernization`, `sharepoint-discovery` |

**Export shapes are already fixed** by what the analysis plugins accept — see their `SKILL.md`
files and `tests/fixtures/`. Those are the contract; collection must match them, not redefine them.

### Source material

`sp-discovering-site-structure`'s backing scripts (`export-sharepoint-inventory.ps1`,
`-custom.ps1`) are the obvious starting point, but carry **147 and 178 project literals** — the
most saturated files in the source. Budget genericization accordingly, or write fresh against the
already-known target shapes, which may well be cheaper. **Recommend evaluating both before
committing to extraction.**

### Open questions for the human

- **Auth model:** device-code (as `workbench-setup`'s `validate-app-registration` uses) only, or
  also app-only? App-only implies a stored secret and a different risk posture.
  **Evidence found 2026-08-07:** a working certificate-based App-Only pattern exists in the source
  repo's `ords-integration-migration` plugin (`scripts/ag-tenant/test-spo-connection-certificate.ps1`
  — 30 lines, zero ORDS/JUSTIN/CEIS references, a plain `Connect-PnPOnline -Thumbprint` call reading
  a cert from `Cert:\CurrentUser\My`). Not extracted — it is live-tenant I/O, out of scope for
  every currently-built plugin, and Part A itself is not authorized to build. Recorded here as a
  real precedent for whichever auth model is chosen, not as a recommendation for either.
- **Does this need Phase 3's exit gate?** Probably not — it is read-only and touches no publication
  contract — but confirm rather than assume.

---

## Part B — Configuration orchestration

> **Status: IMPLEMENTED.** The `resolve-workbench-paths` skill and
> `plugins/workbench-setup/scripts/path_resolution.py` now exist, following exactly the
> "Recommended shape" and "What this deliberately does NOT do" sections below (print-don't-execute,
> no dependency added to `workbench-setup`, no execution). See
> `plugins/workbench-setup/skills/resolve-workbench-paths/SKILL.md` and
> `docs/architecture/sharepoint-engineering-plugin-set.md`'s Seam 2 entry. Part A below remains
> unimplemented and `REQUIRES_HUMAN_DECISION`.

### The constraint that shapes the answer

Plugins must **not** read a shared config themselves; that would break standalone installability
(§1.3), which all four currently satisfy and which is verified per plugin by
`isolated_install_check.py`. So the resolution layer must sit **above** the plugins and pass
explicit paths **down** — never the reverse.

```text
config.psd1  +  document-workflows/<Id>.workflow.psd1  +  publication-profiles/<Id>.publication.psd1
        │
        ▼
  [ orchestration layer ]  ← resolves config into explicit paths/parameters
        │
        ▼
  plugin CLIs, invoked with explicit --paths (unchanged, still standalone)
```

### Recommended shape: a skill in `workbench-setup`, not a new plugin

`workbench-setup` already owns exactly this responsibility — it generates all three config
artifacts and validates them. A `resolve-workbench-paths` skill there would:

- read the connection config, workflow, and publication profile for a given `DocumentId`;
- resolve them into a concrete, printable set of paths and parameters for each downstream plugin;
- **validate that the referenced paths exist**, reporting `UNAVAILABLE` honestly if not;
- **print the resolved invocations rather than executing them** — at least initially.

Print-don't-execute keeps the layer inspectable, keeps `workbench-setup` free of any dependency on
the four plugins (preserving *its* standalone installability), and makes the resolution logic
testable without running anything. Execution can be added later if it proves warranted; it should
not be assumed up front.

### What this deliberately does NOT do

- It does not make any plugin depend on `workbench-setup`.
- It does not introduce a shared runtime config object imported across plugins.
- It does not become a general workflow engine. If it starts growing conditional orchestration
  logic, that is the signal it has outgrown this design and needs its own review.

### Open questions for the human

- Should the profile model extend to non-document work? The current
  `document-workflows/<DocumentId>` model is document-centric, but site *migration* is
  site-centric. A `site-profiles/<SiteId>` sibling may be the right shape — this interacts with
  `2026-08-02-multi-document-destination-configuration-design.md` and should be decided with it,
  not separately.
- Print-only, or eventually execute?

---

## Sequencing recommendation

**Part A before Part B.** Orchestration over a pipeline whose first stage does not exist would be
resolving paths to inputs nobody can produce. Collection is also the higher-value half: it is the
rank-1 gap, and every analysis plugin is currently gated behind manual export work.

## Explicit non-authorization

This document authorizes nothing. Both parts need: human approval of the safety contract (Part A
especially), a decision on the open questions above, `superpowers:brainstorming` before
implementation per the repo's Mandatory Planning Protocol, and their own branch/worktree.
