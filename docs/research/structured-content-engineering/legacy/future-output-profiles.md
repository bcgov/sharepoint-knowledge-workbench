# Future Output Profiles

This document surveys the output profiles the docx-to-content pipeline
could render canonical content to beyond Phase 1. It is documentation
only — it does not implement, schedule, or authorize building any of the
non-Markdown profiles below. Building a new renderer, adding a publishing
adapter, or selecting a delivery mode for any profile other than
Multipage Markdown is explicitly out of scope for this document and for
Phase 1.

Every profile is described using the same fields: purpose, audience,
canonical content accepted, semantic components supported, generated
elements, presentation-template mechanism, document-library upload
behavior, media handling, validation requirements, edit ownership,
round-trip policy, accessibility considerations, known fidelity
limitations, and implementation status.

---

## Multipage Markdown

- **Purpose**: the default, plain-text-native published form of a manual —
  one page per topic chunk plus a hierarchical index.
- **Audience**: readers viewing content in a Markdown-native or
  Git-hosted context (e.g. a documentation site, a repository viewer).
- **Canonical content accepted**: any promoted canonical content package
  whose manifest `schema_version` the renderer declares support for.
- **Semantic components supported**: all components in
  `templates/components/README.md` pass through as authored (GitHub-style
  `> [!TYPE]` callouts render natively in most Markdown viewers).
- **Generated elements**: table of contents (`index.md`) and page-to-page
  navigation — see `references/generated-elements.md`.
- **Presentation-template mechanism**: none — output is plain Markdown,
  styled by whatever viewer renders it.
- **Document-library upload behavior**: none — output is written to a
  local directory; there is no upload step.
- **Media handling**: media files are copied byte-for-byte from the
  canonical package's `media/` directory into the rendered output's own
  `media/` directory; references are rewritten to page-relative paths.
- **Validation requirements**: rendered-output validation (index/page
  existence, working links, page completeness, manifest hash match,
  traceability back to canonical chunks) via
  `renderers/validate_rendered.py`.
- **Edit ownership**: rendered output is never edited directly — canonical
  Markdown is the source of truth and is re-rendered on every change.
- **Round-trip policy**: one-way (canonical → rendered). There is no
  mechanism to edit rendered Markdown and reconcile changes back into
  canonical content.
- **Accessibility considerations**: plain Markdown with standard heading
  structure and alt text on images is broadly accessible to screen readers
  in any Markdown-aware viewer.
- **Known fidelity limitations**: no visual styling beyond what the
  viewing tool applies to standard Markdown.
- **Implementation status: implemented.**

---

## PDF

- **Purpose**: a fixed-layout, printable/distributable form of a manual.
- **Audience**: readers who need an offline, print-ready, or
  archival-quality document.
- **Canonical content accepted**: same canonical package shape as
  Multipage Markdown.
- **Semantic components supported (planned)**: notes, warnings, and other
  callouts rendered as visually distinct styled blocks.
- **Generated elements (planned)**: table of contents with page numbers,
  running headers/footers, page breaks between topics.
- **Presentation-template mechanism (planned)**: a print stylesheet/layout
  template applied at render time (e.g. via a PDF-generation toolchain);
  no such template exists yet.
- **Document-library upload behavior**: none — a local file is produced.
- **Media handling (planned)**: images embedded at print resolution.
- **Validation requirements (planned)**: page-count sanity, image
  embedding verification, no broken cross-references.
- **Edit ownership**: canonical Markdown remains the source of truth; a
  generated PDF is never hand-edited and reconciled back.
- **Round-trip policy**: one-way only, no silent round-trip — a PDF is a
  disposable rendering, not an editable source.
- **Accessibility considerations (planned)**: would require tagged-PDF
  output and reading-order preservation to meet accessibility standards;
  not solved by this document.
- **Known fidelity limitations**: fixed pagination cannot reflow content
  the way Markdown or HTML can.
- **Implementation status: designed-only.**

---

## Word

- **Purpose**: a distributable, commonly editable document format for
  audiences who expect `.docx` deliverables.
- **Audience**: readers/reviewers working in Microsoft Word workflows.
- **Canonical content accepted (planned)**: same canonical package shape
  as Multipage Markdown.
- **Semantic components supported (planned)**: callouts mapped to Word
  paragraph/character styles.
- **Generated elements (planned)**: Word-native table of contents field,
  styled headings.
- **Presentation-template mechanism (planned)**: a `.dotx`/reference-doc
  template supplying corporate styling; none exists yet.
- **Document-library upload behavior**: none defined.
- **Media handling (planned)**: images embedded as Word inline images.
- **Validation requirements (planned)**: structural round-trip check
  (headings/order preserved), no lost content.
