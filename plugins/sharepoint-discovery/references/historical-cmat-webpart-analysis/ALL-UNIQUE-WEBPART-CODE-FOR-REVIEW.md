# All Unique Web Part Code — Manual Review Source

> One representative code sample per unique functional group (38 groups, 121 total web part instances).
> Generated for manual human review — see `PROBLEMATIC-WEBPARTS-SUMMARY.md` Section 7 for findings.

---

---

## Executive Summary (Variance Analysis)

> The 121 legacy Content Editor and Script Editor web-part instances represent **38 unique functional
> patterns**, not 121 unique cases. Only **17 instances, across 14 patterns (Groups 11-13, 28-38), are
> static text or links that map directly to the modern SharePoint Online Text web part**. Another **31
> instances are empty placeholders** and should not be migrated. This means **48 of 121 instances (39.7%)
> require no custom implementation**. The remaining **73 instances** contain script-driven behavior and
> must be assessed by business outcome, not by porting the legacy DOM manipulation directly. Most recurring
> concerns are conditional list formatting, link presentation, command wording, attachment display,
> parent-child form prefill, and closed-case rules. These should be implemented using supported modern
> SharePoint configuration, JSON formatting, permissions, Power Apps, or Power Automate where appropriate.
> **SPFx should be reserved for a small number of confirmed MVP gaps** — reserved for last, after removal,
> modern OOB web parts, list/form configuration, JSON formatting, permissions, Power Apps, Power Automate,
> and acceptable UX simplification have all been assessed and found insufficient.

### Disposition totals

| Disposition | Instances | Unique groups |
|---|---:|---:|
| Modern Text web part | **17** | **14** (Groups 11-13, 28-38) |
| Empty placeholder — do not migrate | **31** | **1** (Group 1) |
| External helper scripts — modern list/form config first, SPFx last resort | **51** | **14** |
| Inline JavaScript logic — forms/rules/SPFx assessment | **22** | **9** |
| **Total** | **121** | **38** |

- **14.0%** of instances map directly to the Text web part; **36.8%** of unique patterns do.
- **48 of 121 instances (39.7%)** require no custom implementation once empty placeholders are included.
- The remaining **73 instances are not Text web-part scenarios** — but that does not mean all 73 need SPFx.

### Corrections applied to this document from the variance analysis

1. Preserved the distinction between **121 deployed instances** and **38 unique functional groups** throughout.
2. **Groups 22-27** (6 separate InlineLogic singletons, "hide buttons when case closed") are documented as
   **one modernization pattern deployed 6 times**, not 6 separate components — while retaining all 6 source
   group IDs for traceability.
3. **Groups 4 and 9** (`fillfromParent` targeting "Related to Case" vs. "Related to Person") are documented
   as **one reusable parent-context prefill design**, while retaining both source group IDs for traceability.
4. **Group 14**'s `link_case.js` — previously flagged as an unrecognized/evidence-gap helper — is resolved:
   Part 2 of this document (external JS file review) confirms it is a JSLink field-renderer with a hardcoded
   SharePoint View GUID, the same family as `linkCase.js`/`linkPIOCase.js`. Disposition updated accordingly.
5. **Group 37**'s full source text was already captured verbatim in this document (not truncated) — the
   truncation concern applied only to the separate auto-generated preview in `webpart-code-analysis.md`.
6. The unverified claim that Group 4's `fillfromParent` pattern requires "a Power Automate flow triggered on
   form load" is now flagged as one candidate mechanism to validate during prototyping, not a confirmed fact.
7. An explicit SPFx-last-resort rule is stated in the Executive Summary above: SPFx is considered only after
   removal, modern OOB web parts, list/form configuration, JSON formatting, permissions, Power Apps, and
   Power Automate have been assessed and found insufficient.

*Variance analysis source: `CMAT-WEBPART-MODERNIZATION-VARIANCE-ANALYSIS.md` (same folder), merged into this
document 2026-07-15.*

---

## Group 1 — Empty (31 instances)

**Representative:** `/cmat/Lists/PIO_Approval_Requests/DispForm.aspx` (WebPartId `6a34cf79-56a7-4bd8-8745-b251a923b962`, Content Editor)

**All pages in this group:** `/cmat/Lists/PIO_Approval_Requests/DispForm.aspx`, `/cmat/Lists/Briefings/DispForm.aspx`, `/cmat/Pages/ICM_My_Tasks.aspx`, `/cmat/Pages/ICM_My_Tasks.aspx`, `/cmat/Pages/ICM_All_Approval_Requests.aspx`, `/cmat/Pages/ICM_All_Approval_Requests.aspx`, `/cmat/Pages/ICM_All_Approval_Requests.aspx`, `/cmat/Pages/ICM_All_Approval_Requests.aspx`, `/cmat/Pages/ICM_My_Approval_Requests.aspx`, `/cmat/Pages/ICM_My_Approval_Requests.aspx`, `/cmat/Pages/ICM_My_Approval_Requests.aspx`, `/cmat/Pages/Persons_PIO.aspx`, `/cmat/Pages/PIO_My_Tasks.aspx`, `/cmat/Pages/Approval_Requests_for_Supervisors.aspx`, `/cmat/Pages/ITAU_My_Tasks.aspx`, `/cmat/Pages/ITAU_All_Tasks.aspx`, `/cmat/Pages/ITAU_All_Approval_Requests.aspx`, `/cmat/Pages/ITAU_All_Approval_Requests.aspx`, `/cmat/Pages/ITAU_All_Approval_Requests.aspx`, `/cmat/Pages/Purge_Planning.aspx`, `/cmat/Pages/ITAU_Cases.aspx`, `/cmat/Pages/PIO_My_Approval_Requests.aspx`, `/cmat/Pages/ICM_All_Tasks.aspx`, `/cmat/Pages/ICM_All_Tasks.aspx`, `/cmat/Pages/PIO_All_Tasks.aspx`, `/cmat/Pages/Persons_ICM.aspx`, `/cmat/Pages/My_ITAU_Cases.aspx`, `/cmat/Pages/Persons_ITAU.aspx`, `/cmat/Pages/ITAU_My_Approval_Requests.aspx`, `/cmat/Pages/ITAU_My_Approval_Requests.aspx`, `/cmat/Pages/PIO_All_Approval_Requests.aspx`

```html
<style type="text/css">

.ms-recommendations-panel{

  DISPLAY: none !important

}

</style>​<br/>
```

### Modernization Assessment

- **Business behavior:** Empty or hidden placeholder web part — no content, no functional impact.
- **Text web part sufficient:** No — none needed.
- **Recommended modern replacement:** Do not migrate.
- **MVP decision:** Remove.
- **SPFx candidate:** No.
- **Validation required:** Confirm the extracted content is actually empty and that no external CSS/page script selected the web-part container by ID. Once confirmed, remove from the MVP inventory.

### Modernization Behaviour Analysis

**User-visible effect:**  
None.

**Business intent:**  
None — this is a leftover/hidden placeholder, not a deliberate feature.

**Actual enforcement level:**  
Not applicable — no behavior.

**Modern SharePoint Online approach:**  
Do not migrate.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 2 — ExternalHelpersOnly (14 instances)

**Representative:** `/cmat/Pages/ICM_Documents.aspx` (WebPartId `6d94b28b-b2ba-4717-8967-0e76c59c9a12`, Content Editor)

**All pages in this group:** `/cmat/Pages/ICM_Documents.aspx`, `/cmat/Pages/Orphan_Approval_Requests.aspx`, `/cmat/Pages/All_Cases.aspx`, `/cmat/Pages/all_progress_logs.aspx`, `/cmat/Pages/Orphan_Progress_Logs.aspx`, `/cmat/Pages/Orphan_Tasks.aspx`, `/cmat/Pages/All_Tasks.aspx`, `/cmat/Pages/ITAU_Documents.aspx`, `/cmat/Pages/Manage_Reference_and_Templates.aspx`, `/cmat/Pages/All_Approval_Requests.aspx`, `/cmat/Pages/Judiciary_Crown_Related_Cases.aspx`, `/cmat/Pages/Unfiled_Documents.aspx`, `/cmat/Pages/PIO_Documents.aspx`, `/cmat/Pages/All_Case_Documents.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}
</style> 

<script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script>
<script src="/cmat/SiteAssets/JS/HideLinksToPersons.js" type="text/javascript"></script>​​​​<br/>
<script src="/sandbox/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script>​<br/>​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Applies conditional list-cell/row colouring (ConditionalColoring.js) and removes links to Person detail records in selected views (HideLinksToPersons.js).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON column/row formatting for colouring. For person links, use a modern field/view design that renders plain text, or accept the link if it causes no business or security problem.
- **MVP decision:** Simplify — reimplement via list formatting; drop the link-hiding script.
- **SPFx candidate:** No — only if formatting/permissions genuinely cannot achieve the effect.
- **Validation required:** Confirm whether hiding the Person link is cosmetic or a security requirement. If security, it must be enforced by permissions, not cosmetic hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
Rows in the list view are colour-highlighted based on a column value (e.g. status/priority), and any hyperlink that would normally take the user to a Person's detail record is removed from these views — the person's name still shows as plain text, it's just not clickable.

**Business intent:**  
The colouring appears to be a visual triage aid (spot urgent/overdue/flagged items at a glance). The link removal appears intended to stop users from navigating into Person records from these particular views — possibly to reduce accidental exposure of person details from a context where that wasn't the point.

**Actual enforcement level:**  
Presentation-only for both behaviors. The colouring is cosmetic. The link removal only hides the `<a>` tag in the browser — the Person record is still reachable directly by URL, by search, or via any other view/link elsewhere in the site that isn't similarly patched. This is not access control.

**Modern SharePoint Online approach:**  
Row/cell colouring: JSON column or view formatting (no code). Link removal: if the real requirement is "users in this context shouldn't be able to reach Person records," that must be enforced with item-level/list permissions, not by omitting a link — otherwise it's a false sense of restriction. If the requirement is purely "don't clutter this view with a link," a plain-text (non-hyperlinked) column formatting rule achieves that with no code.

**SPFx assessment:**  
No — both effects are achievable with native JSON formatting once the actual intent (cosmetic vs. access-control) is confirmed.

**Migration note:**  
jQuery-dependent; relies on DOM class selectors that don't exist in the modern list view rendering, so this code cannot be ported as-is regardless of the decision above.

---

## Group 3 — ExternalHelpersOnly (11 instances)

**Representative:** `/cmat/Lists/PIO_Approval_Requests/PIO_Approval_Requests_Mgrs.aspx` (WebPartId `90cc4c04-1db8-4ec6-a53c-13d2b18f2bb6`, Content Editor)

**All pages in this group:** `/cmat/Lists/PIO_Approval_Requests/PIO_Approval_Requests_Mgrs.aspx`, `/cmat/Pages/ICM_My_Tasks.aspx`, `/cmat/Pages/All_Appearances.aspx`, `/cmat/Pages/Add_Edit_Persons.aspx`, `/cmat/Pages/PIO_My_Tasks.aspx`, `/cmat/Pages/ITAU_My_Tasks.aspx`, `/cmat/Pages/ITAU_All_Tasks.aspx`, `/cmat/Pages/Orphan_Appearances.aspx`, `/cmat/Pages/ICM_All_Tasks.aspx`, `/cmat/Pages/PIO_All_Tasks.aspx`, `/cmat/Pages/All_Persons.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}

#QCB1_Button2
{ display: none }

div.ms-dragDropAttract-subtle
{ display: none }

</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script>​​<br/>​​​​​<br/><script src="/cmat/SiteAssets/JS/HideLinksToPersons.js" type="text/javascript"></script><script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>​​​<br/>​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Group 2's behavior (colouring + hidden Person links) plus renaming the classic “New Item” command via NewItemToAddNewHeadingChanger.js.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON formatting and permissions/view configuration. Treat command renaming as an MVP UX variance unless business validation proves the exact label is essential.
- **MVP decision:** Simplify.
- **SPFx candidate:** No for colouring; conditional only for command customization after accepting or rejecting the modern label.
- **Validation required:** Same security question as Group 2 for the hidden links.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same colouring and Person-link removal as Group 2, plus the classic "New Item" command label is renamed to a more descriptive label (e.g. "Add New Task" instead of the generic default).

**Business intent:**  
Same as Group 2 for colouring/link hiding. The relabeled command is a small UX clarity improvement so users understand what "New Item" actually creates on that particular list.

**Actual enforcement level:**  
Presentation-only across the board — colouring, link hiding, and the button label are all cosmetic; none of it changes what a user is actually permitted to do.

**Modern SharePoint Online approach:**  
JSON formatting for colouring, permissions if link removal must be a real restriction, and the modern list view already supports customizing the "New" command label/behavior through list/form configuration without code.

**SPFx assessment:**  
No for colouring and link hiding. Conditional only if a specific custom command wording cannot be achieved through native list configuration — validate the native option first.

**Migration note:**  
Same jQuery/DOM-class dependency as Group 2; the command-renaming script hardcodes the target button by ID, which will not exist in the modern command bar.

---

## Group 4 — InlineLogic (10 instances)

**Representative:** `/cmat/Lists/ICM_Case_Tasks/NewForm.aspx` (WebPartId `2028ece5-31c3-4b6d-8642-1d2b980d0769`, Content Editor)

**All pages in this group:** `/cmat/Lists/ICM_Case_Tasks/NewForm.aspx`, `/cmat/Lists/ICM_Approval_Requests/NewForm.aspx`, `/cmat/Lists/PIO_Approval_Requests/NewForm.aspx`, `/cmat/Lists/ITAU_Case_Tasks/AllItems.aspx`, `/cmat/Lists/ITAU_Case_Tasks/NewForm.aspx`, `/cmat/Lists/PIO_Log_Entries/NewForm.aspx`, `/cmat/Lists/PIO_Case_Tasks/NewForm.aspx`, `/cmat/Lists/ITAU_Log_Entries/NewForm.aspx`, `/cmat/Lists/ICM_Log_Entries/NewForm.aspx`, `/cmat/Lists/ITAU_Approval_Requests/NewForm.aspx`

```html
<script src="/cmat/SiteAssets/JS/jquery-1.4.4.min.js" type="text/javascript"></script>​<script src="/cmat/SiteAssets/JS/RLHelper-ChildNewForm.js" type="text/javascript"></script><script type="text/javascript">
_spBodyOnLoadFunctionNames.push('fillfromParent("Related to Case")');
</script>​​​​​​​<br/>​​​​​<br/>​<br/>​​<br/>​​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads parent context from the query string and prepopulates a Related Case lookup on child New forms (RLHelper-ChildNewForm.js, inline `fillfromParent()` call).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Power Apps customized form using page parameters and a reusable prefill pattern. Prototype once, then apply consistently to all affected lists.
- **MVP decision:** Implement as one shared Power Apps pattern (with Group 9).
- **SPFx candidate:** No, unless a supported customized-form pattern fails a validated requirement.
- **Validation required:** The requirement is prepopulation before submission — implementation mechanism (Power Apps form formula vs. Power Automate flow) should be chosen during prototyping, not assumed.
- **Evidence gap / caveat:** A prior version of this analysis stated a Power Automate flow is "triggered on form load" as fact — this was not verified against an actual working implementation and must be treated as one candidate mechanism, not a confirmed design.

### Modernization Behaviour Analysis

**User-visible effect:**  
A user opens a case from a case list, clicks to add a related child record (e.g. a new Task), and the "Related to Case" field on the New form is already filled in with the correct parent case — no manual lookup/typing required. This pattern repeats across 10 different child-list New forms (Case Tasks, Approval Requests, Log Entries) for ICM/PIO/ITAU.

**Business intent:**  
Reduce user error and effort when creating a child record from a parent case — ensures the child is always correctly linked without relying on the user to remember/select the right case.

**Actual enforcement level:**  
Form/data-entry convenience only. It prepopulates a field; it does not validate that the value is correct, does not prevent the user from changing it, and enforces no business rule — it's a time-saver, not a guardrail.

**Modern SharePoint Online approach:**  
A Power Apps customized form using page/query-string parameters (`Param()`) to prepopulate the lookup when the New form is launched from a parent context — this is a native, no-code capability. A Power Automate flow is one possible supporting mechanism but should not be assumed as required without prototyping (see evidence-gap note above).

**SPFx assessment:**  
No — this is a standard Power Apps form-customization scenario, not a custom-code scenario.

**Migration note:**  
Depends on `RLHelper-ChildNewForm.js`, an unmaintained public snippet from 2010 (`sp2010-related-list-prefill`) that reads a raw query-string parameter (`SelectedID`) via `window.location.search` parsing — fragile, framework-agnostic string parsing that has no equivalent in modern SPO and should not be ported.

---

## Group 5 — ExternalHelpersOnly (7 instances)

**Representative:** `/cmat/Pages/ICM_All_Approval_Requests.aspx` (WebPartId `6dc70d61-46c5-43e0-8e98-77182690bd98`, Content Editor)

**All pages in this group:** `/cmat/Pages/ICM_All_Approval_Requests.aspx`, `/cmat/Pages/ICM_My_Approval_Requests.aspx`, `/cmat/Pages/Approval_Requests_for_Supervisors.aspx`, `/cmat/Pages/ITAU_All_Approval_Requests.aspx`, `/cmat/Pages/PIO_My_Approval_Requests.aspx`, `/cmat/Pages/ITAU_My_Approval_Requests.aspx`, `/cmat/Pages/PIO_All_Approval_Requests.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}

#QCB1_Button2
{ display: none }

div.ms-dragDropAttract-subtle
{ display: none }

</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script>​<br/>​​​​​​<br/><script src="/cmat/SiteAssets/JS/HideLinksToPersons.js" type="text/javascript"></script><script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script>​​​​​<br/>
```

### Modernization Assessment

- **Business behavior:** Group 3's behavior plus display of attachment file names in list rows (showattachmentname.js).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON formatting where supported, a modern attachment/link column or view, standard modern command labels where acceptable.
- **MVP decision:** Simplify, pending validation of the exact attachment need.
- **SPFx candidate:** Conditional — only if the required attachment presentation cannot be achieved with modern lists and formatting.
- **Validation required:** Determine whether users need only an attachment indicator, the actual filename, or direct opening of the attachment — these are different requirements.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same colouring, Person-link removal, and command relabeling as Group 3, plus each row in the list view shows the actual attached file's name as a clickable link (rather than just a generic paperclip icon).

**Business intent:**  
Let users see which specific document is attached to a row without opening the item first — a genuine usability improvement over the generic attachment icon.

**Actual enforcement level:**  
Presentation-only. It changes how the attachment is displayed; it doesn't change what's attached or who can access it.

**Modern SharePoint Online approach:**  
SPO's modern list view already renders attachment indicators and, depending on configuration, can show attachment counts/names via native columns or JSON formatting — validate whether the built-in behavior already meets the need before building anything custom.

**SPFx assessment:**  
Conditional — only if native modern attachment rendering genuinely cannot show the filename the way business requires (e.g. exact filename inline, not just a count).

**Migration note:**  
The underlying `showattachmentname.js` makes a **synchronous** AJAX call per row (`$.ajax({..., async:false})`) — a real performance anti-pattern that blocks the browser UI thread once per list row. This should not be replicated even in a modern equivalent; use a native/async approach only.

---

## Group 6 — ExternalHelpersOnly (6 instances)

**Representative:** `/cmat/Pages/My_ICM_Cases.aspx` (WebPartId `d869a52f-e1e6-4ec4-b744-9d45df478920`, Content Editor)

**All pages in this group:** `/cmat/Pages/My_ICM_Cases.aspx`, `/cmat/Pages/ICM_Cases.aspx`, `/cmat/Pages/PIO_Cases.aspx`, `/cmat/Pages/My_PIO_Cases.aspx`, `/cmat/Pages/ITAU_Cases.aspx`, `/cmat/Pages/My_ITAU_Cases.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}

#QCB1_Button1
{ display: none }

div.ms-dragDropAttract-subtle
{ display: none }

</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script>​<br/>​​​​​​​<br/><script src="/cmat/SiteAssets/JS/HideLinksToPersons.js" type="text/javascript"></script>​​​​​​​<br/><script src="/cmat/SiteAssets/JS/RLHelper-ParentDisplayForm.js" type="text/javascript"></script><script src="/cmat/SiteAssets/JS/NewTaskToAddNewHeadingChanger.js" type="text/javascript"></script>​​ 
<script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>​​​​ 
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script>​​​​​<br/>
```

### Modernization Assessment

- **Business behavior:** Bundle of unrelated concerns across 6 case dashboard pages (My_ICM_Cases, ICM_Cases, PIO_Cases, My_PIO_Cases, ITAU_Cases, My_ITAU_Cases): formatting, link suppression, command labels, attachment display, and parent-to-child navigation/prefill (RLHelper-ParentDisplayForm.js).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Decompose into separate requirements: JSON formatting for display, standard modern commands where acceptable, native attachment behavior, and Power Apps/page-parameter design for parent-child creation.
- **MVP decision:** Decompose and rebuild per-concern — do not port as one bundle.
- **SPFx candidate:** No monolithic port — consider a reusable component only for a confirmed gap after decomposition.
- **Validation required:** Re-evaluate each concern (formatting/links/labels/attachments/prefill) independently.

### Modernization Behaviour Analysis

**User-visible effect:**  
On the six main case dashboard pages (My_ICM_Cases, ICM_Cases, PIO_Cases, My_PIO_Cases, ITAU_Cases, My_ITAU_Cases): row colouring, Person-link removal, relabeled "New Task"/"New Item" commands, attachment filenames shown inline, and — when a user opens a case's display form from the list — the child form correctly carries the parent case context forward (`RLHelper-ParentDisplayForm.js`, the display-form-side companion to Group 4's `RLHelper-ChildNewForm.js`).

**Business intent:**  
Each concern individually is a small UX aid (see Groups 2/3/5 for colouring/links/labels/attachments) — this group is really five unrelated concerns bundled into one Content Editor because they happened to be pasted together on these six high-traffic pages, not because they're one feature.

**Actual enforcement level:**  
Presentation and navigation-convenience only across all five concerns — none of it is business-rule enforcement.

**Modern SharePoint Online approach:**  
Do not port this as one bundle. Decompose into: JSON formatting (colouring), permissions or plain-text columns (Person links), native list configuration (command labels), native attachment behavior (filenames), and the same Power Apps `Param()` pattern from Group 4 (parent-to-child context).

**SPFx assessment:**  
No monolithic SPFx replacement. Assess each of the five concerns independently against the SPFx-last-resort order; most resolve without any custom code.

**Migration note:**  
This is the same "kitchen sink" Content Editor pattern found on all six dashboard pages — treat it as one reusable decomposition, applied six times, not six separate analyses.

---

## Group 7 — ExternalHelpersOnly (3 instances)

**Representative:** `/cmat/Lists/PIO_Cases/DispForm.aspx` (WebPartId `39bff197-fecf-4f71-a811-2624668ceee8`, Content Editor)

**All pages in this group:** `/cmat/Lists/PIO_Cases/DispForm.aspx`, `/cmat/Lists/PIO_Log_Entries/DispForm.aspx`, `/cmat/Lists/Persons/DispForm.aspx`

```html
<script type="text/javascript" src="/cmat/SiteAssets/JS/jquery-3.5.0.js"></script><script type="text/javascript" src="/cmat/SiteAssets/JS/HideLinksInDisplayForm.js"></script>​<br/>​​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Removes edit/delete or list-form links while leaving displayed labels (HideLinksInDisplayForm.js, HideLinksToPersons.js).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Permissions and form/view configuration.
- **MVP decision:** Enforce via permissions if the intent is preventing modification.
- **SPFx candidate:** No, unless the business requires a presentation-only difference that modern configuration cannot provide.
- **Validation required:** Same security question as Group 2 — cosmetic link hiding is insufficient if the intent is to stop modification; enforce the rule using permissions or form behavior.

