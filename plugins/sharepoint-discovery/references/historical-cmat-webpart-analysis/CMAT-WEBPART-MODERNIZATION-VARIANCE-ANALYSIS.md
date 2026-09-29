# CMAT CEWP/SEWP Modernization Variance Analysis

## Purpose

This note is intended to be handed to another agent to update `ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md` and the related analysis documents. It classifies all 121 Content Editor and Script Editor web-part instances, using the 38 functional groups already defined in the source analysis.

## Direct answer

**17 of the 121 web-part instances can be replaced directly by the modern SharePoint Online Text web part.** These 17 instances are represented by **14 unique functional groups: Groups 11-13 and 28-38**.

That is:

- **17 / 121 instances = 14.0%** direct Text web-part replacements.
- **14 / 38 unique groups = 36.8%** direct Text web-part replacement patterns.
- **31 / 121 instances = 25.6%** are empty or hidden placeholders and should not be migrated.
- Combining direct Text replacements and removals, **48 / 121 instances = 39.7%** require no custom implementation.
- The remaining **73 / 121 instances = 60.3%** are not Text web-part scenarios. They require analysis against modern list formatting, native list and form behavior, Power Apps, Power Automate, permissions, or SPFx only as a last resort.

Do not describe all 121 items as "unique cases." The source identifies **121 instances grouped into 38 unique functional patterns**.

## Category totals from the source analysis

| Source category | Unique groups | Instances | Text web part alone? | Primary disposition |
|---|---:|---:|---|---|
| Empty | 1 | 31 | No, and none is needed | Remove or do not migrate |
| TextOnly | 14 | 17 | Yes | Modern Text web part |
| ExternalHelpersOnly | 14 | 51 | No | Reproduce business outcome with modern list configuration, JSON formatting, native field types, permissions, Power Platform, or defer |
| InlineLogic | 9 | 22 | No | Power Apps or supported configuration for form logic; permissions or SPFx Command Set only when command behavior is genuinely required |
| **Total** | **38** | **121** | **17 instances** | |

## Important interpretation

The fact that a legacy item lived in a Content Editor web part does not mean it was content. Most Content Editor instances were being used as script loaders. Only the `TextOnly` category is a direct modern Text web-part mapping.

The modern target should reproduce the required business outcome, not the old DOM manipulation. For example:

- Conditional colouring is a list-formatting requirement, not a Text web-part requirement.
- Hiding links is either a presentation decision or a security requirement. If it is security, it must be enforced by permissions, not cosmetic hiding.
- Renaming classic commands is usually a usability preference and may be accepted as a modern UI variance.
- Parent-to-child lookup prefill is form behavior, not page text.
- Preventing changes to closed cases is a business rule, not merely command-bar presentation.

## Required document update structure

For every group in `ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md`, add these fields below the existing representative code:

- **Business behavior**
- **Text web part sufficient:** Yes or No
- **Recommended modern replacement**
- **MVP decision:** Keep, simplify, remove, defer, or pending business validation
- **SPFx candidate:** No, Conditional, or Yes with justification
- **Validation required**
- **Evidence gap or caveat**

The detailed group-by-group disposition follows.

# 1. Empty

## Group 1 - Empty - 31 instances

- **Representative:** `/cmat/Lists/PIO_Approval_Requests/DispForm.aspx`
- **Business behavior:** The analysis classifies these as empty or hidden placeholders with no content and no functional impact.
- **Text web part sufficient:** No. A replacement is unnecessary.
- **Recommended modern replacement:** Do not migrate.
- **SPFx candidate:** No.
- **Validation:** Confirm the extracted content is actually empty and that no external CSS or page script selected the web-part container by ID. Once confirmed, remove it from the MVP inventory.

# 2. TextOnly

All 17 instances in this category are direct modern Text web-part candidates. WYSIWYG editing is appropriate. Rebuild the content on a modern page rather than carrying the classic Content Editor web part forward.

