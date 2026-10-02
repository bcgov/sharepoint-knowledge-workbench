# Path resolution API

## Contents

- [Public interface](#public-interface)
- [Result statuses](#result-statuses)

## Public interface

```python
from path_resolution import resolve_workbench_paths, format_invocations

result = resolve_workbench_paths(
    document_id="sample-manual",
    connection=connection,               # Layer 1 connection-config dict
    workflow_profile=workflow_profile,   # Layer 1b document-workflow dict
    publication_profile=publication_profile,  # Layer 2 publication-profile dict
    workbench_root=".",
)
print(format_invocations(result))
```

## Result statuses

`result.overall_status` is `"PASS"` (every downstream invocation has all its required paths
present), `"EMPTY"` (none of them do), or `"PARTIAL"` (a mix; the individual
`ResolvedInvocation.status` values name which).

Each `ResolvedInvocation` carries `plugin`, `skill`, `status` (`"AVAILABLE"` | `"PARTIAL"` |
`"UNAVAILABLE"`), `args` (resolved `Path`s for the files that exist), and `missing`
(filenames that do not).

`document_id` is cross-checked against `workflow_profile` and `publication_profile`'s own
`Document.DocumentId` when present. A mismatch raises `ValueError` rather than silently
resolving against the wrong document.

Standard library only.