- **Edit ownership**: canonical Markdown remains the source of truth. A
  generated Word document is a rendering, not an authoring surface — this
  is an explicit drift warning: if someone edits the generated `.docx`
  directly, those edits are not captured anywhere and will be silently
  lost the next time the topic is re-rendered from canonical content.
  There is no silent round-trip back into canonical Markdown.
- **Round-trip policy**: one-way only; no automatic round-trip editing is
  supported or planned.
- **Accessibility considerations**: would need to preserve heading
  structure and alt text through Word's own accessibility features.
- **Known fidelity limitations**: complex Markdown constructs (nested
  callouts, certain table shapes) may not have a clean Word equivalent.
- **Implementation status: designed-only.**

---

## PowerPoint

- **Purpose**: a slide-based summary or training form of manual content.
- **Audience**: readers in a training/presentation context rather than a
  detailed-reference context.
- **Canonical content accepted (planned)**: a subset of canonical content
  — likely one slide per procedure step or key point, not a full-fidelity
  rendering of every topic.
- **Semantic components supported (planned)**: warnings/important notes as
  highlighted slide callout boxes; most other components condensed into
  slide bullets.
- **Generated elements (planned)**: a title/agenda slide generated from
  the table of contents.
- **Presentation-template mechanism (planned)**: a corporate slide
  template/theme; none exists yet.
- **Document-library upload behavior**: none defined.
- **Media handling (planned)**: images embedded as slide images, resized
  to fit slide layout.
- **Validation requirements (planned)**: slide-count sanity, no orphaned
  content dropped silently during condensation.
- **Edit ownership**: canonical Markdown remains the source of truth for
  the underlying content; a generated deck is not an authoring surface.
- **Round-trip policy**: one-way only, no automatic round-trip editing.
- **Accessibility considerations**: would need slide reading order and
  alt text carried through to be screen-reader accessible.
- **Known fidelity limitations**: slide format inherently loses procedural
  detail and long-form prose compared to the source topic.
- **Implementation status: designed-only.**

---

## Audio/Video

- **Purpose**: a narrated or recorded walkthrough form of manual content
  for auditory/visual learners or hands-busy situations.
- **Audience**: readers who prefer or need listening/watching over
  reading.
- **Canonical content accepted (planned)**: topic prose and procedure
  steps as script source; images/diagrams as visual reference material.
- **Semantic components supported (planned)**: warnings/important notes
  called out with distinct audio cues or on-screen emphasis.
- **Generated elements (planned)**: a chapter/segment index mirroring the
  table of contents.
- **Presentation-template mechanism (planned)**: a narration voice/style
  and video template; none exists yet.
- **Document-library upload behavior**: none defined.
- **Media handling (planned)**: source images referenced as on-screen
  visuals; no automated diagram-to-video conversion is planned.
- **Validation requirements (planned)**: script-to-content coverage check
  (no topic silently dropped).
- **Edit ownership**: canonical Markdown remains the source of truth for
  the script; a rendered audio/video file is not an authoring surface.
- **Round-trip policy**: one-way only, no automatic round-trip editing.
- **Accessibility considerations**: would require captions/transcripts
  generated alongside the media, not as an afterthought.
- **Known fidelity limitations**: audio/video is inherently linear and
  loses the skimmability of structured text.
- **Implementation status: designed-only.**

---

## HTML

- **Purpose**: a styled, web-viewable form of a manual, e.g. for
  publishing to a documentation website.
- **Audience**: readers browsing content in a standard web browser.
- **Canonical content accepted (planned)**: same canonical package shape
  as Multipage Markdown.
- **Semantic components supported (planned)**: callouts rendered as
  styled `<div>` blocks matching each component type.
- **Generated elements (planned)**: table of contents/site navigation,
  breadcrumbs, search index.
- **Presentation-template mechanism (planned)**: an HTML/CSS site
  template; none exists yet.
- **Document-library upload behavior**: none defined — a local static
  site output, not tied to any specific hosting/upload target.
- **Media handling (planned)**: images copied and referenced with
  web-relative paths.
- **Validation requirements (planned)**: link checking, page
  completeness, accessible markup checks.
- **Edit ownership**: canonical Markdown remains the source of truth; the
  generated site is a rendering, not an authoring surface.
- **Round-trip policy**: one-way only, no automatic round-trip editing.
- **Accessibility considerations (planned)**: would target WCAG-conformant
  semantic HTML, proper heading order, and alt text carried through from
  canonical content.
- **Known fidelity limitations**: visual design depends entirely on the
  chosen template, which does not exist yet.
