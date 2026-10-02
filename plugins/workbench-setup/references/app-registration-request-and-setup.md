# Service request and setup sequence

## Contents

- [Generate a service-request document](#generate-a-service-request-document)
- [The setup sequence](#the-setup-sequence)

## Generate a service-request document

```python
from app_registration_request import render_service_request, AppRegistrationRequestError

with open("assets/service-request-interactive-registration-template.md") as f:
    template = f.read()

rendered = render_service_request(template, answers)
# raises AppRegistrationRequestError naming every <PLACEHOLDER> missing an answer
```

Two templates are available in `assets/`, one per registration type:

- `service-request-interactive-registration-template.md`
- `service-request-application-registration-template.md`

`render_service_request` is pure string templating. It never leaves an unfilled `<PLACEHOLDER>`
token in a document meant to be submitted; it raises `AppRegistrationRequestError` naming
exactly what's missing.

## The setup sequence

`SETUP_STEPS` covers two separate control planes that are easy to conflate but both required:

```python
from app_registration_request import SETUP_STEPS

for step in SETUP_STEPS:
    print(f"{step['number']}. {step['title']}")
    print(f"   {step['detail']}")
```

1. Decide which registration type you need (see `app-registration-types.md`).
2. Request the app registration (redirect URI for interactive; certificate for App-Only).
3. Request the API permissions matching your type.
4. Assign users/service accounts to the Enterprise Application entry, **interactive only**,
   before admin consent. A user missing from this list can often still sign in successfully
   and only fail later with access-denied/app-assignment errors that look like a permissions
   problem. Check this list first if that happens.
5. Grant admin consent.
6. A tenant admin (a SharePoint Admin specifically; a non-admin gets Access Denied, the correct
   security boundary) runs `Grant-PnPAzureADAppSitePermission` once per target site, requesting
   the tier matching your type's intended purpose. This is the second control plane: step 3's
   Entra permission only enables this mechanism to exist, and it must be repeated per site. Do
   not assume the tier requested here predicts the actual capability boundary; see
   `app-registration-capability-caution.md`.
7. **Populate the repository's root `config.psd1` with the new registration.** Use the
   `workbench-initialize-workbench-config` skill (`config_setup.write_config`); don't hand-edit
   the file. It is easy to skip because it feels like a detour, but step 8's live scripts
   default to reading `ClientId` and `TenantId` from `config.psd1`. Skipping it makes step 8
   fail outright or silently validate the wrong registration against a stale config. For a
   certificate-based (ETL) registration, pass `-ClientId`, `-TenantId` and `-CertThumbprint`
   explicitly to the probe instead; the `config.psd1` schema has no canonical
   certificate-thumbprint field yet.
8. Validate end-to-end via `test-pnp-effective-capability-probe.ps1`. Report the stored grant
   role and observed capabilities separately, and test an App-Only registration with
   `-AuthMode Certificate` and its own credentials. An interactive-session probe never
   validates a different, certificate-based registration.