### Modernization Behaviour Analysis

**User-visible effect:**  
On these three Display forms (a case, a log entry, a person record), edit/delete or list-navigation links that would normally appear are removed from view — the displayed data itself is unchanged.

**Business intent:**  
Appears intended to discourage or prevent users from editing/deleting from this particular display context.

**Actual enforcement level:**  
Presentation-only. Hiding the link does not remove the user's underlying edit/delete permission — if they have permission, they can still reach the edit/delete action another way (ribbon, direct URL, API). This must not be treated as security.

**Modern SharePoint Online approach:**  
If the real requirement is "these users cannot edit/delete these items," enforce it with SharePoint permissions (item-level or list-level). If the requirement is only "don't show the edit/delete affordance to reduce clutter/accidental clicks," modern display forms have simpler, cleaner default chrome than the classic form, which may make this unnecessary entirely.

**SPFx assessment:**  
No, unless a validated presentation-only requirement survives after the permissions question above is answered.

**Migration note:**  
jQuery/DOM-class dependent; will not function against the modern display form's markup.

---

## Group 8 — InlineLogic (3 instances)

**Representative:** `/cmat/Lists/PIO_Cases/EditForm.aspx` (WebPartId `df3f5110-d3d4-4994-ba8b-61297aad080e`, Script Editor)

**All pages in this group:** `/cmat/Lists/PIO_Cases/EditForm.aspx`, `/cmat/Lists/ITAU_Cases/EditForm.aspx`, `/cmat/Lists/ICM_Cases/EditForm.aspx`

```html
<script src = "https://code.jquery.com/jquery-1.7.2.min.js"type = "text/javascript"> </script>
<script type = "text/javascript">

$(document).ready(function() {
    var status_input = $("select[title^='Status']");
    var status = status_input.val();

    function GetNow(){
        var currentdate = new Date(); 
        var datetime = currentdate.getFullYear()+"-"
                + (currentdate.getMonth()+1)  + "-" 
                + currentdate.getDate();
        return datetime;
    }

    function set_closing_date(){
        var now = GetNow();
        $("input[title='Case Closed Date']").val(now);
    }

    function lock_editing(){
        //$("input[title^='Brief Description']").attr('disabled', 'disabled');
       // $("input[title='Open Date']").attr('disabled', 'disabled');
        $("input[title='Case Closed Date']").attr('disabled', 'disabled');
        $( "td.ms-dtinput > a" ).hide();
    }

    function unlock_editing(){
       // $("input[title^='Brief Description']").removeAttr('disabled');
       // $("input[title^='Open Date']").removeAttr('disabled');
        $("input[title^='Case Closed Date']").removeAttr('disabled');
        $( "td.ms-dtinput > a" ).show();
    }


    if(status === "Closed"){
      // Make all other fields read only
      // console.log(1);
        lock_editing()
    }

    status_input.on("change" , function(e){
      var status_value = e.target.value;
      if(status_value === "Closed"){
          // Make all other fields read only
          set_closing_date();
          lock_editing();
      } else {
        unlock_editing()
      }
    });

    
});
</script>
```

### Modernization Assessment

- **Business behavior:** The 3 Script Editors (PIO/ITAU/ICM Cases Edit forms): watches Status; when Status becomes Closed, sets Case Closed Date to the current date and makes the field read-only; changing away from Closed unlocks it. Commented-out code for other fields (Brief Description, Open Date) is inactive.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Shared Power Apps customized-form pattern (DisplayMode/Default formulas). Consider server-side or workflow enforcement as a second control if the date rule must hold outside the form.
- **MVP decision:** Implement as one shared Power Apps pattern.
- **SPFx candidate:** No.
- **Validation required:** Confirm whether reopening a closed case is allowed, and what should happen to the Closed Date value when a case is reopened.

### Modernization Behaviour Analysis

**User-visible effect:**  
On the Edit form for a PIO/ITAU/ICM case, when the user changes Status to "Closed," the Case Closed Date field is automatically stamped with today's date and becomes read-only (greyed out, un-editable, its date-picker button hidden). If the user changes Status away from Closed again, the field unlocks and becomes editable.

**Business intent:**  
Ensure every closed case has an accurate, non-tampered closure date — capture the date automatically at the moment of closure rather than relying on the user to remember to set it, and prevent accidental after-the-fact edits to that date while the case remains closed.

**Actual enforcement level:**  
**Form behavior, not backend enforcement.** The read-only attribute is applied client-side in the browser; it stops a user from editing the field through this form's UI, but does not stop the value being changed by a direct list-item edit, a bulk edit, a Quick Edit/datasheet view, a flow, or the REST API. If the business truly needs the date protected once set, form-level locking is necessary but not sufficient on its own.

**Modern SharePoint Online approach:**  
Recreate the same UX with a Power Apps customized form: a formula-driven `DisplayMode` (Edit/View) on the Case Closed Date control based on the Status field's value, and a `Patch`/default-value rule to set the date automatically when Status changes to Closed. If the date must be protected from all edit paths (not just this one form), add a Power Automate flow or column validation as a second, backend-level control.

**SPFx assessment:**  
No — this is squarely a Power Apps form-rule scenario; no custom code component is required.

**Migration note:**  
The commented-out lines locking "Brief Description" and "Open Date" are dead code (never executes) — do not carry them forward, but do flag them for business confirmation in case they represent an intended-but-never-shipped requirement.

---

## Group 9 — InlineLogic (3 instances)

**Representative:** `/cmat/Lists/ITAU_Narratives/NewForm.aspx` (WebPartId `4ebf257c-7158-4cc7-b569-baad5c94985f`, Content Editor)

**All pages in this group:** `/cmat/Lists/ITAU_Narratives/NewForm.aspx`, `/cmat/Lists/PIOs_Narrative/NewForm.aspx`, `/cmat/Lists/ICM_Narratives/NewForm.aspx`

```html
<script src="/cmat/SiteAssets/JS/jquery-1.4.4.min.js" type="text/javascript"></script>​<script src="/cmat/SiteAssets/JS/RLHelper-ChildNewForm.js" type="text/javascript"></script><script type="text/javascript">
_spBodyOnLoadFunctionNames.push('fillfromParent("Related to Person")');
</script>​​​​​<br/>​​​​<br/>​​​<br/>​​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Same parent-context lookup prefill pattern as Group 4, targeting “Related to Person” instead of “Related to Case,” with a different code signature (ITAU/PIO/ICM Narratives New forms).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Reuse the same Power Apps/page-parameter pattern as Group 4.
- **MVP decision:** Implement as part of the same shared pattern as Group 4.
- **SPFx candidate:** No, unless prototyping proves a supported form cannot meet the requirement.
- **Evidence gap / caveat:** Groups 4 and 9 should be merged at the design level as one reusable parent-context prefill pattern, while preserving both source group IDs for traceability.

### Modernization Behaviour Analysis

**User-visible effect:**  
Identical behavior to Group 4, on Narrative New forms instead of Task/Approval/Log New forms: opening "New Narrative" from a parent case automatically fills in the "Related to Person" field rather than requiring manual lookup.

**Business intent:**  
Same as Group 4 — accurate, effortless linkage of a child record to its parent context, this time for the person the narrative concerns rather than the case.

**Actual enforcement level:**  
Same as Group 4 — form/data-entry convenience only, not validation or enforcement.

**Modern SharePoint Online approach:**  
Same Power Apps `Param()`-driven prefill pattern as Group 4 — this is the same reusable design applied to a different lookup field, not a different requirement.

**SPFx assessment:**  
No — reuse the Group 4 decision.

**Migration note:**  
Same `RLHelper-ChildNewForm.js` dependency and fragility as Group 4.

---

## Group 10 — ExternalHelpersOnly (2 instances)

**Representative:** `/cmat/Pages/All_Briefings_and_Security_Alerts.aspx` (WebPartId `4f7d10a4-8ce0-4772-a171-3ddf3b657943`, Content Editor)

**All pages in this group:** `/cmat/Pages/All_Briefings_and_Security_Alerts.aspx`, `/cmat/Pages/Briefings_and_Security_Alerts.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}

#QCB1_Button2
{ display: none }

div.ms-dragDropAttract-subtle
{ display: none }

</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script><script src="/cmat/SiteAssets/JS/NewTasktoAddNewHeadingChanger.js" type="text/javascript"></script>​​​ 
<script src="/cmat/SiteAssets/JS/HideLinksToPersons.js" type="text/javascript"></script>​​​​​​​​<br/>​​<br/>
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script>​​​​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Formatting, link suppression, task command relabeling (NewTasktoAddNewHeadingChanger.js), and attachment filename presentation on briefing/security-alert pages.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON list formatting, native modern attachment behavior, permissions where needed, and acceptance of modern command wording.
- **MVP decision:** Simplify.
- **SPFx candidate:** Conditional — only for a validated attachment or command gap.

### Modernization Behaviour Analysis

**User-visible effect:**  
On the combined Briefings/Security Alerts pages: row colouring, Person-link removal, "New Task" relabeled, and attachment filenames shown inline in the list — same set of concerns as Groups 3/5/6, applied to this page pair.

**Business intent:**  
Same individual intents as the equivalent groups above — this is the same recurring bundle, not a new pattern.

**Actual enforcement level:**  
Presentation-only, same as the equivalent groups above.

**Modern SharePoint Online approach:**  
Same decomposition as Groups 3/5/6: JSON formatting, permissions if link removal is a real requirement, native list command config, native attachment behavior.

**SPFx assessment:**  
Conditional — only for a validated attachment-display gap, same as Group 5.

**Migration note:**  
Same jQuery/DOM-class dependencies as the equivalent groups.

---

## Group 11 — TextOnly (2 instances)

**Representative:** `/cmat/Pages/PIO_Cases.aspx` (WebPartId `0cec3d70-ebfe-48a8-b9cb-027c1b4f55c3`, Content Editor)

**All pages in this group:** `/cmat/Pages/PIO_Cases.aspx`, `/cmat/Pages/My_PIO_Cases.aspx`

```html
<b class="ms-rteForeColor-9">Note: <br/></b><span class="ms-rteForeColor-9">When Adding a New Case make sure all Subjects and Affected Persons&#160;are already in t​he</span><span class="ms-rteForeColor-9"> </span><span class="ms-rteForeColor-9"><a href="/cmat/Pages/Add_Edit_Persons.aspx">ITAU Persons Database</a>.</span><span class="ms-rteForeColor-9">​</span><br/>
```

### Modernization Assessment

- **Business behavior:** Instruction telling users to ensure Subjects and Affected Persons exist in the ITAU Persons Database before adding a case.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part with a hyperlink to the modern Persons page.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Update the destination URL and verify whether “ITAU Persons Database” remains the correct product wording for PIO pages.
- **Evidence gap / caveat:** Groups 11 and 13 may be one reusable content pattern even though their legacy HTML signatures differ.

### Modernization Behaviour Analysis

**User-visible effect:**  
A short instructional note above the case list telling users to make sure Subjects/Affected Persons already exist in the Persons database before creating a new case, with a link to that database.

**Business intent:**  
Data-quality reminder — avoid duplicate/orphaned Person records by getting users to check first.

**Actual enforcement level:**  
Informational only — a reminder, not a validation. Nothing stops a user from creating a case without checking.

**Modern SharePoint Online approach:**  
Text web part with an updated link to the modern Persons page. If data-quality is a real concern, consider whether the Power Apps case form could add an actual lookup/duplicate check as a stronger control — that would be a separate, later enhancement, not required for content parity.

**SPFx assessment:**  
No.

**Migration note:**  
None — plain rich text and a link, no script.

---

## Group 12 — TextOnly (2 instances)

**Representative:** `/cmat/Pages/Add_Edit_Persons.aspx` (WebPartId `e5ed7084-5356-40f9-9700-a086a655863b`, Content Editor)

**All pages in this group:** `/cmat/Pages/Add_Edit_Persons.aspx`, `/cmat/Pages/All_Persons.aspx`

```html
​​​Note: Use * at the end for an Incomplete Name Search e.g. Mack*​<br/>
```

### Modernization Assessment

- **Business behavior:** Search instruction explaining use of `*` for an incomplete name search.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part.
- **MVP decision:** Keep, pending validation.
- **SPFx candidate:** No.
- **Validation required:** Validate whether modern SharePoint search or list filtering still uses the same wildcard behavior. If not, rewrite or remove the instruction rather than copying inaccurate guidance.

### Modernization Behaviour Analysis

**User-visible effect:**  
A one-line search tip: use `*` at the end of a name for a wildcard/incomplete-name search (e.g. "Mack*").

**Business intent:**  
Help users find records without knowing the exact spelling of a name.

**Actual enforcement level:**  
Informational only.

**Modern SharePoint Online approach:**  
Text web part — but the wildcard syntax must be re-verified against modern SPO list search/filter behavior before copying it forward; classic SharePoint search syntax does not always carry over unchanged.

**SPFx assessment:**  
No.

**Migration note:**  
None — plain text, but factually dependent on legacy search behavior that must be re-verified.

---

## Group 13 — TextOnly (2 instances)

**Representative:** `/cmat/Pages/ITAU_Cases.aspx` (WebPartId `cb3cd474-80f5-47e6-9226-663582f83717`, Content Editor)

**All pages in this group:** `/cmat/Pages/ITAU_Cases.aspx`, `/cmat/Pages/My_ITAU_Cases.aspx`

```html
<b class="ms-rteForeColor-9">Note: <br/></b><span class="ms-rteForeColor-9">When Adding a New Case make sure all Subjects and Affected Persons&#160;are already in t​he&#160;</span><a href="/cmat/Pages/Add_Edit_Persons.aspx"><span class="ms-rteForeColor-9">ITAU Persons Database</span></a><span class="ms-rteForeColor-9">​.</span><br/><div><span class="ms-rteForeColor-9"><br/></span>&#160;</div>
```

### Modernization Assessment

- **Business behavior:** Same precondition notice as Group 11, with a link to the Persons page.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part with updated modern-page link.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Same URL/wording checks as Group 11.
- **Evidence gap / caveat:** Groups 11 and 13 may be one reusable content pattern — consider consolidating.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same as Group 11 — precondition notice about confirming Subjects/Affected Persons exist in the Persons database, with a link, shown on the ITAU case pages instead of PIO.

**Business intent:**  
Same as Group 11.

**Actual enforcement level:**  
Informational only, same as Group 11.

**Modern SharePoint Online approach:**  
Same as Group 11 — Text web part with an updated modern-page link. Consider consolidating with Group 11 into one shared content block reused across PIO and ITAU pages.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 14 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Lists/ITAU_Cases/SIO_Case_Involvement.aspx` (WebPartId `927ef028-9c06-40f8-ae44-28323e443c60`, Content Editor)

**All pages in this group:** `/cmat/Lists/ITAU_Cases/SIO_Case_Involvement.aspx`

```html
<script type="text/javascript" src="/cmat/SiteAssets/JS/link_case.js"></script>

​​​​​<br/>
```

### Modernization Assessment

- **Business behavior:** Unrecognized helper (`link_case.js`) — the automated analysis could not classify its intent.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Pending source review. Likely candidates include a native lookup link, JSON hyperlink formatting, or modern list configuration, but this must not be asserted until the script is read.
- **MVP decision:** Pending business validation — evidence gap, not an automatic disposition.
- **SPFx candidate:** Undetermined — this is an evidence gap, not an automatic SPFx requirement.
- **Validation required:** Inspect `link_case.js` source directly (see Part 2 of this document) before selecting a replacement.
- **Evidence gap / caveat:** Source has since been read in Part 2 of this document under linkCase.js — confirms it is a JSLink field-renderer with hardcoded View GUIDs, not an unrecognized/unknown script. Update disposition accordingly: modern replacement is an SPFx Field Customizer or modern column formatting, not "pending".

### Modernization Behaviour Analysis

**User-visible effect:**  
In the `Case` field of this list view, the value renders as a clickable link (rather than plain text) that takes the user directly to that case's detail row on `ITAU_Cases.aspx`, `PIO_Cases.aspx`, or `ICM_Cases.aspx` depending on which list the case belongs to.

**Business intent:**  
One-click navigation from a related record straight to the parent case's detail view, instead of requiring the user to search/filter for it manually.

**Actual enforcement level:**  
Navigation/presentation only — it builds a link, nothing more.

**Modern SharePoint Online approach:**  
This uses classic SharePoint CSR/JSLink (`SPClientTemplates.TemplateManager.RegisterTemplateOverrides` targeting the `Case` field), hardcoding three View GUIDs (`ITAU_Cases`/`PIO_Cases`/`ICM_Cases`) that will not exist after migration. First assess a native lookup column, a hyperlink-formatted column, or JSON column formatting pointing to the modern case page (no hardcoded view GUID needed in SPO — a relative URL + item ID is enough). Only fall back to an SPFx Field Customizer if none of those can reproduce the required link target.

**SPFx assessment:**  
Conditional — likely unnecessary. JSON column formatting can build a hyperlink to a modern page using the item's ID without needing a legacy View GUID at all.

**Migration note:**  
Hardcoded View GUIDs (`{FF014B5A-...}`, `{F7393396-...}`, `{248FD0E2-...}`) are the core fragility here — they are SP2016-specific and guaranteed not to survive migration. This is the same underlying script family as `linkPIOCase.js` (Group 22) and `link_case.js`/`link_Case.js` (Groups 17/20/21) — treat all four as one modernization requirement, not four separate ones, pending a byte-level diff to confirm they're truly identical logic.

---

## Group 15 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Lists/Security_Alerts/DispForm.aspx` (WebPartId `cd479b12-676e-4057-8a0c-ef011f3aca92`, Content Editor)

**All pages in this group:** `/cmat/Lists/Security_Alerts/DispForm.aspx`

```html
<script type="text/javascript" src="/sandbox/SiteAssets/JS/jquery-3.5.0.js"></script><script type="text/javascript" src="/cmat/SiteAssets/JS/HideLinksInDisplayForm.js"></script>​​ 
<script type="text/javascript" src="/cmat/SiteAssets/JS/HideLinksToPersons.js"></script>​​​​​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Removes classic action/detail links (HideLinksInDisplayForm.js, HideLinksToPersons.js) on the Security_Alerts Display form.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Permissions plus modern form/view configuration.
- **MVP decision:** Enforce via permissions if intent is preventing access, otherwise view-config only.
- **SPFx candidate:** No, unless a presentation-only link suppression requirement survives validation.

### Modernization Behaviour Analysis

**User-visible effect:**  
On the Security_Alerts Display form, action/detail links (including links to related Person records) are removed from the display.

**Business intent:**  
Likely intended to restrict navigation away from the alert into related records — possibly a privacy/need-to-know consideration given this is a Security Alerts list.

**Actual enforcement level:**  
Presentation-only — same caveat as Group 8/2: hiding a link is not access control. If Security Alerts genuinely have privacy requirements, cosmetic hiding does not satisfy them.

**Modern SharePoint Online approach:**  
Given this is a Security Alerts list, this is the strongest case in the current groups for a real permissions review rather than cosmetic hiding — confirm with the business whether item/list-level permissions already restrict who can even open this Display form, and layer that instead of/in addition to any presentation change.

**SPFx assessment:**  
No, unless a validated presentation-only requirement remains after the permissions question is resolved.

**Migration note:**  
jQuery/DOM-class dependent, will not function on the modern display form.

---

## Group 16 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Pages/Appearing_Persons_Briefing.aspx` (WebPartId `fb324dfd-1d66-439e-8fb0-6dec563e4838`, Content Editor)

**All pages in this group:** `/cmat/Pages/Appearing_Persons_Briefing.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}
.ms-cellstyle.ms-vb2
{
   font-family: Arial,calibri,Helvetica, sans-serif; 
   font-size: 13px;
}

#DeltaPlaceHolderMain{
    margin-top:-75px;
}

</script><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/RLHelper-ParentDisplayForm.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>​​ 
<br/>​​<br/>​​<br/></style>​<br/>
```

### Modernization Assessment

- **Business behavior:** Conditional display (ConditionalColoring.js), command relabeling (NewItemToAddNewHeadingChanger.js), and parent-context propagation to a child form (RLHelper-ParentDisplayForm.js) on the Appearing Persons Briefing page.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON formatting, accept standard command labels where possible, and Power Apps/page parameters for parent-child prefill.
- **MVP decision:** Decompose.
- **SPFx candidate:** Conditional — only after the parent-child interaction is prototyped with supported form capabilities.

### Modernization Behaviour Analysis

**User-visible effect:**  
On the Appearing Persons Briefing page: conditional row display/colouring, a relabeled "New Item" command, and correct parent-context carry-through when navigating to a related child form.

**Business intent:**  
Same recurring UX concerns as elsewhere (visual triage, clearer command wording, correct context linkage) applied to this specific briefing page.

**Actual enforcement level:**  
Presentation and navigation-convenience only.

**Modern SharePoint Online approach:**  
JSON formatting for conditional display, native list command config for labels, and the Power Apps `Param()` pattern (Group 4) for parent-child context.

**SPFx assessment:**  
Conditional — only after the parent-child interaction is prototyped and found insufficient with the native Power Apps approach.

**Migration note:**  
Same jQuery/DOM dependency pattern as the other ExternalHelpersOnly groups.

---

## Group 17 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Pages/Persons_PIO.aspx` (WebPartId `2174ec07-be33-4097-9bbc-a83ebb7fa380`, Content Editor)

**All pages in this group:** `/cmat/Pages/Persons_PIO.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}

</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script><script src="/cmat/SiteAssets/JS/makehyperlink.js" type="text/javascript"></script>​ ​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/RLHelper-ParentDisplayForm.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/link_Case.js" type="text/javascript"></script>​​​​<br/>​​​​<br/>​<br/> ​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Composite Persons page pattern (Persons_PIO.aspx) covering list formatting, command wording, parent-child creation, case links (link_Case.js), URL conversion (makehyperlink.js), and attachment display.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Decompose into JSON formatting, hyperlink field/formatting, native attachments, and Power Apps/page-parameter patterns.
- **MVP decision:** Decompose — pending link_Case.js evidence.
- **SPFx candidate:** Conditional — do not create one monolithic replacement for the legacy bundle.
- **Evidence gap / caveat:** link_Case.js is documented in Part 2 of this document as linkPIOCase.js's sibling pattern (linkCase.js) — a JSLink field-renderer with a hardcoded View GUID, confirming the earlier "must be inspected" gap is now closed.

### Modernization Behaviour Analysis

**User-visible effect:**  
On Persons_PIO.aspx: list formatting/colouring, a relabeled command, a clickable link from a related record to its parent case (same mechanism as Group 14, `link_Case.js`), plain-text URLs in a field converted to real clickable hyperlinks (`makehyperlink.js`), and attachment filenames shown inline.

**Business intent:**  
Five separate, unrelated UX aids bundled onto the Persons_PIO page: visual triage, navigation to the parent case, usable links instead of raw URL text, and visible attachment names.

**Actual enforcement level:**  
Presentation/navigation only across all five concerns.

**Modern SharePoint Online approach:**  
Decompose per-concern, same as Group 6: JSON formatting (colouring), native list config (labels), JSON/native hyperlink column formatting or a Field Customizer only if needed (case link — see Group 14's fuller writeup), a hyperlink-type column (URL-to-link conversion), and native attachment behavior.

**SPFx assessment:**  
Conditional at most, and only for the case-link piece if native/JSON approaches genuinely can't reproduce it — do not build one monolithic component for this bundle.

**Migration note:**  
Same `link_Case.js` hardcoded-View-GUID fragility described under Group 14 applies here.

---

## Group 18 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Pages/Manage_Security_Alerts.aspx` (WebPartId `656e1256-dfa9-4d40-9ca0-dd297e25c5fe`, Content Editor)

