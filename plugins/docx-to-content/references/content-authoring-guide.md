# Content Authoring Guide

This guide is for the people who write and maintain the canonical Markdown
content behind published manuals — not for the pipeline that converts or
renders it.

## Two kinds of ownership

Content in this system has two clearly separated owners:

- **Authors maintain** the words: topic prose, procedure steps, callouts,
  images, expected results, exceptions, troubleshooting notes, and related
  links — everything a reader actually reads. Authors edit this directly
  in Markdown, following `templates/content/manual-topic.md` and
  `references/supported-markdown-profile.md`.
- **Code maintains** everything mechanical that must stay consistent
  across every rendered output: tables of contents, page navigation,
  cross-reference resolution, and formatting for the target output. See
  `references/generated-elements.md` for the current list. Authors never
  hand-write these — hand-editing a generated element only creates drift
  the next time content is rendered.

If you find yourself typing a table of contents, a "next/previous page"
link, or a page number into a topic file, stop — that is a code-maintained
element and belongs in the render step, not in your content.

## Writing a topic

1. Copy `templates/content/manual-topic.md` to start a new topic.
2. Fill in the front matter: `title`, `owner`, `status`, `review_date`,
   `audience`.
3. Write only the sections that apply. Optional sections (`Before You
   Begin`, `Exceptions and Special Cases`, `Troubleshooting`) may be
   omitted entirely when there is nothing to say — never leave a section
   heading in place with "N/A" or "TBD" as filler.
4. Use the semantic callouts and components documented in
   `templates/components/README.md` (notes, warnings, procedure steps,
   expected results, etc.) instead of ad-hoc bold text or emoji to signal
   meaning.
5. Reference images and other topics using the rules in
   `references/supported-markdown-profile.md`.

## What authors do not need to know

You do not need to understand how content is packaged, validated, or
rendered to write a topic well. Those mechanics exist to keep every
topic's structure consistent and traceable, but they operate on the
Markdown you write without requiring you to think about them while
writing.

## Review checklist before marking a topic `status: reviewed`

- Front matter is complete and `review_date` is current.
- Every optional section present has real content — none are empty
  placeholders.
- Semantic callouts are used from the approved component list, not
  invented ad hoc.
- Every image reference and every related-topic link is a working
  relative path.
