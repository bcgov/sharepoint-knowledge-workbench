# Service Request Template — App-Only ETL App Registration

Fill in the `< >` placeholders before submitting to your cloud/IT team.

---

**Category:** Consulting Services
**Consulting Topic:** Security
**Who is the Principal Technical Contact?** `<NAME> | <EMAIL>`
**Who is the Principal ONSITE Contact?** `<NAME>`
**Short Description:** App-Only Azure App Registration for Nightly ETL Integration – `<PROJECT_NAME>` SharePoint Online

---

## Request Details

We are requesting the creation of an App-Only Azure App Registration to support an
unattended nightly ETL integration job as part of the `<PROJECT_NAME>` migration to
SharePoint Online.

`<PROJECT_NAME>` is a `<DATA_CLASSIFICATION>` system. SharePoint 2016 reaches end of
life `<EOL_DATE>`; this migration is mandatory.

The project includes a nightly integration job that reads data from `<SOURCE_SYSTEM>`
and writes it directly to SharePoint Online lists. This job runs unattended on a
scheduled basis (no human operator). Because no user is present to satisfy MFA, this
job must use App-Only certificate-based authentication — interactive/delegated auth
cannot be used for unattended processes.

This registration is permanent — it must remain active at go-live and continue
operating as a production integration.

---

## Requested App Registration Configuration

**App Registration Name:** `<APP_REGISTRATION_NAME_ETL>`
**Type:** App-Only (Service Principal / Application permissions)
**Authentication:** X.509 certificate (no client secret, no user account, no MFA prompt)
**Redirect URI:** None required
**M365 licence required:** No — App-Only service principals do not require a user licence

### API Permissions Required (Application — Admin Consent Required)

**Microsoft Graph:**
- `Sites.Selected` (Application)

**SharePoint:**
- `Sites.Selected` (Application)

⚠️ **Important:** SharePoint `Sites.Selected` (Application) requires a **separate**
admin consent action by the SharePoint Administrator. Global Admin consent alone does
NOT cover the SharePoint row. Both consent actions must be completed before site-level
grants can be applied.

### Site-Level Grants

`Sites.Selected` does not grant access to any site by itself. After both admin consent
actions are complete, the SharePoint Admin must apply explicit site-level Write grants
per site collection:

```powershell
Grant-PnPAzureADAppSitePermission -AppId <CLIENT_ID> -Permissions Write -Site <SITE_URL>
```

**Initial sites requiring grants:**
- `<SITE_NAME_1>` (sandbox)
- `<SITE_NAME_2>` (dev)
- `<SITE_NAME_3>` (test)
- `<SITE_NAME_4>` (production)

Write (Contribute) permission = read, write, and delete list items. No provisioning
capability granted or requested.

---

**Who should approve this item?** `<APPROVER_NAME>`
**GL Code:** `<GL_CODE>`
**When do you need this?** `<DATE>`
**Tenant:** `<TENANT_NAME>`

---

## Business Case (required only if expediting)

This migration is mandatory — SharePoint 2016 reaches end of life `<EOL_DATE>`. The
nightly `<SOURCE_SYSTEM>` ETL integration is a non-negotiable operational requirement
that must continue at go-live on SharePoint Online. The integration runs unattended
and cannot use interactive/delegated auth with MFA. App-Only certificate authentication
is the only technically compliant approach for an unattended scheduled job on a
`<DATA_CLASSIFICATION>` system. Without this registration, the nightly integration
cannot write to SharePoint Online and the operational system cannot go live.
