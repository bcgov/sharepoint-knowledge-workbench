# Page preview composition details

## Contents

- [Why](#why)
- [Inputs](#inputs)
- [Honest outcomes](#honest-outcomes)
- [Scope and provenance](#scope-and-provenance)

## Why

A reviewer confirming a page conversion needs to see the result in context: the page with the site's own navigation, header, logo and breadcrumb trail in place, not a bare
content fragment. The skill merges a page folder's extracted content with a chrome folder's structural data into one complete, self-contained offline HTML file.

## Inputs

- **Page folder**: `metadata.json` (page title, source URL, extraction timestamp) and `modern-preview.html` (the extracted content, wrapped in a `<main class="page-content">` or
  `<div class="page-content">` element; falls back to `<body>` if that wrapper is absent).
- **Chrome folder**: `site-chrome.json` with `Web` (title, and optionally `SiteLogoUrl` or `SiteLogoLocalFile`), `TopNav` (a list of `{Title, Url, Children}`) and `Ancestors` (a list of
  `{Title, Url}` breadcrumb entries).

## Honest outcomes

| Condition | Outcome | Output written? |
|---|---|---|
| Page or chrome folder missing a required file | `Unavailable` | No |
| Page content is empty | `Empty` | No |
| Chrome present but missing logo, ancestors and/or navigation | `Partial` (missing parts named) | Yes |
| Full chrome and content present | `Observed` | Yes |

A missing logo is never replaced with a placeholder image, and missing ancestors or navigation never fabricate breadcrumb or menu entries. The preview is built from exactly what is on
disk, and every gap is named in the outcome detail.

## Scope and provenance

Disk-only: reads the two folders and writes the one output file (`--output`, or `full-preview.html` in the page folder by default). No network calls and no tenant I/O.

Adapted from a component of `sp-running-sharegate-jobs` in the originating SharePoint migration repository. That skill otherwise depends on a commercial migration tool; this component was
independently verified to have zero calls into it and zero live-tenant I/O. Source repository only: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
