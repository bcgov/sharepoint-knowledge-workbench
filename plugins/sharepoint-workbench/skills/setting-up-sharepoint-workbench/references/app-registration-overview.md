# SharePoint Online Trial / Sandbox — App Registration Testing & Verification Plan

## Purpose

This document is a test-plan structure for empirically verifying app
registration configurations in a trial or sandbox tenant **before**
submitting formal app registration requests to a cloud/IT team — covering
the two auth models this skill validates:

1. **App-Only integration** (unattended job, certificate-based auth, no MFA).
2. **Interactive/Delegated migration** (human operator, MFA enforced).

Use `validate_app_registration` (device-code flow) for Scenario 2 and the
service-request templates in `assets/` once either scenario's manual
verification below has passed.

---

## Scenario 1: Unattended App-Only integration

**Goal:** Verify that a certificate-authenticated Service Principal with
`Sites.Selected` (Application) permissions can successfully write to a
target site.

**Steps:**

1. **Create the app registration.** Under *Certificates & secrets*, upload
   a public certificate (`.cer`). Generate a self-signed cert locally for
   testing.
2. **Grant API permissions (admin consent).** Add Microsoft Graph →
   Application Permissions → `Sites.Selected`, and SharePoint → Application
   Permissions → `Sites.Selected`. Grant admin consent for both.
   ⚠️ SharePoint `Sites.Selected` (Application) requires a **separate**
   admin consent action by the SharePoint Administrator — Global Admin
   consent alone does not cover the SharePoint row.
3. **Provision a test site collection.**
4. **Apply a site-level write grant** to the app registration on that site.
5. **Execute a write against the target site** using certificate-based
   auth and confirm it succeeds.
6. **Verify attribution** — confirm items show as created by the app
   registration, not a human identity.

## Scenario 2: Interactive/Delegated migration permissions

**Goal:** Verify delegated auth behaves as expected for schema and content
operations, and that the permission boundary holds (see
`delegated-permission-boundary-test.md`).

**Steps:**

1. **Verify SCA requirement for schema changes.** Connect as a user with
   only Contribute access and attempt to create a site column/content
   type — expect Access Denied. Elevate the user to Site Collection
   Administrator and retry — expect success.
2. **Run the permission-boundary test** (`delegated-permission-boundary-test.md`)
   against one authorized and one unauthorized site with the same
   registration.
3. **Confirm audit attribution** shows the expected identity (a neutral
   service account, not a personal admin account, is recommended for any
   production migration/integration app).

---

## Output / next steps

Once both scenarios pass, use the empirical results as evidence when
requesting production app registrations from a cloud/IT team — see the
service-request templates in this skill's `assets/` folder.
