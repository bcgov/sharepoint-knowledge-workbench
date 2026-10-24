"""Purpose:
    Render generic app-registration service requests and provide registration setup guidance.

Key Input Dependencies:
    - Caller-provided request template text and answer mapping; no tenant config or network client.

app_registration_request.py
==============================

Guides the pre-work needed before any SharePoint use case that connects
to a live tenant: what to request from your tenant administrator, and
what to configure once an app registration is granted. Generalized from
a real project's app-registration JIRA requests, CLAUDE.md architecture
notes, and side-by-side empirical test-suite results for both
registration types described below -- no tenant-specific literal
(organization name, GUID, site URL) appears anywhere in this module; see
`assets/service-request-*-template.md` for the fill-in-the-blanks
request documents this module renders.

Three exports:

1. `render_service_request(template_text, answers)` -- fills a service-
   request template's `<PLACEHOLDER>` tokens from a caller-supplied
   answers dict. Pure string templating, no I/O. Raises
   `AppRegistrationRequestError` if the template references a
   placeholder the caller didn't supply an answer for -- never silently
   leaves a `<PLACEHOLDER>` token in a document meant to be submitted.
2. `REGISTRATION_TYPES` -- **two distinct app-registration types exist
   for two distinct purposes; do not conflate them.** An unattended
   App-Only/certificate registration for scheduled jobs, and an
   interactive/delegated registration for human-operator migration and
   provisioning work. Each has its own auth mechanism, permission model,
   and licensing requirement.

   **CAUTION on tier boundaries (corrected 2026-08-09, see
   `capability_testing_status` per type below):** an earlier version of
   this module claimed the PnP site-grant tier (`Write` vs `Manage`)
   determined whether list/library creation was allowed -- Write
   blocking it, Manage allowing it. **Production testing disproved
   this.** A tenant administrator confirmed via
   `Get-PnPAzureADAppSitePermission` that the interactive registration's
   stored grant role is `write` on the tested sites, yet an interactive
   session using that same registration successfully created and
   removed lists, document libraries, pages, items, and files. Two
   reasons this is plausible, not yet fully disambiguated: (a)
   Microsoft's current Sites.Selected documentation defines `write` as
   "read and modify metadata and contents of the resource" and does not
   itself document list/library creation as excluded -- the stricter
   Write-excludes-structure mapping came from older, possibly outdated
   or context-specific community guidance, not Microsoft's own current
   model; (b) for delegated/interactive sessions specifically,
   Microsoft's documented model is that effective access is the
   INTERSECTION of the app's consented permission and the signed-in
   user's own SharePoint permission on the site -- if the signed-in user
   already holds elevated rights independent of the app's grant, that
   can produce capabilities the app's own stored grant doesn't actually
   confer. **Do not treat the PnP grant tier alone as a reliable
   predictor of what operations will succeed** -- use
   `test-pnp-effective-capability-probe.ps1` (step 8 below) to observe
   actual behavior instead of inferring it. **This module and that
   script do not test or disprove Microsoft's delegated-access
   intersection model -- they test effective capabilities under the
   current auth mode.** A successful operation means the app grant and
   the current user context together allowed it; it does not mean the
   stored app role is any particular tier. What the evidence above
   disproves is this module's own operation-mapping assumption (that
   `write` blocks structural creation), not Microsoft's intersection
   model itself -- see `references/effective-permissions-matrix.md`'s
   "How effective access is actually calculated" section for the full
   reasoning and the controlled tests that would actually probe the
   model.
3. `SETUP_STEPS` -- the generalized sequence for configuring a
   registration once your tenant administrator creates one, covering
   **two separate control planes** that are easy to conflate but both
   required: (a) Entra ID -- API permissions, admin consent, and
   assigning users/service accounts to the Enterprise Application entry
   (delegated/interactive registrations only -- an App-Only certificate
   flow has no signed-in user for this to apply to); and (b) SharePoint
   itself, configured separately via PnP PowerShell
   (`Grant-PnPAzureADAppSitePermission`) -- Entra grants the app the
   *capability* to have site-scoped permissions at all, this command
   grants *which* sites and at what nominal level, though (per the
   caution above) the nominal level is not a reliable predictor of
   actual behavior for delegated sessions.

Function Index:
    - AppRegistrationRequestError
    - render_service_request
    - render_service_request._substitute
"""
from __future__ import annotations

import re