**All pages in this group:** `/cmat/Pages/Manage_Security_Alerts.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}

#QCB1_Button2
{ display: none }

div.ms-dragDropAttract-subtle
{ display: none }

</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/NewTasktoAddNewHeadingChanger.js" type="text/javascript"></script>​​​ 
<script src="/cmat/SiteAssets/JS/HideLinksToPersons.js" type="text/javascript"></script>​​​​​​​​<br/>​​<br/>
```

### Modernization Assessment

- **Business behavior:** Formatting, link suppression, and command relabeling (ConditionalColoring.js, HideLinksToPersons.js, NewTasktoAddNewHeadingChanger.js) on Manage_Security_Alerts.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON formatting, permissions/view design, and acceptance of modern command wording.
- **MVP decision:** Simplify.
- **SPFx candidate:** Unlikely for MVP.

### Modernization Behaviour Analysis

**User-visible effect:**  
On Manage_Security_Alerts.aspx: list formatting/colouring, Person-link removal, and a relabeled task command.

**Business intent:**  
Same recurring concerns as elsewhere, applied to the security alert management page.

**Actual enforcement level:**  
Presentation-only.

**Modern SharePoint Online approach:**  
Same decomposition as Groups 2/3 — JSON formatting, permissions if link removal is a real requirement, native list command config.

**SPFx assessment:**  
No — unlikely for MVP.

**Migration note:**  
Same jQuery/DOM dependency pattern as related groups.

---

## Group 19 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Pages/Purge_Planning.aspx` (WebPartId `c1a2cfc5-1776-4e69-baaf-f59e8650bdca`, Content Editor)

**All pages in this group:** `/cmat/Pages/Purge_Planning.aspx`

```html
   <style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}
</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/makehyperlink.js" type="text/javascript"></script>​ ​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script>​​​​<br/>​<br/>​​<br/><br/>
```

### Modernization Assessment

- **Business behavior:** Formatting, command relabeling, converting URL text into links (makehyperlink.js), and attachment filename display on Purge_Planning.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Hyperlink columns or JSON link formatting, JSON status formatting, native attachments, and standard command labels.
- **MVP decision:** Simplify.
- **SPFx candidate:** Conditional — only for a confirmed attachment presentation gap.

### Modernization Behaviour Analysis

**User-visible effect:**  
On Purge_Planning.aspx: list formatting, a relabeled command, plain-text URLs converted into real clickable links, and attachment filenames shown inline.

**Business intent:**  
Same recurring UX concerns — visual clarity, usable links, visible attachment names — applied to the purge-planning workflow.

**Actual enforcement level:**  
Presentation-only.

**Modern SharePoint Online approach:**  
Hyperlink-type column or JSON link formatting for URL text, JSON status formatting for colouring, native attachment behavior, native list command config.

**SPFx assessment:**  
Conditional — only for a confirmed attachment-presentation gap.

**Migration note:**  
Same recurring jQuery/DOM dependency pattern.

---

## Group 20 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Pages/Persons_ICM.aspx` (WebPartId `c6b503c2-e234-4ea4-b418-c83bf8f90f3b`, Content Editor)

**All pages in this group:** `/cmat/Pages/Persons_ICM.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}
</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/makehyperlink.js" type="text/javascript"></script>​ ​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script><script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script>​​​​ 
<script src="/cmat/SiteAssets/JS/link_Case.js" type="text/javascript"></script>​​​​<br/><br/>​​<br/>​​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Formatting, command wording, related-case navigation (link_Case.js), URL conversion, and attachment display on Persons_ICM.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** JSON formatting, native hyperlink fields, native attachment behavior, and a validated related-case navigation pattern.
- **MVP decision:** Decompose — pending link_Case.js evidence.
- **SPFx candidate:** Conditional.
- **Evidence gap / caveat:** See Part 2 of this document — link_Case.js/linkCase.js/linkPIOCase.js are all JSLink field-renderers with hardcoded View GUIDs; this gap is now closed.

### Modernization Behaviour Analysis

**User-visible effect:**  
On Persons_ICM.aspx: list formatting, a relabeled command, a clickable link from a related record to its parent case (`link_Case.js`, same mechanism as Group 14), plain-text URLs converted to clickable links, and attachment filenames shown inline.

**Business intent:**  
Same five-concern bundle as Group 17, applied to the ICM Persons page instead of PIO.

**Actual enforcement level:**  
Presentation/navigation only, same as Group 17.

**Modern SharePoint Online approach:**  
Same decomposition as Group 17 — JSON formatting, native list config, native/JSON hyperlink formatting or Field Customizer only if needed for the case link, hyperlink column for URL conversion, native attachments.

**SPFx assessment:**  
Conditional at most, and only for the case-link piece — same as Group 17.

**Migration note:**  
Same hardcoded-View-GUID fragility as Group 14 applies to the `link_Case.js` reference here.

---

## Group 21 — ExternalHelpersOnly (1 instance)

**Representative:** `/cmat/Pages/Persons_ITAU.aspx` (WebPartId `4c6a64d0-d7f2-4162-8af8-7a57db19f0bb`, Content Editor)

**All pages in this group:** `/cmat/Pages/Persons_ITAU.aspx`

```html
<style type="text/css">
.ms-webpart-titleText {
   font-style: italic;
   font-weight: bold;
}
</style><script src="/cmat/SiteAssets/JS/jquery-3.5.0.js" type="text/javascript"></script>​ 
<script src="/cmat/SiteAssets/JS/makehyperlink.js" type="text/javascript"></script>​ ​ 
<script src="/cmat/SiteAssets/JS/ConditionalColoring.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/NewItemToAddNewHeadingChanger.js" type="text/javascript"></script> 
<script src="/cmat/SiteAssets/JS/showattachmentname.js" type="text/javascript"></script>
<script type="text/javascript" src="/cmat/SiteAssets/JS/link_case.js"></script>​​​​​<br/>
​<br/>​<br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Same broad concern set as Group 20 (Persons_ITAU.aspx), using a differently-cased case-link helper filename (link_case.js).
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Same decomposition as Group 20.
- **MVP decision:** Decompose.
- **SPFx candidate:** Conditional.
- **Evidence gap / caveat:** Part 2 of this document confirms `linkCase.js` (capital C) is the real filename read and reviewed; `link_case.js`/`link_Case.js` naming variants across groups 14/17/20/21 appear to be case-sensitivity/filename inconsistencies in how the page references the same underlying script family, not behaviorally distinct scripts — treat as one modernization requirement across all four groups pending a byte-level diff of each referenced file.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same bundle as Group 20, on Persons_ITAU.aspx.

**Business intent:**  
Same as Group 20.

**Actual enforcement level:**  
Presentation/navigation only, same as Group 20.

**Modern SharePoint Online approach:**  
Same decomposition as Group 20.

**SPFx assessment:**  
Conditional at most, same as Group 20.

**Migration note:**  
Same case-link fragility as Group 14/17/20 — all four groups (14/17/20/21) reference the same underlying script family under naming variants and should be resolved as one modernization decision.

---

## Group 22 — InlineLogic (1 instance)

**Representative:** `/cmat/Pages/My_ICM_Cases.aspx` (WebPartId `946f4f5a-a0e3-4472-841a-ced12c4a57f3`, Content Editor)

**All pages in this group:** `/cmat/Pages/My_ICM_Cases.aspx`

```html
&#160;​<br/> 
<script src="/cmat/SiteAssets/JS/linkPIOCase.js" type="text/javascript"></script>​<script src="https://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"> </script><script type="text/javascript">

$(document).ready(function() {
function getTheStatusColumnIndex(){
    var final_index = null;
    $('#scriptWPQ4> table > thead > tr > th').each(function(index, value) {
        var result = $(value).find('div[displayname = "Status"]').length;
        if (result){
            final_index = index;
        }
   });
   return final_index;
};

var index = getTheStatusColumnIndex();

if (!index){
    console.log("Error: Status Column is not available");
} else {
    var case_status = $('#scriptWPQ4> table > tbody > tr > td:eq('+index+')').text();

    if (case_status === 'Closed'){
        $(".ms-heroCommandLink").each((index, element) => {
            var identifier = $(element).parents(".ms-webpartzone-cell").attr('id');
            if(identifier != "MSOZoneCell_WebPartWPQ11"){
                $(element).hide();
                $("#QCB1_Button2").hide();
            }
        });
         $(".ms-vb-icon").each((index, el) => {
                var identifier = $(el).parents(".ms-webpartzone-cell").attr('id');
                if (identifier != "MSOZoneCell_WebPartWPQ4"){
                    $(el).find('a').hide();
                }
            });
    }
}
});
</script>​​​​​​​​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons for that web part zone. Also loads a case-link helper (linkPIOCase.js). Deployed identically (with page-specific selector IDs) on 6 dashboard pages: My_ICM_Cases.aspx, ICM_Cases.aspx, PIO_Cases.aspx, My_PIO_Cases.aspx, ITAU_Cases.aspx, My_ITAU_Cases.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Enforce the underlying business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **MVP decision:** Consolidate as ONE modernization pattern deployed 6 times — do not build 6 separate components.
- **SPFx candidate:** Conditional — a reusable List View Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Validation required:** Business-rule question: is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Evidence gap / caveat:** Critical security note: hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization — if the rule must actually hold, enforce it via permissions/workflow, not command-bar hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
When the page loads, the script checks the case Status in the `scriptWPQ4` list view table. If the Status value is `Closed`, it hides most New/Add command links and most row-level action links on the page. The page appears mostly read-only for a closed case. It leaves specific web parts alone using hardcoded web-part zone IDs.

**Business intent:**  
The apparent intent is to discourage users from adding or changing related work once a case is closed.

**Actual enforcement level:**  
Presentation-only. The script only hides buttons and links in the browser. It does not change permissions, lock records, validate saves, block direct URLs, or prevent API updates. It should not be treated as security or true business-rule enforcement.

**Related helper behaviour:**  
The same Content Editor also loads `linkPIOCase.js`. That helper uses classic SharePoint CSR/JSLink to render the `RelatedPIOCases` lookup field as a clickable link to the related PIO case page. It builds a URL to `/cmat/Pages/PIO_Cases.aspx` using a hardcoded View GUID and `SelectedID=<lookupId>`. This is navigation/presentation logic only.

**Modern SharePoint Online approach:**  
For the closed-case behaviour, first decide whether the business rule is "users must not add/change related records after closure" or merely "do not show clutter on closed cases." If the rule must be enforced, implement it through permissions, Power Apps form logic, Power Automate, validation, or process rules. If the business only wants the old visual behaviour, consider accepting the modern command bar as-is. Use an SPFx ListView Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement.

For the related PIO case link, first assess native lookup rendering, a hyperlink column, or JSON column formatting. Consider an SPFx Field Customizer only if JSON/native rendering cannot reproduce the required navigation.

**SPFx assessment:**  
Conditional. Group 22 does not prove SPFx is required. One reusable SPFx Command Set may be justified only if exact closed-case command hiding is mandatory. A Field Customizer may be considered only if the related-case link cannot be handled through native lookup/link rendering or JSON formatting.

**Migration note:**  
The script depends on classic DOM IDs such as `scriptWPQ4`, `MSOZoneCell_WebPartWPQ11`, `MSOZoneCell_WebPartWPQ4`, and `QCB1_Button2`. These are classic SharePoint page implementation details and should not be carried forward. `linkPIOCase.js` also contains a hardcoded View GUID that is fragile and unlikely to survive migration to SPO.

---

## Group 23 — InlineLogic (1 instance)

**Representative:** `/cmat/Pages/ICM_Cases.aspx` (WebPartId `60b3dbe6-882e-4b67-a8a2-8e322e0f4645`, Content Editor)

**All pages in this group:** `/cmat/Pages/ICM_Cases.aspx`

```html
&#160;<br/> 
<script src="/cmat/SiteAssets/JS/linkPIOCase.js" type="text/javascript"></script>​<script src="https://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"> </script><script type="text/javascript">

$(document).ready(function() {
function <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd52988" class="ms-spellcheck-error ms-rtegenerate-skip">getTheStatusColumnIndex</span></span>(){
    <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd49589" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd48494" class="ms-spellcheck-error ms-rtegenerate-skip">final_index</span></span> = null;
    $('#scriptWPQ7> table > <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd17898" class="ms-spellcheck-error ms-rtegenerate-skip">thead</span></span> > <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90028" class="ms-spellcheck-error ms-rtegenerate-skip">tr</span></span> > <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38463" class="ms-spellcheck-error ms-rtegenerate-skip">th</span></span>').each(function(index, value) {
        <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90271" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span> result = $(value).find('div[<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd67590" class="ms-spellcheck-error ms-rtegenerate-skip">displayname</span></span> = "Status"]').length;
        if (result){
            <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21350" class="ms-spellcheck-error ms-rtegenerate-skip">final_index</span></span> = index;
        }
   });
   return <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd7842" class="ms-spellcheck-error ms-rtegenerate-skip">final_index</span></span>;
};

<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd29951" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span> index = <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd64626" class="ms-spellcheck-error ms-rtegenerate-skip">getTheStatusColumnIndex</span></span>();

if (!index){
    console.log("Error: Status Column is not available");
} else {
    <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd30558" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd18947" class="ms-spellcheck-error ms-rtegenerate-skip">case_status</span></span> = $('#scriptWPQ7> table > <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46570" class="ms-spellcheck-error ms-rtegenerate-skip">tbody</span></span> > <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd32692" class="ms-spellcheck-error ms-rtegenerate-skip">tr</span></span> > <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd99671" class="ms-spellcheck-error ms-rtegenerate-skip">td:eq</span></span>('+index+')').text();

    if (<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83917" class="ms-spellcheck-error ms-rtegenerate-skip">case_status</span></span> === 'Closed'){
        $(".<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46622" class="ms-spellcheck-error ms-rtegenerate-skip">ms-heroCommandLink</span></span>").each((index, element) => {
            <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd67883" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span> identifier = $(element).parents(".<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41658" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41931" class="ms-spellcheck-error ms-rtegenerate-skip">webpartzone</span></span>-cell").<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25455" class="ms-spellcheck-error ms-rtegenerate-skip">attr</span></span>('id');
            if(identifier != "MSOZoneCell_WebPartWPQ8"){
                $(element).hide();
                $("#QCB1_Button2").hide();
            }
        });
         $(".<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98927" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21221" class="ms-spellcheck-error ms-rtegenerate-skip">vb</span></span>-icon").each((index, el) => {
                <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96968" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span> identifier = $(el).parents(".<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80522" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21972" class="ms-spellcheck-error ms-rtegenerate-skip">webpartzone</span></span>-cell").<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd61188" class="ms-spellcheck-error ms-rtegenerate-skip">attr</span></span>('id');
                if (identifier != "MSOZoneCell_WebPartWPQ7"){
                    $(el).find('a').hide();
                }
            });
    }
}
});
</script>​​​​​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons for that web part zone. Also loads a case-link helper (linkPIOCase.js). Deployed identically (with page-specific selector IDs) on 6 dashboard pages: My_ICM_Cases.aspx, ICM_Cases.aspx, PIO_Cases.aspx, My_PIO_Cases.aspx, ITAU_Cases.aspx, My_ITAU_Cases.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Enforce the underlying business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **MVP decision:** Consolidate as ONE modernization pattern deployed 6 times — do not build 6 separate components.
- **SPFx candidate:** Conditional — a reusable List View Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Validation required:** Business-rule question: is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Evidence gap / caveat:** Critical security note: hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization — if the rule must actually hold, enforce it via permissions/workflow, not command-bar hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
Identical pattern to Group 22, deployed on ICM_Cases.aspx: closed-case Status check hides New/Add and row action links, leaving specific web-part zones alone via hardcoded zone IDs.

**Business intent:**  
Same as Group 22 — discourage changes to a closed case's related work.

**Actual enforcement level:**  
Presentation-only, same as Group 22 — not security, not real enforcement.

**Related helper behaviour:**  
Same `linkPIOCase.js` reference and behavior as Group 22.

**Modern SharePoint Online approach:**  
Same as Group 22 — this is the same reusable decision (Groups 22–27), not a separate design question.

**SPFx assessment:**  
Conditional, same as Group 22 — one shared decision across all six groups, not six.

**Migration note:**  
Same classic-DOM-ID and hardcoded-View-GUID fragility as Group 22, with this page's own selector IDs.

---

## Group 24 — InlineLogic (1 instance)

**Representative:** `/cmat/Pages/PIO_Cases.aspx` (WebPartId `a810a82e-173f-4aa7-a8e0-fb29a6c32587`, Content Editor)

**All pages in this group:** `/cmat/Pages/PIO_Cases.aspx`

```html
&#160;​<br/><script src="/cmat/SiteAssets/JS/linkPIOCase.js" type="text/javascript"></script>​<script src="https://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"> </script> 
<script type="text/javascript">

$(document).ready(function() {
function getTheStatusColumnIndex(){
    var final_index = null;
    $('#scriptWPQ9> table > thead > tr > th').each(function(index, value) {
        var result = $(value).find('div[displayname = "Status"]').length;
        if (result){
            final_index = index;
        }
   });
   return final_index;
};

var index = getTheStatusColumnIndex();

if (!index){
    console.log("Error: Status Column is not available");
} else {
    var case_status = $('#scriptWPQ9> table > tbody > tr > td:eq('+index+')').text();

    if (case_status === 'Closed'){
        $(".ms-heroCommandLink").each((index, element) => {
            var identifier = $(element).parents(".ms-webpartzone-cell").attr('id');
            if(identifier != "MSOZoneCell_WebPartWPQ3"){
                $(element).hide();
                $("#QCB1_Button2").hide();
            }
        });
         $(".ms-vb-icon").each((index, el) => {
                var identifier = $(el).parents(".ms-webpartzone-cell").attr('id');
                if (identifier != "MSOZoneCell_WebPartWPQ9"){
                    $(el).find('a').hide();
                }
            });
    }
}
});
</script>​​​​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons for that web part zone. Also loads a case-link helper (linkPIOCase.js). Deployed identically (with page-specific selector IDs) on 6 dashboard pages: My_ICM_Cases.aspx, ICM_Cases.aspx, PIO_Cases.aspx, My_PIO_Cases.aspx, ITAU_Cases.aspx, My_ITAU_Cases.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Enforce the underlying business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **MVP decision:** Consolidate as ONE modernization pattern deployed 6 times — do not build 6 separate components.
- **SPFx candidate:** Conditional — a reusable List View Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Validation required:** Business-rule question: is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Evidence gap / caveat:** Critical security note: hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization — if the rule must actually hold, enforce it via permissions/workflow, not command-bar hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
Identical pattern to Group 22, deployed on PIO_Cases.aspx.

**Business intent:**  
Same as Group 22.

**Actual enforcement level:**  
Presentation-only, same as Group 22.

**Related helper behaviour:**  
Same `linkPIOCase.js` reference and behavior as Group 22.

**Modern SharePoint Online approach:**  
Same as Group 22 — one shared decision across Groups 22–27.

**SPFx assessment:**  
Conditional, same as Group 22.

**Migration note:**  
Same classic-DOM-ID and hardcoded-View-GUID fragility as Group 22, with this page's own selector IDs.

---

## Group 25 — InlineLogic (1 instance)

**Representative:** `/cmat/Pages/My_PIO_Cases.aspx` (WebPartId `b3eb4d32-e234-4708-b64a-0afdc0d8186b`, Content Editor)

**All pages in this group:** `/cmat/Pages/My_PIO_Cases.aspx`

```html
&#160;​​<br/> 
<script src="/cmat/SiteAssets/JS/linkPIOCase.js" type="text/javascript"></script>​<script src="https://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"> </script>
<script type="text/javascript">

$(document).ready(function() {
function getTheStatusColumnIndex(){
    var final_index = null;
    $('#scriptWPQ3> table > thead > tr > th').each(function(index, value) {
        var result = $(value).find('div[displayname = "Status"]').length;
        if (result){
            final_index = index;
        }
   });
   return final_index;
};

var index = getTheStatusColumnIndex();

if (!index){
    console.log("Error: Status Column is not available");
} else {
    var case_status = $('#scriptWPQ3> table > tbody > tr > td:eq('+index+')').text();

    if (case_status === 'Closed'){
        $(".ms-heroCommandLink").each((index, element) => {
            var identifier = $(element).parents(".ms-webpartzone-cell").attr('id');
            if(identifier != "MSOZoneCell_WebPartWPQ7"){
                $(element).hide();
                $("#QCB1_Button2").hide();
            }
        });
         $(".ms-vb-icon").each((index, el) => {
                var identifier = $(el).parents(".ms-webpartzone-cell").attr('id');
                if (identifier != "MSOZoneCell_WebPartWPQ3"){
                    $(el).find('a').hide();
                }
            });
    }
}
});
</script>​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons for that web part zone. Also loads a case-link helper (linkPIOCase.js). Deployed identically (with page-specific selector IDs) on 6 dashboard pages: My_ICM_Cases.aspx, ICM_Cases.aspx, PIO_Cases.aspx, My_PIO_Cases.aspx, ITAU_Cases.aspx, My_ITAU_Cases.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Enforce the underlying business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **MVP decision:** Consolidate as ONE modernization pattern deployed 6 times — do not build 6 separate components.
- **SPFx candidate:** Conditional — a reusable List View Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Validation required:** Business-rule question: is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Evidence gap / caveat:** Critical security note: hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization — if the rule must actually hold, enforce it via permissions/workflow, not command-bar hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
Identical pattern to Group 22, deployed on My_PIO_Cases.aspx.

**Business intent:**  
Same as Group 22.

**Actual enforcement level:**  
Presentation-only, same as Group 22.

**Related helper behaviour:**  
Same `linkPIOCase.js` reference and behavior as Group 22.

**Modern SharePoint Online approach:**  
Same as Group 22 — one shared decision across Groups 22–27.

**SPFx assessment:**  
Conditional, same as Group 22.

**Migration note:**  
Same classic-DOM-ID and hardcoded-View-GUID fragility as Group 22, with this page's own selector IDs.

---

## Group 26 — InlineLogic (1 instance)

**Representative:** `/cmat/Pages/ITAU_Cases.aspx` (WebPartId `03ac1682-1a86-4c9e-9e85-d636eabad9ce`, Content Editor)

**All pages in this group:** `/cmat/Pages/ITAU_Cases.aspx`

