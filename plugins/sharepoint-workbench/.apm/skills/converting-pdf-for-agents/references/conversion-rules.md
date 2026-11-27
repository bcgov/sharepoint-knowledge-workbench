# Conversion rules

## Contents

- [Topics file](#topics-file)
- [Proposing topics for a weak PDF](#proposing-topics-for-a-weak-pdf)
- [How structure is detected](#how-structure-is-detected)
- [Output layout](#output-layout)
- [Images](#images)
- [Limits and troubleshooting](#limits-and-troubleshooting)

## Topics file

`topics.xlsx` (or `topics.csv` when openpyxl is missing), one row per topic page.

| Column | Meaning |
|---|---|
| `topic_no` | Order number, informational. |
| `title` | Page title and link text. Required. |
| `level` | 1 for a top topic, 2 for a sub-topic. Controls index indentation and sub-heading depth. |
| `start_page` | First page of the topic. Required. A topic ends where the next one starts. |
| `start_heading` | Optional heading text. When set, the split happens at that line, not the page start. Leave blank for AI-proposed topics. |
| `source` | `outline`, `font`, `ai` or `manual`. `ai` adds a notice to the index page. |
| `notes` | Free text, ignored. |

Rows are sorted by `start_page`. Text before the first topic becomes a `Front matter` page when it is longer than about 200 characters.

## Proposing topics for a weak PDF

Use `pages-digest.md` (page numbers, detected headings, opening text of each page).

1. Group consecutive pages by subject. Aim for 5 to 30 topics; fewer pages per topic is better than very long topics.
2. Title each topic in sentence case, 8 words or fewer, using words found in the text. Do not invent content.
3. Set `start_page` to the first page of the subject, `level` to 1 unless it is clearly a sub-topic, `source` to `ai`, `start_heading` blank.
4. Boundaries are at page level. Say so when a subject starts mid-page.
5. Show the list to the user and wait for approval before building. Never build from an unconfirmed AI proposal.

## How structure is detected

1. PDF bookmarks, when two or more top-level entries exist (uses pypdf).
2. Otherwise heading font sizes: the most common size is body text; lines at least 12 percent larger, or short bold lines, are headings; up to three sizes become levels 1 to 3. Sections (levels 1 and 2) become topics when that gives between 2 and 40 topics (change with `plan --max-topics N`); otherwise only level 1 headings do.
3. Otherwise `weak`: the agent proposes topics.

Running headers, footers and bare page numbers (top or bottom 8 percent of the page, repeated on many pages) are removed.

## Output layout

Common to both formats: `images/` (when pictures were extracted), the PDF copy (so page links work, skip with `build --no-pdf-copy`), `topics.xlsx`, `manifest.json` (every file with its kind), `validation.json`.

`--format agent-md`:

```text
<document>/
  index.md             front matter + topic list: link, PDF pages, one-line description; "Not converted" list
  01-<topic>.md ...    YAML front matter, one H1, source/summary block, body with "Source: PDF page N" links, previous | index | next
  chunks.jsonl         one JSON object per chunk (about 1800 characters or less, split at headings and paragraphs, never inside a table)
  validation.md        status, character counts, image-only pages, warnings
```

`--format html`:

```text
<document>/
  index.html           cover with topic cards
  01-<topic>.html ...  sidebar TOC, breadcrumbs, summary, content, previous/next
  style.css            shared stylesheet (responsive, print)
  validation.html      conversion report
```

`--format markdown-basic` is the original layout (index.md and topic pages without front matter).

Summary rule (deterministic): the first one to three sentences of the topic's own prose, at most 280 characters; for a table-only topic, "Table with columns: ..."; for a list-only topic, the first items. Keywords: the 8 most frequent non-stop-words in the topic.

Formatting rules applied to the text: wrapped lines are joined into paragraphs and list items; list nesting follows the indent on the page (numbered steps, bullets, lettered items); `Image N` labels stay as their own italic lines; a Contents page becomes an indented list with dot leaders turned into `(p. N)`; ruled tables become pipe tables (Markdown) or `<table>` (HTML).

Page links use `file.pdf#page=N`, which opens the right page in most browsers and PDF viewers (some viewers ignore the page number). Keep the PDF in the same folder as the pages or the links break.

File names are lower-case, ASCII, and free of characters SharePoint rejects (`# % * : < > ? / \ | " ~ & { }`).

## Images

Deterministic; same PDF and flags give identical files.

1. **Embedded pictures** are read with pdfplumber/pdfminer. A JPEG in the PDF is written unchanged (`.jpg`); other encodings are decoded and saved as PNG; if decoding fails the picture's page region is rasterized (`kind` is `rendered` in the manifest and validation report).
2. **Skipped as decorative**: source size under `--min-image-px` (default 64) on either side; shown smaller than 24 pt on the page; the same picture (SHA-256) on at least 3 pages and at least 40% of the pages (logos, watermarks). Counts are in `validation.json` under `images`.
3. **Duplicates**: identical pictures are written once; every place they appear links to the same file.
4. **Vector figures** (`--vector-figures`): clusters of at least 6 lines, rectangles or curves, at least 80 x 60 pt, outside tables and not overlapping an extracted picture, are rasterized at `--image-dpi` (default 150) with 6 pt padding. Text inside the figure also stays in the page text. Off by default: shaded boxes and borders can be mistaken for figures.
5. **Names**: `images/<topic-file-stem>-p<page>-<n>.<ext>`, numbered per page within the topic. They change only if the topic list changes.
6. **Captions**: a text line starting "Figure/Fig./Image/Chart/Diagram/Photo/Screenshot/Illustration N" within 40 pt below or 24 pt above the picture becomes its caption and alt text, and is shown with the picture rather than repeated in the body. Otherwise alt text is `Figure on page N` and there is no caption line.
7. **Placement**: pictures are placed at their vertical position among the page's text lines. Multi-column pages can place them imprecisely; the validation report lists pages with both text and images for checking.

Markdown: `![alt](images/name.png)` then, when a caption exists, `*caption*` on the next line. HTML: `<figure><img src="images/name.png" alt loading="lazy"><figcaption>...</figcaption></figure>`; the figcaption is the caption or the alt text. Both use relative paths, so the folder works offline when copied as a whole.

## Limits and troubleshooting

- Scanned pages (no text) are listed as warnings. Tesseract may exist for OCR, but OCR text has no font sizes, so heading detection will not work on it.
- Two-column layouts may interleave columns. Report this if body text reads out of order.
- Ruled tables (cell borders drawn in the PDF) are kept as tables; tables without ruling lines become plain lines of text.
- Images are extracted (see [Images](#images)). Text inside a picture is not read: no OCR is run, even where tesseract is installed. Pages that are only images (scans, screenshots) come out as pictures with no text and are listed in `validation.json` under `image_only_pages`. A document with no text layer and extracted pictures passes the check with that warning; with `--no-images` it fails because nothing is left.
- Transparency masks (alpha) of embedded images are not applied. CMYK and indexed-colour images are converted to RGB for PNG output; colours can differ slightly from a print viewer.
- Pictures that could not be extracted leave `*[N image(s) on this page not extracted]*` and are counted under `images.failed`.
- A heading with no text of its own that is directly followed by a deeper topic (a chapter title above its first section) appears in the index as a group heading and gets no page of its own.
- Heading not found on its page: the script splits at the page start and warns. Fix the `start_heading` or clear it.
- Front matter (text before the first topic) becomes the topic "About this manual". Table-of-contents lines with leaders ("Title ____ 6", "Title ..... 6") become links to the matching topic pages (a group heading links to its first page); leader lines and printed page numbers are dropped, and they are left out of the card summary.
- Several topics starting on the same page (e.g. a chapter heading and two sub-headings on one page): each topic's heading is searched only after the previous topic's start, so a heading text that also appears inside an earlier topic's intro no longer steals its split. Fixed Nov 2026 (CEIS manual: "User Role (Type)" came out empty).
- SharePoint publishing: pages go to Site Pages and every other file to Site Assets, same folder path in both (e.g. `Manuals/CEIS`); see "Publishing HTML to a SharePoint site" in SKILL.md. Uploaded Site Pages files are checked out to the uploader: check every file in (`checkInAs: published`) before `verify`; `verify` fails on any file not published.
- `FAIL` means less than 98 percent of the extracted text reached the pages, or a topic is empty. The staging folder is kept for diagnosis.
- Very large PDFs (hundreds of pages) are slow; convert one file at a time.
