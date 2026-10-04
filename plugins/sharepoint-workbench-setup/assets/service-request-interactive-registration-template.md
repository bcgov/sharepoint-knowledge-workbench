# Service Request Template — Interactive / Delegated Migration App Registration

Fill in the `< >` placeholders before submitting to your cloud/IT team.

---

**Category:** Consulting Services
**Consulting Topic:** Security
**Who is the Principal Technical Contact?** `<NAME> | <EMAIL>`
**Who is the Principal ONSITE Contact?** `<NAME>`
**Short Description:** PnP PowerShell Schema Provisioning & Content Migration — SharePoint 2016 to SharePoint Online (`<PROJECT_NAME>`)

---

## Request Details

We are requesting approval to run PnP PowerShell scripts to provision schema and
migrate content from SharePoint 2016 to SharePoint Online as part of the
`<PROJECT_NAME>` migration. SharePoint 2016 reaches end of life `<EOL_DATE>`; this
migration is mandatory.

### Users Requiring Permission

- **Primary Technical Lead:** `<TECHNICAL_LEAD_NAME>` (`<USER_ID>`) — primary user of the Migration Account during the project.
- **Business SME:** `<BUSINESS_SME_NAME>` (`<USER_ID>`) — project subject matter expert.
- **Service Account:** `<SERVICE_ACCOUNT>` — neutral migration service account.
- **Vendor user (if applicable):** `<VENDOR_USER_NAME>` (`<USER_ID>`).

### Target Site Collections

**Sandbox:**
- Site Name: `<SANDBOX_SITE_1>`
- Site Name: `<SANDBOX_SITE_2>`

**Main Pipeline:**
- Site Name: `<DEV_SITE_NAME>` (dev)
- Site Name: `<TEST_SITE_NAME>` (test)
- Site Name: `<PROD_SITE_NAME>` (production)

---

## Requested App Registration Configuration

**App Registration Name:** `<APP_REGISTRATION_NAME>`
**Type:** Delegated (interactive browser login with MFA enforced)
**Redirect URI Platform:** Public client/native (mobile & desktop)
**Redirect URI Value:** `http://localhost`

### API Permissions Required (Admin Consent Required)

**Microsoft Graph:**
- `Sites.Selected` (Application)
- `User.Read` (Delegated)

**SharePoint:**
- `Sites.Selected` (Application)

⚠️ **`Sites.Selected` grants zero site access by itself** — it only enables the
per-site grant mechanism below to exist. After admin consent, a SharePoint
Administrator must separately run, once per target site:

```powershell
Grant-PnPAzureADAppSitePermission -AppId "<APP_CLIENT_ID>" -DisplayName "<APP_REGISTRATION_NAME>" `
  -Permissions Write -Site "<SITE_URL>"
```

⚠️ **Empirically validated against production (2026-08-09):** a `write` PnP site
grant, combined with a Site-Collection-Administrator-level signed-in user, was
confirmed sufficient for the full content/schema provisioning surface — list, library,
item, file, page, **site column, and content type** create/delete all succeeded. It
was **not** sufficient for group or permission-management operations (create group,
modify permissions), which remain unverified/likely blocked without Site Collection
Administrator rights specifically. Do not request `Manage` or `FullControl` unless a
specific capability genuinely needs them beyond content/schema provisioning — see
`effective-permissions-matrix.md` in this plugin's references for the full evidence
and the open question of exactly what `write` does *not* cover.

⚠️ **Admin consent is a two-step action:** Adding the permission does not activate it.
"Grant admin consent for `<TENANT_NAME>`" must be **explicitly clicked** in the Entra
portal after the permission is added. Without this step all operations return 403
Access Denied.

⚠️ **A separate Enterprise Application step is also required:** the tenant
administrator must add every named user/service account that will use this
registration under Entra ID → Enterprise applications → this app → Users and groups —
independent of the API-permission consent above. An account missing from this list
can often still sign in successfully and only fail later with a confusing
access-denied error.

---

## Security Boundary Verification

The `write` PnP site grant has been empirically verified to be bounded by the
logged-in user's actual SharePoint site permissions — the app cannot access any site
the user does not already have explicit access to. See
`delegated-permission-boundary-test.md` and `effective-permissions-matrix.md` in this
plugin's references folder for the full evidence, including the open question of
whether this boundary reflects the app's own grant, the user's permissions, or both
together (unresolved as of 2026-08-09 — see the referenced document's "How effective
access is actually calculated" section before treating either explanation as settled).

---

**Who should approve this item?** `<APPROVER_NAME>`
**GL Code:** `<GL_CODE>`
**When do you need this?** `<DATE>`
**Tenant:** `<TENANT_NAME>`

---

## Business Case (if expediting)

This migration is mandatory — SharePoint 2016 reaches end of life `<EOL_DATE>`.
`<PROJECT_NAME>` is a `<DATA_CLASSIFICATION>` system that cannot remain on SharePoint
2016 beyond that date. Schema provisioning and content migration cannot proceed without
this app registration. PnP PowerShell v2.x no longer supports generic interactive
login without a Client ID — this registration is a hard technical prerequisite for
the migration to start. Access will be fully revoked and decommissioned once migration
is verified complete.