```html
<script src="/cmat/SiteAssets/JS/linkPIOCase.js" type="text/javascript"></script> 
​<script src="https://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"></script>

<script type="text/javascript">

$(document).ready(function() {
function getTheStatusColumnIndex(){
    var final_index = null;
    $('#scriptWPQ7 > table > thead > tr > th').each(function(index, value) {
        var result = $(value).find('div[displayname = "Status"]').length;
        if (result){
            final_index = index;
        }
   });
   return final_index;
};

var index = getTheStatusColumnIndex();

if (!index){
    console.log("Error: Status Column is not available");
} else {
    var case_status = $('#scriptWPQ7> table > tbody > tr > td:eq('+index+')').text();
    console.log(case_status , "status");
    if (case_status === 'Closed'){
        $(".ms-heroCommandLink").each((index, element) => {
            var identifier = $(element).parents(".ms-webpartzone-cell").attr('id');
            if(identifier != "MSOZoneCell_WebPartWPQ6"){
                $(element).hide();
                $("#QCB1_Button2").hide();
            }
        });
         $(".ms-vb-icon").each((index, el) => {
                var identifier = $(el).parents(".ms-webpartzone-cell").attr('id');
                if (identifier != "MSOZoneCell_WebPartWPQ7"){
                    $(el).find('a').hide();
                }
         });
    }
}
});
</script>​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons for that web part zone. Also loads a case-link helper (linkPIOCase.js). Deployed identically (with page-specific selector IDs) on 6 dashboard pages: My_ICM_Cases.aspx, ICM_Cases.aspx, PIO_Cases.aspx, My_PIO_Cases.aspx, ITAU_Cases.aspx, My_ITAU_Cases.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Enforce the underlying business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **MVP decision:** Consolidate as ONE modernization pattern deployed 6 times — do not build 6 separate components.
- **SPFx candidate:** Conditional — a reusable List View Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Validation required:** Business-rule question: is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Evidence gap / caveat:** Critical security note: hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization — if the rule must actually hold, enforce it via permissions/workflow, not command-bar hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
Identical pattern to Group 22, deployed on ITAU_Cases.aspx.

**Business intent:**  
Same as Group 22.

**Actual enforcement level:**  
Presentation-only, same as Group 22.

**Related helper behaviour:**  
Same `linkPIOCase.js` reference and behavior as Group 22.

**Modern SharePoint Online approach:**  
Same as Group 22 — one shared decision across Groups 22–27.

**SPFx assessment:**  
Conditional, same as Group 22.

**Migration note:**  
Same classic-DOM-ID and hardcoded-View-GUID fragility as Group 22, with this page's own selector IDs.

---

## Group 27 — InlineLogic (1 instance)

**Representative:** `/cmat/Pages/My_ITAU_Cases.aspx` (WebPartId `b9a982ff-9200-4112-bcb0-9b76e9f9fbfc`, Content Editor)

**All pages in this group:** `/cmat/Pages/My_ITAU_Cases.aspx`

```html
<script src="/cmat/SiteAssets/JS/linkPIOCase.js" type="text/javascript"></script> 
​<script src="https://code.jquery.com/jquery-1.7.2.min.js" type="text/javascript"></script>

<script type="text/javascript">

$(document).ready(function() {
function <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28065" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd5572" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36859" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd71173" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91370" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd95585" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3550" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd73715" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd27895" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11322" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96234" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77714" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81854" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98408" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd27100" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35979" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd40917" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd44514" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76925" class="ms-spellcheck-error ms-rtegenerate-skip">getTheStatusColumnIndex</span></span></span></span>(){
    <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd99984" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59204" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16177" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11238" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33427" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45138" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41897" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd26176" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd23643" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21684" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91185" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd94029" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd18878" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd78128" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd80746" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd17053" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd47548" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28702" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25785" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span></span></span> <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd55825" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd14547" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46645" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33526" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd34479" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45516" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36539" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58636" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58797" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22965" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38416" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88290" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58665" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd19785" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd64206" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51085" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79968" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3737" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd26665" class="ms-spellcheck-error ms-rtegenerate-skip">final_index</span></span></span></span> = null;
    $('#scriptWPQ11 > table > <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28941" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11207" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd99686" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65981" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91618" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33786" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd43007" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39128" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76996" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd8527" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd1615" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39277" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd34892" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd48618" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd44214" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd541" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80711" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81107" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91436" class="ms-spellcheck-error ms-rtegenerate-skip">thead</span></span></span></span> > <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd27205" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd60697" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd85004" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd24507" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd14229" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81659" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80226" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd18859" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77594" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33589" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58115" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25818" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd99754" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79403" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd55105" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd9237" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd20058" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd979" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd40452" class="ms-spellcheck-error ms-rtegenerate-skip">tr</span></span></span></span> > <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79769" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65208" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83555" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83896" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88985" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3595" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd40872" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35888" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd13765" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd50859" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd37018" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd40562" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd63832" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd26361" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd53940" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79093" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38127" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59794" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98490" class="ms-spellcheck-error ms-rtegenerate-skip">th</span></span></span></span>').each(function(index, value) {
        <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33398" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96411" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd57894" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd71679" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd44431" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd23722" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd26154" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65700" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd1847" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59784" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd87202" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd69522" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd49247" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41423" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd22659" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd5093" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd82967" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd23982" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92822" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span></span></span> result = $(value).find('div[<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45309" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd95072" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd512" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd13910" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd71591" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd19671" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd89450" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88593" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd86810" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77726" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd66396" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd73659" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36066" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98907" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd54626" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd17009" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd54143" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd34077" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd24010" class="ms-spellcheck-error ms-rtegenerate-skip">displayname</span></span></span></span> = "Status"]').length;
        if (result){
            <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd2462" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35319" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd12769" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58403" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35823" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59765" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33873" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36520" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd17604" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd24415" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33573" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd86416" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81207" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd12322" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd82551" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25065" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd31366" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd37938" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45987" class="ms-spellcheck-error ms-rtegenerate-skip">final_index</span></span></span></span> = index;
        }
   });
   return <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd95481" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79558" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51564" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11211" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98359" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd34072" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd60322" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd78676" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11472" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd31512" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd53063" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39229" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd14313" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd52696" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd98940" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd29645" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd5886" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd71403" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd56956" class="ms-spellcheck-error ms-rtegenerate-skip">final_index</span></span></span></span>;
};

<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35276" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11324" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74712" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25543" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35271" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd95951" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd4010" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35303" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd37268" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd44088" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74779" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33414" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd57397" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92504" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd25386" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74699" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3213" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd24757" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd54098" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span></span></span> index = <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98856" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd10357" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd86871" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd43165" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd30808" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd48792" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35585" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd50976" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd15534" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd82644" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51506" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92703" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd48358" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77696" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd84413" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88694" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79910" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83102" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38486" class="ms-spellcheck-error ms-rtegenerate-skip">getTheStatusColumnIndex</span></span></span></span>();

if (!index){
    console.log("Error: Status Column is not available");
} else {
    <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd62391" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76078" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd20960" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd50015" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd7466" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd40162" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd52215" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd47955" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45421" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3794" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd6734" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd7325" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd55677" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd78155" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd93304" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd47694" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76250" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd23973" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28961" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span></span></span> <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd18262" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3616" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21677" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd63195" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80064" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd84163" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd54401" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd95611" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80280" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd9219" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd23943" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25949" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58246" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98870" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd30388" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38532" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21982" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd62646" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd31458" class="ms-spellcheck-error ms-rtegenerate-skip">case_status</span></span></span></span> = $('#scriptWPQ11> table > <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59595" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25194" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74829" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd55185" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79121" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51016" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd33864" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd61681" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd66408" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74174" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88194" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46045" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22897" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd34937" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd86516" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd17396" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77634" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd95588" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81929" class="ms-spellcheck-error ms-rtegenerate-skip">tbody</span></span></span></span> > <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd71378" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd29490" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65050" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96044" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd13745" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21949" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39365" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd923" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd43604" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd31443" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88565" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98370" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd71870" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46703" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd39982" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd1924" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90250" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd89224" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41427" class="ms-spellcheck-error ms-rtegenerate-skip">tr</span></span></span></span> > <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd97345" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd97445" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd50322" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16329" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd4373" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd19586" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92116" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd8790" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd6224" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd7461" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd56531" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd85642" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51096" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd68798" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd8193" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd1552" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd73408" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd87944" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd82922" class="ms-spellcheck-error ms-rtegenerate-skip">td:eq</span></span></span></span>('+index+')').text();
    console.log(<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd6741" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd7297" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81253" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd15061" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd42169" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65113" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd21015" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd69137" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd60815" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98140" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd66141" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd893" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd61744" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd10664" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd41251" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd6197" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd66614" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd20125" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd67416" class="ms-spellcheck-error ms-rtegenerate-skip">case_status</span></span></span></span> , "status");
    if (<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16240" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd5014" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd42898" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd32469" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd29911" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51545" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77310" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd43263" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd44589" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd19983" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd56740" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35659" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98753" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41723" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd62390" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58367" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd17114" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11740" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36737" class="ms-spellcheck-error ms-rtegenerate-skip">case_status</span></span></span></span> === 'Closed'){
        $(".<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96354" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92557" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59535" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd31693" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd60633" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd4235" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd31329" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd94804" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd69225" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd24765" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd69782" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28325" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd64180" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79057" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd56275" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd72497" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd64279" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd52861" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd10551" class="ms-spellcheck-error ms-rtegenerate-skip">ms-heroCommandLink</span></span></span></span>").each((index, element) => {
            <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd58184" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd86776" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd52156" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd3336" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd63096" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81042" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd75545" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd10989" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46169" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38616" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd38430" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41507" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd20626" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91459" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd57327" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74757" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28183" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd62397" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16843" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span></span></span> identifier = $(element).parents(".<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41854" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77287" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39109" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd87314" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51581" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98859" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd64735" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd40317" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd44376" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd88085" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd62921" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96220" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd67562" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90407" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd74880" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd97244" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36176" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22277" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16973" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span></span></span>-<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd51214" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45284" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd67932" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96463" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd9417" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd20615" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd197" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd84008" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16676" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65111" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41913" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd97225" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22653" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96813" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd2638" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd15764" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd27011" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd30226" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76069" class="ms-spellcheck-error ms-rtegenerate-skip">webpartzone</span></span></span></span>-cell").<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd30718" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd94634" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd65907" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83960" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39115" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22863" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11366" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22226" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91688" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90867" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd2209" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd70189" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd32014" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd39583" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd7829" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd43201" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59259" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92466" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd44493" class="ms-spellcheck-error ms-rtegenerate-skip">attr</span></span></span></span>('id');
            if(identifier != "MSOZoneCell_WebPartWPQ6"){
                $(element).hide();
                $("#QCB1_Button2").hide();
            }
        });
         $(".<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd749" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd562" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd50636" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd82573" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd91237" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd28653" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd14101" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd72772" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd47130" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd55756" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81261" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd85766" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd57994" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83691" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd67081" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd49823" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81415" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd4679" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90578" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span></span></span>-<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd49515" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd47931" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd75043" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd10776" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd8398" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd830" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83988" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd89178" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd63712" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd86143" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd768" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd379" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd22915" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd83121" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd54458" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd68909" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd57102" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd19720" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd8773" class="ms-spellcheck-error ms-rtegenerate-skip">vb</span></span></span></span>-icon").each((index, el) => {
                <span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd82866" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd63236" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd6992" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd82290" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35553" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd81525" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd14334" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98541" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd84161" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd25221" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd47175" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd59773" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd78954" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd45928" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd35391" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd96830" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd15950" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd5007" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd18620" class="ms-spellcheck-error ms-rtegenerate-skip">var</span></span></span></span> identifier = $(el).parents(".<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd48049" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd97034" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd56642" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd57371" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd90916" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76703" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd72513" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd32280" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80431" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd98029" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd4" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35225" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd37047" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd42520" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd27116" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd67362" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd32574" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd27853" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd70382" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span></span></span>-<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd34789" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd70808" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd2869" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd43763" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd12391" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd53618" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd61037" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd41691" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74842" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd74216" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd46447" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd79106" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd73153" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77504" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd33941" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77532" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd99850" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd8982" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd5805" class="ms-spellcheck-error ms-rtegenerate-skip">webpartzone</span></span></span></span>-cell").<span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd97785" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd35307" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="white-space: <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd69071" class="ms-spellcheck-error ms-rtegenerate-skip">nowrap</span></span>;"><span class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd4070" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd80392" class="ms-spellcheck-error ms-rtegenerate-skip">rtestate</span></span>-read <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd54907" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd76184" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77630" class="ms-spellcheck-error ms-rtegenerate-skip">contenteditable</span></span>="false" style="font-size: 8pt;"><a class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd70106" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36207" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd73039" class="ms-spellcheck-error ms-rtegenerate-skip">img</span></span> <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd36550" class="ms-spellcheck-error ms-rtegenerate-skip">src</span></span>="/_layouts/images/blank.gif" alt="Misspelled Word" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd77912" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd26315" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip" style="width: 0px;"></a></span><span id="rnd37995" class="<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd11221" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-spellcheck-error <span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd7392" class="ms-spellcheck-error ms-rtegenerate-skip">ms</span></span>-<span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd16860" class="ms-spellcheck-error ms-rtegenerate-skip">rtegenerate</span></span>-skip"><span class="ms-rtegenerate-skip" style="white-space: nowrap;"><span class="ms-rtestate-read ms-rtegenerate-skip" contenteditable="false" style="font-size: 8pt;"><a class="ms-rtegenerate-skip"><img src="/_layouts/images/blank.gif" alt="Misspelled Word" class="ms-rtegenerate-skip" style="width: 0px;"></a></span><span id="rnd92642" class="ms-spellcheck-error ms-rtegenerate-skip">attr</span></span></span></span>('id');
                if (identifier != "MSOZoneCell_WebPartWPQ11"){
                    $(el).find('a').hide();
                }
         });
    }
}
});
</script>​<br/>
```

### Modernization Assessment

- **Business behavior:** Reads case Status from the rendered list view. If the case is Closed, hides New Item/command buttons and row action icons for that web part zone. Also loads a case-link helper (linkPIOCase.js). Deployed identically (with page-specific selector IDs) on 6 dashboard pages: My_ICM_Cases.aspx, ICM_Cases.aspx, PIO_Cases.aspx, My_PIO_Cases.aspx, ITAU_Cases.aspx, My_ITAU_Cases.aspx.
- **Text web part sufficient:** No.
- **Recommended modern replacement:** Enforce the underlying business rule through permissions, form rules, or workflow where possible. Use list formatting for visual status treatment. Accept the standard modern command bar if hiding it is not essential.
- **MVP decision:** Consolidate as ONE modernization pattern deployed 6 times — do not build 6 separate components.
- **SPFx candidate:** Conditional — a reusable List View Command Set only if exact context-sensitive command hiding is confirmed as an MVP requirement after security/business-rule options are exhausted.
- **Validation required:** Business-rule question: is the intent merely to reduce clutter, or to prevent creation/editing against closed cases? The answer changes the design.
- **Evidence gap / caveat:** Critical security note: hiding buttons does not prevent direct URL, API, or alternate-client edits. Do not treat the legacy behavior as authorization — if the rule must actually hold, enforce it via permissions/workflow, not command-bar hiding.

### Modernization Behaviour Analysis

**User-visible effect:**  
Identical pattern to Group 22, deployed on My_ITAU_Cases.aspx — the sixth and final instance of this pattern.

**Business intent:**  
Same as Group 22.

**Actual enforcement level:**  
Presentation-only, same as Group 22.

**Related helper behaviour:**  
Same `linkPIOCase.js` reference and behavior as Group 22.

**Modern SharePoint Online approach:**  
Same as Group 22 — this closes out the shared decision covering Groups 22–27. Build (at most) one reusable component or business-rule enforcement mechanism, applied to all six pages, not six separate implementations.

**SPFx assessment:**  
Conditional, same as Group 22.

**Migration note:**  
Same classic-DOM-ID and hardcoded-View-GUID fragility as Group 22, with this page's own selector IDs.

---

## Group 28 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/ICM_My_Tasks.aspx` (WebPartId `1947c9b9-ea5d-4909-930a-1ea116c4adeb`, Content Editor)

**All pages in this group:** `/cmat/Pages/ICM_My_Tasks.aspx`

```html
<br/>​<br/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​Covering for someone?&#160;&#160;</span><a href="/cmat/Pages/ICM_All_Tasks.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Click here to see all ICM, ITAU and PIO Tasks and Progress Logs​​</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​​ ​</span><br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** “Covering for someone?” link to all ICM, ITAU and PIO tasks and progress logs.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part. Quick Links or Button also acceptable if the modern design uses stronger navigation affordance.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Update the destination to the new consolidated tasks page.

### Modernization Behaviour Analysis

**User-visible effect:**  
A "Covering for someone?" link that takes the user to a consolidated view of all ICM/ITAU/PIO tasks and progress logs, not just their own.

**Business intent:**  
Support coverage scenarios — a user filling in for a colleague needs to see everyone's tasks, not just their own filtered view.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Text web part, or Quick Links/Button for stronger visual affordance if the modern page design favors that pattern.

**SPFx assessment:**  
No.

**Migration note:**  
None — verify the link target still exists in the modern site structure.

---

## Group 29 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/ICM_My_Approval_Requests.aspx` (WebPartId `0cf83500-ca69-4e90-a076-787592f71e72`, Content Editor)

**All pages in this group:** `/cmat/Pages/ICM_My_Approval_Requests.aspx`

```html
<br/>​<br/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​Covering for someone?&#160;&#160;</span><a href="/cmat/Pages/ICM_All_Approval_Requests.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Click here to see all ICM, ITAU and PIO Approval Requests</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​​​​</span><br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** “Covering for someone?” link to all ICM, ITAU and PIO approval requests.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part, Quick Links, or Button.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Confirm the consolidated approval-request page remains in MVP.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same "Covering for someone?" navigation pattern as Group 28, pointing to consolidated approval requests instead of tasks.

**Business intent:**  
Same coverage-scenario support as Group 28.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Same as Group 28.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 30 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/Reference_Material_and_Templates.aspx` (WebPartId `2f31eb14-4e78-4ceb-8510-eaec89773767`, Content Editor)

**All pages in this group:** `/cmat/Pages/Reference_Material_and_Templates.aspx`

```html
<ul>
   <li><p><span class="ms-rteFontSize-2"><strong><strong style="font-size: 14.6667px;">​</strong><a href="/cmat/Supervisor%20Reference%20Material%20and%20Templates/Forms/AllItems.aspx" style="text-decoration-line: underline; font-size: 14.6667px;"><strong>Supervisor&#160;Reference Material and Templates</strong></a></strong></span></p></li><li>
      <p>
         <span class="ms-rteFontSize-2"><strong>​</strong><a href="/cmat/PIO%20Reference%20Material%20and%20Templates/Forms/Root_Folder.aspx" style="text-decoration-line: underline;"><strong>PIO Reference Material and Templates</strong></a><strong>​</strong></span></p></li>
   <li><span class="ms-rteFontSize-2">
      </span><a href="/cmat/ITAU%20Reference%20Material%20and%20Templates/Forms/Root_Folder.aspx" style="text-decoration-line: underline;"><span class="ms-rteFontSize-2"><strong>ITAU Reference Material and Templates</strong></span></a>​​​<br/>​<br/>​<br/><br/></li>
</ul>
```

### Modernization Assessment

- **Business behavior:** Three links to Supervisor, PIO, and ITAU reference material and template locations.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Quick Links may provide a better modern navigation experience, but Text alone is sufficient.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** All three legacy library URLs must be mapped to their SharePoint Online destinations.

### Modernization Behaviour Analysis

**User-visible effect:**  
Three navigation links to document/template libraries by audience (Supervisor, PIO, ITAU).

**Business intent:**  
Quick access to reference material and templates without navigating the site structure manually.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Quick Links web part is likely a better fit than plain Text given this is pure navigation, though Text alone remains sufficient for content parity.

**SPFx assessment:**  
No.

**Migration note:**  
All three legacy document library URLs must be re-mapped to their SPO equivalents — this is a link-target migration task, not a code migration task.

---

## Group 31 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/portal.aspx` (WebPartId `c781bff6-444a-4799-9924-838a139bf718`, Content Editor)

**All pages in this group:** `/cmat/Pages/portal.aspx`

```html
<strong class="ms-rteForeColor-9">​<strong class="ms-rteThemeForeColor-5-0" style="text-decoration-style: solid; text-decoration-color: #0072c6;"><span class="ms-rteFontSize-1" style="font-family: &quot;bc sans&quot;, arial, helvetica, sans-serif;"><span class="ms-rteThemeForeColor-2-0 ms-rteFontSize-1" style="text-decoration-style: solid; text-decoration-color: #444444;">​​</span><span><span class="ms-rteThemeForeColor-2-0 ms-rteFontSize-1" style="text-decoration-style: solid; text-decoration-color: #444444;">For&#160;CMAT&#160;technical&#160;support issues please contact:</span>&#160;<a href="mailto:CMAT.BusinessSupport@gov.bc.ca">CMAT.BusinessSupport@gov.bc.ca​</a>&#160;</span></span></strong>​</strong><div><strong class="ms-rteForeColor-9"><br/></strong></div><div><strong class="ms-rteForeColor-9">Notes:</strong><span class="ms-rteForeColor-9"> 
</span><div> 
   <ul> 
      <li><span class="ms-rteForeColor-9"><span>Press F11 to display a Full Screen.</span><br/></span></li> 
      <li><span class="ms-rteForeColor-9">Click on the ITAU Emblem or the&#160;adjacent​&#160;Large Bold Title from&#160;any page to return to this page.</span><br/></li> 
   </ul> 
</div> 
<div> 
   <br/> ​<br/>​<br/></div></div>
```

### Modernization Assessment

- **Business behavior:** CMAT support contact plus instructions about full-screen mode and using the emblem/title to return to the portal.
- **Text web part sufficient:** Yes, for the content.
- **Recommended modern replacement:** Text web part.
- **MVP decision:** Keep, with revalidation.
- **SPFx candidate:** No.
- **Validation required:** Revalidate every instruction. The F11 browser instruction may be unnecessary, and modern site navigation may replace the emblem/title behavior. Keep the support contact only if current.

### Modernization Behaviour Analysis

**User-visible effect:**  
A support-contact email plus two usage tips: press F11 for full-screen, and click the site emblem/title to return to the portal home.

**Business intent:**  
Direct users to support, and explain two classic-SharePoint navigation conveniences.

**Actual enforcement level:**  
Informational/support-note only.

**Modern SharePoint Online approach:**  
Text web part for the support contact (verify the address is still current). Drop the F11 instruction unless still relevant to the modern UI. The "click the title to go home" behavior is standard modern SPO site navigation already — no instruction needed.

**SPFx assessment:**  
No.

**Migration note:**  
None — but this content is the most likely in the whole document to contain stale, no-longer-applicable instructions; do not port verbatim.

---

## Group 32 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/PIO_My_Tasks.aspx` (WebPartId `19ac63de-57c9-46a9-a4e2-8ab1c97d60a3`, Content Editor)

**All pages in this group:** `/cmat/Pages/PIO_My_Tasks.aspx`

