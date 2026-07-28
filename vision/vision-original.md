# Vision: From Documents to Content-Centric Knowledge

This merges `plan.md` (content-centric knowledge management) and `plan-part2.md` (Copilot Studio /
M365 agent knowledge access) into one vision, and maps both onto the actual workflow this repo is
building — see `docs/superpowers/specs/diagrams/docx-to-content-workflow.png`
(`.mmd` source alongside it). The two plans are not separate initiatives; Part 2 is the concrete
payoff case that only becomes possible once Part 1's separation is real.

## The Problem (from `plan.md`)

Organizations have accumulated hundreds or thousands of Word-authored documents over years —
policies, procedures, manuals, training materials. Content and formatting are authored together in
one file, so:

- Template changes require updating every document individually
- Consistency erodes over time; formatting consumes effort that should go to accuracy
- Documents go stale, accumulate broken links, drift into outdated formats
- AI tools must process heavy Word/PDF files instead of clean structured text — expensive and
  low-quality for retrieval
- These documents were designed in an era before AI/Copilot agents existed as consumers of them
  at all

## The Shift: Content + Template + Renderer

Instead of `Content + Formatting = Document`, separate into three independent layers
(`plan.md`, Layers 1–3):

1. **Content** — pure business knowledge (policy text, procedure steps, training material),
   no formatting concerns
2. **Templates** — presentation standards (heading structure, numbering, fonts, layout, branding)
   defined once, reused across many content items
3. **Renderer** — combines Content + Template into a Published Output: HTML, Word, PDF, training
   packages, audio scripts, chat-based assistance — whatever the destination needs

This is not a free win. People have authored documents in the comfortable, familiar
content+formatting-together model for decades; separating them is genuine friction and change
management (`plan.md`, "Challenges"). **The hypothesis this POC tests is whether that disruption
is worth it** — using the CEIS Manual as the concrete evidence-gathering vehicle. If the resulting
content can't actually support multiple different renderers without rework, the hypothesis isn't
being tested, it's being asserted.

## Why the Extraction Alone Isn't the Content (the transitory-format insight)

Converting a `.docx` through pandoc produces raw markdown that mirrors whatever heading/section
structure happened to exist in that particular Word document — arbitrary and inconsistent across
documents. That raw extraction is **transitory**, not the content artifact itself. Something has
to analyze it and map it onto a defined content template's expected shape (a Policy template's
slots differ from a Procedure template's slots) before it's real, reusable "Content" in the
Layer 1 sense. This is why the workflow diagram has an explicit **Analyze → Map into Template**
stage between raw extraction and canonical content, authored/maintained separately by a
**Template Creator** — templates are reusable artifacts, not something derived fresh per document.

## The Payoff: Knowledge Access Through Conversational AI (from `plan-part2.md`)

Once content exists as clean, structured, AI-consumable material — not buried in heavy Word/PDF
files — it can ground a Copilot Studio / M365 agent that provides:

- Policy and procedure support, grounded in approved source material
- Guided, step-by-step assistance through business processes
- Just-in-time training support and knowledge reinforcement
- Generated quizzes and knowledge checks
- Faster knowledge discovery — asking a question directly instead of searching/reading entire
  manuals

This only works if the grounding source is the **canonical, template-mapped Content +
Metadata** (`chunk_id`, `source_heading_path`, `topic`) — not the raw transitory pandoc
extraction, which lacks the structure a retrieval system needs and still carries extraction noise.
The workflow diagram marks this explicitly: the canonical Content node is the grounding source: the
raw extraction only feeds the mapping step, it doesn't feed the agent directly.

Plan Part 2 frames its own pilot approach the same way Part 1 does: a limited pilot with a small
user group, validating response quality/consistency/adoption/training effectiveness before wider
rollout — not a big-bang deployment.

## Success Criteria (combined)

**Part 1 (content):** reduced maintenance effort, faster updates, consistent formatting, better
content reuse, improved AI usability, improved author productivity, reduced publishing effort.

**Part 2 (agent access):** response accuracy, response consistency, user adoption, training
effectiveness, user satisfaction, operational value, cost effectiveness.

## The Combined Key Question

Should knowledge be treated as documents, or as structured content that can be rendered into many
outputs — including a conversational agent — as needed? This repo's Phase 1 work (see the design
spec at `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design.md`) is the first real
evidence toward answering that, using the CEIS Manual as the pilot case for both plans at once.