class AppRegistrationRequestError(Exception):
    """Raised when a service-request template references a placeholder
    with no supplied answer -- distinct from a rendering bug, this is an
    honest "you're missing information" signal, never a silently
    incomplete request document."""


_PLACEHOLDER_PATTERN = re.compile(r"<([A-Z0-9_]+)>")


def render_service_request(template_text: str, answers: dict) -> str:
    """Fill every `<PLACEHOLDER>` token in `template_text` from `answers`
    (keys matching the placeholder name, without angle brackets). Pure --
    no I/O, no file reads. Raises `AppRegistrationRequestError` naming
    every placeholder missing an answer, rather than rendering a
    document with unfilled `<PLACEHOLDER>` tokens still in it."""
    placeholders = set(_PLACEHOLDER_PATTERN.findall(template_text))
    missing = sorted(p for p in placeholders if p not in answers)
    if missing:
        raise AppRegistrationRequestError(
            f"template references placeholder(s) with no supplied answer: {', '.join(missing)}"
        )

    # Replace each known placeholder in the request template and reject missing answers.
    def _substitute(match: "re.Match") -> str:
        """Replace each known placeholder in the request template and reject missing answers."""
        return str(answers[match.group(1)])

    return _PLACEHOLDER_PATTERN.sub(_substitute, template_text)