```html
<br/>​<br/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​Covering for someone?&#160;&#160;</span><a href="/cmat/Pages/PIO_All_Tasks.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Click here to see all PIO Tasks and Progress Logs</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​</span><br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** “Covering for someone?” link to all PIO tasks and progress logs.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part, Quick Links, or Button.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Update destination link if the consolidated tasks page changes.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same "Covering for someone?" pattern as Group 28, scoped to PIO tasks/progress logs.

**Business intent:**  
Same as Group 28.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Same as Group 28.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 33 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/ITAU_My_Tasks.aspx` (WebPartId `a3982ac5-fcaf-4d30-9799-3183d8615f9e`, Content Editor)

**All pages in this group:** `/cmat/Pages/ITAU_My_Tasks.aspx`

```html
<br/>​<br/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​Covering for someone?&#160;&#160;</span><a href="/cmat/Pages/ITAU_All_Tasks.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Click here to see all ITAU and PIO Tasks and Progress Logs</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​</span><br/>​​<br/>
```

### Modernization Assessment

- **Business behavior:** “Covering for someone?” link to all ITAU and PIO tasks and progress logs.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part, Quick Links, or Button.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Update destination link if the consolidated tasks page changes.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same "Covering for someone?" pattern as Group 28, scoped to ITAU/PIO tasks and progress logs.

**Business intent:**  
Same as Group 28.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Same as Group 28.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 34 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/Manage_Security_Alerts.aspx` (WebPartId `f16ca5f7-518f-437a-93ac-f8d886112530`, Content Editor)

**All pages in this group:** `/cmat/Pages/Manage_Security_Alerts.aspx`

```html
<b>Note:</b> ​Security Alerts can have pdf attachments​​.​<br/>
```

### Modernization Assessment

- **Business behavior:** Note that Security Alerts can have PDF attachments.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Confirm whether "can have" should be "must have" based on the current business rule.

### Modernization Behaviour Analysis

**User-visible effect:**  
A one-line note stating Security Alerts can have PDF attachments.

**Business intent:**  
Inform users of supported attachment format for this list.

**Actual enforcement level:**  
Informational only — nothing prevents a non-PDF attachment.

**Modern SharePoint Online approach:**  
Text web part. If PDF is actually a hard requirement rather than a suggestion, that should be enforced separately (e.g. column/file validation), not just stated in a note.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 35 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/Briefings_and_Security_Alerts.aspx` (WebPartId `ebc0d268-46dc-44bf-817f-8491a791178e`, Content Editor)

**All pages in this group:** `/cmat/Pages/Briefings_and_Security_Alerts.aspx`

```html
<b class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Notes:</b><div><ul><li><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Informatio​​​n entered in Briefings​​ and Security Alerts are sent by Email to persons being&#160;notified.&#160;&#160;Confidential information should be in an attachment, not in the notes and comments.​</span></li><li><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;"><span style="text-decoration: none solid #00008b;">​Security Alerts should have pdf attachments​​ to facilitate printing.</span><br style="text-decoration: none solid #00008b;"/></span></li><li><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;"><span style="text-decoration: none solid #00008b;">Briefings created by others&#160;will appear in the Subject&#39;s&#160;Information Page (Persons Database).</span><br style="text-decoration: none solid #00008b;"/></span></li><li><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Open attachments by right-clicking on it and choose&#160;&quot;Open link in new tab&quot; or &quot;Open link in new window&quot;</span><br/></li></ul><b></b></div>
```

### Modernization Assessment

- **Business behavior:** Multi-item operational guidance covering email notification, handling confidential information in attachments, PDF attachment expectations, where briefings appear, and opening attachments.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part.
- **MVP decision:** Keep, pending business/privacy review.
- **SPFx candidate:** No.
- **Validation required:** This content needs business and privacy review before migration. Modern attachment behavior may make the right-click instruction obsolete. Do not copy stale operational instructions unchanged.

### Modernization Behaviour Analysis

**User-visible effect:**  
A multi-item notes block: email notifications go out when Briefings/Security Alerts are created; confidential information belongs in an attachment, not the notes/comments field; PDF attachments are expected; briefings appear on the Subject's Person page; and how to open an attachment in a new tab/window.

**Business intent:**  
Operational guidance to prevent confidential data being typed into a field that gets emailed out, and to set expectations about attachment format and where content surfaces.

**Actual enforcement level:**  
Informational only — none of these are enforced; a user can still type confidential text into notes/comments.

**Modern SharePoint Online approach:**  
Text web part, but this content needs a genuine privacy/business review before being carried forward as-is — it references specific legacy behavior (right-click to open attachments) that may not apply in the modern experience, and the confidential-information warning implies a real data-handling risk that arguably deserves stronger controls than a text note (e.g. column validation, DLP, or a genuine field for confidential attachments).

**SPFx assessment:**  
No.

**Migration note:**  
Do not port the right-click/"open in new tab" instruction without confirming it's still accurate in modern SPO — attachment handling UX has changed since SP2016.

---

## Group 36 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/PIO_My_Approval_Requests.aspx` (WebPartId `e850ce4b-c76b-4a2f-9832-4a8a232065fc`, Content Editor)

**All pages in this group:** `/cmat/Pages/PIO_My_Approval_Requests.aspx`

```html
<br/>​<br/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​Covering for someone?&#160;&#160;</span><a href="/cmat/Pages/PIO_All_Approval_Requests.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Click here to see all PIO Approval Requests</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​​​​</span><br class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;"/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​</span><br/>​​<br/>
```

### Modernization Assessment

- **Business behavior:** “Covering for someone?” link to all PIO approval requests.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part, Quick Links, or Button.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Update destination link if the consolidated approvals page changes.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same "Covering for someone?" pattern as Group 28, scoped to PIO approval requests.

**Business intent:**  
Same as Group 28.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Same as Group 28.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 37 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/ITAU_My_Approval_Requests.aspx` (WebPartId `8cd9983c-95b6-4b59-b343-7fb78b57b1f4`, Content Editor)

**All pages in this group:** `/cmat/Pages/ITAU_My_Approval_Requests.aspx`

```html
<b>​​​​​</b>
<div>
   <b><br/></b></div>
<div>
   <b class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Notes:​</b><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">
   </span><div> 
      <ul> 
         <li><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">To Add a New Approval Request&#160;use the 
            </span><a href="/cmat/Pages/ITAU_Cases.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">ITAU Cases Page</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​​</span><br class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;"/></li> 
         <li><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Don&#39;t Forget to Add or Upadate a Progress Log Entry for work perfor​med on&#160;any Task.&#160;&#160;You can enter Progress Logs in this Page if you know the related Case ID.​​​</span><br/>​<br/></li> 
      </ul> 
   </div>
</div>
```

### Modernization Assessment

- **Business behavior:** Static notes block: instructs users to add new Approval Requests via the ITAU Cases page, and reminds them to add/update a Progress Log entry for work performed on any Task.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Full source text is already captured verbatim in this document (see code block above) — the truncation noted against the auto-generated group summary in webpart-code-analysis.md does not apply to the raw content stored here. No further text recovery needed.

### Modernization Behaviour Analysis

**User-visible effect:**  
A notes block: instructs users to add new Approval Requests via the ITAU Cases page (not this page directly), and reminds them to add/update a Progress Log entry for work performed on any Task, directly from this page if they know the related Case ID.

**Business intent:**  
Point users to the correct entry point for creating approval requests, and reinforce a process reminder (log progress against tasks).

**Actual enforcement level:**  
Informational only.

**Modern SharePoint Online approach:**  
Text web part with an updated link to the modern ITAU Cases page.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

## Group 38 — TextOnly (1 instance)

**Representative:** `/cmat/Pages/ITAU_My_Approval_Requests.aspx` (WebPartId `71d624e3-11c9-4402-9674-df4037ab3381`, Content Editor)

**All pages in this group:** `/cmat/Pages/ITAU_My_Approval_Requests.aspx`

```html
<br/>​​​<br/><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​Covering for someone?&#160;&#160;</span><a href="/cmat/Pages/ITAU_All_Approval_Requests.aspx"><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">Click here to see all ITAU and PIO Approval Requests</span></a><span class="ms-rteForeColor-9" style="text-decoration: none solid #00008b;">​​​​</span><br/>​<br/>​<br/>
```

### Modernization Assessment

- **Business behavior:** “Covering for someone?” link to all ITAU and PIO approval requests.
- **Text web part sufficient:** Yes.
- **Recommended modern replacement:** Text web part, Quick Links, or Button.
- **MVP decision:** Keep.
- **SPFx candidate:** No.
- **Validation required:** Update destination link if the consolidated approvals page changes.

### Modernization Behaviour Analysis

**User-visible effect:**  
Same "Covering for someone?" pattern as Group 28, scoped to ITAU/PIO approval requests.

**Business intent:**  
Same as Group 28.

**Actual enforcement level:**  
Navigation only.

**Modern SharePoint Online approach:**  
Same as Group 28.

**SPFx assessment:**  
No.

**Migration note:**  
None.

---

---

# Part 2 — External JS Helper Files (Section 8 companion)

> All 23 non-jQuery external `.js` files referenced (directly or indirectly) by the CEWP/SEWP web parts above, read in full for manual review. See `PROBLEMATIC-WEBPARTS-SUMMARY.md` Section 8 for the consolidated findings summary. Files are ordered substantial-first, then confirmed-trivial.

## Files with substantial or noteworthy logic

### `linkCase.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** JSLink field-renderer override for the **Case** field. Hardcodes 3 SharePoint View GUIDs (ITAU_Cases/PIO_Cases/ICM_Cases) and builds a link to that case's detail view with `SelectedID` set. **Not a simple link-hider — this is a field-rendering customizer.** Hardcoded View GUIDs are fragile and won't exist in SPO. Modern equivalent: SPFx Field Customizer, or modern column formatting JSON if the target view can be parameterized differently.

```javascript
(function () {
    var overrideCtx = {};
    overrideCtx.Templates = {};
    overrideCtx.OnPostRender = [];

    overrideCtx.Templates.Fields =
    {
        'Case': { 'View': renderButton }
    };

    SPClientTemplates.TemplateManager.RegisterTemplateOverrides(overrideCtx);

})();

function renderButton(ctx){ 
    console.log(ctx.ListTitle);
    console.log(ctx);

    var btnTxt = ctx.CurrentItem["Case"];
    var viewList = {
    	"ITAU_Cases":"%7BFF014B5A-6EEE-4EE5-A11E-1E511193E9E1%7D",
    	"PIO_Cases":"%7BF7393396-41AF-41C6-8541-26C266DA0594%7D",
    	"ICM_Cases":"%7B248FD0E2-D69A-4A00-9FB3-B3B250AC7051%7D"

    };
    var listTitle = ctx.ListTitle;
    var fullCaseId = ctx.CurrentItem["Case_x0020_ID"]

	return "<a href='/cmat/Pages/"+listTitle+".aspx?View="+viewList[listTitle]+"&SelectedID="+ btnTxt + "'>"+fullCaseId+"</div>";


    //var id = ctx.CurrentItem.ID;
   														
}

```

---

### `makehyperlink.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** JSLink field override on a `link_to_print_appearance` field — renders a link to `Appearing_Persons_Briefing.aspx` using the item's `ID` and a hardcoded View GUID. Not referenced by any of the 121 scanned CEWP/SEWP web parts — likely wired via list-level JSLink settings, outside the CEWP/SEWP scan's scope. Confirm whether still active before assuming dead code.

```javascript
(function () {  
    // Create an object that have the context information about the fields that we want to change the rendering of.   
    var nameFiledContext = {};  
    nameFiledContext.Templates = {};  
    nameFiledContext.Templates.Fields = {  
        // Apply the new hyperlink HTML Rendering to the field in your view.  
        "link_to_print_appearance": { "View": nameFiledTemplate }  
    };  
    SPClientTemplates.TemplateManager.RegisterTemplateOverrides(nameFiledContext);  
})();  
  
// This function applies the rendering logic 
function nameFiledTemplate(ctx) {  
    var name = ctx.CurrentItem.ID;  //Swap out name variable for whatever field contains your hyperlink name
            
    return "<a href='/cmat/Pages/Appearing_Persons_Briefing.aspx?View=%7B0A092433-A1AF-4D71-8DA8-7E8EA9E4A85D%7D&SelectedID="   
        + name + "'> Click Here for the Printable Briefing Page.</a>"; 
}  

```

---

### `showattachmentname.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** JSLink override on the **Attachments** field. Makes a **synchronous** (`async: false`) AJAX call to `_api/web/lists/getbytitle(...)/items(...)/AttachmentFiles` and renders each attachment as a clickable link inline in the list view. Real REST-based renderer, not just a name display — the synchronous call is a genuine performance anti-pattern (blocks the UI thread per row). SPO's native attachment rendering may make this fully unnecessary in the modern list view.

```javascript
(function () {

    var attachmentsFiledContext = {};

    attachmentsFiledContext.Templates = {};

    attachmentsFiledContext.Templates.Fields = {
         
        "Attachments": { "View": AttachmentsFiledTemplate }
    };

    SPClientTemplates.TemplateManager.RegisterTemplateOverrides(attachmentsFiledContext);

})();

function AttachmentsFiledTemplate(ctx) {
    var itemId = ctx.CurrentItem.ID;
    var listName = ctx.ListTitle;       
    return getAttachments(listName, itemId);
}

function getAttachments(listName,itemId) {
  
    var url = _spPageContextInfo.webAbsoluteUrl;
    var requestUri = url + "/_api/web/lists/getbytitle('" + listName + "')/items(" + itemId + ")/AttachmentFiles";
    var str = "";
    $.ajax({
        url: requestUri,
        type: "GET",
        headers: { "ACCEPT": "application/json;odata=verbose" },
        async: false,
        success: function (data) {
            for (var i = 0; i < data.d.results.length; i++) {
                str += "<a href='" + data.d.results[i].ServerRelativeUrl + "?web=1 '>" + data.d.results[i].FileName + "</a>";
                if (i != data.d.results.length - 1) {
                    str += "<br/>";
                }                
            }          
        },
        error: function (err) {
        }
    });
    return str;
}
```

---

### `RLHelper-ChildNewForm.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Public snippet ("SharePoint 2010 Related List Pre-fill v1.2"). Detects if the New form was opened as a modal dialog (`IsDlg=1` query param) from a parent item, extracts the parent's numeric ID from `SelectedID`, and sets a lookup dropdown to that ID. This is the mechanism behind `fillfromParent()` (13 instances across the CMAT web parts). Native SPO/Power Apps equivalent: Power Automate flow or Power Apps `Param()` function — no SPFx required.

```javascript
/*
SharePoint 2010 Related List Pre-fill Version 1.2
Call JQuery and this file from the child list's new item page.
Instructions: http://code.google.com/p/sp2010-related-list-prefill/
RLHelper-ChildNewForm.js
*/
function getQuerystring(ji, fromParent) {
var hu;
if(fromParent){
hu = parent.window.location.search.substring(1);
}
else{
hu = window.location.search.substring(1);
}
var gy = hu.split("&");
var i = 0;
for (i=0;i<gy.length;i++) {
var ft = gy[i].split("=");
if (ft[0] === ji) {
return ft[1];
}
}
}
function fillfromParent(childfield) {
var dlg = getQuerystring("IsDlg", false);
if (isNaN(dlg) === false && dlg == 1) {
var SelId = getQuerystring("SelectedID", true);
var parentid = SelId.match(/\d+$/);
if (isNaN(parentid) === false && parentid > 0) {
$("select[title="+childfield+"]").val(parentid);
}
}
}
```

---

### `Greeting.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** Uses the client-side object model (`SP.ClientContext`, not jQuery) to fetch the current user's title/display name and inject a time-of-day greeting ("Good Morning/Afternoon/Evening, {FirstName}") into an element with id `userTitle`. Not referenced by any of the 121 scanned web parts — likely used on the classic portal homepage. Modern SPO/Viva Connections has this as a built-in home-site feature.

```javascript
ExecuteOrDelayUntilScriptLoaded(init,'sp.js');
var currentUser;
var title;
var trimmed;
var titleAry;
var currentDate;
var currentHours;

function init(){
    this.clientContext = new SP.ClientContext.get_current();
    this.oWeb = clientContext.get_web();
    currentUser = this.oWeb.get_currentUser();
    this.clientContext.load(currentUser);
    this.clientContext.executeQueryAsync(Function.createDelegate(this,this.onQuerySucceeded), Function.createDelegate(this,this.onQueryFailed));
}

function onQuerySucceeded() {
    currentDate = new Date();
    currentHours = currentDate.getHours();
    if (currentHours >= 5 && currentHours < 12) { greeting = "Good Morning"; }
    else if (currentHours >= 12 && currentHours <= 17) { greeting = "Good Afternoon"; }
    else if (currentHours < 5 || currentHours > 17) { greeting = "Good Evening"; }

    title = currentUser.get_title();
    trimmed = title.replace(/^\s+|\s+$/g, '');
    titleAry = trimmed.split(" ");
    document.getElementById('userTitle').innerHTML = greeting + ", " + titleAry[1];
}

function onQueryFailed(sender, args) {
    alert('Request failed. \nError: ' + args.get_message() + '\nStackTrace: ' + args.get_stackTrace());
}

```

---

### `OpenCalendarItemModal.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** Substantial: hooks `SP.UI.ApplicationPages.CalendarStateHandler.prototype.onItemsSucceed` (patches SharePoint's internal calendar rendering pipeline) to rewrite every calendar item link to open in a modal dialog instead of navigating away, and re-applies itself after the "Show n more items" expander is clicked. Not found on any currently-scanned CEWP/SEWP — likely applied via calendar list/view JSLink settings, outside this scan's scope. Recommend a separate JSLink audit of the ITAU_Cal_* calendars before assuming dead code. Modern SPO calendars have no modal-dialog equivalent by default — would need an SPFx Application Customizer if still wanted.

```javascript
"use strict";

if (!window.console) window.console = {};
if (!window.console.log) window.console.log = function () { };

// modify Calendar markup to open items in dialog
function setCalendarItemsToOpenInDialog() {
    try {
            var time = new Date();
            console.log(time.getSeconds() + ":" + time.getMilliseconds() + " Modifying Calendar Links..");

            jQuery('a[href*="DispForm.aspx"]').each(function () {
                jQuery(this).attr('onclick', 'openDialog("' + jQuery(this).attr('href') + '")');
                jQuery(this).attr('href', 'javascript:void(0)');
                jQuery(this).removeAttr("target");
            });

    } catch (e) {
        console.log("Exception in setCalendarItemsToOpenInDialog: " + e.name + ", " + e.message);
    }
}

function myCalendarHook() {
    try {
        //  save the original onItemsSucceed function
        var _onItemsSucceed = SP.UI.ApplicationPages.CalendarStateHandler.prototype.onItemsSucceed;

        // override a function that is called whenever calendar items are loaded (onItemsSucceed)
        SP.UI.ApplicationPages.CalendarStateHandler.prototype.onItemsSucceed = function($p0, $p1) {
            // call the original onItemsSucceed to make sure that all calendar functionality is as it used to be
            _onItemsSucceed.call(this, $p0, $p1);

            // modify Calendar links
            setCalendarItemsToOpenInDialog();

            // For more than 3 items per day there is 'Show n more items' link.
            // This link rewrites all modified links when clicked, so we need to wait a little and call our function again:
            jQuery('a.ms-cal-nav').on('click', function() {
                setTimeout(function() {
                    setCalendarItemsToOpenInDialog();
                }, 500);
            });
        };
    } catch (e) {
        console.log("Exception in myCalendarHook: " + e.name + ", " + e.message);
    }
}

// When called, this function opens the dialog.
function openDialog(pUrl) {
    var options = {
        autoSize: true,
        url: pUrl
    };
    SP.SOD.execute('sp.ui.dialog.js', 'SP.UI.ModalDialog.showModalDialog', options);
}

ExecuteOrDelayUntilScriptLoaded(function () {
    myCalendarHook();
}, "SP.UI.ApplicationPages.Calendar.js");
```

---

### `calendar-month-backlink.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** Substantial: on a calendar item's Display form, parses a hidden field-metadata HTML comment to extract the EventDate, computes month/year, builds a "back to month view" link, and rewrites the Close button's onclick handler to redirect to that computed calendar URL. Same status as OpenCalendarItemModal.js — real logic, not found in current scan scope, needs the same calendar JSLink audit.

```javascript
<!-- create the style for the link back to the month we came from -->
<style>
  .backlink {
    font-size: 16px;
	font-weight: bold;
  }
</style>

<!-- create the link back to the month we came from -->
<div><br/><a class="backlink" href="#">&nbsp;</a></div>

<!-- add an eventlistener function to configure the link back to the month we came from -->
<script type="text/javascript">

//--- On page finished load
document.addEventListener("DOMContentLoaded", function() {

	const backlink = document.querySelector('a.backlink');
	const cells = document.querySelectorAll('td.ms-formbody');
	const monthNames = [
			"January", "February", "March", "April", "May", "June",
			"July", "August", "September", "October", "November", "December"
		];

	var calendarDate = "";
	var calendarURL = "";
	var calendarText = "";
	var monthName = "";
	var yearName = "";
	var done = false;
	
	//--- loop to find the cell with the date we are looking for
	cells.forEach(function(cell) {
			
			//--- loop through the nodes of the cell
			for (var i = 0; i < cell.childNodes.length; i++) {
				var node = cell.childNodes[i];
				
				//--- does this node have a comment in it?
				if (node.nodeType === Node.COMMENT_NODE) {
				
					//--- Check if comment contains our identifier
					if (node.nodeValue && node.nodeValue.includes('FieldInternalName="EventDate"')) {
						//--- Found it! Now get the text content
						calendarDate = cell.textContent.trim().substring(0,10);
						//console.log("calendarDate: ", calendarDate);
						var monthText = calendarDate.substring(5,7);
						//console.log("monthText: ", monthText);
						var monthNum = parseInt(monthText)-1;
						//console.log("monthNum: ", monthNum);
						monthName = monthNames[monthNum];
						//console.log("monthName: ", monthName)
						yearName = calendarDate.substring(0,4);
						//console.log("yearName: ", yearName);
						
						//--- We are done, get out of the nested loop
						done = true;
						break;
					}
				}
			
			if (done) break;
			}
		}
	);
	
	//--- format the backlink to the page
	calendarText = `Click here to return to the ${monthName} ${yearName} Calendar page`;
	//console.log("calendarText: ", calendarText);
	calendarURL = location.origin + location.pathname.replace(/\/DispForm\.aspx.*/i, "/Calendar.aspx") +
            "?CalendarPeriod=month" +
            "&CalendarDate=" + encodeURIComponent(calendarDate);
	//console.log("calendarURL: " + calendarURL);
	
	//--- give the link the correct new values for display and behaviour
	backlink.text = calendarText;
	backlink.href = calendarURL;
	
	//--- modify the close button at the bottom of the detail page
	var buttons = document.querySelectorAll('input.ms-ButtonHeightWidth');
	
	//--- loop through all the buttons to find the close button
	buttons.forEach(function(button) {
		var oldFnString = button.onclick.toString();
		
		//--- ensure this button has the things we need
		if(button.value === "Close" && oldFnString.indexOf("STSNavigate") >= 0){
			
			//--- we found the right one
			//console.log("button.value: ", button.value);
			//console.log("oldFnString: ", oldFnString);
			
			//--- format the link back to the Calendar
			var buttonCalendarURL = calendarURL.replace("/", "\u002f");
			
			//--- replace the old url with the new url we've created
			var newFnString = oldFnString.replace(/STSNavigate\('.*?'\)/,`STSNavigate('${buttonCalendarURL}')`);
			//console.log("newFnString: ", newFnString);

			//--- replace the onclick function to use the new url
			var newFn = new Function("return " + newFnString)();
			button.onclick = newFn;
		};
	});
});
</script>


```