## Group 11 - TextOnly - 2 instances

- **Pages:** `/cmat/Pages/PIO_Cases.aspx`, `/cmat/Pages/My_PIO_Cases.aspx`
- **Content:** Instruction telling users to ensure Subjects and Affected Persons exist in the ITAU Persons Database before adding a case.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part with a hyperlink to the modern Persons page.
- **Variance:** Update the destination URL and verify whether "ITAU Persons Database" remains the correct product wording for PIO pages.

## Group 12 - TextOnly - 2 instances

- **Pages:** `/cmat/Pages/Add_Edit_Persons.aspx`, `/cmat/Pages/All_Persons.aspx`
- **Content:** Search instruction explaining use of `*` for an incomplete name search.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part.
- **Variance:** Validate whether modern SharePoint search or list filtering still uses the same wildcard behavior. If not, rewrite or remove the instruction rather than copying inaccurate guidance.

## Group 13 - TextOnly - 2 instances

- **Pages:** `/cmat/Pages/ITAU_Cases.aspx`, `/cmat/Pages/My_ITAU_Cases.aspx`
- **Content:** Same precondition notice as Group 11, with a link to the Persons page.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part with updated modern-page link.
- **Variance:** Groups 11 and 13 may be one reusable content pattern even though their legacy HTML signatures differ.

## Group 28 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/ICM_My_Tasks.aspx`
- **Content:** "Covering for someone?" link to all ICM, ITAU and PIO tasks and progress logs.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part. Quick Links or Button is also acceptable if the modern design uses stronger navigation affordance.
- **Variance:** Update the destination to the new consolidated tasks page.

## Group 29 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/ICM_My_Approval_Requests.aspx`
- **Content:** "Covering for someone?" link to all ICM, ITAU and PIO approval requests.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part, Quick Links, or Button.
- **Variance:** Confirm the consolidated approval-request page remains in MVP.

## Group 30 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/Reference_Material_and_Templates.aspx`
- **Content:** Three links to Supervisor, PIO, and ITAU reference material and template locations.
- **Text web part sufficient:** Yes.
- **Preferred modern replacement:** Quick Links may provide a better modern navigation experience, but Text alone is sufficient.
- **Variance:** All three legacy library URLs must be mapped to their SharePoint Online destinations.

## Group 31 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/portal.aspx`
- **Content:** CMAT support contact plus instructions about full-screen mode and using the emblem/title to return to the portal.
- **Text web part sufficient:** Yes for the content.
- **Variance:** Revalidate every instruction. The F11 browser instruction may be unnecessary, and modern site navigation may replace the emblem/title behavior. Keep the support contact only if current.

## Group 32 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/PIO_My_Tasks.aspx`
- **Content:** "Covering for someone?" link to all PIO tasks and progress logs.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part, Quick Links, or Button.

## Group 33 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/ITAU_My_Tasks.aspx`
- **Content:** "Covering for someone?" link to all ITAU and PIO tasks and progress logs.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part, Quick Links, or Button.

## Group 34 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/Manage_Security_Alerts.aspx`
- **Content:** Note that Security Alerts can have PDF attachments.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part.
- **Variance:** Confirm whether "can have" should be "must have" based on the current business rule.

## Group 35 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/Briefings_and_Security_Alerts.aspx`
- **Content:** Multi-item operational guidance covering email notification, handling confidential information in attachments, PDF attachment expectations, where briefings appear, and opening attachments.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part.
- **Variance:** This content needs business and privacy review before migration. Modern attachment behavior may make the right-click instruction obsolete. Do not copy stale operational instructions unchanged.

## Group 36 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/PIO_My_Approval_Requests.aspx`
- **Content:** "Covering for someone?" link to all PIO approval requests.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part, Quick Links, or Button.

