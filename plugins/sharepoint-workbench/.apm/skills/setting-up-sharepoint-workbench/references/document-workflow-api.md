# Document workflow Python API

## Contents

- [Public interface](#public-interface)
- [Validation and overwrite behavior](#validation-and-overwrite-behavior)
- [Installation and dependencies](#installation-and-dependencies)

## Public interface

```python
from document_workflow import (
    classify_renderer_requests, build_workflow_profile,
    build_publication_profile, write_document_workflow,
)

workflow = build_workflow_profile(document_id=..., source_path=..., source_format=...,
                                   is_revision=..., requested_stages=[...],
                                   requested_renderer_profiles=[...],
                                   human_confirmation_gates={...},
                                   publication_profile_path=...,
                                   agent_actions_requested=[...], outstanding_decisions=[...])

publication = build_publication_profile(document_id=..., title=..., content_type=...,
                                         content_owner=..., source_package_path=...,
                                         package_identity=..., human_publication={...})

workflow_path, publication_path = write_document_workflow(repo_root, document_id, workflow, publication)
```

## Validation and overwrite behavior

Both `build_*` functions validate before returning and raise `DocumentWorkflowError`
on invalid input, for example an empty `document_id` or an unimplemented renderer
profile placed in `HumanPublication.PublicationProfile`. `write_document_workflow`
refuses to silently overwrite existing profile files unless `overwrite=True` is
passed explicitly.

## Installation and dependencies

Import from the skill's own `scripts/` directory (`sys.path.insert(0, 'scripts')` when running
from the skill root). `document_workflow` imports its sibling `psd1_writer`, which ships in the
same folder.

No dependencies beyond the Python standard library.
