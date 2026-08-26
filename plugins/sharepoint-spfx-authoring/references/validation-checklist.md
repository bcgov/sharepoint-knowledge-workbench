# SPFx Form Customizer Validation and Testing Checklist

## Overview

Deploying a custom form experience into a production or test SharePoint tenant requires strict verification at both the local code level and the live tenant integration level. Use this checklist as the test gate before signing off on any Form Customizer implementation.

---

## 1. Automated / Local Unit Testing Checklist

Verify core helper functions and component behaviors with unit tests (e.g. Jest / Mocha / Vitest):

| Test Case | Description | Expected Outcome |
|---|---|---|
| **Valid Positive Integer** | `parseAndValidateParentId("?SelectedID=2411")` | Returns integer `2411`. |
| **Missing Parameter** | `parseAndValidateParentId("")` or `"?other=123"` | Returns `null`. |
| **Malformed / Non-numeric** | `parseAndValidateParentId("?SelectedID=abc")` or `"?SelectedID=12.34"` | Returns `null` without throwing. |
| **Negative and Zero Values** | `parseAndValidateParentId("?SelectedID=0")` or `"?SelectedID=-5"` | Returns `null` (rejected). |
| **Overflow / Max Integer** | `parseAndValidateParentId("?SelectedID=99999999999999")` | Returns `null` (> 2147483647 rejected). |
| **Safe Source URL Validation** | `getSafeReturnUrl` with valid internal relative URL | Returns internal relative path. |
| **Open Redirect Attack Vector** | `getSafeReturnUrl` with `https://evil-attacker.com` | Rejects external domain; returns default safe site fallback. |
| **Payload Assembly** | Assemble creation JSON payload for child item | Lookup property formatted as integer ID (`RelatedPersonId: 2411`). |
| **Required Field Validation** | Trigger Save with empty mandatory fields | Form shows inline validation errors; focus jumps to first invalid field. |
| **Double-Submit Prevention** | Click Save button twice rapidly | Save button disables immediately upon first click; only 1 API call dispatched. |
| **Component Cleanup / Unmount** | Call `onDispose()` on Form Customizer instance | React DOM tree unmounts cleanly; no lingering memory leaks or event listeners. |

---

## 2. SharePoint Online Tenant Integration Checklist

Execute against the designated non-production development site (`AG-CSB-intRANET-DEV` or Trial Tenancy):

### Phase A: Pre-Association Baseline
- [ ] Open the target list New form before associating the customizer.
- [ ] Confirm standard out-of-the-box SharePoint form loads cleanly.

### Phase B: Form Customizer Loading & Rendering
- [ ] Associate the Form Customizer via `associate-form-customizer.ps1`.
- [ ] Navigate to `NewForm.aspx?SelectedID=2411`. Confirm custom UI loads instead of default form.
- [ ] Confirm parent item banner renders resolved display details (e.g. "Related Person: Jane Doe (ID: 2411)").
- [ ] Test with missing `SelectedID` parameter (`NewForm.aspx`). Confirm appropriate validation warning or fallback behavior.
- [ ] Test with invalid `SelectedID` parameter (`NewForm.aspx?SelectedID=999999999` non-existent item). Confirm error message: parent not found.

### Phase C: Form Submission & State Integrity
- [ ] Fill in required fields and click **Save**.
- [ ] Confirm Save button disables during transit and displays loading spinner.
- [ ] Verify save completion redirects back to validated `Source` page or invokes `this.formSaved()`.
- [ ] Inspect the newly created item in the SharePoint list view. Confirm `RelatedPerson` lookup column contains the correct parent item reference.
- [ ] Open `EditForm.aspx?ID=<new_item_id>`. Confirm existing values populate correctly.
- [ ] Open `DispForm.aspx?ID=<new_item_id>`. Confirm form displays in read-only mode with accessible labels.

### Phase D: Cancellation & Dismissal
- [ ] Open `NewForm.aspx?SelectedID=2411`.
- [ ] Enter partial data and click **Cancel**.
- [ ] Verify no item was created in the SharePoint list.
- [ ] Confirm browser navigates safely to `Source` location or triggers `this.formClosed()`.

### Phase E: Detach & Rollback Verification
- [ ] Run `remove-form-customizer-association.ps1` to clear content type properties.
- [ ] Navigate to `NewForm.aspx`. Confirm the standard out-of-the-box SharePoint form experience is restored immediately.