## Group 37 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/ITAU_My_Approval_Requests.aspx`
- **Content:** A static notes block. The generated summary truncates the sample after "Notes:".
- **Text web part sufficient:** Yes based on the `TextOnly` classification.
- **Modern replacement:** Text web part.
- **Evidence gap:** The other agent must copy the full source text from the representative code and summarize it accurately. Do not retain the truncated generated description.

## Group 38 - TextOnly - 1 instance

- **Page:** `/cmat/Pages/ITAU_My_Approval_Requests.aspx`
- **Content:** "Covering for someone?" link to all ITAU and PIO approval requests.
- **Text web part sufficient:** Yes.
- **Modern replacement:** Text web part, Quick Links, or Button.

# 3. ExternalHelpersOnly

None of these 51 instances can be replaced by the Text web part alone. They load JavaScript that changes list views, links, command labels, attachments, or parent-child navigation.

The source analysis repeatedly recommends modern list column/row formatting first and SPFx only if the required effect cannot otherwise be achieved. That recommendation must be made per helper function, not per legacy Content Editor container.

## Group 2 - ExternalHelpersOnly - 14 instances

- **Helpers:** `ConditionalColoring.js`, `HideLinksToPersons.js`
- **Behavior:** Applies conditional list-cell or row colouring and removes links to Person detail records in selected views.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON column/row formatting for colouring. For person links, use a modern field/view design that renders plain text, or accept the link if it causes no business or security problem.
- **Security note:** Hiding a hyperlink is not access control. If users must not open Person records, enforce permissions.
- **SPFx candidate:** Only if a confirmed requirement cannot be met through field/view configuration or permissions.

## Group 3 - ExternalHelpersOnly - 11 instances

- **Helpers:** Group 2 helpers plus `NewItemToAddNewHeadingChanger.js`.
- **Behavior:** Conditional colouring, removal of Person links, and renaming classic "New Item" wording.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON formatting and permissions/view configuration. Treat command renaming as an MVP UX variance unless business validation proves the exact label is essential.
- **SPFx candidate:** No for colouring; conditional only for command customization after accepting or rejecting the modern label.

## Group 5 - ExternalHelpersOnly - 7 instances

- **Helpers:** Group 3 helpers plus `showattachmentname.js`.
- **Behavior:** Colouring, hidden Person links, renamed create command, and display of attachment file names in list rows.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON formatting where supported, a modern attachment/link column or view, and standard modern command labels where acceptable.
- **Validation:** Determine whether users need only an attachment indicator, the actual filename, or direct opening of the attachment. These are different requirements.
- **SPFx candidate:** Conditional only if the required attachment presentation cannot be achieved with modern lists and formatting.

## Group 6 - ExternalHelpersOnly - 6 instances

- **Pages:** The six My/All ICM, PIO, and ITAU case pages identified in the source.
- **Helpers:** `ConditionalColoring.js`, `HideLinksToPersons.js`, new-item and new-task heading changers, `RLHelper-ParentDisplayForm.js`, and `showattachmentname.js`.
- **Behavior:** A bundle of unrelated concerns: formatting, link suppression, command labels, attachment display, and parent-to-child navigation/prefill.
- **Text web part sufficient:** No.
- **Modern replacement:** Decompose into separate requirements. Use JSON formatting for display, standard modern commands where acceptable, native attachment behavior, and Power Apps/page-parameter design for parent-child creation.
- **SPFx candidate:** Do not port the bundle as one SPFx component. Consider a reusable component only for a confirmed gap after decomposition.

## Group 7 - ExternalHelpersOnly - 3 instances

- **Helpers:** `HideLinksInDisplayForm.js`, `HideLinksToPersons.js`
- **Behavior:** Removes edit/delete or list-form links while leaving displayed labels.
- **Text web part sufficient:** No.
- **Modern replacement:** Permissions and form/view configuration.
- **Security note:** If the intent is to stop modification, cosmetic link hiding is insufficient. Enforce the rule using permissions or form behavior.
- **SPFx candidate:** No unless the business requires a presentation-only difference that modern configuration cannot provide.

