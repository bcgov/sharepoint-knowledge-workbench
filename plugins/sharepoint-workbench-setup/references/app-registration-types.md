# The two app-registration types

## Contents

- [Choosing a type](#choosing-a-type)
- [etl: unattended App-Only, certificate auth](#etl-unattended-app-only-certificate-auth)
- [interactive: human-operator, delegated auth](#interactive-human-operator-delegated-auth)

Read `app-registration-capability-caution.md` before trusting any capability claim here.

## Choosing a type

Two distinct types exist for two distinct purposes. Requesting the wrong one is a real source
of confusing Access Denied errors later.

```python
from app_registration_request import REGISTRATION_TYPES

for t in REGISTRATION_TYPES:
    print(t["key"], "-", t["purpose"])
    print("  capability_testing_status:", t["capability_testing_status"])
```

## etl: unattended App-Only, certificate auth

| | |
|---|---|
| Purpose | Scheduled/unattended jobs (nightly ETL, sync) with no human present |
| Auth | X.509 certificate, no MFA, runs as the app's own service principal |
| Graph / SharePoint permission | `Sites.Selected` (Application) / `Sites.Selected` (Application) |
| PnP site grant tier | `Write` (intended/requested) |
| Licensing | **None**: authenticates as the app itself, not a signed-in user |
| Capability status | **UNVERIFIED against production.** Intended for pure item CRUD against pre-provisioned lists, not structural provisioning, but whether `Write` actually enforces that boundary has not been tested with this app's own certificate. Run the probe in `-AuthMode Certificate` before trusting any specific claim. |

**Pros:** no human/MFA dependency, no licence cost, narrowest tier requested for the job (actual
enforced boundary unverified).
**Cons:** certificate lifecycle is an operational burden (expiry, rotation, secure key storage),
harder to audit "who did this" (every action is attributed to the service principal), and its
actual capability boundary is unproven. Don't assume it's limited to item CRUD just because
that's what was requested.

## interactive: human-operator, delegated auth

| | |
|---|---|
| Purpose | Provisioning/migration work by a person (or service account acting on a person's behalf) |
| Auth | Interactive sign-in (browser or device code), MFA on every session, no certificate |
| Graph / SharePoint permission | `Sites.Selected` (Application) + `User.Read` (Delegated) / `Sites.Selected` (Application) |
| PnP site grant tier | `write`, confirmed by a tenant administrator via `Get-PnPAzureADAppSitePermission` against production |
| Licensing | M365 E3 or E5 required for whichever account signs in |
| Capability status | **Corrected 2026-08-09.** Observed in production on tested target sites: list/library/page creation, item and file CRUD, **and site-column and content-type creation** all succeeded, covering every content/schema-provisioning operation `sharepoint-site-build-and-publish` needs, despite the stored grant being `write`, not `manage`. Group/permission-management operations remain the one category still observed blocked (trial-tenant testing only, unverified against production). This doesn't prove `write` is broader than documented; it may mean the signed-in user's own permissions are doing the work, not the app's grant. See `effective-permissions-matrix.md`'s Test A/B/C for how to disambiguate. |

**Same Entra-level API permission as the ETL type.** Confirmed on a real production tenant: both
registrations show `Sites.Selected` (Application). The two types differ by auth mechanism, not
by Entra permission.

**Group operations (create/membership/delete) were observed blocked** in earlier trial-tenant
testing and treated as a deliberate design decision (site permission groups managed manually by
admins) rather than a permission gap. That finding predates the write-vs-capability correction
and has not been re-verified against production. Treat as plausible, not confirmed.

**Pros:** in production, interactive sessions with this registration have performed the full
provisioning/migration surface (whether that's the app's own grant or the signed-in user's
permissions is unresolved); delegated auth means effective access is at most the signed-in
user's own SharePoint permissions, so the app can never exceed what the user could already do.
**Cons:** every operation needs a human plus MFA (not for unattended jobs), recurring
per-account licence cost, and the stored grant role does not reliably predict what the app can
actually do. Don't rely on the Entra/PnP-recorded tier alone.
