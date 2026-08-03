# Phase 6 Task 3 — Shared Capability Specification: `review-manual-topics`

Derived from Task 1/2's brainstorming record and inventory
(`task-1-brainstorming-and-task-2-inventory.md`). Every element below is classified
`ESSENTIAL` / `TARGET_SPECIFIC` / `ACCIDENTAL` / `DEFERRED` / `REJECTED`, each traced back to the
original intent evidence that justifies its classification — per the design spec's Non-goals,
this is explicitly not a forced lowest-common-denominator intersection, and outputs are not
required to be textually identical between runtimes.

## Shared Capability Contract

**Name:** `review-manual-topics`
**Intent:** Read-only, single-topic-scoped semantic editorial review of exactly one CEIS manual
topic page, optionally consulting up to 2 explicitly cross-referenced related topics, performed
by a runtime that never claims deterministic/cryptographic guarantees a repository tool alone can
make.

### Essential elements (must survive identically in intent, in every runtime)

| Element | Classification | Traced to |
|---|---|---|
| Exactly one primary topic per invocation | `ESSENTIAL` | Phase 4 spec §2 In-Scope #2; bounds review scope, auditability |
| At most 2 related topics, only when explicitly cross-referenced/requested | `ESSENTIAL` | Phase 4 spec §2 In-Scope #3; bounds prompt-injection/hallucination blast radius |
| Read-only — no document/list/site writes | `ESSENTIAL` | Phase 4 spec §1 Core Architectural Principle; `SKILL.md` Prohibited Scope |
| No hash/cryptographic-proof claims | `ESSENTIAL` | Repository/deterministic-tooling seam — the whole basis for the skill's trust boundary |
| No canonical-package-identity claims | `ESSENTIAL` | Same seam |
| No deterministic technical link-validation claims | `ESSENTIAL` | Same seam |
| No auto-approval/publication | `ESSENTIAL` | `SKILL.md` Prohibited Scope |
| No inventing missing metadata values | `ESSENTIAL` | `SKILL.md` Prohibited Scope; "Honest Metadata Unavailable Language" |
| No full-library scanning | `ESSENTIAL` | `SKILL.md` Prohibited Scope |
| No execution of embedded prompt-injection content | `ESSENTIAL` | `SKILL.md` Prohibited Scope |
| Honest "not evaluated" phrasing for unavailable metadata | `ESSENTIAL` | `SKILL.md` — prevents silent overclaiming |
| Never invent content for an unresolvable primary topic | `ESSENTIAL` | Both runtimes already implement this independently (agent-context resolution + `TopicNotFoundError`) — convergent evidence it's essential, not accidental |

### Target-specific elements (legitimately differ per runtime, do not force equivalence)

| Element | Classification | Reasoning |
|---|---|---|
| Content source format (`.aspx` live tenant vs. `.md` rendered file) | `TARGET_SPECIFIC` | Each runtime's native content representation; forcing one format onto the other would misrepresent what each runtime actually reads |
| Topic-resolution mechanism (agent-context vs. deterministic Python) | `TARGET_SPECIFIC` | Native runtime has no equivalent to a repo-local deterministic resolver; repository runtime has no live agent context to resolve against — each is the correct mechanism for its own environment |
| Related-topic-cap enforcement (context-adherence vs. code-enforced exception) | `TARGET_SPECIFIC`, **but flagged for Task 9** | Both achieve the same *intent* (≤2 related topics); the repository runtime's mechanism happens to be strictly stronger (code-enforced vs. behavioral). Not forcing the native runtime to somehow gain code-level enforcement it structurally cannot have (it doesn't own the SharePoint agent runtime's execution engine) — but Task 9's reuse-vs-specific decision should note this asymmetry explicitly rather than let it go unremarked. |
| Permission-model applicability | `TARGET_SPECIFIC` | Native runtime operates under real tenant identity/permissions; repository runtime has no tenant identity concept at all — this is a structural property of *where* each runtime executes, not a capability gap |
| Deployment/human-authorization mechanism | `TARGET_SPECIFIC` | Tenant deployment (manual UI/reviewed PnP script) vs. this repo's own code-review/merge process — both are "human-authorized," via the correct mechanism for each environment |

### Accidental elements (present in one runtime for incidental/historical reasons, not part of the shared intent)

| Element | Classification | Reasoning |
|---|---|---|
| Evaluation case filenames referencing `.aspx` extensions | `ACCIDENTAL` | An artifact of the cases having been authored for the native runtime first (Phase 4, before the repository runtime existed) — the underlying topic slug is what matters, not the extension. Task 5/6 should normalize this rather than propagate it as if it were meaningful. |

### Deferred elements (real, but out of this capability's current scope)

| Element | Classification | Reasoning |
|---|---|---|
| A third runtime (e.g. a different agent host, per Phase 3.0 §18's Teams cross-surface finding) | `DEFERRED` | No third real runtime exists yet — per spec Non-goals, "no speculative universal capability schema before two implementations exist." Revisit if/when a third runtime is built. |
| Formal drift-detection tooling comparing runtime outputs | `DEFERRED` | This is Task 8's own job, not Task 3's — noted here only to avoid Task 3 accidentally trying to solve it early. |

### Rejected elements

| Element | Classification | Reasoning |
|---|---|---|
| Requiring textually identical output between runtimes | `REJECTED` | Explicitly rejected by the design spec's own Non-goals ("No requirement that outputs be textually identical"). Different content formats and resolution mechanisms make textual identity neither achievable nor meaningful — semantic/intent equivalence is the actual target. |
| Forcing the native runtime to adopt code-level related-topic-cap enforcement to match the repository runtime | `REJECTED` (for now) | The native runtime does not own its own execution engine the way the repository runtime does — this would require capability the native-SharePoint-skill authoring surface doesn't currently expose. Not rejected as "wrong to want," rejected as "not achievable within this capability's current authoring surface" — a `DECISIONS NEEDED FROM A HUMAN` item if this is judged worth pursuing anyway (see Task 4 below). |

## Open item carried to Task 4 (adversarial review)

The one asymmetry worth an adversarial second look: is "behavioral, not code-enforced" really an
acceptable target-specific difference for the related-topic cap, or does it constitute an eroded
safety control on the native-sharepoint side that Task 4 should push back on? Task 3's own
classification leans toward "acceptable, structurally unavoidable" — but that conclusion was
reached by the same pass doing the classification, which is exactly the kind of self-confirming
reasoning Task 4 exists to challenge independently.