---

### `sputility.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** **Full third-party library** — "SPUtility.js" v0.14.2 by Kit Menke (MIT license, sputility.codeplex.com, built 2016-04-19). ~2,000 lines providing a complete field-abstraction API (SPField, SPTextField, SPChoiceField, SPDateTimeField, SPUserField, etc.) for getting/setting/showing/hiding any classic SharePoint form field client-side. Not referenced by any of the 121 scanned web parts — likely a vendored dependency for other custom scripts not captured by this scan, or an unused leftover. If any page depends on it, that dependent script needs individual review.

```javascript
/*
   Name: SPUtility.js
   Version: 0.14.2
   Built: 2016-04-19
   Author: Kit Menke
   https://sputility.codeplex.com/
   Copyright (c) 2016
   License: The MIT License (MIT)
*/
// Object.create shim for class inheritance
if (!Object.create) {
   Object.create = function (o) {
      if (arguments.length > 1) {
         throw new Error('Object.create implementation only accepts the first parameter.');
      }
      function F() {}
      F.prototype = o;
      return new F();
   };
}

// Export SPUtility global variable
var SPUtility = (function ($) {
   "use strict";

   /*
    *   SPUtility Private Variables
   **/
   var _fieldsHashtable = null, // stores all fields by display name
      _internalNamesHashtable = null, // stores all fields by internal name
      _isDispForm = null, // whether or not current form is the display form
      _spVersion = 12,    // current sharepoint version
      _settings = {                 // DEFAULT SETTINGS:
         'timeFormat': '12HR',      // 12HR or 24HR
         'dateSeparator': '/',      // separates month/day/year with / or .
         'decimalSeparator': '.',   // separates decimal from number
         'thousandsSeparator': ',', // separates thousands in number
         'stringYes': 'Yes',        // Text for when boolean field is True
         'stringNo': 'No'           // Text for when boolean field is False
      };

   /*
    *   SPUtility Private Methods
   **/
   function isDispForm() {
      if (_isDispForm === null) {
         _isDispForm = $("table.ms-formtoolbar input[value='Close']").length >= 1;
      }
      return _isDispForm;
   }

   function isInternetExplorer() {
      return navigator.userAgent.toLowerCase().indexOf('msie') >= 0;
   }

   function isUndefined(obj) {
      return typeof obj === 'undefined';
   }

   function isString(obj) {
      return typeof obj === 'string';
   }

   function isNumber(obj) {
      return typeof obj === 'number';
   }

   function getInteger(str) {
      return parseInt(str, 10);
   }

   // escapeRegExp and replaceAll from http://stackoverflow.com/a/1144788/98933
   function escapeRegExp(str) {
      return str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
   }

   function replaceAll(str, find, replace) {
     return str.replace(new RegExp(escapeRegExp(find), 'g'), replace);
   }

   function convertStringToNumber(val) {
      if (typeof val === "string") {
         // remove all thousands separators including spaces
         val = replaceAll(val, ' ', '');
         val = replaceAll(val, _settings['thousandsSeparator'], '');
         // replace the first instance of the decimal separator
         val = val.replace(_settings['decimalSeparator'], '.');
         val = parseFloat(val);
      }
      return val;
   }

   function htmlEscape(str) {
      return String(str)
         .replace(/&/g, '&amp;')
         .replace(/"/g, '&quot;')
         .replace(/''/g, '&#39;')
         .replace(/</g, '&lt;')
         .replace(/>/g, '&gt;');
   }

   function is2013() {
      return _spVersion === 15;
   }

   //+ Jonas Raoni Soares Silva
   //@ http://jsfromhell.com/number/fmt-money [rev. #2]
   // Modified to pass JSLint
   // n = the number to format
   // c = # of floating point decimal places, default 2
   // d = decimal separator, default "."
   // t = thousands separator, default ","
   function formatMoney(n, c, d, t) {
      c = (isNaN(c = Math.abs(c)) ? 2 : c);
      d = (d === undefined ? _settings['decimalSeparator'] : d);
      t = (t === undefined ? _settings['thousandsSeparator'] : t);
      var s = (n < 0 ? "-" : ""),
         i = parseInt(n = Math.abs(+n || 0).toFixed(c), 10) + "",
         j = (j = i.length) > 3 ? j % 3 : 0;
      return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
   }

   // Gets the input controls for a field (used for Textboxes)
   function getInputControl(spField) {
      if (spField.Controls === null) {
         // if running on DispForm.aspx Controls will be null
         return null;
      }
      var controls = $(spField.Controls).find('input');
      if (null !== controls && 1 === controls.length) {
         return controls[0];
      }

      throw 'Unable to retrieve the input control for ' + spField.Name;
   }

   function getHashFromInputControls(spField, selector) {
      var oHash = [], i,
         inputs = $(spField.Controls).find(selector),
         labels = $(spField.Controls).find("label");
      if (labels.length < inputs.length) {
         throw "Unable to get hashtable of controls.";
      }
      for (i = 0; i < inputs.length; i++) {
         oHash.push({
            key: $(labels[i]).text(),
            value: inputs[i]
         });
      }
      return oHash;
   }

   function getHashValue(hash, key) {
      var val = null;
      $(hash).each(function (index, pair) {
         if (pair.key === key) {
            val = pair.value;
            return false;
         }
      });
      return val;
   }

   function fillSPFieldInfo(element, fieldParams) {
      // find the HTML comment and fill fieldparams with type and internal name
      for (var n = 0; n < element.childNodes.length; n += 1) {
         if (8 === element.childNodes[n].nodeType) {
            var comment = element.childNodes[n].data;

            // Retrieve field type
            var typeMatches = comment.match(/SPField\w+/);
            if (typeMatches !== null && typeMatches.length > 0) {
               fieldParams.type = typeMatches[0];
            }

            // Retrieve field name
            var nameMatches = comment.match(/FieldName="[^"]+/);
            if (nameMatches !== null && nameMatches.length > 0) {
               fieldParams.name = nameMatches[0].substring(11); // remove FieldName from the beginning
            }

            // Retrieve field internal name
            var internalNameMatches = comment.match(/FieldInternalName="\w+/);
            if (internalNameMatches !== null && internalNameMatches.length > 0) {
               fieldParams.internalName = internalNameMatches[0].substring(19); // remove FieldInternalName from the beginning
            }
            break;
         }
      }

      if (fieldParams.type === null && $(element).find('select[name$=ContentTypeChoice]').length > 0) {
         // small hack to support content type fields
         fieldParams.type = 'ContentTypeChoice';
         fieldParams.internalName = 'ContentType';
         fieldParams.name = 'Content Type';
      }
   }

   function getFieldParams(formBody) {
      var elemLabel = null;
      var isRequired = null;

      var formLabel = $(formBody).siblings(".ms-formlabel");
      if (formLabel !== null) {
         // find element which contains the field's display name
         var elems = formLabel.children('h3');

         // normally, the label is an h3 element inside the td
         // but on surveys the h3 doesn't exist
         // special case: content type label is contained within the td.ms-formlabel
         elemLabel = elems.length > 0 ? elems[0] : formLabel;

         // If label row not null and not attachment row
         if (elemLabel !== null && elemLabel.nodeName !== 'NOBR') {
            var fieldName = $.trim($(elemLabel).text());
            if (fieldName.length > 2 && fieldName.substring(fieldName.length-2) === ' *') {
               isRequired = true;
            }
         }
      }

      var fieldParams = {
         name: null,
         internalName: null,
         label: elemLabel !== null ? $(elemLabel) : null,
         labelRow: elemLabel !== null ? elemLabel.parentNode : null,
         labelCell: formLabel,
         isRequired: isRequired,
         controlsRow: formBody.parentNode,
         controlsCell: formBody,
         type: null,
         spField: null
      };

      // Retrieve type and internalName
      fillSPFieldInfo(formBody, fieldParams);

      return fieldParams;
   }

   function lazyLoadSPFields() {
      if (_fieldsHashtable !== null && _internalNamesHashtable !== null) {
         return;
      }

      // detect sharepoint version based on global variables which are
      // always defined for sharepoint 2013/2010
      if (typeof _spPageContextInfo === 'object') {
         _spVersion = _spPageContextInfo.webUIVersion === 15 ? 15 : 14;
      }

      _fieldsHashtable = {};
      _internalNamesHashtable = {};

      var formBodies = $('table.ms-formtable td.ms-formbody');
      for (var i = 0; i < formBodies.length; i += 1) {
         var fieldParams = getFieldParams(formBodies[i]);
         if (fieldParams !== null) {
            _fieldsHashtable[fieldParams.name] = fieldParams;
            _internalNamesHashtable[fieldParams.internalName] = fieldParams;
         }
      }
   }

   function toggleSPFieldRows(labelRow, controlsRow, bShowField) {
      // on survey forms, the labelRow and controlsRow are different
      // for normal forms, they are the same so it is a redundant call
      if (bShowField) {
          if (labelRow !== null) {
            $(labelRow).show();
          }
         $(controlsRow).show();
      } else {
          if (labelRow !== null) {
            $(labelRow).hide();
          }
         $(controlsRow).hide();
      }
   }

   function toggleSPField(strFieldName, bShowField) {
      lazyLoadSPFields();

      var fieldParams = _fieldsHashtable[strFieldName];

      if (isUndefined(fieldParams)) {
         throw 'toggleSPField: Unable to find a SPField named ' + strFieldName + ' - ' + bShowField;
      }

      toggleSPFieldRows(fieldParams.labelRow, fieldParams.controlsRow, bShowField);
   }

   /*
    *   SPUtility Classes
   **/

   /*
    *   SPField class
    *   Contains all of the common properties and functions used by the specialized
    *   sub-classes. Typically, this should not be intantiated directly.
    */
   function SPField(fieldParams) {
      // Public Properties
      this.Label = fieldParams.label;
      this.LabelRow = fieldParams.labelRow;
      this.Name = fieldParams.name;
      this.InternalName = fieldParams.internalName;
      this.IsRequired = fieldParams.isRequired;
      this.Type = fieldParams.type;

      var children = $(fieldParams.controlsCell).children().not("script"); // support for binding framework e.g. jsviews
      if (children.length > 0) {
         this.Controls = children[0];
      } else {
         this.Controls = null;
      }
      this.ControlsRow = fieldParams.controlsRow;
      this.ReadOnlyLabel = null;
   }

   /*
    *   Public SPField Methods
    */
   SPField.prototype.Show = function () {
      toggleSPFieldRows(this.LabelRow, this.ControlsRow, true);
      return this;
   };

   SPField.prototype.Hide = function () {
      toggleSPFieldRows(this.LabelRow, this.ControlsRow, false);
      return this;
   };

   SPField.prototype.GetDescription = function () {
      if (is2013()) {
         return $(this.Controls.parentNode).children('span.ms-metadata').text();
      } else {
         var ctls = this.Controls.parentNode,
         text = $($(ctls).contents().toArray().reverse()).filter(function() {
            return this.nodeType === 3;
         }).text();
         return text.replace(/^\s+/, '').replace(/\s+$/g, '');
      }
   };

   SPField.prototype.SetDescription = function (descr) {
      var ctls;
      descr = isUndefined(descr) ? '' : descr;
      if (is2013()) {
         ctls = $(this.Controls.parentNode).children('span.ms-metadata');
         if (ctls.length === 0) {
            ctls = $('<span class="ms-metadata"/>');
            $(this.Controls.parentNode).append(ctls);
         }
         $(ctls).html(descr);
      } else {
         ctls = this.Controls.parentNode;
         // look for the text node
         var textNode = $($(ctls).contents().toArray().reverse()).filter(function() {
            return this.nodeType === 3;
         });
         if (textNode.length === 0) {
            // create a new text node and append it after the other controls
            textNode = document.createTextNode(descr);
            ctls.appendChild(textNode);
         } else {
            $(textNode)[0].nodeValue = descr;
         }
      }
   };

   // should be called in SetValue to update the read-only label
   SPField.prototype._updateReadOnlyLabel = function (htmlToInsert) {
      if (this.ReadOnlyLabel) {
         this.ReadOnlyLabel.html(htmlToInsert);
      }
   };

   // should be called in MakeReadOnly to change a field into read-only mode
   SPField.prototype._makeReadOnly = function (htmlToInsert) {
      try {
         $(this.Controls).hide();
         if (null === this.ReadOnlyLabel) {
            this.ReadOnlyLabel = $('<div/>').addClass('sputility-readonly');
            $(this.Controls).after(this.ReadOnlyLabel);
         }
         this.ReadOnlyLabel.html(htmlToInsert);
         this.ReadOnlyLabel.show();
      } catch (ex) {
         throw 'Error making ' + this.Name + ' read only. ' + ex.toString();
      }
      return this;
   };

   SPField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(this.GetValue().toString());
   };

   SPField.prototype.MakeEditable = function () {
      try {
         $(this.Controls).show();
         if (null !== this.ReadOnlyLabel) {
            $(this.ReadOnlyLabel).hide();
         }
      } catch (ex) {
         throw 'Error making ' + this.Name + ' editable. ' + ex.toString();
      }
      return this;
   };

   SPField.prototype.toString = function () {
      return this.Name;
   };

   /*
    *   Public SPField Override Methods
    *   All of the below methods need to be implemented in each sub-class
    */
   SPField.prototype.GetValue = function () {
      throw 'GetValue not yet implemented for ' + this.Type + ' in ' + this.Name;
   };

   SPField.prototype.SetValue = function () {
      throw 'SetValue not yet implemented for ' + this.Type + ' in ' + this.Name;
   };

   /*
    *   SPTextField class
    *   Supports Single line of text fields
    */
   function SPTextField(fieldParams) {
      SPField.call(this, fieldParams);
      // public Textbox property
      this.Textbox = getInputControl(this);
   }

   // SPTextField inherits from the SPField base class
   SPTextField.prototype = Object.create(SPField.prototype);

   /*
    *   SPTextField Public Methods
    *   Overrides SPField class methods.
    */
   SPTextField.prototype.GetValue = function () {
      return $(this.Textbox).val();
   };

   SPTextField.prototype.SetValue = function (value) {
      $(this.Textbox).val(value);
      this._updateReadOnlyLabel(this.GetValue().toString());
      return this;
   };

   SPTextField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(htmlEscape(this.GetValue()));
   };

   /*
    *   SPNumberField class
    *   Supports Number fields
    */
   function SPNumberField(fieldParams) {
      SPTextField.call(this, fieldParams);
   }

   // SPNumberField inherits from the SPTextField base class
   SPNumberField.prototype = Object.create(SPTextField.prototype);

   /*
    *   SPNumberField Public Methods
    *   Overrides SPTextField class methods.
    */
   SPNumberField.prototype.GetValue = function () {
      return convertStringToNumber($(this.Textbox).val());
   };

   // override SetValue function to prevent NaN
   SPNumberField.prototype.SetValue = function (value) {
      $(this.Textbox).val(value);
      this._updateReadOnlyLabel(this.GetValueString());
      return this;
   };

   SPNumberField.prototype.GetValueString = function () {
      var val = this.GetValue();
      if (isNaN(val)) {
         val = "";
      } else {
         val = val.toString();
      }
      return val;
   };

   // Override the default MakeReadOnly function to allow displaying
   // empty number fields as empty string instead of NaN
   SPNumberField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(this.GetValueString());
   };


   /*
    *   SPCurrencyField class
    *   Supports currency fields (SPCurrencyField)
    */
   function SPCurrencyField(fieldParams) {
      SPNumberField.call(this, fieldParams);
      this.FormatOptions = {
         eventHandler: null,
         autoCorrect: false,
         decimalPlaces: 2
      };
   }

   // SPCurrencyField inherits from the SPNumberField base class
   SPCurrencyField.prototype = Object.create(SPNumberField.prototype);

   /*
    *   Overrides SPNumberField class methods.
    */
   SPCurrencyField.prototype.Format = function () {
      if (this.FormatOptions.autoCorrect) {
         this.FormatOptions.eventHandler = $.proxy(function () {
            this.SetValue(this.GetFormattedValue());
         }, this);
         $(this.Textbox).on('change', this.FormatOptions.eventHandler);
         this.FormatOptions.eventHandler(); // run once
      } else {
         if (this.FormatOptions.eventHandler) {
            $(this.Textbox).off('change', this.FormatOptions.eventHandler);
            this.FormatOptions.eventHandler = null;
         }
      }
   };

   SPCurrencyField.prototype.GetFormattedValue = function () {
      var text = this.GetValue();
      if (typeof text === "number") {
         text = formatMoney(text, this.FormatOptions.decimalPlaces);
      }
      return text;
   };

   SPCurrencyField.prototype.SetValue = function (value) {
      $(this.Textbox).val(value);
      this._updateReadOnlyLabel(this.GetFormattedValue());
      return this;
   };

   // Override the default MakeReadOnly function to allow displaying
   // the value with currency symbols
   SPCurrencyField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(this.GetFormattedValue());
   };

   /*
   *   ContentTypeChoiceField class
   *   Support for Content Type special field
   */
   function ContentTypeChoiceField(fieldParams) {
      SPField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      // in the content type field, there is no controls span
      // so this.Controls is already set to the select element
      this.Dropdown = this.Controls;
   }

   // Inherit from SPFIeld
   ContentTypeChoiceField.prototype = Object.create(SPField.prototype);

   ContentTypeChoiceField.prototype.GetValue = function () {
      return this.Dropdown.options[this.Dropdown.selectedIndex].text;
   };

   ContentTypeChoiceField.prototype.SetValue = function (value) {
      var i, options, option;
      // allow value to be either the text or the content type's ID
      // so we check option.text and option.value
      options = this.Dropdown.options;
      for (i = 0; i < options.length; i += 1) {
         option = options[i];
         if (option.text === value || option.value === value) {
            this.Dropdown.selectedIndex = i;
            if (typeof ChangeContentType === 'function') {
               // ChangeContentType is a built-in function that is bound to the
               // onchange event on the SELECT control
               // calling the function switches the form to use different
               // fields configured on the content type
               ChangeContentType(this.Dropdown.id);
            }

            break;
         }
      }
      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
   *   SPChoiceField class
   *   Base class for dropdown, radio, and checkbox fields
   */
   function SPChoiceField(fieldParams) {
      SPField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      var controls = $(this.Controls).find('input'), numControls = controls.length;
      if (numControls > 1 && controls[numControls - 1].type === "text") {
         // fill-in textbox is always the last input control
         this.FillInTextbox = controls[numControls - 1];
         // fill-in element (radio or checkbox) is always second to last
         this.FillInElement = controls[numControls - 2];
         this.FillInAllowed = true;
      } else {
         this.FillInAllowed = false;
         this.FillInTextbox = null;
         this.FillInElement = null;
      }
   }

   // Inherit from SPField
   SPChoiceField.prototype = Object.create(SPField.prototype);

   SPChoiceField.prototype._getFillInValue = function () {
      return $(this.FillInTextbox).val();
   };

   SPChoiceField.prototype._setFillInValue = function (value) {
      this.FillInElement.checked = true;
      $(this.FillInTextbox).val(value);
   };

   /*
    *   SPDropdownChoiceField class
    *   Supports single select choice fields that show as a dropdown
    */
   function SPDropdownChoiceField(fieldParams, dropdown) {
      SPChoiceField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      this.Dropdown = dropdown;
      this.Dropdown = this.Dropdown.length === 1 ? this.Dropdown[0] : [];
   }

   // Inherit from SPChoiceField
   SPDropdownChoiceField.prototype = Object.create(SPChoiceField.prototype);

   SPDropdownChoiceField.prototype.GetValue = function () {
      if (this.FillInAllowed && this.FillInElement.checked === true) {
         return this._getFillInValue();
      }
      return $(this.Dropdown).val();
   };

   SPDropdownChoiceField.prototype.SetValue = function (value) {
      var found = $(this.Dropdown).find('option[value="' + value + '"]').length > 0;
      if (!found && this.FillInAllowed) {
         if (found) {
            $(this.Dropdown).val(value);
            this.FillInElement.checked = false;
         } else {
            this._setFillInValue(value);
         }
      } else if (found) {
         $(this.Dropdown).val(value);
      } else {
         throw 'Unable to set value for ' + this.Name + ' the value "' + value + '" was not found.';
      }
      this._updateReadOnlyLabel(this.GetValue().toString());
      return this;
   };

   /*
    *   SPRadioChoiceField class
    *   Supports single select choice fields that show as radio buttons
    */
   function SPRadioChoiceField(fieldParams) {
      SPChoiceField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      this.RadioButtons = getHashFromInputControls(this, 'input[type="radio"]');
      if (this.FillInAllowed) {
         // remove the last radio button, which is to select fill-in value
         this.RadioButtons.pop();
      }
   }

   // Inherit from SPChoiceField
   SPRadioChoiceField.prototype = Object.create(SPChoiceField.prototype);

   SPRadioChoiceField.prototype.GetValue = function () {
      var value = null;
      // find the radio button we need to get in our hashtable
      $(this.RadioButtons).each(function (index, pair) {
         var radioButton = pair.value;
         if (radioButton.checked) {
            value = pair.key;
            return false;
         }
      });

      if (this.FillInAllowed && value === null && this.FillInElement.checked === true) {
         value = $(this.FillInTextbox).val();
      }

      return value;
   };

   SPRadioChoiceField.prototype.SetValue = function (value) {
      // find the radio button we need to set in our hashtable
      var radioButton = getHashValue(this.RadioButtons, value);

      // if couldn't find the element in the hashtable and fill-in
      // is allowed, assume they want to set the fill-in value
      if (null === radioButton) {
         if (this.FillInAllowed) {
            this._setFillInValue(value);
         } else {
            throw 'Unable to set value for ' + this.Name + ' the value "' + value + '" was not found.';
         }
      } else {
         radioButton.checked = true;
      }
      this._updateReadOnlyLabel(this.GetValue().toString());
      return this;
   };

   /*
   *   SPCheckboxChoiceField class
   *   Supports multi-select choice fields which show as checkboxes
   */
   function SPCheckboxChoiceField(fieldParams) {
      SPChoiceField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      this.Checkboxes = getHashFromInputControls(this, 'input[type="checkbox"]');

      // when fill-in is allowed, it shows up as an extra checkbox
      // remove it and set the fill-in element because it isn't a normal value
      if (this.FillInAllowed) {
         this.FillInElement = this.Checkboxes.pop().value;
      }
   }

   // Inherit from SPChoiceField
   SPCheckboxChoiceField.prototype = Object.create(SPChoiceField.prototype);

   // display as semicolon delimited list
   SPCheckboxChoiceField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(this.GetValue().join("; "));
   };

   SPCheckboxChoiceField.prototype.GetValue = function () {
      var values = [];
      $(this.Checkboxes).each(function (index, pair) {
         var checkbox = pair.value;
         if (checkbox.checked) {
            values.push(pair.key);
         }
      });

      if (this.FillInAllowed && this.FillInElement.checked === true) {
         values.push($(this.FillInTextbox).val());
      }

      return values;
   };

   SPCheckboxChoiceField.prototype.SetValue = function (value, isChecked) {
      var checkbox = getHashValue(this.Checkboxes, value);
      isChecked = isUndefined(isChecked) ? true : isChecked;

      // if couldn't find the element in the hashtable
      // and fill-in is allowed, assume they meant the fill-in value
      if (null === checkbox) {
         if (this.FillInAllowed) {
            checkbox = this.FillInElement;
            $(this.FillInTextbox).val(value);
            checkbox.checked = isChecked;
         } else {
            throw 'Unable to set value for ' + this.Name + ' the value "' + value + '" was not found.';
         }
      } else {
         checkbox.checked = isChecked;
      }

      this._updateReadOnlyLabel(this.GetValue().join("; "));
      return this;
   };

   /*
    * SPDateTimeFieldValue class
    * Used to set/get values for SPDateTimeField fields
    */
   function SPDateTimeFieldValue(year, month, day, hour, minute, format, separator) {
      this.Year = null;
      this.Month = null;
      this.Day = null;
      this.IsTimeIncluded = false;
      this.Hour = null;
      this.Minute = null;
      this.TimeFormat = null; // 12HR or 24HR
      this.DateSeparator = null;

      if (!isUndefined(year) && !isUndefined(month) && !isUndefined(day)) {
         this.SetDate(year, month, day);
         if (!isUndefined(hour) && !isUndefined(minute)) {
            this.SetTime(hour, minute);
            if (!isUndefined(format)) {
               this.TimeFormat = format;
               if (!isUndefined(separator)) {
                  this.DateSeparator = separator;
               }
            }
         }
      }
   }

   /*
    * SPDateTimeFieldValue Public Methods
    */
   /*
    * Set the date portion of the value
    * year (integer), example: 2014
    * month (integer), example: 5
    * day (integer), example: 14
    */
   SPDateTimeFieldValue.prototype.SetDate = function (year, month, day) {
      if (isString(year)) {
         year = getInteger(year);
      }
      if (isString(month)) {
         month = getInteger(month);
      }
      if (isString(day)) {
         day = getInteger(day);
      }
      if (!isNumber(year) || !isNumber(month) || !isNumber(day)) {
         throw "Unable to set date, invalid arguments (requires year, month, and day as integers).";
      }
      this.Year = year;
      this.Month = month;
      this.Day = day;
   };

   // hour either an integer 0-23 or a string like '1 PM' or '12 AM'
   // hour either an integer 0-55 or a string like '00' or '35' (must be increments of 5)
   SPDateTimeFieldValue.prototype.SetTime = function (hour, minute) {
      this.IsTimeIncluded = false;
      if (isNumber(hour)) {
         if (hour < 0 || hour > 23) {
            throw 'Hour number parameter must be between 0 and 23.';
         }
         this.Hour = hour;
      } else if (isString(hour)) {
         if (!this.IsValidHour(hour)) {
            throw 'Hour string parameter must be formatted like "1 PM" or "12 AM".';
         }
         this.Hour = this.ConvertHourToNumber(hour);
      }
      if (isNumber(minute)) {
         if (minute < 0 || minute >= 60 || (minute % 5) !== 0) {
            throw 'Minute parameter is not in the correct format. Needs to be formatted like 0, 5, or 35.';
         }
         this.Minute = minute;
      } else if (isString(minute)) {
         if (!this.IsValidMinute(minute)) {
            throw 'Minute parameter is not in the correct format. Needs to be formatted like "00", "05" or "35".';
         }
         this.Minute = getInteger(minute);
      }
      this.IsTimeIncluded = true;
   };

   SPDateTimeFieldValue.prototype.IsValidDate = function () {
      return this.Year !== null && this.Month !== null && this.Day !== null;
   };

   SPDateTimeFieldValue.prototype.IsValidHour = function (h) {
      return !isUndefined(h) && (/^([1-9]|10|11|12) (AM|PM)$/).test(h);
   };

   SPDateTimeFieldValue.prototype.IsValidMinute = function (m) {
      return !isUndefined(m) && (/^([0-5](0|5))$/).test(m);
   };

   SPDateTimeFieldValue.prototype.ConvertHourToNumber = function (str) {
      var hour;
      str = str.split(' ');
      hour = getInteger(str[0]);
      if (str[1] === 'AM') {
         if (hour === 12) {
            hour = 0;
         }
      } else if (str[1] === 'PM') {
         hour += 12;
      }
      return hour;
   };

   // returns the part of a date as a string and pads with a 0 if necessary
   SPDateTimeFieldValue.prototype.PadWithZero = function (d) {
      if (isUndefined(d) || null === d) {
         return '';
      }
      if (isString(d)) {
         d = getInteger(d);
         if (isNaN(d)) {
            return '';
         }
      }
      if (isNumber(d) && d < 10) {
         return '0' + d.toString();
      }
      return d.toString();
   };

   // transforms a date object into a string
   SPDateTimeFieldValue.prototype.GetShortDateString = function () {
      if (!this.IsValidDate()) {
         return '';
      }
      var strDate;
      if (this.TimeFormat === '12HR') {
         // m/d/YYYY
         strDate = this.Month + _settings['dateSeparator'] +
            this.Day + _settings['dateSeparator'] +
            this.Year;
      } else {
         // DD/MM/YYYY
         strDate = this.PadWithZero(this.Day) + _settings['dateSeparator'] +
            this.PadWithZero(this.Month) + _settings['dateSeparator'] +
            this.Year;
      }

      return strDate;
   };

   // transforms a date object into a string
   SPDateTimeFieldValue.prototype.GetHour = function () {
      var h = this.Hour;
      if (this.TimeFormat === '12HR') {
         if (h === 0) {
            h = 12;
         } else if (h > 12) {
            h = h - 12;
         }
      }
      return h;
   };

   // transforms a date object into a string
   SPDateTimeFieldValue.prototype.GetShortTimeString = function () {
      if (this.IsTimeIncluded) {
         if (this.TimeFormat === '12HR') {
            // ex: 3/14/2014 1:00 AM
            return this.GetHour() + ':' + this.PadWithZero(this.Minute) + (this.Hour < 12 ? ' AM' : ' PM');
         } else {
            // ex: 14/03/2014 01:00
            return this.PadWithZero(this.GetHour()) + ':' + this.PadWithZero(this.Minute);
         }
      }
      return '';
   };

   SPDateTimeFieldValue.prototype.toString = function () {
      var date = this.GetShortDateString();
      var time = this.GetShortTimeString();
      if (date === '' && time === '') {
         return '';
      } else if (date === '') {
         return '';
      } else if (time === '') {
         return date;
      } else {
         return date + ' ' + time;
      }
   };

   function SPDateTimeField(fieldParams) {
      SPField.call(this, fieldParams);
      this.DateTextbox = getInputControl(this);
      this.HourDropdown = null;
      this.MinuteDropdown = null;
      this.IsDateOnly = true;
      this.HourValueFormat = null;

      if (this.Controls === null) {
         return;
      }

      var timeControls = $(this.Controls).find('select');
      if (null !== timeControls && 2 === timeControls.length) {
         this.HourDropdown = timeControls[0];
         if ($(this.HourDropdown).val().indexOf(' ') > -1) {
            this.HourValueFormat = 'string';
         } else {
            this.HourValueFormat = 'number';
         }
         this.MinuteDropdown = timeControls[1];
         this.IsDateOnly = false;
      }
   }

   // Inherit from SPField
   SPDateTimeField.prototype = Object.create(SPField.prototype);

   SPDateTimeField.prototype.GetValue = function () {
      var hour, strMinute, arrShortDate = $(this.DateTextbox).val().split(_settings['dateSeparator']);

      var spDate = new SPDateTimeFieldValue();
      spDate.TimeFormat = _settings['timeFormat'];
      spDate.DateSeparator = _settings['dateSeparator'];

      if (arrShortDate.length === 3) {
         var year, month, day;
         if (_settings['timeFormat'] === '12HR') {
            month = arrShortDate[0];
            day = arrShortDate[1];
            year = arrShortDate[2];
         } else {
            day = arrShortDate[0];
            month = arrShortDate[1];
            year = arrShortDate[2];
         }
         spDate.SetDate(year, month, day);
      }

      if (!this.IsDateOnly) {
         hour = $(this.HourDropdown).val();
         if (this.HourValueFormat === 'number') {
            hour = getInteger(hour);
         }
         strMinute = $(this.MinuteDropdown).val();
         spDate.SetTime(hour, strMinute);
      }

      return spDate;
   };

   SPDateTimeField.prototype.SetValue = function (year, month, day, hour, minute) {
      if (isUndefined(year) || year === null || year === "") {
         this.SetDate(null);
         if (!this.IsDateOnly) {
            this.SetTime(null);
         }
         return this;
      }
      this.SetDate(year, month, day);
      if (!isUndefined(hour) && !isUndefined(minute)) {
         this.SetTime(hour, minute);
      }
      return this;
   };

   SPDateTimeField.prototype.SetDate = function (year, month, day) {
      if (year === null || year === "") {
         $(this.DateTextbox).val('');
         return this;
      }
      var spDate = new SPDateTimeFieldValue();
      spDate.TimeFormat = _settings['timeFormat'];
      spDate.DateSeparator = _settings['dateSeparator'];
      spDate.SetDate(year, month, day);
      $(this.DateTextbox).val(spDate.GetShortDateString());
      this._updateReadOnlyLabel(this.GetValue().toString());
      return this;
   };

   SPDateTimeField.prototype.SetTime = function (hour, minute) {
      if (this.IsDateOnly) {
         throw "Unable to set the time for a Date only field.";
      }

      var spDate = new SPDateTimeFieldValue();
      spDate.TimeFormat = _settings['timeFormat'];
      spDate.DateSeparator = _settings['dateSeparator'];

      if (hour === null || hour === "") {
         spDate.SetTime(0, 0);
      } else {
         spDate.SetTime(hour, minute);
      }

      // is the hour dropdown values in string or number format
      // sharepoint 2013 uses number format exclusively
      // sharepoint 2007 uses string format
      // ex: 12 AM versus 0, 1 AM versus 1, etc.
      if (this.HourValueFormat === 'string') {
         var strHour;
         if (spDate.Hour === 0) {
            strHour = '12 AM';
         } else if (spDate.Hour === 12) {
            strHour = '12 PM';
         } else if (spDate.Hour > 12) {
            strHour = (spDate.Hour - 12).toString() + ' PM';
         } else {
            strHour = spDate.Hour.toString() + ' AM';
         }
         $(this.HourDropdown).val(strHour);
      } else {
         $(this.HourDropdown).val(spDate.Hour);
      }

      $(this.MinuteDropdown).val(spDate.PadWithZero(spDate.Minute));

      this._updateReadOnlyLabel(this.GetValue().toString());
      return this;
   };

   /*
    * SPBooleanField class
    * Supports yes/no fields (SPFieldBoolean)
    */
   function SPBooleanField(fieldParams) {
      SPField.call(this, fieldParams);
      this.Checkbox = getInputControl(this);
   }

   // Inherit from SPField
   SPBooleanField.prototype = Object.create(SPField.prototype);

   /*
    * SPBooleanField Public Methods
    * Overrides SPField class methods.
    */
   SPBooleanField.prototype.GetValue = function () {
      // double negative to return a boolean value
      return !!this.Checkbox.checked;
   };

   // Get the Yes/No field's value as a string
   // By default this returns Yes when True and No when False
   // Customize this behavior by altering the stringYes and stringNo settings
   SPBooleanField.prototype.GetValueString = function () {
      return this.GetValue() ? _settings['stringYes'] : _settings['stringNo'];
   };

   SPBooleanField.prototype.SetValue = function (value) {
      if (isString(value)) {
         if (_settings['stringYes'].toUpperCase() === value.toUpperCase()) {
            value = true;
         } else {
            value = false;
         }
      } else {
         if (value) {
            value = true;
         } else {
            value = false;
         }
      }
      this.Checkbox.checked = value;
      this._updateReadOnlyLabel(this.GetValueString());
      return this;
   };

   // overriding the default MakeReadOnly function
   // translate true/false to Yes/No
   SPBooleanField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(this.GetValueString());
   };

   /*
    * SPURLField class
    * Supports hyperlink fields (SPFieldURL)
    */
   function SPURLField(fieldParams) {
      SPField.call(this, fieldParams);
      if (this.Controls === null) {
         return;
      }

      this.TextboxURL = null;
      this.TextboxDescription = null;
      this.TextOnly = false;

      var controls = $(this.Controls).find('input');
      if (null !== controls && 2 === controls.length) {
         this.TextboxURL = $(controls[0]);
         this.TextboxDescription = $(controls[1]);
      }
   }

   // Inherit from SPField
   SPURLField.prototype = Object.create(SPField.prototype);

   /*
    * SPURLField Public Methods
    * Overrides SPField class methods.
    */
   SPURLField.prototype.GetValue = function () {
      return [this.TextboxURL.val(), this.TextboxDescription.val()];
   };

   SPURLField.prototype.SetValue = function (url, description) {
      this.TextboxURL.val(url);
      this.TextboxDescription.val(description);
      this._updateReadOnlyLabel(this.GetHyperlink());
      return this;
   };

   SPURLField.prototype.GetHyperlink = function () {
      var values = this.GetValue();
      var hyperlink;
      if (this.TextOnly) {
         hyperlink = values[0] + ', ' + values[1];
      } else {
         hyperlink = '<a href="' + values[0] + '">' + values[1] + '</a>';
      }
      return hyperlink;
   };

   // overriding the default MakeReadOnly function because we have multiple values returned
   // and we want to have the hyperlink field show up as a URL
   SPURLField.prototype.MakeReadOnly = function (options) {
      if (options && true === options.TextOnly) {
         this.TextOnly = true;
      }

      return this._makeReadOnly(this.GetHyperlink());
   };

   /*
    * SPDropdownLookupField class
    * Supports single select lookup fields
    */
   function SPDropdownLookupField(fieldParams, elemSelect) {
      SPField.call(this, fieldParams);
      if (this.Controls === null) {
         return;
      }

      if (1 === elemSelect.length) {
         // regular dropdown lookup
         this.Dropdown = elemSelect[0];
      } else {
         throw "Unable to get dropdown element for " + this.Name;
      }
   }

   // Inherit from SPField
   SPDropdownLookupField.prototype = Object.create(SPField.prototype);

   SPDropdownLookupField.prototype.GetValue = function () {
      return this.Dropdown.options[this.Dropdown.selectedIndex].text;
   };

   SPDropdownLookupField.prototype.SetValue = function (value) {
      if (isNumber(value)) {
         $(this.Dropdown).val(value);
      } else {
         var i, options, option;
         // need to set the dropdown based on text
         options = this.Dropdown.options;
         for (i = 0; i < options.length; i += 1) {
            option = options[i];
            if (option.text === value) {
               this.Dropdown.selectedIndex = i;
               break;
            }
         }
      }
      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
    * SPDropdownLookupField class
    * Supports single select lookup fields
    */
   function SPAutocompleteLookupField(fieldParams, elemInputs) {
      SPField.call(this, fieldParams);
      if (this.Controls === null) {
         return;
      }

      if (1 === elemInputs.length) {
         // autocomplete lookup
         this.Textbox = $(elemInputs[0]);
         this.HiddenTextbox = $('input[id="' + this.Textbox.attr('optHid') + '"]');
      } else {
         throw "Unable to get input elements for " + this.Name;
      }
   }

   // Inherit from SPField
   SPAutocompleteLookupField.prototype = Object.create(SPField.prototype);

   SPAutocompleteLookupField.prototype.GetValue = function () {
      return this.Textbox.val();
   };

   SPAutocompleteLookupField.prototype.SetValue = function (value) {
      var choices, lookupID, lookupText, i, c = [], pipeIndex;

      // a list item ID was passed to the function so attempt to lookup the text value
      choices = this.Textbox.attr('choices');

      // options are stored in a choices attribute in the following format:
      // (None)|0|Alpha|1|Bravo|2|Charlie|3
      // split the string on every pipe character followed by a digit
      choices = choices.split(/\|(?=\d+)/);
      c.push(choices[0]);
      for (i = 1; i < choices.length - 1; i++) {
         pipeIndex = choices[i].indexOf('|'); // split on the first pipe only
         c.push(choices[i].substring(0, pipeIndex));
         c.push(choices[i].substring(pipeIndex + 1));
      }
      c.push(choices[choices.length - 1]);

      if (isString(value)) {
         // since the pipe character is used as a delimiter above, any values
         // which have a pipe in them were doubled up
         value = value.replace("|", "||");
      }

      // options are stored in a choices attribute in the following format:
      // text|value|text 2|value2
      for (i = 0; i < c.length; i += 2) {
         lookupID = getInteger(c[i + 1]);
         lookupText = c[i];
         // if value is an integer, assume they are passing the list item ID
         // otherwise, a string will match the text value
         if (value === lookupID || value === lookupText) {
            this.Textbox.val(lookupText.replace("||", "|"));
            break;
         }
      }

      if (null !== lookupID) {
         this.HiddenTextbox.val(lookupID);
      }

      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
    * SPPlainNoteField class
    * Supports multi-line plain text fields (SPFieldNote)
    */
   function SPPlainNoteField(fieldParams, textarea) {
      SPField.call(this, fieldParams);
      this.Textbox = textarea;
      this.TextType = "Plain";
   }

   // Inherit from SPField
   SPPlainNoteField.prototype = Object.create(SPField.prototype);

   SPPlainNoteField.prototype.GetValue = function () {
      return $(this.Textbox).val();
   };

   SPPlainNoteField.prototype.SetValue = function (value) {
      $(this.Textbox).val(value);
      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
    * SPRichNoteField class
    * Supports multi-line rich text fields (SPFieldNote)
    */
   function SPRichNoteField(fieldParams, textarea) {
      SPPlainNoteField.call(this, fieldParams, textarea);
      this.TextType = "Rich";
   }

   // Inherit from SPField
   SPRichNoteField.prototype = Object.create(SPPlainNoteField.prototype);

   // RTE functions are defined in layouts/1033/form.js
   SPRichNoteField.prototype.GetValue = function () {
      return window.RTE_GetIFrameContents(this.Textbox.id);
   };

   SPRichNoteField.prototype.SetValue = function (value) {
      $(this.Textbox).val(value);
      window.RTE_TransferTextAreaContentsToIFrame(this.Textbox.id);
      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
    * SPEnhancedNoteField class
    * Supports multi-line, enhanced rich text fields in SharePoint 2010/2013 (SPFieldNote)
    */
   function SPEnhancedNoteField(fieldParams, hiddenInputs) {
      SPField.call(this, fieldParams);
      this.Textbox = hiddenInputs[0];
      this.ContentDiv = $(this.Controls).find('div[contenteditable="true"]')[0];
      this.TextType = "Enhanced";
   }

   // Inherit from SPField
   SPEnhancedNoteField.prototype = Object.create(SPField.prototype);

   SPEnhancedNoteField.prototype.GetValue = function () {
      return $(this.ContentDiv).html();
   };

   SPEnhancedNoteField.prototype.SetValue = function (value) {
      $(this.ContentDiv).html(value);
      $(this.Textbox).val(value);
      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
    * SPFileField class
    * Supports the name field of a Document Library
    */
   function SPFileField(fieldParams) {
      SPTextField.call(this, fieldParams);
      this.FileExtension = $(this.Textbox).parent().text();
   }

   // Inherit from SPTextField
   SPFileField.prototype = Object.create(SPTextField.prototype);

   /*
    * SPFileField Public Methods
    * Overrides SPTextField class methods.
    */
   SPFileField.prototype.GetValue = function () {
      return $(this.Textbox).val() + this.FileExtension;
   };

   /*
    * SPLookupMultiField class
    * Supports multi select lookup fields
    */
   function SPLookupMultiField(fieldParams) {
      SPField.call(this, fieldParams);
      if (this.Controls === null) {
         return;
      }

      var controls = $(this.Controls).find('select');
      if (2 === controls.length) {
         // multi-select lookup
         this.ListChoices = controls[0];
         this.ListSelections = controls[1];
         controls = $(this.Controls).find('button');
         if (controls.length === 0) {
            controls = $(this.Controls).find('input[type="button"]');
         }
         this.ButtonAdd = controls[0];
         this.ButtonRemove = controls[1];
      } else {
         throw "Error initializing SPLookupMultiField named " + this.Name + ", unable to get select controls.";
      }
   }

   // Inherit from SPField
   SPLookupMultiField.prototype = Object.create(SPField.prototype);

   SPLookupMultiField.prototype.GetValue = function () {
      var values = [], i, numOptions;

      numOptions = this.ListSelections.options.length;
      for (i = 0; i < numOptions; i += 1) {
         values.push(this.ListSelections.options[i].text);
      }

      return values;
   };

   // display as semicolon delimited list
   SPLookupMultiField.prototype.MakeReadOnly = function () {
      return this._makeReadOnly(this.GetValue().join("; "));
   };

   SPLookupMultiField.prototype.SetValue = function (value, addValue) {
      if (isUndefined(addValue)) {
         addValue = true;
      }

      var i, option, options, numOptions, button, prop;

      if (addValue) {
         options = this.ListChoices.options;
         button = this.ButtonAdd;
      } else {
         options = this.ListSelections.options;
         button = this.ButtonRemove;
      }

      numOptions = options.length;

      // select the value
      if (isNumber(value)) {
         value = value.toString();
         prop = "value";
      } else {
         prop = "text";
      }

      for (i = 0; i < numOptions; i += 1) {
         option = options[i];

         if (option[prop] === value) {
            option.selected = true;
            break; // found what we were looking for
         } else {
            option.selected = false;
         }
      }

      // the button may be disabled if this is the second time
      // we are performing a certain operation
      button.disabled = "";

      // add or remove the value
      $(button).click();

      this._updateReadOnlyLabel(this.GetValue().join("; "));
      return this;
   };

   /*
    * SPUserField class
    * Supports people fields (SPFieldUser)
    */
   function SPUserField(fieldParams) {
      SPField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      this.spanUserField = null;
      this.upLevelDiv = null;
      this.textareaDownLevelTextBox = null;
      this.linkCheckNames = null;
      this.txtHiddenSpanData = null;

      var controls = $(this.Controls).find('span.ms-usereditor');
      if (null !== controls && 1 === controls.length) {
         this.spanUserField = controls[0];
         this.upLevelDiv = byid(this.spanUserField.id + '_upLevelDiv');
         this.textareaDownLevelTextBox = byid(this.spanUserField.id + '_downlevelTextBox');
         this.linkCheckNames = byid(this.spanUserField.id + '_checkNames');
         this.txtHiddenSpanData = byid(this.spanUserField.id + '_hiddenSpanData');
      }
   }

   // Inherit from SPField
   SPUserField.prototype = Object.create(SPField.prototype);

   SPUserField.prototype.GetValue = function () {
      return $(this.upLevelDiv).text().replace(/^\s+|\u00A0|\s+$/g, '');
   };

   SPUserField.prototype.SetValue = function (value) {
      this.upLevelDiv.innerHTML = value;
      this.textareaDownLevelTextBox.innerHTML = value;
      if (isInternetExplorer()) { // internet explorer
         $(this.txtHiddenSpanData).val(value);
      }
      this.linkCheckNames.click();
      this._updateReadOnlyLabel(this.GetValue());
      return this;
   };

   /*
    * SPUserField2013 class
    * Supports people fields for SharePoint 2013 (SPFieldUser)
    */
   function SPUserField2013(fieldParams) {
      SPField.call(this, fieldParams);

      if (this.Controls === null) {
         return;
      }

      // sharepoint 2013 uses a special autofill named SPClientPeoplePicker
      // _layouts/15/clientpeoplepicker.debug.js
      var pickerDiv = $(this.Controls).children()[0];
      this.ClientPeoplePicker = window.SPClientPeoplePicker.SPClientPeoplePickerDict[$(pickerDiv).attr('id')];
      this.EditorInput = $(this.Controls).find("[id$='_EditorInput']")[0];

      //this.ClientPeoplePicker.OnUserResolvedClientScript = function () {...}
      //this.HiddenInput = $(this.Controls).find("[id$='_HiddenInput']")[0];
      //this.AutoFillDiv = $(this.Controls).find("[id$='_AutoFillDiv']")[0];
      //this.ResolvedList = $(this.Controls).find("[id$='_ResolvedList']")[0];
   }

   // Inherit from SPField
   SPUserField2013.prototype = Object.create(SPField.prototype);

   SPUserField2013.prototype.GetValue = function () {
      // returns an array of objects
      return this.ClientPeoplePicker.GetAllUserInfo();
   };

   // Iterates over all entities currently in the field, gets the user ID
   // for each one, and builds an HTML link
   // callback should be a function which takes one parameter for the returned HTML
   SPUserField2013.prototype._getValueLinks = function (callback) {
      // TODO: doesn't support sharepoint groups

      var tmpArray = [], self = this;

      // build an array of all the entities currently resolved
      $.each(self.GetValue(), function (key, val) {
         if (val.Key !== null) {
            tmpArray.push(val.Key);
         }
      });

      function successCallback(parms) {
         var o = { 'users': parms.users };
         parms.d.resolve(o);
      }

      function failCallback(parms) {
         parms.d.reject("Something went wrong...");
      }

      function getUserId(loginNames, field) {
         var d = $.Deferred();
         var context = new SP.ClientContext.get_current();
         var arrayLength = loginNames.length;
         var users = [];

         for (var i = 0; i < arrayLength; i++) {
            var user = context.get_web().ensureUser(loginNames[i]);
            context.load(user);
            users.push(user);
         }

         var parms = { d: d, loginNames: loginNames, users: users };
         context.executeQueryAsync(
            successCallback.bind(field, parms),
            failCallback.bind(field, parms));
         return d.promise();
      }

      var x = getUserId(tmpArray, self);

      x.done(function (result) {
         // result is an SP.List because that is what we passed to resolve()!
         var htmlText = "";
         for (var i = 0; i < result.users.length; i++) {
            var user = result.users[i];
            if (htmlText !== "") { htmlText += "; "; }
               htmlText += '<a href="/_layouts/15/userdisp.aspx?ID=' + user.get_id().toString() + '&amp;RootFolder=*">' + user.get_title() + '</a>';
         }
         // finally! send the result to our callback
         return callback(htmlText);
      });

      x.fail(function (result) {
         // result is a string because that is what we passed to reject()!
         var error = result;
         console.log(error);
      });
   };

   // should be called in SetValue to update the read-only label
   // Customized for SPUserField2013 because updating the label is async
   SPUserField2013.prototype._updateReadOnlyLabel = function () {
      var self = this;
      if (self.ReadOnlyLabel) {
         // after getting links, update the label inside callback
         this._getValueLinks(function (html) {
            self.ReadOnlyLabel.html(html);
         });
      }
   };

   // Get the field's value as a comma delimited string
   SPUserField2013.prototype.GetValueString = function() {
      return $.map(this.GetValue(), function (val) {
          return val.DisplayText;
      }).join(", ");
   };

   SPUserField2013.prototype.SetValue = function (value) {
      if (isUndefined(value) || value === null || value === '') {
         // delete the user if passed null/empty
         this.ClientPeoplePicker.DeleteProcessedUser();
      } else {
         $(this.EditorInput).val(value);
         this.ClientPeoplePicker.AddUnresolvedUserFromEditor(true);
      }
      // schedule a callback to update the read-only label if necessary
      this._updateReadOnlyLabel();
      return this;
   };

   // Make the field read only and display a link to each person or group
   SPUserField2013.prototype.MakeReadOnly = function () {
      // make the field read-only
      // field will display empty until callback resolves in _updateReadOnlyLabel
      this._makeReadOnly('');
      // schedule callback to update read only label
      this._updateReadOnlyLabel();
      return this;
   };

   /*
    *   SPDispFormTextField class
    *   Supports DispForm text fields
    */
   function SPDispFormTextField(fieldParams, textNode) {
      SPField.call(this, fieldParams);
      this.Controls = fieldParams.controlsCell;
      this.TextNode = textNode;
   }

   // SPDispFormField inherits from the SPField base class
   SPDispFormTextField.prototype = Object.create(SPField.prototype);

   /*
    *   SPDispFormField Public Methods
    *   Overrides SPField class methods.
    */
   SPDispFormTextField.prototype.GetValue = function () {
      return $.trim($(this.TextNode).text());
   };

   SPDispFormTextField.prototype.SetValue = function (value) {
      this.TextNode.nodeValue = value;
      return this;
   };

   SPDispFormTextField.prototype.MakeEditable = function () {
      // does nothing
      return this;
   };

   SPDispFormTextField.prototype.MakeReadOnly = function () {
      // does nothing, already read-only
      return this;
   };

   /*
    *   SPDispFormField class
    *   Supports DispForm html fields
    */
   function SPDispFormField(fieldParams, element) {
      SPField.call(this, fieldParams);
      this.Controls = fieldParams.controlsCell;
      this.Element = element;
   }

   // SPDispFormField inherits from the SPField base class
   SPDispFormField.prototype = Object.create(SPField.prototype);

   /*
    *   SPDispFormField Public Methods
    *   Overrides SPField class methods.
    */
   SPDispFormField.prototype.GetValue = function () {
      // TODO: need to figure out some more advanced parsing
      return $(this.Element).text();
   };

   SPDispFormField.prototype.SetValue = function () {
      // TODO: not supported yet
      return this;
   };

   SPDispFormField.prototype.MakeEditable = function () {
      // does nothing
      return this;
   };

   SPDispFormField.prototype.MakeReadOnly = function () {
      // does nothing, already read-only
      return this;
   };

   function getSPFieldFromType(spFieldParams) {
      var field = null, controls;

      if (isDispForm()) {
         // DispForm fields display differently
         controls = spFieldParams.controlsCell.childNodes;
         if (controls.length === 5) {
            // fields which have an HTML element
            return new SPDispFormField(spFieldParams, controls[3]);
         }
         // fields which have a text node element
         return new SPDispFormTextField(spFieldParams, controls[2]);
      }

      switch (spFieldParams.type) {
      case 'SPFieldText':
         field = new SPTextField(spFieldParams);
         break;
      case 'SPFieldNumber':
         field = new SPNumberField(spFieldParams);
         break;
      case 'SPFieldCurrency':
         field = new SPCurrencyField(spFieldParams);
         break;
      case 'ContentTypeChoice': // special type for content type field
         field = new ContentTypeChoiceField(spFieldParams);
         break;
      case 'SPFieldChoice':
         // is this a normal dropdown field?
         controls = $(spFieldParams.controlsCell).find('select');
         if (controls.length > 0) {
            field = new SPDropdownChoiceField(spFieldParams, controls);
         } else {
            field = new SPRadioChoiceField(spFieldParams);
         }
         break;
      case 'SPFieldMultiChoice':
         field = new SPCheckboxChoiceField(spFieldParams);
         break;
      case 'SPFieldDateTime':
         field = new SPDateTimeField(spFieldParams);
         break;
      case 'SPFieldBoolean':
         field = new SPBooleanField(spFieldParams);
         break;
      case 'SPFieldUser':
      case 'SPFieldUserMulti':
      case 'SPFieldBusinessData':
         if (typeof window.SPClientPeoplePicker === 'undefined') {
            field = new SPUserField(spFieldParams);
         } else {
            field = new SPUserField2013(spFieldParams);
         }
         break;
      case 'SPFieldURL':
         field = new SPURLField(spFieldParams);
         break;
      case 'SPFieldLookup':
         // is this a normal dropdown field?
         controls = $(spFieldParams.controlsCell).find('select');
         if (controls.length > 0) {
            field = new SPDropdownLookupField(spFieldParams, controls);
         } else {
            controls = $(spFieldParams.controlsCell).find('input');
            field = new SPAutocompleteLookupField(spFieldParams, controls);
         }
         break;
      case 'SPFieldNote':
         controls = $(spFieldParams.controlsCell).find('textarea');
         if (controls.length > 0) {
            // either plain text or rich text
            controls = controls[0];
            if (window.RTE_GetEditorIFrame && window.RTE_GetEditorIFrame(controls.id) !== null) {
               // rich text field detected
               field = new SPRichNoteField(spFieldParams, controls);
            }
         } else {
            controls = $(spFieldParams.controlsCell).find('input[type="hidden"]');
            // is this an "enhanced rich text field" in sp 2010/2013?
            if (controls.length >= 1) {
               field = new SPEnhancedNoteField(spFieldParams, controls);
            }
         }
         if (null === field) {
            // default to plain text note field (on DispForm there is no way to tell)
            field = new SPPlainNoteField(spFieldParams, controls);
         }
         break;
      case 'SPFieldFile':
         field = new SPFileField(spFieldParams);
         break;
      case 'SPFieldLookupMulti':
         field = new SPLookupMultiField(spFieldParams);
         break;
      default:
         field = new SPField(spFieldParams);
         break;
      }
      return field;
   }

   /*
    * Create an instance of the correct class based on the field's type
    */
   function createSPField(spFieldParams) {
      try {
         // if we can't get the type then we can't create the field
         if (null === spFieldParams.type) {
            throw 'Unknown SPField type.';
         }
         return getSPFieldFromType(spFieldParams);
      } catch (e) {
         throw 'Error creating field named ' + spFieldParams.name + ': ' + e.toString();
      }
   }

   /**
    *   SPUtility Global object and Public Methods
   **/
   var SPUtility = {};
   SPUtility.Debug = function () {
      // Debug method has been deprecated in favor of
      // exceptions being thrown from the library
      // Catch the exception, then use console.log or alert
      return false;
   };

   // Searches the page for a specific field by name
   SPUtility.GetSPField = function (strFieldName) {
      lazyLoadSPFields();

      var fieldParams = _fieldsHashtable[strFieldName];

      if (isUndefined(fieldParams)) {
         throw 'Unable to get a SPField named ' + strFieldName;
      }

      if (fieldParams.spField === null) {
         // field hasn't been initialized yet
         fieldParams.spField = createSPField(fieldParams);
      }

      return fieldParams.spField;
   };

   SPUtility.GetSPFieldByInternalName = function (strInternalName) {
      lazyLoadSPFields();

      var fieldParams = _internalNamesHashtable[strInternalName];

      if (isUndefined(fieldParams)) {
         throw 'Unable to get a SPField with internal name ' + strInternalName;
      }

      if (fieldParams.spField === null) {
          // field hasn't been initialized yet
          fieldParams.spField = createSPField(fieldParams);
      }

      return fieldParams.spField;
   };

   // Gets all of the SPFields by name on the page
   SPUtility.GetSPFields = function () {
      lazyLoadSPFields();
      return _fieldsHashtable;
   };

   // Gets all of the SPFields by internal name on the page
   SPUtility.GetSPFieldsInternal = function () {
       lazyLoadSPFields();
       return _internalNamesHashtable;
   };

   SPUtility.HideSPField = function (strFieldName) {
      toggleSPField(strFieldName, false);
   };

   SPUtility.ShowSPField = function (strFieldName) {
      toggleSPField(strFieldName, true);
   };

   /*
    * True if the current page is the DispForm. Otherwise, will return
    * False if it is EditForm or NewForm.
   **/
   SPUtility.IsDispForm = function () {
      return isDispForm();
   };

   /*
    * Configure SPUtility by passing an object containing settings.
    _settings = {                 // DEFAULT SETTINGS:
      'timeFormat': '12HR',      // 12HR or 24HR
      'dateSeparator': '/',      // separates month/day/year with / or .
      'decimalSeparator': '.',   // separates decimal from number
      'thousandsSeparator': ',', // separates thousands in number
      'stringYes': 'Yes',        // Text for when boolean field is True
      'stringNo': 'No'           // Text for when boolean field is False
    }
   **/
   SPUtility.Setup = function (settings) {
      var s = $.extend( {}, _settings, settings );
      // validate the passed settings
      if (s['timeFormat'] !== '12HR' && s['timeFormat'] !== '24HR') {
         throw "Unable to set timeFormat, should be 12HR or 24HR.";
      }
      // TODO: validate other settings?
      _settings = s;
      return s;
   };

   // deprecated
   SPUtility.GetTimeFormat = function () {
      return _settings['timeFormat'];
   };

   // deprecated
   SPUtility.SetTimeFormat = function (format) {
      SPUtility.Setup({ 'timeFormat': format });
   };

   // deprecated
   SPUtility.GetDateSeparator = function () {
      return _settings['dateSeparator'];
   };

   // deprecated
   SPUtility.SetDateSeparator = function (separator) {
      SPUtility.Setup({ 'dateSeparator': separator });
   };

   // deprecated
   SPUtility.GetDecimalSeparator = function () {
      return _settings['decimalSeparator'];
   };

   // deprecated
   SPUtility.SetDecimalSeparator = function (separator) {
      SPUtility.Setup({ 'decimalSeparator': separator });
   };

   // deprecated
   SPUtility.GetThousandsSeparator = function () {
      return _settings['thousandsSeparator'];
   };

   // deprecated
   SPUtility.SetThousandsSeparator = function (separator) {
      SPUtility.Setup({ 'thousandsSeparator': separator });
   };

   return SPUtility;
}(jQuery));
```