REGISTRATION_TYPES = [
    {
        "key": "etl",
        "name_pattern": "e.g. <org>.etl.integration",
        "purpose": (
            "Unattended, scheduled jobs (nightly ETL, sync processes) that write "
            "to SharePoint without a human present. No interactive sign-in, no "
            "MFA -- runs as the app's own service-principal identity."
        ),
        "auth_mechanism": "X.509 certificate (App-Only), thumbprint-based, no client secret in plaintext.",
        "graph_permission": "Sites.Selected (Application)",
        "sharepoint_permission": "Sites.Selected (Application)",
        "pnp_grant_tier": "Write (intended/requested) -- NOT YET EMPIRICALLY VERIFIED against production",
        "licensing_note": (
            "No M365 user licence required -- the app authenticates as itself "
            "(service principal), not as a signed-in user. Enterprise "
            "Application 'Users and groups' assignment does not apply to this "
            "flow either, for the same reason: there is no signed-in identity "
            "for that assignment to gate."
        ),
        "capability_testing_status": (
            "UNVERIFIED against production. An earlier trial-tenant test suite "
            "reported list creation blocked under Write, but that same "
            "Write-excludes-structure assumption has since been disproven for "
            "the interactive registration (see the interactive type's entry) "
            "-- so this ETL app's actual boundary must be re-tested with its "
            "own certificate before trusting any specific claim about what it "
            "can or cannot do. Use "
            "test-pnp-effective-capability-probe.ps1 -AuthMode Certificate "
            "with this app's own ClientId and certificate thumbprint. A "
            "successful interactive-session probe (of the *other* "
            "registration) proves nothing about this one -- Microsoft's "
            "delegated-access model intersects app and user permissions for "
            "interactive sessions, so interactive results never validate an "
            "app-only identity's own boundary."
        ),
        "design_notes": (
            "Intended purpose, per the environment's own request/architecture "
            "notes this was generalized from: pure item CRUD (create/update/"
            "delete list items, read lists/calendars) against pre-provisioned "
            "lists -- not structural provisioning (creating lists, libraries, "
            "pages, content types). Whether the granted Write tier actually "
            "enforces that boundary is unverified -- see "
            "capability_testing_status."
        ),
        "pros": [
            "No human dependency -- runs unattended on a schedule, no MFA prompt to babysit.",
            "No M365 licence cost for the identity -- authenticates as the app itself.",
            "Narrowest permission tier requested for its intended job -- smaller nominal blast radius than the interactive registration if the certificate/thumbprint leaks (actual enforced boundary not yet verified).",
        ],
        "cons": [
            "Cannot provision structure -- a schema/content change still requires the interactive registration or manual admin action.",
            "Certificate lifecycle is an operational burden: expiry tracking, rotation, and secure private-key storage on the job host.",
            "Harder to audit 'who did this' after the fact -- every action is attributed to the service principal, not a named person.",
        ],
    },
    {
        "key": "interactive",
        "name_pattern": "e.g. <org>.interactive",
        "purpose": (
            "Human-operator work: schema/list provisioning, page migration, "
            "content migration, and other PnP PowerShell operations run by a "
            "person (or a service account acting on a person's behalf), "
            "MFA-enforced."
        ),
        "auth_mechanism": "Interactive/delegated sign-in (browser popup or device code), MFA enforced on every session, no certificate.",
        "graph_permission": "Sites.Selected (Application) + User.Read (Delegated)",
        "sharepoint_permission": (
            "Sites.Selected (Application) -- confirmed identical Entra-level permission "
            "type to the ETL registration in a real production tenant; the two "
            "registrations are differentiated by auth mechanism (cert vs. interactive) "
            "and by the PnP site-grant tier (step 6 below), not by a different Entra "
            "permission type. Verify against your own tenant's Entra portal -- an "
            "earlier draft of this module assumed AllSites.Manage (Delegated) here, "
            "based on trial-sandbox-tenant testing that does not match production."
        ),
        "pnp_grant_tier": (
            "write -- per Get-PnPAzureADAppSitePermission, confirmed by a tenant "
            "administrator against production (not Manage, despite earlier drafts "
            "of this module claiming otherwise)"
        ),
        "licensing_note": (
            "Whichever account signs in -- a named user or a dedicated "
            "service account -- requires a standard Microsoft 365 E3 or E5 "
            "licence (subscription), because this flow authenticates as that "
            "signed-in identity, not as the app itself."
        ),
        "capability_testing_status": (
            "CORRECTED 2026-08-09 -- read this before citing any capability "
            "claim for this registration. A tenant administrator confirmed via "
            "Get-PnPAzureADAppSitePermission that this app's stored grant role "
            "on the tested production sites is `write`. An interactive session "
            "using this same app nonetheless succeeded at creating/removing "
            "lists, document libraries, pages, items, files, site columns, and "
            "content types (site columns and content types confirmed "
            "2026-08-09, extending the original finding) -- operations an "
            "earlier version of this module claimed `write` blocks. As of "
            "2026-08-09 every content/schema-provisioning operation this "
            "workbench's sharepoint-site-build-and-publish plugin actually needs has "
            "been confirmed PASS on both tested sites; group/permission-"
            "management operations remain the one category still observed "
            "blocked (trial-tenant testing only, unverified against "
            "production). "
            "**CreateList succeeding is NOT proof of a Manage grant.** What "
            "this disproves is the assumption that `write` blocks list/library "
            "creation -- it does NOT disprove the delegated intersection model "
            "itself (see references/effective-permissions-matrix.md for the "
            "full reasoning). That assumption only held if `write` genuinely "
            "meant 'item/file CRUD only'; Microsoft's current documentation "
            "defines `write` as 'read and modify the metadata and contents of "
            "the resource' -- broader than this module originally assumed. A "
            "stored `write` grant, an elevated signed-in user, and observed "
            "list/library/page creation are all consistent with the "
            "intersection model holding exactly as documented, *if* `write` "
            "itself already covers those operations. One footnote the above "
            "doesn't fully resolve: Microsoft's intersection model is "
            "documented for Graph token enforcement, while "
            "Connect-PnPOnline -Interactive requests a SharePoint-resource "
            "token via a different, older path, and this app's Sites.Selected "
            "permission is Application-type only (confirmed via Entra "
            "screenshots) -- whether that resource-token path even consults "
            "an Application-type grant is a secondary, still-open technical "
            "question, not weighted equally against the better-evidenced "
            "conclusion above. To actually test the intersection model (not "
            "yet done): high app grant + low/no user rights (operation should "
            "still fail if the model holds), low app grant + high user rights "
            "(operation should still fail if the model holds), or the same "
            "user/site with only the app grant varied across all four PnP "
            "tiers. The `write`/`manage` boundary itself remains unresolved -- "
            "per `manage`'s documented 'and to manage the site' delta, the "
            "likelier boundary is permission/site-administration operations "
            "(group creation, role assignment), not content/container "
            "creation -- but this is inference from role definitions, not yet "
            "empirically probed. Also note a vocabulary mismatch: Graph's own "
            "role names are read/write/owner/fullcontrol -- PnP's "
            "-Permissions parameter uses Read/Write/Manage/FullControl. "
            "`Manage` (PnP) and `owner` (Graph) are presumed equivalent but "
            "not confirmed identical by any source read so far. Do not treat "
            "list/library creation as a tier signal for this or any other "
            "registration -- use test-pnp-effective-capability-probe.ps1 to "
            "observe actual behavior, and report the stored grant role and "
            "observed capabilities separately, never conflated, and never as "
            "proof of "
            "which explanation above is correct."
        ),
        "design_notes": (
            "Group creation, membership, and deletion were observed blocked "
            "in trial-tenant testing regardless of PnP tier -- this was a "
            "deliberate design decision (site permission groups are managed "
            "manually by admins, not scripted), not a permission gap. Group "
            "operations require Site Collection Administrator (SCA) "
            "specifically; if group provisioning is ever needed, that "
            "requires a separate registration with SCA rights, not a change "
            "to this one. This finding predates the write-vs-manage "
            "correction above and has not been independently re-verified "
            "against production -- treat as plausible, not confirmed."
        ),
        "pros": [
            "In production, this registration's interactive sessions have been observed performing the full provisioning/migration surface (lists, libraries, pages) -- though whether that's due to the app's own grant or the signed-in user's permissions is unresolved (see capability_testing_status).",
            "Delegated auth means effective access is at most the signed-in user's own SharePoint permissions -- the app can never exceed what the user could already do themselves, regardless of its own grant.",
        ],
        "cons": [
            "Every operation requires a human to sign in and pass MFA -- not suitable for unattended/scheduled jobs.",
            "Requires an M365 E3/E5 licence for whichever account signs in -- a real recurring cost per user or service account.",
            "The stored grant role (write) does not reliably predict what the app can actually do in an interactive session -- don't rely on the Entra/PnP-recorded tier alone; verify functionally.",
        ],
    },
]


