# Dynamic page migration: web-part mapping and SPFx gate

How to decide, with the user, what each classic web part becomes on the modern page. Source files: `inventory\webpart-mapping.json` (mapping, recorded `decisions`, `spfxGate`, `existingSpfx`) and [spo-webparts.json](../spo-webparts.json) (official SPO web parts and `suggestions`).

## Contents

- [Mapping sources](#mapping-sources)
- [Asking per instance](#asking-per-instance)
- [Preference order](#preference-order)
- [SPFx gate (hard stop)](#spfx-gate-hard-stop)
- [BC accordion configuration](#bc-accordion-configuration)

## Mapping sources

- `inventory\webpart-mapping.json` is the mapping source (options, recommended default, SPFx requirement, recorded `decisions`). `spo-webparts.json` is the full list of official SharePoint Online web parts, grouped by the page toolbox sections, with a suggested choice and alternatives per classic web part (`suggestions`).
- Always use the official names when asking (for example "Text", "Embed", "Hero", "List", "FAQ"), never internal ids; each option's `spoWebPart` field gives the official name. The classic Content Editor defaults to the modern **Text** web part.
- A `recommended` value is a suggestion only. Never assume or auto-apply it, even when a prior `decisions` entry exists (show it as the previous answer and ask to reuse or change). Unknown or unclear mapping: ask, never guess. Answers are written back to the mapping file.
- Plain language: write every question so a non-developer can answer it (no jargon, no file-internal ids, say what each choice will do). A source and destination that differ on purpose (for example PROD on-prem copied to SPO DEV) is the normal case, not an error.

## Asking per instance

For each instance of each web part on the downloaded page (page order: zone, then part order), look it up in `inventory\webpart-mapping.json` and `ask_user`, one instance at a time.

- A page can hold several web parts of the same type (two Content Editors, several accordions); quote each instance's title and a short content preview, and offer "Apply to the rest of this type on this page" as its own option, never assumed.
- Show the suggested web part and its alternatives from `spo-webparts.json` (`suggestions`) with the one-line `why`; mark the suggestion "[Recommended]". Offer only a short list: the suggestion, its alternatives, "Drop it", and "Something else (browse by category)". Never put the full list in one dropdown.
- Only if the user picks "Something else", ask a second question listing the `toolboxSections` categories, then a third listing only that category's web parts.
- Put choices in the form options, not the message text, which may not be displayed; if a form is cancelled, give the choices as plain chat text. Map the chosen name to the option in `inventory\webpart-mapping.json`. Wait for the answer; never proceed on silence.
- Entries with `requiresDecision: true` (no recommendation) must be chosen by the user; a web part with no entry needs an explicit disposition. Record every answer by appending to `decisions` in `inventory\webpart-mapping.json` (see its `decisionsGuide`). If a web part has no entry, ask how to handle it, add it to `unmapped`, and stop for that web part; once analysed, add a `webParts` entry.
- Components whose disposition is not `convert` or `replace-native` are listed for their own workstream, not converted here.

## Preference order

`spfxGate.preferenceOrder`: an OOTB SPO web part first, then an existing SPFx solution (`existingSpfx` lists every project under `spfx\webparts`, `spfx\extensions` and `spfx\html`, with its status), and a new SPFx web part only when neither fits and the user agrees.

## SPFx gate (hard stop)

If the chosen option has `requiresSpfx: true` and `spfxProject` is null (or the solution is not deployed and added to the site), STOP. Do not convert or publish the page.

1. Check `existingSpfx` first; an option with `reviewRequired: true` (such as the Enterprise MyFavDocs candidate) needs the user's review before use.
2. If nothing fits, tell the user which web part is needed and start the design conversation.
3. With the user's agreement, build it with the installed `.agents\skills` SPFx skills (`spfxGate.scaffoldSkills`/`buildSkills`) and BC Design System components (`design-system-react`, `standard-design-system`), then follow `spfxGate.deploymentSteps` in order: (1) the agent packages it with `sharepoint-package-spfx-solution`; (2) the user uploads the `.sppkg` to the App Catalog; (3) the user adds the app to the site; (4) only after the user confirms both, the agent adds the web part to the page. Record its path as `spfxProject`.

## BC accordion configuration

A page can hold several accordion instances (for example Operations-Policy-Manual: a Text notice, a 12-item two-column accordion, and a one-item Appendices accordion that is open by default). When recommending the BC accordion for an instance, analyse the source markup and propose its configuration one accordion at a time: `columns` (1 or 2, from the source layout), per-section `defaultOpen` (sections open in the source), per-section `badge` text such as "NEW!" (a red tag from coloured/bold suffix text in the source title), plus `showButtons`, `allowMultiple` and `startExpanded`. Record the settings in the decision and in the page plan so the publish step can set the web part properties. Rich-text titles and open-by-default need the amended `bc-accordion-group` (map-debt SPMIG-23); until deployed, note them as pending rather than dropping them.