---

### `HideGear.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** Continuously polls (`setInterval`, every 500ms, indefinitely, never cleared) to hide the O365 top-nav Settings gear icon for users without ManageWeb permission. Cosmetic only — not a real permission boundary (the gear is still functionally reachable via direct URL). Not found in current CEWP/SEWP scan scope.

```javascript
$(document).ready(function() {
    if (_spPageContextInfo.hasManageWebPermissions == false) {
        setInterval(function() {
            $("#O365_MainLink_Settings.o365cs-nav-item.o365cs-nav-button.o365cs-topnavText.ms-bgc-tdr-h.o365button").hide();
        }, 500);
    }
});
```

---

### `connect_to_Outlook-hold.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** Calls `ExportHailStorm(...)` (the classic "Connect to Outlook" iCal export handler) with hardcoded parameters pointing to `https://itau.dev.jag.gov.bc.ca` (DEV environment) and a list named `Security_Events` — this list name does not match any list documented elsewhere in this project (`Security_Alerts` is the actual CMAT list name). **Likely broken/stale** — points to DEV not PROD, references a non-existent list name, and the `-hold` filename suffix suggests it was already disabled. Flag as probable dead code; confirm with SMEs before considering for SPO migration.

```javascript
ExportHailStorm(
'calendar',
'https://itau.dev.jag.gov.bc.ca/cmat/Lists/Security_Events' ,
'{5BFD43A9-E132-4B0E-A040-A060EF54DA39}',
'cmat',
'Security_Events',
'/cmat/Lists/Security_Events',
'',
'/cmat/Lists/Security_Events')


```

