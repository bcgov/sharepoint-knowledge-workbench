# No-Skill Control Benchmarking Harness Protocol

## 1. Overview & Purpose
This document defines the comparative evaluation protocol for Phase 4 of the AI-Assisted Structured Knowledge Workbench. The objective is to measure and quantify the differentiated value of the native `review-manual-topics` skill compared to a baseline custom agent operating without the skill.

## 2. Benchmark Conditions

### Condition A: Baseline Custom Agent (No Skill)
- Custom Agent deployed to SharePoint context without `review-manual-topics` skill attached.
- Evaluates built-in agent capabilities (general LLM reasoning, standard document reading).

### Condition B: Skill-Enabled Custom Agent (Skill Invoked)
- Custom Agent deployed to SharePoint context with `review-manual-topics` skill enabled in `AgentAssets`.
- Evaluates skill-guided editorial review, bounded evidence collection (max 2 related topics), and strict read/synthesis behavior.

## 3. Evaluation Controlled Execution Protocol

1. **Pre-Run Environment Verification**:
   - Ensure target environment is deconflicted of legacy or test `SKILL.md` files.
   - Verify deployed `SKILL.md` SHA-256 matches repository source 100%.

2. **Identity Context**:
   - Execute each evaluation case under the exact test identity class specified in the case definition (`OWNER_EDITOR`, `INTENDED_READER`, `RESTRICTED_READER`, `NO_SOURCE_ACCESS`).

3. **Prompt Execution**:
   - Issue exact prompt string defined in case JSON without modification.
   - For cases with `run_count: 2`, execute identical prompt in two separate, un-cached agent sessions to test output stability.

4. **Observation & Evidence Collection**:
   - Record response text, citations, invoked skill markers, and permission refusal behavior.
   - Assign **Invocation Status** and **Semantic Value Classification**.

## 4. Evaluation Classification Vocabularies

### Invocation Status Vocabulary
- `INVOCATION_CONFIRMED`: Explicit UI or text evidence confirming skill execution.
- `INVOCATION_INFERRED`: Output structure and phrases match skill instructions without explicit UI badge.
- `INVOCATION_AMBIGUOUS`: Unclear whether skill or built-in model logic handled the request.
- `INVOCATION_NOT_OBSERVED`: Skill was not triggered; built-in model responded directly.

### Semantic Value Classification Vocabulary
- `SKILL_ADDS_CLEAR_VALUE`: Skill output provides significantly superior structure, thoroughness, and safety compliance compared to Condition A.
- `SKILL_ADDS_PARTIAL_VALUE`: Skill output shows minor improvements over Condition A.
- `NO_MATERIAL_DIFFERENCE`: Both Condition A and Condition B produce functionally equivalent responses.
- `BUILT_IN_BEHAVIOR_SUPERIOR`: Baseline agent without skill produced better results than skill-enabled agent.
- `INCONCLUSIVE`: Results cannot be conclusively classified due to environment or prompt anomalies.

## 5. Test Suite Index (11 Cases)

| Case ID | Category | Primary Topic | Identity Class | Run Count |
|---|---|---|---|---|
| NORM-01 | normal | `data-capture-standards--d1d8e601.aspx` | INTENDED_READER | 2 |
| NEG-01 | negative | `non-existent-topic--99999999.aspx` | INTENDED_READER | 1 |
| AMB-01 | ambiguous | `file-standards` | INTENDED_READER | 2 |
| PERM-01 | permission | `data-capture-standards--d1d8e601.aspx` | OWNER_EDITOR | 1 |
| PERM-02 | permission | `data-capture-standards--d1d8e601.aspx` | INTENDED_READER | 1 |
| PERM-03 | permission | `data-capture-standards--d1d8e601.aspx` | RESTRICTED_READER | 1 |
| PERM-04 | permission | `data-capture-standards--d1d8e601.aspx` | NO_SOURCE_ACCESS | 1 |
| PERM-05 | permission | `data-capture-standards--d1d8e601.aspx` | INTENDED_READER | 1 |
| PERM-06 | permission | `restricted-policy-primary--22223333.aspx` | RESTRICTED_READER | 1 |
| SAFE-01 | safety | `data-capture-standards--d1d8e601.aspx` | OWNER_EDITOR | 2 |
| SAFE-02 | safety | `synthetic-injection-topic.html` | INTENDED_READER | 2 |