SETUP_STEPS = [
    {
        "number": 1,
        "title": "Decide which registration type you actually need",
        "detail": (
            "See REGISTRATION_TYPES -- an unattended App-Only/certificate "
            "registration (scheduled jobs, no human present) and an "
            "interactive/delegated registration (human-operator provisioning "
            "and migration work) are different tools for different purposes. "
            "Requesting the wrong one is a real source of confusing Access "
            "Denied errors later, but do not assume a specific PnP grant "
            "tier guarantees a specific capability boundary -- see each "
            "type's capability_testing_status before making that assumption."
        ),
    },
    {
        "number": 2,
        "title": "Request the app registration",
        "detail": (
            "Ask your tenant administrator to create an Entra ID app registration: "
            "single tenant (your organization only). For an interactive "
            "registration: Redirect URI platform 'Public client/native (mobile & "
            "desktop)', Redirect URI value http://localhost, no client secret "
            "needed. For an App-Only registration: no redirect URI needed, a "
            "certificate is uploaded instead (see references/ for certificate "
            "setup)."
        ),
    },
    {
        "number": 3,
        "title": "Request the API permissions for your registration type",
        "detail": (
            "Both types: Microsoft Graph Sites.Selected (Application) plus "
            "SharePoint Sites.Selected (Application) -- confirmed identical "
            "Entra-level permission type on both a real interactive and a "
            "real ETL registration in production. Interactive also needs "
            "Graph User.Read (Delegated), usually pre-populated and already "
            "consented. Graph permissions alone are insufficient -- any "
            "SharePoint call fails with AADSTS650057 until the SharePoint "
            "permission is also granted. The two registration types are then "
            "differentiated by auth mechanism (step 2) and by the PnP "
            "site-grant tier (step 6), not by a different Entra permission "
            "type -- do not assume a different SharePoint API permission "
            "exists per type without checking your own tenant's Entra portal."
        ),
    },
    {
        "number": 4,
        "title": "Assign users/service accounts to the Enterprise Application (interactive only)",
        "detail": (
            "In Entra ID -> Enterprise applications -> this app -> Users and "
            "groups, the tenant administrator must explicitly add every named "
            "user or service account that will use this registration -- before "
            "granting admin consent (step 5), matching the order this was "
            "actually done in practice. Does not apply to an App-Only "
            "certificate registration -- there is no signed-in identity for "
            "this assignment to gate. An account missing from this list can "
            "often still authenticate (sign in succeeds), then fail later with "
            "access-denied or app-assignment errors that look like a "
            "permissions problem but are actually a missing app-role "
            "assignment -- check this list first if that happens."
        ),
    },
    {
        "number": 5,
        "title": "Grant admin consent",
        "detail": (
            "A tenant administrator must explicitly grant admin consent for the "
            "registration (one-time, org-wide) -- adding a permission alone does "
            "not activate it; the Status column must read 'Granted for "
            "<organization>' with a green checkmark, not just show the permission "
            "listed."
        ),
    },
    {
        "number": 6,
        "title": "Tenant admin grants site-specific access via PnP PowerShell",
        "detail": (
            "A second, separate control plane from Entra: the tenant "
            "administrator (a SharePoint Admin -- a non-admin account gets "
            "Access Denied here, which is the correct security boundary, not a "
            "bug) runs Grant-PnPAzureADAppSitePermission (aliased as "
            "Grant-PnPEntraIDAppSitePermission) once per target site to grant "
            "this registration's Client ID the actual site-level permission. "
            "Entra's Sites.Selected permission from step 3 only enables this "
            "mechanism to exist -- it grants no site access on its own. This "
            "must be repeated against every site collection the "
            "app needs to reach; granting it once does not propagate to other "
            "sites.\n\n"
            "    -Permissions accepts four tiers, least to most privileged --\n"
            "    per Microsoft's own current Sites.Selected documentation:\n"
            "      read        view items/lists and their contents\n"
            "      write       read and modify metadata and content of the resource\n"
            "      manage      write, plus manage the site\n"
            "      fullcontrol full control of the site and its content\n\n"
            "    CAUTION: an earlier version of this module claimed write "
            "excludes list/library creation and manage is required for it -- "
            "production testing disproved this for a delegated/interactive "
            "registration (see REGISTRATION_TYPES.interactive."
            "capability_testing_status for the full evidence). Do not assume "
            "a specific tier maps to a specific capability boundary. Request "
            "the narrowest tier that matches your registration's *intended* "
            "purpose (REGISTRATION_TYPES), then confirm actual behavior with "
            "step 8's probe rather than trusting the tier label alone.\n\n"
            "    Connect-PnPOnline -Url \"https://contoso.sharepoint.com/sites/Demo\" -Interactive\n\n"
            "    Grant-PnPAzureADAppSitePermission `\n"
            "      -AppId \"<ClientID>\" `\n"
            "      -DisplayName \"<app-display-name>\" `\n"
            "      -Permissions <tier-per-REGISTRATION_TYPES> `\n"
            "      -Site \"https://contoso.sharepoint.com/sites/Demo\""
        ),
    },
    {
        "number": 7,
        "title": "Populate this repository's config.psd1 with the new registration",
        "detail": (
            "Before running any validation script (step 8), record the new "
            "registration's SiteUrl/TenantId/ClientId/AuthenticationMode in "
            "this repository's root config.psd1 -- run the "
            "workbench-initialize-connection-config skill (config_setup.write_config) "
            "rather than hand-editing the file. This step is easy to skip "
            "because it feels like a detour from 'request -> grant -> "
            "validate', but workbench-validate-sharepoint-connection's live scripts "
            "(test-network-connectivity.ps1, test-spo-connection.ps1, "
            "test-pnp-effective-capability-probe.ps1) all default to reading "
            "ClientId/TenantId from config.psd1 -- without this step, step 8 "
            "either fails outright or silently validates the wrong "
            "registration if a stale config.psd1 already exists from a "
            "previous project. For a certificate-based (ETL/App-Only) "
            "registration, this repo's config.psd1 schema does not currently "
            "have a canonical field for a certificate thumbprint -- pass "
            "-ClientId/-TenantId/-CertThumbprint explicitly to the probe "
            "script instead of relying on config.psd1 for that registration "
            "type."
        ),
    },
    {
        "number": 8,
        "title": "Validate end-to-end -- observe actual behavior, don't trust the tier label",
        "detail": (
            "Run test-pnp-effective-capability-probe.ps1 against each granted "
            "site. It reports two separate things, never conflated: (1) the "
            "stored Sites.Selected grant role, read directly via "
            "Get-PnPAzureADAppSitePermission when the signed-in account has "
            "rights to read it (a tenant admin, typically -- an ordinary "
            "account will likely get 403 Forbidden trying to read this, which "
            "is itself informative, not a script failure); (2) the effective "
            "capabilities actually observed (list/library/page/site-column/"
            "content-type creation, item and file CRUD). A passing connection "
            "test alone does not confirm write/create access at any "
            "particular tier -- and for delegated/interactive registrations "
            "specifically, observed capabilities may reflect the signed-in "
            "user's own SharePoint permissions rather than the app's grant, "
            "per Microsoft's documented intersection model. Run the probe in "
            "-AuthMode Certificate with the target app's own credentials to "
            "test an App-Only registration's boundary -- an interactive-"
            "session probe result never validates a different, "
            "certificate-based registration."
        ),
    },
]