---

### `HideLinksToPersons.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same unlink pattern, targeting links to `userdisp.aspx?ID=` (user profile) URLs. Uses the JSLink `RegisterTemplateOverrides` mechanism (not just a plain jQuery DOM-ready handler) like the linkCase/linkPIOCase files, but its actual effect is just text-only unlinking.

```javascript

SPClientTemplates.TemplateManager.RegisterTemplateOverrides({

OnPostRender: function(ctx) {
    $(document).ready(function() {
        $('a[href*="userdisp.aspx?ID="]').each(function(index) {
            var link = $(this);
            $(this).after("<span>" + link.text() + "</span>");
            $(this).remove();
        });
    });
   ctx.skipNextAnimation = true;
 }


});

```

---

## Files confirmed trivial (as originally assumed)

### `linkPIOCase.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Same JSLink field-override mechanism as linkCase.js, applied to the `RelatedPIOCases` lookup field. Also hardcodes a View GUID. Same migration note as linkCase.js.

```javascript
(function () {
    var overrideCtx = {};
    overrideCtx.Templates = {};
    overrideCtx.OnPostRender = [];

    overrideCtx.Templates.Fields =
    {
        'RelatedPIOCases': { 'View': renderButton }
    };

    SPClientTemplates.TemplateManager.RegisterTemplateOverrides(overrideCtx);

})();

function renderButton(ctx){ 
    var current_case = ctx.CurrentItem.hasOwnProperty("RelatedPIOCases") && ctx.CurrentItem["RelatedPIOCases"].hasOwnProperty(0) ? ctx.CurrentItem["RelatedPIOCases"][0] : null;
    
    if (current_case){
	    var lookupId = current_case.lookupId;
	    var lookupValue= current_case.lookupValue;
	    var viewList = "%7BF7393396-41AF-41C6-8541-26C266DA0594%7D";
	    var listTitle = ctx.ListTitle;	
		return "<a href='/cmat/Pages/PIO_Cases.aspx?View="+viewList+"&SelectedID="+ lookupId + "'>"+lookupValue+"</div>";
    }
       														
}

```

---

### `RLHelper-ParentDisplayForm.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Companion to RLHelper-ChildNewForm.js — reads the `SelectedID` query string parameter on the parent item's display page (used to build the child form's dialog URL with that parameter included).

```javascript
/*
SharePoint 2010 Related List Prefill Version 1.2
Call JQuery and this file from the parent list's view item page that contains related list web parts.
Instructions: http://code.google.com/p/sp2010-related-list-prefill/
RLHelper-ParentDisplayForm.js
*/
function getQuerystring(ji) {
hu = window.location.search.substring(1);
gy = hu.split("&");
for (i=0;i<gy.length;i++) {
ft = gy[i].split("=");
if (ft[0] == ji) {
return ft[1];
}
}
}
_spBodyOnLoadFunctionNames.push("updateSelection");
function updateSelection() {
var selId = getQuerystring("SelectedID");
return false;
}
```

---

### `default_All_Day_Event.js`

**Referenced by scanned CEWP/SEWP:** No — not referenced by any of the 121 scanned web parts

**Finding:** Trivial: auto-checks the "All Day Event" checkbox on calendar New-item forms. Modern SPO calendar column default values can replicate this without code.

```javascript
$(function() {
  $('span[title=All Day Event] > input').attr("checked","checked"); // checks All Day Event
  
  });

```

---

### `ConditionalColoring.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial as assumed: conditional text coloring by keyword match in list view cells (High=Red, Medium=Orange, Low=Green, Extreme=Red bold, Yes=bold, Overdue=bold).

```javascript
SPClientTemplates.TemplateManager.RegisterTemplateOverrides({

OnPostRender: function(ctx) {


$(document).ready(function(){
$Text = $("td .ms-vb2:contains('High')").filter(function() {
return $(this).text() == "High";})
$Text.css("color", "Red");
$Text = $("td .ms-vb2:contains('Medium')").filter(function() {
return $(this).text() == "Medium";})
$Text.css("color", "Orange");
$Text = $("td .ms-vb2:contains('Low')").filter(function() {
return $(this).text() == "Low";})
$Text.css("color", "ForestGreen");
$Text = $("td .ms-vb2:contains('Extreme')").filter(function() {
return $(this).text() == "Extreme";})
$Text.css("color", "Red");
$Text.css("font-weight", "bold");
$Text = $("td .ms-vb2:contains('Yes')").filter(function() {
return $(this).text() == "Yes";})
$Text.css("font-weight", "bold");
$Text = $("td .ms-vb2:contains('Overdue')").filter(function() {
return $(this).text() == "Overdue";})
$Text.css("font-weight", "bold");
});
    ctx.skipNextAnimation = true;
 }


});
```

---

### `HideLinksInDisplayForm.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: replaces hyperlinks matching a folder-root URL pattern with plain text spans (removes the link, keeps the label) on Display forms.

```javascript
    $(document).ready(function() {
        $('a[href*="RootFolder=*"]').each(function(index) {
            var link = $(this);
            $(this).after("<span>" + link.text() + "</span>");
            $(this).remove();
        });
    });



```

---

### `HideLinksToListForm.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same unlink pattern, targeting links to `listform.aspx?PageType=` URLs.

```javascript
    $(document).ready(function() {
        $('a[href*="listform.aspx?PageType="]').each(function(index) {
            var link = $(this);
            $(this).after("<span>" + link.text() + "</span>");
            $(this).remove();
        });
    });

```

---

### `ItemToCaseHeadingChanger.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: brute-force scans all `<span>` elements for exact text "new item" and replaces with "new case" (stops after first match).

```javascript
$(document).ready(function(){

var spans = document.getElementsByTagName("span");
for(var i=0;i<spans.length; i++) {
    if(spans[i].innerHTML == "new item") { 
        spans[i].innerHTML = "new case";  
        break;                                  
    }
}

});
```

---

### `ItemToPersonHeadingChanger.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same pattern, replaces "new item" with "new person".

```javascript
$(document).ready(function(){

var spans = document.getElementsByTagName("span");
for(var i=0;i<spans.length; i++) {
    if(spans[i].innerHTML == "new item") { 
        spans[i].innerHTML = "new person";  
        break;                                  
    }
}

});
```

---

### `NewItemToAddNewHeadingChanger.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same span-scan pattern, replaces ALL matches of "new item" with "Add New" (no break — unlike the other HeadingChanger variants, this one doesn't stop after the first match).

```javascript
$(document).ready(function(){

var spans = document.getElementsByTagName("span");
for(var i=0;i<spans.length; i++) {
    if(spans[i].innerHTML == "new item") { 
        spans[i].innerHTML = "Add New"
    }
}

});
```

---

### `NewTaskToAddNewHeadingChanger.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same pattern, replaces "new task" with "Add New".

```javascript
$(document).ready(function(){

var spans = document.getElementsByTagName("span");
for(var i=0;i<spans.length; i++) {
    if(spans[i].innerHTML == "new task") { 
        spans[i].innerHTML = "Add New"
    }
}

});
```

---

### `TaskToAlertHeadingChanger.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same pattern, replaces "new task" with "new alert" (stops after first match).

```javascript
$(document).ready(function(){

var spans = document.getElementsByTagName("span");
for(var i=0;i<spans.length; i++) {
    if(spans[i].innerHTML == "new task") { 
        spans[i].innerHTML = "new alert";  
        break;                                  
    }
}

});
```

---

### `TaskToItemHeadingChanger.js`

**Referenced by scanned CEWP/SEWP:** Yes

**Finding:** Confirmed trivial: same pattern, replaces "new task" with "new item" (no break).

```javascript
$(document).ready(function(){

var spans = document.getElementsByTagName("span");
for(var i=0;i<spans.length; i++) {
    if(spans[i].innerHTML == "new task") { 
        spans[i].innerHTML = "new item"
    }
}

});
```

---