- **Implementation status: designed-only.**

---

## ZIP Release Package

- **Purpose**: a single distributable archive bundling one or more
  rendered output profiles (e.g. Multipage Markdown plus its media) for
  offline distribution or archival release.
- **Audience**: anyone needing a self-contained, downloadable snapshot of
  a manual's published output.
- **Canonical content accepted (planned)**: not canonical content
  directly — this profile packages the OUTPUT of one or more other
  renderers, so its input is already-rendered output plus a manifest.
- **Semantic components supported**: inherited unchanged from whichever
  rendered profile(s) are bundled — this profile does not alter content.
- **Generated elements (planned)**: a release manifest listing bundled
  profiles and their versions/hashes.
- **Presentation-template mechanism**: not applicable — this is a
  packaging step, not a rendering step.
- **Document-library upload behavior**: none defined.
- **Media handling**: media files are included unchanged from the bundled
  rendered output(s).
- **Validation requirements (planned)**: archive integrity check (every
  file listed in the manifest is present and unmodified).
- **Edit ownership**: canonical Markdown remains the source of truth; a
  release archive is a frozen snapshot, never edited in place.
- **Round-trip policy**: one-way only — a release archive is not fed back
  into the pipeline as input.
- **Accessibility considerations**: inherited from whichever profile(s)
  are bundled.
- **Known fidelity limitations**: only as fresh as the render it packages;
  does not itself re-render anything.
- **Implementation status: designed-only.**

---

## SharePoint Modern Pages

- **Purpose**: publishing manual content as SharePoint Modern Pages inside
  an organization's existing SharePoint document environment.
- **Audience**: readers who already work inside a SharePoint-based
  environment and expect manuals to live there.
- **Canonical content accepted (planned)**: same canonical package shape
  as Multipage Markdown, mapped to SharePoint's page/web-part model.
- **Semantic components supported (planned)**: callouts mapped to
  SharePoint's built-in web parts (e.g. a "Highlighted content" or "Text"
  web part styled per component type).
- **Generated elements (planned)**: SharePoint site navigation and a
  page-index/landing page mirroring the table of contents.
- **Presentation-template mechanism (planned)**: a SharePoint page/site
  template; none exists yet.
- **Document-library upload behavior (planned)**: rendered pages and media
  would be uploaded into a SharePoint document library and published as
  Modern Pages (individual `.aspx` page files under the hood). Note:
  `.aspx` is SharePoint's own internal page-storage format — it is never
  an authoring format or a canonical format in this pipeline; authors
  never write or edit `.aspx` directly, and canonical content is never
  stored as `.aspx`.
- **Media handling (planned)**: images uploaded into a SharePoint asset
  library and referenced from generated pages.
- **Validation requirements (planned)**: published-page existence and link
  checks against the SharePoint site, equivalent in spirit to
  `renderers/validate_rendered.py`'s checks for Multipage Markdown.
- **Edit ownership**: canonical Markdown remains the source of truth. A
  published SharePoint page is a rendering, not an authoring surface —
  this is an explicit drift warning: editing a published SharePoint page
  directly in SharePoint creates content that is not reflected anywhere in
  canonical Markdown, and the next automated publish would silently
  overwrite those direct edits. There is no silent round-trip between
  SharePoint pages and canonical Markdown.
- **Round-trip policy**: one-way only (canonical → SharePoint); no automatic round-trip editing between SharePoint and canonical content is supported or planned.
- **Accessibility considerations (planned)**: would need to rely on
  SharePoint's own accessibility features for Modern Pages, with heading
  structure and alt text carried through from canonical content.
- **Known fidelity limitations**: SharePoint's web-part model does not map
  1:1 onto every Markdown construct; complex tables or nested callouts may
  need simplification.
- **Publishing boundary (this document draws no implementation)**: this
  profile is documentation only. No SharePoint publishing adapter, Entra
  authentication, PnP PowerShell integration, or Microsoft Graph
  integration exists in this plugin, and none is added by this document.
  Selecting a specific SharePoint delivery mode (app-only auth vs.
  delegated auth, PnP vs. Graph SDK, etc.) is a decision explicitly left
  for a future, separately scoped and separately authorized piece of work.
- **Implementation status: requires-platform-authorization.**

---

## Summary table

| Profile | Implementation status |
|---|---|
| Multipage Markdown | implemented |
| PDF | designed-only |
| Word | designed-only |
| PowerPoint | designed-only |
| Audio/Video | designed-only |
| HTML | designed-only |
| ZIP Release Package | designed-only |
| SharePoint Modern Pages | requires-platform-authorization |
