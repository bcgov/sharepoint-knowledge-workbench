# Provenance and correction history

## Contents

- [Provenance](#provenance)
- [Correction history](#correction-history)

## Provenance

Generalized from a real project's app-registration JIRA requests, `CLAUDE.md` architecture
notes describing both registration types, live Entra portal screenshots, a live
tenant-administrator-run `Get-PnPAzureADAppSitePermission` query against the real production
tenant, and Microsoft's own current Sites.Selected and RSC documentation. Source repository
only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md` covers the
sibling `validate-app-registration` extraction this skill's reference and asset files were
onboarded alongside.

## Correction history

Three real corrections on 2026-08-09, in order, worth knowing if this drifts again:

1. An early draft incorrectly generalized a single "empirical finding" (`Write` alone
   sufficient for list creation) from a misremembered summary. It was corrected against
   trial-tenant test-suite result tables, which showed the opposite: `Write` blocks list
   creation, `Manage` allows it.
2. A second draft assumed the interactive registration uses `AllSites.Manage` (Delegated) at
   the Entra level, based on that same trial-tenant documentation. It was corrected against
   live production-tenant Entra screenshots, which show `Sites.Selected` (Application) on both
   registrations.
3. A third draft still asserted the trial tenant's Write-vs-Manage capability-tier boundary
   (list creation blocked under Write) as a confirmed fact for production. A tenant
   administrator's live `Get-PnPAzureADAppSitePermission` query disproved this: the interactive
   registration's production grant is `write`, yet list/library creation succeeded. This is the
   correction reflected throughout. `REGISTRATION_TYPES` no longer asserts fixed capability
   booleans, only `capability_testing_status` prose describing what is known, unresolved or
   unverified.
