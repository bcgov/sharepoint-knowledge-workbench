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

- **Primary Technical Lead:** `<TECHNICAL_LEAD_NAME>` (`IDIR:<IDIR_ID>`) — primary CSB user of the Migration Account during the project.
- **Business SME:** `<BUSINESS_SME_NAME>` (`IDIR:<IDIR_ID>`) — project subject matter expert.
- **Service Account:** `<SERVICE_ACCOUNT>` — neutral migration service account.
- **Vendor/NTT User (if applicable):** `<VENDOR_USER_NAME>` (`IDIR:<IDIR_ID>`).

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
**Type:** Delegated (interactive IDIR browser login with MFA enforced)
**Redirect URI Platform:** Public client/native (mobile & desktop)
**Redirect URI Value:** `http://localhost`

### API Permissions Required (Delegated — Admin Consent Required)

**Microsoft Graph:**
- `User.Read` (Delegated)

**SharePoint:**
- `AllSites.Manage` (Delegated)

⚠️ **Empirically validated:** `AllSites.Read` is insufficient — connect succeeds but
all write and provisioning operations are blocked. `AllSites.Manage` is the confirmed
minimum for all interactive migration operations including list item write, page
creation, list creation, and page deletion.

⚠️ **Admin consent is a two-step action:** Adding the permission does not activate it.
"Grant admin consent for `<TENANT_NAME>`" must be **explicitly clicked** in the Entra
portal after the permission is added. Without this step all operations return 403
Access Denied.

---

## Security Boundary Verification

`AllSites.Manage` (Delegated) has been empirically verified to be bounded by the
logged-in user's actual SharePoint site permissions. The app cannot access any site
the user does not already have explicit access to. See
`delegated-permission-boundary-test.md` in this references folder for the full proof.

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
