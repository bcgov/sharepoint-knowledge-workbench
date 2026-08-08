# Delegated Permission Boundary Verification Test

This test plan describes how to empirically prove that a delegated Entra ID
app registration's API permission (e.g. `AllSites.Manage` (Delegated)) is
fully restricted by the executing user's actual SharePoint permissions --
not a broader grant across the tenant.

**Security boundary rule:** Effective permissions = App permissions ∩ User permissions.

---

## Objective

Empirically prove that:

1. A delegated app registration only acts as a proxy for the logged-in
   user. It does not grant additional permissions to sites the user does
   not already have access to.
2. It does not grant access to all sites in the tenant.
3. If the logged-in user lacks permissions on a site collection, access is
   immediately blocked with `Access Denied` / `Unauthorized Operation`.

## Test setup

1. **Target app registration:** `<APP_REGISTRATION_NAME>`, Client ID
   `<CLIENT_ID>`, configured with the delegated API scope under test.
2. **User identity:** `<SERVICE_ACCOUNT>@<TENANT>.onmicrosoft.com`.
3. **Site A (authorized — target):** `https://<TENANT>.sharepoint.com/sites/<AUTHORIZED_SITE>`
   — user has permissions on this site.
4. **Site B (unauthorized — boundary test):** `https://<TENANT>.sharepoint.com/sites/<UNAUTHORIZED_SITE>`
   — user has no access to this site.

## Running the test through this skill

`validate_permission_boundary(authorized_connection, unauthorized_connection, http_client)`
(in `app_registration_validation.py`) runs both halves of this test in one
call: it validates the same app registration against both connection dicts
(same `ClientId`/`TenantId`, different `SiteUrl`) and reports a
`PermissionBoundaryResult` that is only `boundary_proven=True` when the
authorized site succeeds AND the unauthorized site is denied. Either sub-
result alone is insufficient — see the module docstring for why an
unexpectedly-successful unauthorized site is reported as a security
finding, not a passing test.

```python
from app_registration_validation import validate_permission_boundary

result = validate_permission_boundary(authorized_connection, unauthorized_connection, http_client)
print(result.boundary_proven, result.detail)
```

Zero tenant I/O ships in this module — `http_client` must be injected by
the caller, same contract as `validate_app_registration`.

## Key takeaway for tenant admins

- A delegated scope does not grant the app access to every site in the
  tenant. The user's own site permissions are the authoritative gate.
- The security boundary is the logged-in user's identity, not the app
  registration's API permissions.
- Admin consent must be explicitly granted in the Entra portal after adding
  the permission — adding without consent leaves it inactive (all
  operations return 403, which looks identical to a real boundary denial;
  do not mistake missing consent for a proven boundary).
