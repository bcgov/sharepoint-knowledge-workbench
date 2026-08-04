---
name: validate-workbench-environment
plugin: workbench-setup
description: Validates already-built connection/document-workflow/publication-profile dicts (the same shape config_setup.py/document_workflow.py build before writing .psd1 files) before they're consumed by other plugins -- required keys present, non-empty DocumentId, only implemented renderer profiles in RequestedRendererProfiles/HumanPublication.PublicationProfile. Always PASS or FAIL, never WARN.
allowed-tools: Bash, Read
examples:
  - "python -c \"import workflow_validation as wv; print(wv.validate_document_workflow_profile(profile).status)\""
---

# Validate Workbench Environment

## Trigger and Purpose

Use this skill to validate configuration/profile data before it's
relied on by another plugin: the Layer 1 connection config
(`config.psd1`), a document-workflow profile
(`document-workflows/<DocumentId>.workflow.psd1`), or a publication
profile (`publication-profiles/<DocumentId>.publication.psd1`).

**Scope boundary (deliberate, this version):** validates already-
PARSED Python dicts, not raw `.psd1` file text — see
`workflow_validation.py`'s module docstring for why raw `.psd1` parsing
is out of scope for this first version rather than attempted with a
fragile custom parser.

## Public Interface

```python
from workflow_validation import (
    validate_connection_config, validate_document_workflow_profile,
    validate_publication_profile,
)

report = validate_document_workflow_profile(workflow_profile_dict)
# ValidationReport(status="PASS"|"FAIL", issues=[...])
```

Detections: missing required top-level keys; empty `Document.
DocumentId`; a renderer profile placed in `RequestedRendererProfiles`
(document-workflow) or `HumanPublication.PublicationProfile`
(publication profile) that is not one of this repo's implemented
renderer profiles. Every issue is `severity="error"` — status is
always `PASS` or `FAIL`, never `WARN`.

## Installation

```bash
pip install -e plugins/workbench-setup
```

## Dependencies

None beyond the Python standard library.