## Group 10 - ExternalHelpersOnly - 2 instances

- **Helpers:** `ConditionalColoring.js`, `HideLinksToPersons.js`, `NewTasktoAddNewHeadingChanger.js`, `showattachmentname.js`.
- **Behavior:** Formatting, link suppression, task command relabeling, and attachment filename presentation on briefing/security-alert pages.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON list formatting, native modern attachment behavior, permissions where needed, and acceptance of modern command wording.
- **SPFx candidate:** Conditional only for a validated attachment or command gap.

## Group 14 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Lists/ITAU_Cases/SIO_Case_Involvement.aspx`
- **Helper:** `link_case.js`
- **Behavior:** The generated analysis marks the helper as unrecognized and says its source must be inspected directly.
- **Text web part sufficient:** No.
- **Modern replacement:** Pending source review. Likely candidates include a native lookup link, JSON hyperlink formatting, or modern list configuration, but this must not be asserted until the script is read.
- **SPFx candidate:** Undetermined. This is an evidence gap, not an automatic SPFx requirement.

## Group 15 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Lists/Security_Alerts/DispForm.aspx`
- **Helpers:** `HideLinksInDisplayForm.js`, `HideLinksToPersons.js`
- **Behavior:** Removes classic action/detail links.
- **Text web part sufficient:** No.
- **Modern replacement:** Permissions plus modern form/view configuration.
- **SPFx candidate:** No unless a presentation-only link suppression requirement survives validation.

## Group 16 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Pages/Appearing_Persons_Briefing.aspx`
- **Helpers:** `ConditionalColoring.js`, `NewItemToAddNewHeadingChanger.js`, `RLHelper-ParentDisplayForm.js`
- **Behavior:** Conditional display, command relabeling, and parent-context propagation to a child form.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON formatting, accept standard command labels where possible, and Power Apps/page parameters for parent-child prefill.
- **SPFx candidate:** Conditional only after the parent-child interaction is prototyped with supported form capabilities.

## Group 17 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Pages/Persons_PIO.aspx`
- **Helpers:** `ConditionalColoring.js`, `NewItemToAddNewHeadingChanger.js`, `RLHelper-ParentDisplayForm.js`, `link_Case.js`, `makehyperlink.js`, `showattachmentname.js`.
- **Behavior:** A composite Persons page pattern covering list formatting, command wording, parent-child creation, case links, URL conversion, and attachment display.
- **Text web part sufficient:** No.
- **Modern replacement:** Decompose into JSON formatting, hyperlink field/formatting, native attachments, and Power Apps/page-parameter patterns.
- **Evidence gap:** `link_Case.js` must be inspected and its exact destination/query-string behavior documented.
- **SPFx candidate:** Conditional. Do not create one monolithic replacement for the legacy bundle.

## Group 18 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Pages/Manage_Security_Alerts.aspx`
- **Helpers:** `ConditionalColoring.js`, `HideLinksToPersons.js`, `NewTasktoAddNewHeadingChanger.js`.
- **Behavior:** Formatting, link suppression, and command relabeling.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON formatting, permissions/view design, and acceptance of modern command wording.
- **SPFx candidate:** Unlikely for MVP.

## Group 19 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Pages/Purge_Planning.aspx`
- **Helpers:** `ConditionalColoring.js`, `NewItemToAddNewHeadingChanger.js`, `makehyperlink.js`, `showattachmentname.js`.
- **Behavior:** Formatting, command relabeling, converting URL text into links, and attachment filename display.
- **Text web part sufficient:** No.
- **Modern replacement:** Hyperlink columns or JSON link formatting, JSON status formatting, native attachments, and standard command labels.
- **SPFx candidate:** Conditional only for a confirmed attachment presentation gap.

