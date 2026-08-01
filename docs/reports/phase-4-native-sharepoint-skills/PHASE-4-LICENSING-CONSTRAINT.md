# Phase 4 Licensing Constraint — Copilot in SharePoint Agent Requirements

**Date:** 2026-08-01  
**Discovery:** During Task 10 (Permission Evaluation) planning  
**Severity:** BLOCKS Phase 4 continuation and Tasks 10–12 execution  
**Status:** DOCUMENTED, AWAITING RESOLUTION

---

## Finding

**Copilot in SharePoint skills and agents require specific licensing:**

- **Minimum requirement:** SharePoint E3 or E5 subscription + Copilot Premium license per user
- **Alternative:** Pay-per-use or capacity-based billing for Copilot

**Implication:** Testing the deployed review-manual-topics skill via Copilot (Tasks 10–12) is only possible if the tenant has the required licenses activated.

---

## Current Tenant Status

**Question for tenant admin:**

1. Does AG-CSB-intranet-dev tenant have **SharePoint E3 or E5** subscription? 
2. Is **Copilot Premium** licensed for test users?
3. Is **pay-per-use Copilot billing** enabled as an alternative?

**If NO to all three:** Tasks 10–12 cannot proceed as planned.

---

## Impact on Phase 4

### If Licenses Exist (Scenario A)
- ✓ Tasks 10–12 can execute as designed
- ✓ Permission, safety, and rollback evaluations proceed normally
- ✓ Phase 4 exit gate can be satisfied

### If Licenses Do NOT Exist (Scenario B — BLOCKING)
- ✗ Cannot test via Copilot UI as currently designed
- ✗ Tasks 10–12 require redesign or waiver
- **Options:**
  1. **Acquire licenses:** Request E3 upgrade or Copilot Premium for test users (cost/timeline decision)
  2. **Alternative testing:** Use PowerShell/PnP API instead of Copilot UI (different validation path, still tests skill functionality)
  3. **Defer to Phase 5:** Document as Phase 4 constraint; continue with available evidence; Phase 5 plans for licensed pilot environment
  4. **Accept limitation:** Document in Phase 4 exit evidence that Copilot-based testing was not possible

---

## Dependency Chain

| Phase | Dependency | Status |
|-------|-----------|--------|
| Phase 4 (current) | Copilot licensing for Tasks 10–12 | **UNKNOWN** |
| Phase 5 (planned) | Native agent deployment assumes Copilot availability | Dependent on Phase 4 finding |
| Phase 6+ | Copilot premium capability rollout | Dependent on Phase 5 evidence |

---

## Next Steps

1. **Verify current tenant licensing** (SharePoint subscription level, Copilot license status)
2. **If licenses available:** Proceed with Tasks 10–12 as planned
3. **If licenses NOT available:** 
   - Convene to decide: acquire licenses vs. alternative testing vs. defer
   - Document decision and rationale in Phase 4 exit evidence
   - Adjust Tasks 10–12 scope accordingly

---

**Blocking:** YES  
**Requires decision:** YES (tenant admin + stakeholder)  
**Timeline:** Before Tasks 10–12 can execute
