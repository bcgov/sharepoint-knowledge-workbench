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
extraction/rendering in this version. `setup-sharepoint-connection`'s
config generation never connects to anything; an explicit,
separately-injected connector is required to opt into a read-only
connection test. `initialize-document-workflow`'s execution boundary is
`ask -> propose defaults -> validate -> display -> write -> stop` —
it never extracts, renders, or touches SharePoint.

```
plugins/workbench-setup/
├── scripts/
│   ├── psd1_writer.py          # shared Python-dict -> PowerShell .psd1 text renderer
│   ├── config_setup.py         # setup-sharepoint-connection logic
│   ├── document_workflow.py    # initialize-document-workflow logic
│   ├── workflow_validation.py  # validate-workbench-environment logic
│   └── app_registration_validation.py  # validate-app-registration logic
├── assets/
│   ├── config.psd1.example
│   ├── document-workflow.psd1.example
│   └── publication-profile.psd1.example
├── skills/
│   ├── setup-sharepoint-connection/
│   ├── initialize-document-workflow/
│   ├── validate-workbench-environment/
│   └── validate-app-registration/
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