## Group 20 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Pages/Persons_ICM.aspx`
- **Helpers:** `ConditionalColoring.js`, `NewItemToAddNewHeadingChanger.js`, `link_Case.js`, `makehyperlink.js`, `showattachmentname.js`.
- **Behavior:** Formatting, command wording, related-case navigation, URL conversion, and attachment display.
- **Text web part sufficient:** No.
- **Modern replacement:** JSON formatting, native hyperlink fields, native attachment behavior, and a validated related-case navigation pattern.
- **Evidence gap:** Inspect `link_Case.js` and document its exact behavior before selecting the replacement.
- **SPFx candidate:** Conditional.

## Group 21 - ExternalHelpersOnly - 1 instance

- **Page:** `/cmat/Pages/Persons_ITAU.aspx`
- **Helpers:** `ConditionalColoring.js`, `NewItemToAddNewHeadingChanger.js`, `link_case.js`, `makehyperlink.js`, `showattachmentname.js`.
- **Behavior:** Same broad concern set as Group 20, but using a differently named case-link helper.
- **Text web part sufficient:** No.
- **Modern replacement:** Same decomposition as Group 20.
- **Evidence gap:** Determine whether `link_case.js` and `link_Case.js` are behaviorally different or only filename/case variants. Merge the modernization requirement if they are equivalent.
- **SPFx candidate:** Conditional.

# 4. InlineLogic

None of these 22 instances can be replaced by the Text web part alone. However, the category does not mean all 22 need SPFx.

## Group 4 - InlineLogic - 10 instances

- **Helper/logic:** `RLHelper-ChildNewForm.js` and inline `fillfromParent()` call.
- **Behavior:** Reads parent context from the query string and prepopulates a Related Case or Related Person lookup on child New forms.
- **Text web part sufficient:** No.
- **Modern replacement:** Power Apps customized form using page parameters and a reusable prefill pattern. Prototype once, then apply consistently to all affected lists.
- **Caveat:** The existing generated report mentions a Power Automate flow "triggered on form load." The updating agent must verify that statement rather than copying it as fact. The key requirement is prepopulation before submission.
- **SPFx candidate:** No unless a supported customized-form pattern fails a validated requirement.

## Group 8 - InlineLogic - 3 instances

- **Pages:** PIO, ITAU, and ICM Case Edit forms.
- **Behavior:** Watches Status. When Status becomes Closed, sets Case Closed Date to the current date and makes the field read-only; changing away from Closed unlocks it. Commented code for other fields is inactive.
- **Text web part sufficient:** No.
- **Modern replacement:** Shared Power Apps customized-form pattern. Consider server-side or workflow enforcement as a second control if the date is a business rule that must hold outside the form.
- **SPFx candidate:** No.
- **Validation:** Confirm whether reopening a case is allowed and what should happen to the closed date when reopened.

## Group 9 - InlineLogic - 3 instances

- **Pages:** ITAU, PIO, and ICM Narrative New forms.
- **Behavior:** Same parent-context lookup prefill pattern as Group 4 with a different code signature.
- **Text web part sufficient:** No.
- **Modern replacement:** Reuse the same Power Apps/page-parameter pattern as Group 4.
- **SPFx candidate:** No unless prototyping proves a supported form cannot meet the requirement.

## Groups 22-27 - InlineLogic - 6 instances total

These six groups appear separately because of page or helper-signature differences, but they represent one modernization requirement.

### Group 22

- **Page:** `/cmat/Pages/My_ICM_Cases.aspx`

### Group 23

- **Page:** `/cmat/Pages/ICM_Cases.aspx`

### Group 24

- **Page:** `/cmat/Pages/PIO_Cases.aspx`

### Group 25

- **Page:** `/cmat/Pages/My_PIO_Cases.aspx`

### Group 26

- **Page:** `/cmat/Pages/ITAU_Cases.aspx`

### Group 27

- **Page:** `/cmat/Pages/My_ITAU_Cases.aspx`

### Shared behavior and disposition

