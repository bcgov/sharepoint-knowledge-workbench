# Use Case: Workbench/Connection Setup

Foundational, cross-cutting connection/config/workflow setup shared by every other use case in
this repository: generates the root SharePoint connection config, runs the document-workflow
intake wizard, and validates written configuration before other plugins consume it.

## When to use this

Before running any other SharePoint use case for the first time in an environment — this is the
upstream-of-everything-else setup step (what document is this, where should outputs go, which
renderer profiles are requested).

## Workflow at a glance

- `request-app-registration` — pure guidance, no I/O: generates a filled service-request document
  for your tenant/cloud administrator, and provides the generalized setup sequence (Entra API
  permissions, admin consent, Enterprise Application user assignment, and the separate PnP
  PowerShell site-level grant) for once it's approved. Run this first.
- `initialize-connection-config` — generates the root, git-ignored connection config
  (`config.psd1`). Never connects to anything by default; a real connection test requires an
  explicitly injected connector.
- `initialize-document-workflow` — intake wizard producing a document-workflow profile and a
  publication profile. Execution boundary: `ask → propose defaults → validate → display → write →
  stop` — it never extracts, renders, or touches SharePoint itself.
- `validate-sharepoint-connection` — validates already-written config/profile files (pure, always
  PASS/FAIL), validates the app registration against the live tenant (device-code auth +
  permission-boundary proof), and provides real, runnable network-reachability + interactive-
  authentication scripts.

**Zero tenant I/O by default** — the live network/auth checks are opt-in scripts you run yourself,
never invoked automatically.

## Full detail

[`plugins/sharepoint-workbench-setup/README.md`](../../plugins/sharepoint-workbench-setup/README.md)
