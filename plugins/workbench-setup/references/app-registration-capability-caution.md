# Capability claims: read before trusting any tier claim

## Contents

- [What was disproven](#what-was-disproven)
- [Two unresolved explanations](#two-unresolved-explanations)
- [How to report results](#how-to-report-results)

## What was disproven

An earlier version of this skill claimed the PnP site-grant tier (`Write` vs `Manage`)
reliably predicts whether an app can create lists and libraries: `Write` blocking it,
`Manage` allowing it. Production testing disproved this. A tenant administrator confirmed via
`Get-PnPAzureADAppSitePermission` that the interactive registration's stored grant role is
`write` on the tested production sites, yet an interactive session using that same
registration successfully created and removed lists, document libraries, pages, items and
files.

`CreateList` succeeding is not proof of a `Manage` grant.

## Two unresolved explanations

1. Microsoft's current Sites.Selected documentation defines `write` as "read and modify
   metadata and content of the resource". It does not document list or library creation as
   excluded. The stricter Write-excludes-structure mapping this skill previously encoded came
   from older, possibly outdated or context-specific community guidance, not Microsoft's
   current model.
2. For delegated (interactive) sessions, Microsoft's documented model is that effective
   access is the intersection of the app's consented permission and the signed-in user's own
   SharePoint permission on the site. If the signed-in user already holds elevated rights
   (for example Site Collection Administrator) independent of the app's grant, that alone
   could explain the observed capabilities. The test account could not even read the stored
   grant (`Get-PnPAzureADAppSitePermission` returned `403 Forbidden` without tenant-admin
   rights), which is itself evidence its effective permissions come from somewhere other than
   a queried app grant. The intersection model is specifically documented for Graph token
   enforcement, while `Connect-PnPOnline -Interactive` requests a SharePoint-resource token
   via a different, older OAuth path, and this app's `Sites.Selected` permission is
   Application-type only (no Delegated-type SharePoint permission exists on it). Whether that
   path consults an Application-type grant at all is unconfirmed.

A single test cannot disambiguate these, and neither explanation should be presented as
settled. Doing so requires re-running the same probe as a user with genuinely low or no
elevated permission on the site, or in `-AuthMode Certificate` (isolates the app grant, no
user-permission variable). Neither has been done yet.

## How to report results

Do not treat list or library creation as a tier signal for any registration. Use
`scripts/test-pnp-effective-capability-probe.ps1` to observe actual behavior. Always report
the stored grant role and the observed capabilities as two separate things, never conflated,
and never as proof of which explanation above is correct.
