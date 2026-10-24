# Effective SharePoint Permissions Matrix — Site User Roles × Entra App Permissions × PnP Grant Tiers

## Contents

- [The three axes](#the-three-axes)
- [The vocabulary mismatch](#️-the-vocabulary-mismatch-dont-conflate-these)
- [How effective access is actually calculated](#how-effective-access-is-actually-calculated-microsofts-own-documented-model)
- [What this workbench has observed vs. still doesn't know](#what-this-workbench-has-actually-observed-vs-still-doesnt-know)
- [Practical checklist](#practical-checklist-when-an-operation-unexpectedly-succeeds-or-fails)

Synthesizes everything this plugin has learned (and unlearned) about what actually determines
whether a PnP operation succeeds against a SharePoint site, across the three independent axes
that all interact: **who the site itself says can do what**, **what the app registration is
allowed to ask for**, and **what the PnP-level site grant records**. Reading only one of these
axes and assuming it's the whole story is exactly the mistake this plugin made twice already
(see `app_registration_request.py`'s `capability_testing_status` correction history) — this
document exists so a future reader doesn't make it a third time.

## The three axes

### 1. SharePoint site-level user permissions

Independent of any app registration — these are the classic SharePoint permission levels a
*person* (or a service account acting as a person, in a delegated flow) holds on a site:

| Level | Can do |
|---|---|
| Visitor / Read | View pages, list items, documents |
| Member / Contribute / Edit | Add, edit, delete items and documents in existing lists/libraries |
| Design | Contribute, plus create/edit lists, libraries, views, and site pages |
| Full Control / Owner | Everything, including changing site structure and managing permissions |
| **Site Collection Administrator (SCA)** | A separate flag, not a permission-level rung — grants full control across the *entire site collection* plus SharePoint-admin-only operations (e.g. some group/permission management APIs, per `delegated-permission-boundary-test.md` and the interactive test-suite's finding that group CRUD required SCA specifically, not just a high permission level). |

### 2. Entra/Graph app API permissions (`Sites.Selected`)

What the **app registration itself** is allowed to request, configured in Entra's API
permissions blade. Two independent sub-questions:

- **Permission type**: `Application` (app-only, e.g. certificate auth, no user context) or
  `Delegated` (acts on behalf of a signed-in user). This workbench's two registrations both show
  `Sites.Selected` as **Application** type in production — confirmed via live Entra screenshots,
  even though the interactive registration is used via a delegated/interactive sign-in flow. See
  `graph-selected-permissions-overview-summary.md` for the four `.Selected` scopes and their
  official role definitions.
- **Role**, once granted per-site: `read` / `write` / `owner` / `fullcontrol` (Graph API
  vocabulary) — **not the same words PnP uses**, see the vocabulary table below.

### 3. PnP-level site grant (`Grant-PnPAzureADAppSitePermission`)

A **separate control plane from Entra's API-permissions blade** — Entra's `Sites.Selected`
permission only enables this mechanism to exist; it grants no site access on its own. This is
where an app is actually pointed at specific sites, using PnP's own tier vocabulary:

| PnP `-Permissions` value | Presumed Graph equivalent |
|---|---|
| `Read` | `read` |
| `Write` | `write` |
| `Manage` | `owner` (not confirmed identical by any source read so far — see below) |
| `FullControl` | `fullcontrol` |

**Read via `Get-PnPAzureADAppSitePermission -Site <url>` — requires elevated (SharePoint Admin
or Global Admin) rights to even query; an ordinary account, even one with strong site-level
permissions, gets `403 Forbidden` trying to read it** (confirmed empirically in this workbench's
own testing).

## ⚠️ The vocabulary mismatch (don't conflate these)

| | Read | Write | Manage / Owner | FullControl |
|---|---|---|---|---|
| **Graph API** (`POST /sites/{id}/permissions` `roles`) | `read` | `write` | `owner` | `fullcontrol` |
| **PnP PowerShell** (`-Permissions`) | `Read` | `Write` | `Manage` | `FullControl` |
| **Classic SharePoint permission level** (site *user* roles, axis 1) | Visitor/Read | Member/Contribute | Design or Full Control | Full Control |

Three different vocabularies for adjacent-but-not-identical concepts, easy to conflate when
skimming a status report. Always note *which axis and which vocabulary* a given "write" or
"manage" claim is using before comparing it to another claim.

## How effective access is actually calculated (Microsoft's own documented model)

For a **delegated** (interactive) session specifically — confirmed verbatim in
`graph-selected-permissions-overview-summary.md`, sourced from Microsoft's own Graph
documentation:

> "the application can never exceed the user's permissions, and the user can never exceed
> (through the application) the consented application permissions."

I.e. effective access ≈ `min(app's PnP/Graph grant, signed-in user's own site permission)` — a
true intersection, not "whichever is more generous wins" and not "the app grant is irrelevant
once a user is present."

**What this workbench's tests actually disprove: the assumption that `write` blocks list/library
creation. They do NOT disprove the intersection model itself.** That distinction matters and was
initially blurred in this document — the assumption "app grant = write, therefore list creation
should fail regardless of user permission" only holds if `write` genuinely means "item/file CRUD
only." Microsoft's current documentation does not define `write` that narrowly — it defines
`write` as "read and modify the metadata and contents of the resource," and `manage` as that plus
"manage the site." A stored `write` grant, an elevated (SCA-level) signed-in user, and observed
list/library/page creation are all simultaneously consistent with the intersection model *if*
`write` itself already covers those content-container operations. **The failed assumption was
about what `write` permits, not about whether the intersection model holds.**

One footnote the above doesn't fully resolve: the intersection model as documented by Microsoft
is specifically about Graph token enforcement, while `Connect-PnPOnline -Interactive` requests a
SharePoint-resource token via a different, older OAuth path, and this app's `Sites.Selected`
permission is Application-type only (confirmed via Entra screenshots — no Delegated-type
SharePoint permission exists on it). Whether that resource-token path even consults an
Application-type Graph permission at all is a secondary, still-open technical question — but it
should not be weighted equally against the better-evidenced conclusion above; it's a minor
addendum, not a competing primary explanation.

### What would actually disprove the intersection model (not yet run)

Three controlled tests, none of which this workbench has performed yet:

- **Test A — high app grant, low/no user rights.** Grant the app `Write` or `Manage`; sign in as
  a user with no access to the site. If list/library creation still succeeds, the app is
  bypassing the user side of the intersection. (This workbench's earlier
  `delegated-permission-boundary-test.md` is adjacent but not equivalent evidence — it showed
  `Get-PnPWeb` correctly failing against a site the signed-in user had no access to, which is
  consistent with the intersection model, but doesn't isolate operation-tier granularity the way
  Test A would.)
- **Test B — low app grant, high user rights.** Grant the app only `Read`; sign in as a
  Site-Collection-Administrator-level user. If list creation still succeeds, the app grant is not
  constraining the user, and the intersection model doesn't hold as documented for this auth
  path.
- **Test C — same user, same site, vary only the app grant.** Run the same capability matrix
  (list, library, item, file, page) once per PnP tier (`Read`, `Write`, `Manage`, `FullControl`)
  against the same site and signed-in user. This isolates exactly which operations the app grant
  actually gates, independent of the user-permission variable.

Until one of these runs, **the honest, defensible conclusion is: `Sites.Selected` `write` is
broader than this workbench originally assumed, at least for the tested interactive PnP path; the
boundary between `write` and `manage` remains unresolved and should be probed through permission/
site-administration operations (group creation, role assignment, permission management — per
`manage`'s documented "and to manage the site" delta), not list/library/page creation.**

For an **application-only** (certificate) session, axis 1 doesn't apply at all — there is no
signed-in user; effective access is axis 3 (the PnP/Graph grant) alone, unambiguously (Test C's
premise, minus the need to vary a user). This is exactly why the ETL app's own boundary remains
unverified, and why a certificate-mode probe of either app is valuable regardless of which
explanation above is correct.

## What this workbench has actually observed vs. still doesn't know

| Operation | ETL app (App-Only, `Write` requested) | Interactive app (delegated, `write` confirmed via `Get-PnPAzureADAppSitePermission`) |
|---|---|---|
| Connect | ✅ tested, PASS (as service principal) | ✅ tested, PASS (as signed-in user), across test sites |
| Read stored PnP grant role | not attempted | ❌ `403 Forbidden` under the signed-in test account; a tenant admin *could* read it |
| Item CRUD | not yet tested with cert auth | ✅ PASS, both sites |
| Page create/delete | not yet tested with cert auth | ✅ PASS, both sites |
| **List create/delete** | not yet tested with cert auth | ✅ PASS, both sites — the finding that disproved this plugin's earlier Write-excludes-structure assumption |
| **Document library create + file upload/delete** | not yet tested with cert auth | ✅ PASS, both sites |
| **Site column (field) create/delete** | not yet tested with cert auth | ✅ PASS, both sites — confirmed 2026-08-09, previously untested; a business-case claim citing this as "covered" before this test would have been an overclaim |
| **Content type create/delete** | not yet tested with cert auth | ✅ PASS, both sites — confirmed 2026-08-09, same caveat |
| Group create/membership/delete | not yet tested with cert auth | ❌ observed blocked in earlier trial-tenant testing (unverified against production) — requires SCA specifically, by design |

**Current state (2026-08-09): every content/schema-provisioning operation this workbench's
`sharepoint-site-build-and-publish` plugin actually needs (lists, libraries, items, files, pages, site
columns, content types) has now been empirically confirmed PASS for the interactive app on both
tested production sites.** Group/permission-management operations remain the one category
observed blocked (trial-tenant testing only, not yet re-confirmed against production).

**The ETL app's own boundary is still genuinely unverified** — every "not yet tested with cert
auth" row above is real, open work, not an oversight. Run
`test-pnp-effective-capability-probe.ps1 -AuthMode Certificate` with the ETL app's own
`ClientId`/thumbprint to fill in that column before trusting any specific claim about what it can
or cannot do. An interactive-session result never validates a certificate-based registration's
boundary — they're different tokens, different axis-1 applicability, evaluated independently.

## Practical checklist when an operation unexpectedly succeeds or fails

1. **Which axis is actually being tested?** Delegated session → all three axes apply
   (intersected). Application-only session → axis 3 alone.
2. **Which vocabulary is a "write"/"manage" claim using** — Graph, PnP, or classic SharePoint
   permission-level language? They are not interchangeable words for the same thing.
3. **Does the signed-in account (if any) have elevated site rights independent of the app** —
   Owner, Design, or especially SCA? A high user grant can never *raise* the effective ceiling
   above the app's own PnP/Graph grant (the intersection model rules that out explicitly) — so if
   an operation succeeds, the app's own grant must genuinely permit it, even if that's broader
   than you assumed from its nominal tier label. A high user grant paired with a *low* app grant
   will still fail; don't mistake user permission alone as sufficient explanation for a pass.
4. **Was the PnP grant tier actually read, or assumed?** A stored grant claim from a tenant admin
   (`Get-PnPAzureADAppSitePermission`) is ground truth; an assumption based on what was
   originally requested in a JIRA ticket is not — grants can be changed after the fact without
   the original request record being updated.
5. **Don't infer a tier from a single capability test.** Use
   `test-pnp-effective-capability-probe.ps1` for a fuller sweep (list, library, item, file, page)
   and report the stored grant role and observed capabilities as two separate results, per the
   design already built into that script.
6. **A single positive capability test disproves an operation-mapping assumption ("this tier
   blocks X"), not the intersection model itself.** To actually test the intersection model,
   run one of Test A/B/C above — varying user rights against a fixed app grant, or vice versa —
   not just a single combination of both.
