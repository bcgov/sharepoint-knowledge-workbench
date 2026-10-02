# Config and profile validation

## Contents

- [Scope boundary](#scope-boundary)
- [Interface](#interface)
- [Detections](#detections)

## Scope boundary

Validates already-parsed Python dicts, not raw `.psd1` file text. See
`workflow_validation.py`'s module docstring for why raw `.psd1` parsing is out of scope for
this version rather than attempted with a fragile custom parser. Pure logic, no I/O.

## Interface

```python
from workflow_validation import (
    validate_connection_config, validate_document_workflow_profile,
    validate_publication_profile,
)

report = validate_document_workflow_profile(workflow_profile_dict)
# ValidationReport(status="PASS"|"FAIL", issues=[...])
```

Targets: the Layer 1 connection config (`config.psd1`), a document-workflow profile
(`document-workflows/<DocumentId>.workflow.psd1`) or a publication profile
(`publication-profiles/<DocumentId>.publication.psd1`).

## Detections

- Missing required top-level keys.
- Empty `Document.DocumentId`.
- A renderer profile placed in `RequestedRendererProfiles` (document-workflow) or
  `HumanPublication.PublicationProfile` (publication profile) that is not one of the
  implemented renderer profiles.

Every issue is `severity="error"`. Status is always `PASS` or `FAIL`, never `WARN`.
