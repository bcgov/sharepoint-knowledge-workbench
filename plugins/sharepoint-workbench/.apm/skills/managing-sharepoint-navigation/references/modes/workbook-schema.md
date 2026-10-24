# Mode: Workbook Schema & Conventions

Defines the structure of the declarative Excel workbook used to drive navigation.

## Column Layout

| Column Name | Required | Description | Example |
|:---|:---:|:---|:---|
| `Top Level` | Yes | Level 1 node title. | `Documents` |
| `2nd Level` | Optional | Level 2 child node title under Top Level. | `Policies` |
| `3rd Level` | Optional | Level 3 child node title under 2nd Level. | `HR Policies` |
| `Url` | Optional | Target URL (site-relative `/...` or `https://`). | `/sites/workbench/Shared Documents/Policies` |
| `OpenInNewTab` | Optional | `Y` or `N` (default `N`). | `N` |
| `Enabled` | Optional | `Y` or `N` (default `Y`). `N` excludes node and its children. | `Y` |

## Hierarchy Rules
- A parent row without a `Url` is provisioned as a linkless header node.
- Sibling order in the workbook defines the visual display order in the SharePoint navigation menu.
- Full path determines identity: nodes with identical titles under different parents remain distinct.
