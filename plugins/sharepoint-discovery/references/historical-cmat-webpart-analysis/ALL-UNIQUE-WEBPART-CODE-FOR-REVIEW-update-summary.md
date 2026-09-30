# ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md — Update Summary

> Companion to the 2026-07-16 update that added a **"Modernization Behaviour Analysis"** section under all 38 groups, explaining each script's behavior from a user/business perspective rather than just listing filenames.

## Groups updated

All 38 groups received a new "Modernization Behaviour Analysis" section (User-visible effect / Business intent / Actual enforcement level / Modern SPO approach / SPFx assessment / Migration note), added directly beneath each group's existing "Modernization Assessment" bullets. No existing content was removed or restructured — group IDs, representative pages, WebPartIds, and source code blocks are all preserved unchanged for traceability.

| Groups | Category | Behaviour theme |
|---|---|---|
| 1 | Empty | No behavior — confirmed do-not-migrate |
| 2, 3, 5, 6, 7, 10, 14–21 | ExternalHelpersOnly | Presentation bundles: conditional colouring, Person-link suppression, command relabeling, attachment filename display, URL-to-hyperlink conversion, case-link navigation (JSLink/CSR) |
| 4, 9 | InlineLogic | Parent-context lookup prefill on child New forms |
| 8 | InlineLogic | Closed-case date stamping + field lock on Edit forms |
| 22–27 | InlineLogic | Closed-case command/action suppression — one pattern, six pages |
| 11–13, 28–38 | TextOnly | Static instructions, "covering for someone" navigation links, reference-material links, support contact/notes |

## Groups where helper code could not be found

None remaining as an open gap. All external helper scripts referenced by the 38 groups were located and read in full in Part 2 of the document (23 files). The two groups that historically carried an "unrecognized helper" evidence gap — Group 14 (`link_case.js`) and the case-link references in Groups 17/20/21 (`link_Case.js`/`link_case.js`) — were already resolved by a prior pass (2026-07-15 variance-analysis merge) and are now further clarified with explicit behavior descriptions in their new Behaviour Analysis sections.

One soft gap remains, not a missing file: Groups 14, 17, 20, and 21 reference the case-link helper under three different filename castings (`link_case.js`, `link_Case.js`) plus the confirmed `linkCase.js` read in Part 2. The current assumption — stated consistently across all four groups' new sections — is that these are casing/reference inconsistencies pointing at the same script, not four distinct scripts. This has **not** been confirmed with a byte-level diff of the actual files on the SP2016 site; that remains a validation task, not a code-reading gap.

## Groups where the analysis changed materially

- **None required a disposition change.** The behaviour analysis pass added explanatory depth (what changes for the user, what business rule is implied, whether it's really enforced) but did not overturn any existing MVP decision, SPFx candidacy, or "Text web part sufficient" verdict from the original Modernization Assessment sections.
- **Groups 22–27** gained the most material new content: each now explicitly states, in plain language, that the closed-case button/link hiding is **presentation-only and must not be treated as security** — this was implicit in the original assessment's "Validation required" note but is now stated directly and repeatedly, since it's the single most likely point of confusion for a business stakeholder skimming the document (a reader could otherwise assume "hides edit buttons" = "prevents edits").
- **Groups 2, 3, 7, 8, 15, 16** (the various "hide links" patterns) now each carry an explicit instruction that cosmetic link-hiding is not a substitute for permissions if the underlying intent is actually access control — previously this was a recurring "Validation required" bullet; it's now framed as a direct actual-enforcement-level statement in each group.
- **Group 22's** new section also separates out `linkPIOCase.js`'s behavior (a CSR/JSLink field renderer building a link to a related PIO case) from the inline closed-case logic — the original Modernization Assessment bullets described both together as one "business behavior," which slightly understated that these are two independent mechanisms coincidentally loaded from the same Content Editor.

## Remaining SPFx candidates after behaviour analysis

No group in this document requires SPFx as a confirmed, unconditional recommendation. The SPFx-last-resort framing from the original Executive Summary holds after the deeper behavioral read:

| Group(s) | Conditional scenario | Prerequisite before considering SPFx |
|---|---|---|
| 22–27 (one shared decision) | A reusable List View Command Set, only if exact context-sensitive closed-case command hiding is confirmed as a hard MVP requirement | Business must first decide whether the real requirement is enforcement (→ permissions/workflow, no SPFx) or cosmetic clutter reduction (→ accept modern command bar, no SPFx) |
| 5, 6, 10, 16, 17, 18–21 | A Field Customizer for the case-link navigation pattern (`linkCase.js`/`linkPIOCase.js`/`link_case.js` family), or a component for attachment presentation | Native lookup rendering, hyperlink columns, and JSON column formatting must be assessed and found insufficient first |
| 4, 9 | None expected | Power Apps `Param()`-driven form prefill is expected to fully cover this; SPFx only if prototyping disproves that |
| 8 | None expected | Power Apps form-rule DisplayMode logic is expected to fully cover this |
| 1, 11–13, 28–38 | None | Text web part / Quick Links covers all of these |

**Net assessment: at most one shared SPFx component (Groups 22–27) and, conditionally, one Field Customizer pattern for the case-link family (Groups 5/6/10/16–21) — not 38, not even close to 38.**

## Reusable patterns that collapse many groups into one modernization decision

1. **Closed-case command/action suppression** (Groups 22, 23, 24, 25, 26, 27) — one pattern, deployed identically (only DOM selector IDs differ) across six dashboard pages. One design decision, one component/rule if needed, retained as six group IDs only for traceability.
2. **Parent-context lookup prefill on child New forms** (Groups 4, 9) — one `RLHelper-ChildNewForm.js`/`fillfromParent()` pattern, differing only in which field it targets ("Related to Case" vs. "Related to Person"). One Power Apps design, two group IDs.
3. **Case-link navigation via JSLink/CSR** (Groups 5, 6, 10, 14, 16, 17, 18–21, plus the `linkPIOCase.js` half of Groups 22–27) — the `linkCase.js`/`linkPIOCase.js`/`link_case.js`/`link_Case.js` family. All render a hardcoded-View-GUID link from a lookup field to a related case. One modernization requirement (native lookup / hyperlink column / JSON formatting, Field Customizer only as fallback), pending a byte-level diff to fully confirm filename-casing variants are truly identical.
4. **"Kitchen sink" ExternalHelpersOnly bundles** (Groups 2, 3, 5, 6, 7, 10, 16–21) — recurring combination of: JSON-formattable colouring, cosmetic Person-link suppression, command relabeling, and attachment-name display. These should be decomposed into four independent, reusable modernization decisions (one per concern) rather than treated as N separate "groups" needing N separate solutions.
5. **"Covering for someone?" navigation links** (Groups 28, 29, 32, 33, 36, 38) — identical text/link pattern pointing at different consolidated task/approval-request pages per business area. One content template, six instances.
6. **Precondition/instruction notes referencing the Persons Database** (Groups 11, 13) — same content, minor HTML variance; one reusable text block.

## Quality bar check

Every group's new section now answers, in plain language: what changes on the page, what user experience results, what business rule or navigation pattern is implied, whether it's actually enforced or only hidden/cosmetic, the simplest supported SPO replacement, and whether SPFx is genuinely required (answer: essentially never, at most twice across all 38 groups, and only conditionally).
