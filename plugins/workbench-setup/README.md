# workbench-setup

Foundational connection/config/workflow setup for the whole SharePoint
Knowledge Workbench: generates the root, git-ignored SharePoint
connection config; runs the document-workflow intake wizard (producing
a document-workflow profile and a publication profile); validates
written configuration/profile files before other plugins consume them.

**Standalone plugin, not folded into an existing domain plugin**: none
of `source-document-extraction`/`document-structure-analysis`/
`structured-content-assembly`/`structured-content-rendering`/
`sharepoint-content-publication`/`sharepoint-agents-and-skills` own
these cross-cutting, upstream-of-everything-else questions (what is
this document, where should outputs go, which renderer profiles are
requested, governance/evidence settings) — see
`docs/superpowers/specs/2026-08-02-multi-document-destination-
configuration-design.md` Section 8.

**Zero SharePoint tenant I/O by default**, and zero document
extraction/rendering in this version. `initialize-workbench-config`'s
config generation never connects to anything; an explicit,
separately-injected connector is required to opt into a read-only
connection test. `initialize-document-workflow`'s execution boundary is
`ask -> propose defaults -> validate -> display -> write -> stop` —
it never extracts, renders, or touches SharePoint.

```
plugins/workbench-setup/
├── scripts/
│   ├── app_registration_request.py  # request-app-registration logic
│   ├── psd1_writer.py               # shared Python-dict -> PowerShell .psd1 text renderer
│   ├── config_setup.py              # initialize-workbench-config logic
│   ├── document_workflow.py         # initialize-document-workflow logic
│   ├── workflow_validation.py       # validate-workbench-environment: config/profile validation
│   ├── app_registration_validation.py  # validate-workbench-environment: app-registration validation
│   ├── network_connectivity.py      # validate-workbench-environment: network-reachability checklist
│   ├── test-network-connectivity.ps1  # validate-workbench-environment: live network + auth check
│   ├── test-spo-connection.ps1      # validate-workbench-environment: minimal live connection check
│   └── test-pnp-effective-capability-probe.ps1  # validate-workbench-environment, request-app-registration:
│                                     # empirically probe effective capabilities (list/library/page/
│                                     # site-column/content-type creation) under the granted PnP tier
├── assets/
│   ├── config.psd1.example
│   ├── document-workflow.psd1.example
│   ├── publication-profile.psd1.example
│   ├── service-request-interactive-registration-template.md   # request-app-registration
│   └── service-request-application-registration-template.md   # request-app-registration
├── references/
│   ├── app-registration-overview.md              # request-app-registration, validate-workbench-environment
│   ├── delegated-permission-boundary-test.md      # validate-workbench-environment
│   ├── effective-permissions-matrix.md            # request-app-registration, validate-workbench-environment:
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
pip install -e plugins/workbench-setup
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
cd plugins/workbench-setup
pip install -e .
python -m pytest tests/ -v
```

## Isolated-install proof

```bash
cd tools/phase-4-5-core-plugin-refactoring
python isolated_install_check.py --plugin workbench-setup --import-package document_workflow
```
