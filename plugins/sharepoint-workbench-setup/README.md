# sharepoint-workbench-setup

Foundational connection/config/workflow setup for the whole SharePoint
Knowledge Workbench: generates the root, git-ignored SharePoint
connection config; runs the document-workflow intake wizard (producing
a document-workflow profile and a publication profile); validates
written configuration/profile files before other plugins consume them.

**Standalone plugin, not folded into an existing domain plugin**: none
of `source-document-extraction`/`document-structure-analysis`/
`structured-content-assembly`/`structured-content-rendering`/
`sharepoint-site-build-and-publish`/`sharepoint-copilot-agents-and-skills` own
these cross-cutting, upstream-of-everything-else questions (what is
this document, where should outputs go, which renderer profiles are
requested, governance/evidence settings) — see
`docs/superpowers/specs/2026-08-02-multi-document-destination-
configuration-design.md` Section 8.

**Zero SharePoint tenant I/O by default**, and zero document
extraction/rendering in this version. `initialize-connection-config`'s
config generation never connects to anything; an explicit,
separately-injected connector is required to opt into a read-only
connection test. `initialize-document-workflow`'s execution boundary is
`ask -> propose defaults -> validate -> display -> write -> stop` —
it never extracts, renders, or touches SharePoint.

```
plugins/sharepoint-workbench-setup/
├── scripts/
│   ├── app_registration_request.py  # request-app-registration logic
│   ├── psd1_writer.py               # shared Python-dict -> PowerShell .psd1 text renderer
│   ├── config_setup.py              # initialize-connection-config logic
│   ├── document_workflow.py         # initialize-document-workflow logic
│   ├── workflow_validation.py       # validate-sharepoint-connection: config/profile validation
│   ├── app_registration_validation.py  # validate-sharepoint-connection: app-registration validation
│   ├── network_connectivity.py      # validate-sharepoint-connection: network-reachability checklist
│   ├── test-network-connectivity.ps1  # validate-sharepoint-connection: live network + auth check
│   ├── test-spo-connection.ps1      # validate-sharepoint-connection: minimal live connection check
│   └── test-pnp-effective-capability-probe.ps1  # validate-sharepoint-connection, request-app-registration:
│                                     # empirically probe effective capabilities (list/library/page/
│                                     # site-column/content-type creation) under the granted PnP tier
├── assets/
│   ├── config.psd1.example
│   ├── document-workflow.psd1.example
│   ├── publication-profile.psd1.example
│   ├── service-request-interactive-registration-template.md   # request-app-registration
│   └── service-request-application-registration-template.md   # request-app-registration
├── references/
│   ├── app-registration-overview.md              # request-app-registration, validate-sharepoint-connection
│   ├── delegated-permission-boundary-test.md      # validate-sharepoint-connection
│   ├── effective-permissions-matrix.md            # request-app-registration, validate-sharepoint-connection:
│   │                                                # start here for "why did/didn't this operation work"
│   ├── resource-specific-consent-summary.md       # request-app-registration
│   └── graph-selected-permissions-overview-summary.md  # request-app-registration
├── skills/
│   ├── request-app-registration/       # pure guidance: service-request generation + setup sequence
│   ├── initialize-workbench-config/
│   ├── initialize-document-workflow/
│   ├── validate-workbench-environment/  # config/profile validation, app-registration validation,
│   │                                     # and live network/auth scripts (merged 2026-08-09)
│   └── resolve-workbench-paths/
└── tests/
```

## Install

```bash
pip install -e plugins/sharepoint-workbench-setup
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Public interface

```python
from config_setup import validate_connection_answers, write_config, test_connection
from document_workflow import (
    classify_renderer_requests, build_workflow_profile,
    build_publication_profile, write_document_workflow,
)
from workflow_validation import (
    validate_connection_config, validate_document_workflow_profile,
    validate_publication_profile,
)
```

See each skill's own `SKILL.md` for the full interface and execution
boundary.

## Tests

```bash
cd plugins/sharepoint-workbench-setup
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin sharepoint-workbench-setup --import-package document_workflow
```

## Skills by functional group

### Access, project/document configuration, path resolution and readiness

- `workbench-initialize-connection-config` -- Creates the root, git-ignored config.psd1 from the canonical config.psd1.example template: Entra ID app-registration details (TenantId, ClientId, AuthenticationMode) and the target SharePoint site (SiteUrl). Use when...
- `workbench-initialize-document-workflow` -- Interactive intake wizard that records a source document's identity, processing stages, output formats (only implemented renderer profiles are executable choices), publication locations, agent-grounding...
- `workbench-request-app-registration` -- Guides the pre-work before any SharePoint use case that connects to a live tenant. Documents the two app-registration types (unattended App-Only/certificate for scheduled jobs, interactive/delegated for...
- `workbench-resolve-document-paths` -- Resolves a DocumentId plus already-parsed connection, document-workflow and publication-profile dicts into the concrete export paths and arguments the two SharePoint analysis plugins (sharepoint-site-assessment,...
- `workbench-validate-sharepoint-connection` -- Confirms the app registration and connection work against a live tenant. Validates config and profile correctness (always PASS or FAIL), validates the Entra ID app registration (device-code auth plus an...

## Previous identities

Skill and plugin names changed in the seven-domain migration (issue #6). Old names are not retained as aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `workbench-initialize-workbench-config` | `workbench-initialize-connection-config` | `workbench-setup` |
| `workbench-resolve-workbench-paths` | `workbench-resolve-document-paths` | `workbench-setup` |
| `workbench-validate-workbench-environment` | `workbench-validate-sharepoint-connection` | `workbench-setup` |

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-workbench-setup@sharepoint-knowledge-workbench
```