- **Behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons. The page also loads a case-link helper.
- **Text web part sufficient:** No.
- **Business-rule question:** Is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Preferred modern replacement:** Enforce the business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **SPFx candidate:** A reusable List View Command Set is conditional only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Critical security note:** Hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization.
- **Consolidation:** Document Groups 22-27 as six deployments of one functional pattern, not six separate components.

# 5. Modernization pattern roll-up

The 38 source groups reduce to a much smaller set of modern requirements:

1. **No-op placeholders:** 31 instances. Remove.
2. **Static instructions and links:** 17 instances. Text web part is sufficient; Quick Links or Button may be preferable for navigation-heavy items.
3. **Conditional visual formatting:** Repeated throughout the 51 helper-only instances. Use JSON column/row formatting.
4. **Hide links:** Treat as view design if cosmetic and permissions if security-related.
5. **Rename classic commands:** Usually accept the modern command label; customize only with a validated business reason.
6. **Attachment filename presentation:** Validate the real user need, then use native attachment behavior or formatting before considering SPFx.
7. **Plain-text URL to hyperlink:** Use hyperlink fields or JSON formatting.
8. **Parent-child lookup prefill:** 13 inline instances plus parent helper usage. Implement as one reusable Power Apps/page-parameter pattern.
9. **Closed-date form rule:** 3 inline instances. Implement as one shared Power Apps pattern, with rule enforcement if required.
10. **Closed-case command suppression:** 6 inline instances. Prefer actual rule enforcement; one reusable SPFx Command Set only if exact hiding is essential.
11. **Related-case link helpers:** Inspect `link_case.js`, `link_Case.js`, and related variants, then map to native lookup/hyperlink formatting where possible.

# 6. What the updating agent must correct or add

1. State clearly that **17 instances, not most of the 121, are direct Text web-part replacements**.
2. Preserve the distinction between **121 deployed instances** and **38 unique functional groups**.
3. Add a roll-up showing that **48 instances require no custom implementation**: 31 removed plus 17 Text replacements.
4. Do not label all helper-only groups as SPFx candidates. Decompose their helper functions and evaluate modern supported equivalents.
5. Merge Groups 22-27 into one modernization pattern while preserving the six source group IDs for traceability.
6. Merge Groups 4 and 9 at the design level as one reusable parent-context prefill pattern while preserving source traceability.
7. Flag Group 14 and the `link_case.js`/`link_Case.js` variants as evidence gaps requiring direct source inspection.
8. Validate Group 37's complete notes text because the generated summary is truncated.
9. Remove or qualify any unsupported procedural claim, especially the phrase about a Power Automate flow being triggered on form load.
10. Add an explicit rule: SPFx is considered only after removal, modern OOB web parts, list/form configuration, JSON formatting, permissions, Power Apps, Power Automate, and acceptable UX simplification have been assessed.

# 7. Suggested executive summary for the main document

> The 121 legacy Content Editor and Script Editor web-part instances represent 38 unique functional patterns. Only 17 instances, across 14 patterns, are static text or links that map directly to the modern SharePoint Online Text web part. Another 31 instances are empty placeholders and should not be migrated. This means 48 of 121 instances require no custom implementation. The remaining 73 instances contain script-driven behavior and must be assessed by business outcome. Most recurring concerns are conditional list formatting, link presentation, command wording, attachment display, parent-child form prefill, and closed-case rules. These should be implemented using supported modern SharePoint configuration, JSON formatting, permissions, Power Apps, or Power Automate where appropriate. SPFx should be reserved for a small number of confirmed MVP gaps, particularly where exact context-sensitive command behavior cannot be achieved through supported configuration or acceptable UX simplification.

# 8. Source traceability

This analysis is based on:

- `ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW.md`
- `webpart-code-analysis.md`
- `webpart-code-groups.json`
- `webpart-instance-review.csv`

Before finalizing Jira estimates or SPFx scope, reconcile this analysis with the latest production extraction and inspect all helper files currently marked unrecognized.
