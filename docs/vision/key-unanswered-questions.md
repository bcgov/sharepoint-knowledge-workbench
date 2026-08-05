# Key Unanswered Questions
The biggest things still underexplored are the **operating model after conversion** and the difference between a **heading, a reusable topic, a publication, and an official record**.

The most important overlooked question is:

> **What is the stable unit of knowledge, and how are those units assembled into manuals, procedures, training, and other publications?**

A heading is not automatically a knowledge unit. A file is not automatically a publication. A publication is not automatically the source of truth.

## 1. What is the actual unit of knowledge?

The current CEIS proposal risks creating one canonical file for every heading—159 files. Technically stable IDs do not prove those are sensible authoring units.

A good topic should usually:

* address one subject or user question;
* make sense with enough context;
* be maintainable without pulling together fragments from many files;
* remain reusable where reuse provides real value;
* preserve procedural cohesion.

DITA’s topic model explicitly distinguishes topic identity from publication hierarchy: topics are authoring and reuse units, while maps assemble those topics into hierarchies and deliverables. It also says a topic should generally be short enough to address one subject but long enough to make sense on its own. 

Ask:

* What qualifies as a standalone topic?
* Can a heading remain inside a parent topic without becoming a file?
* What is the minimum useful topic size?
* When should child sections remain together?
* Do warnings, examples, expected results, and troubleshooting belong with their procedure?
* Who decides topic boundaries—the algorithm, author, or information architect?
* Can topic boundaries change without breaking permanent identifiers?

**Recommendation:** Make “topic suitability” separate from heading-anchor detection.

***

## 2. Where is the assembly or map layer?

You need something analogous to a publication map:

```text
Canonical topic library
        ↓
Manual assembly
Procedure assembly
Training assembly
Quick-reference assembly
        ↓
Destination renderers
```

Without an assembly layer, the canonical folder hierarchy may become an accidental replacement for the original Word document hierarchy.

Ask:

* Can one topic appear in more than one manual?
* Can topics be ordered differently for different audiences?
* Can a training package reuse procedure topics without copying them?
* Can a manual include a topic by reference?
* Can one topic be excluded from a public output but included internally?
* Does the manifest describe storage, one publication, or both?
* Can there be multiple publication manifests over the same canonical topics?

Structured-authoring practice emphasizes modularity, information typing, reuse, and producing multiple deliverables from a single source. 

**Recommendation:** Eventually separate:

```text
topic manifest = what canonical topics exist

publication map = which topics form this deliverable, in what order

renderer profile = how that deliverable is presented
```

***

## 3. What happens after migration when someone changes the original Word file?

This is a major lifecycle question.

After cutover, decide whether Word is:

* retired as authoring source;
* retained only as historical evidence;
* still accepted as an update source;
* or periodically re-imported.

Ask:

* What happens if someone edits the old Word manual after canonical cutover?
* Can a later DOCX import overwrite canonical edits?
* How does the system distinguish a migration from an update?
* Is re-import a three-way reconciliation among original source, current Word, and current canonical content?
* When is the Word source formally frozen?
* How is the cutover communicated?
* What prevents two active sources of truth?

**Recommendation:** Once canonical content is accepted, ordinary DOCX conversion should not overwrite it. Future import should be a deliberate reconciliation workflow.

***

## 4. How will content changes be triggered by system or policy changes?

Should documentation be reviewed after system updates and business-process changes, and that impact assessment should determine documentation, communication, and training needs. 
Ask:

* How does an application change identify affected topics?
* Can source-code changes, release notes, Jira items, or policy changes link to content IDs?
* Who decides whether a change needs:
  * manual updates;
  * training updates;
  * quick-reference updates;
  * communications?
* Can the pipeline show all publications using an affected topic?
* Can a release be blocked when required documentation remains stale?

This is where the system becomes a knowledge-management pipeline rather than a publishing tool.

***

## 5. Who owns, reviews, approves, publishes, and retires content?

What is the target governance model?

Assigning documentation owners and ensuring content remains accurate and maintained. Distinguish accountable roles for business-process, user, architecture, technical, operational, and security documentation and approach for tandardized templates, plain language, accuracy, assigned owners, collaboration, access restrictions, and links between knowledge and training. 

Ask:

* Who can author?
* Who is accountable for accuracy?
* Who approves policy content?
* Who can publish?
* Who can accept validation warnings?
* Who can retire content?
* Who owns shared reusable content?
* What happens when the owner leaves?
* What review intervals differ by knowledge type?
* What constitutes substantive versus editorial change?
* Which changes require reapproval?

Define a lifecycle such as:

```text
draft
→ in review
→ approved
→ published
→ superseded
→ retired
→ archived
```

Do not overload `status: draft` with every governance meaning.

***

## 6. Is reuse by reference or by copying?

Reuse sounds attractive but can become dangerous.

Ask:

* Is reusable content included by reference or copied?
* If included by reference, do all publications receive updates immediately?
* Can one publication pin a topic version?
* What if two audiences require slightly different wording?
* When do variants become separate topics?
* How are conditional variants governed?
* Who owns a shared warning or legal statement?
* How do reviewers understand the blast radius of changing reused content?

Structured-content guidance warns that reuse without clear governance, metadata, ownership, and lifecycle controls can produce duplicate or conflicting components and reduce trust. 

**Recommendation:** Do not implement broad reuse until you define:

```text
reference
version pinning
variant policy
impact analysis
ownership
retirement
```

***

## 7. What metadata is authoritative, controlled, or derived?

You have author front matter and machine sidecars, which is good. But metadata governance still needs definition.

Ask:

* Which fields use controlled vocabularies?
* Who can create a new content type, audience, status, or topic category?
* Is `owner` a person, position, team, or durable organizational identifier?
* What happens when teams are renamed?
* Which metadata is inherited from a publication map?
* Which metadata is calculated?
* Which metadata can be overridden?
* How are sensitivity, records classification, language, jurisdiction, and review date represented?
* How do schemas evolve without invalidating old content?

Internal governance material stresses common models, data stewards, version history, auditability, integrity, and issue-resolution processes. 

**Recommendation:** Add a metadata dictionary before expanding beyond the pilot.

***

## 8. How are records management and archival handled?

Canonical content may become an official record, while Git history, rendered documents, and publication packages may each have different retention value.

Ask:

* What is the official record:
  * approved canonical source;
  * signed PDF;
  * published SharePoint output;
  * approval record;
  * release package?
* Which artifacts are transitory?
* What retention schedule applies?
* Is Git history an operational history or an official record?
* How are legal holds handled?
* How are superseded versions retained?
* Can content be deleted from Git when retention expires?
* How are media assets disposed of?
* How is final approval preserved outside a mutable repository?

Your internal records notes identify the need to distinguish transitory from final information, classify content, choose appropriate storage, and define destruction models. 

This should be addressed before calling the repository the permanent enterprise system of record.

***

## 9. What is the security and access model at topic level?

Breaking one protected manual into many topics can unintentionally alter its security boundary.

Ask:

* Are all topics in one manual subject to the same classification?
* Can one topic be more sensitive than its parent publication?
* Can a less-protected output accidentally include a sensitive reused topic?
* Can generated indexes expose titles of restricted content?
* Can Copilot retrieve sensitive topics based on inherited permissions?
* Are media files protected identically to their topics?
* Can publication maps cross access boundaries?
* Are exports labelled appropriately?
* Do diagnostic artifacts contain sensitive content?
* Are temporary extractions deleted or protected?

Internal governance examples emphasize classification, ownership sign-off, access controls, audit logs, and documented data-sharing decisions. 

Also add ingestion controls for:

* malicious DOCX content;
* embedded files;
* macros;
* external links;
* oversized media;
* unsafe paths;
* decompression bombs.

Your internal security assessment guidance specifically calls for approved file types and sizes, malware scanning, quarantine, sandboxed rendering, and restricted active content. 
***

## 10. Is accessibility validated at the canonical layer or only after rendering?

Accessibility should start with authoring structure, not only output checking.

Ask:

* Are headings meaningful and sequential?
* Is meaningful alt text mandatory?
* How are decorative images identified?
* How are complex tables described?
* Do links make sense outside surrounding text?
* Are acronyms expanded?
* Is document language recorded?
* Are warnings distinguishable without colour?
* Do audio outputs have transcripts?
* Do video outputs have captions and descriptions?
* Is reading order verified in PDF, PowerPoint, HTML, and SharePoint outputs?
* Is the authoring interface itself accessible?

W3C guidance says headings, paragraphs, lists, and meaningful sequence help users orient, understand, and navigate content; authoring tools should also help authors create accessible content. 

**Recommendation:** Define accessibility rules in both:

```text
canonical validation
and
renderer-specific validation
```

***

## 11. How are links and identities preserved over years?

Stable chunk IDs are a good start, but URLs and references also need lifecycle rules.

Ask:

* What happens when a topic title changes?
* What happens when one topic splits into three?
* What happens when three topics merge?
* Are old IDs retained as aliases?
* Can renderers create redirects?
* Can external systems reference canonical IDs rather than filenames?
* How are retired topics represented?
* How are inbound links discovered before restructuring?
* How are cross-repository references validated?
* Is identity global, repository-local, or publication-local?

You need operations such as:

```text
rename without identity change
split with predecessor links
merge with successor links
retire with replacement
redirect old publication path
```

Without this, the model may improve authoring while creating link rot.

***

## 12. How will localization and multi-jurisdiction variants work?

Even if translation is not immediate, the model should avoid making it impossible.

Ask:

* Is language metadata required?
* Are IDs shared across language variants?
* Can translations pin to a source version?
* How does a translator know which topics changed?
* Are screenshots language-specific?
* Can one policy have jurisdiction-specific requirements?
* Are variants separate topics or conditional content?
* How are translation status and approval tracked?

Do not implement localization now, but reserve the metadata and identity model.

***

## 13. What is the schema-evolution policy?

The canonical contract is versioned, but contract evolution needs operational decisions.

Ask:

* Who can release schema version 1.1 or 2.0?
* Are migrations automatic or reviewed?
* Can old renderers consume newer packages?
* Can newer renderers consume older packages?
* Are migrations reversible?
* Is schema migration separate from content modification?
* Are package and content versions different?
* How long are old schema versions supported?

A schema version field without a compatibility policy postpones the problem rather than resolving it.

***

## 14. What are the quality metrics?

“Conversion passed” is not enough.

Measure at least:

### Migration quality

* content coverage;
* media preservation;
* link validity;
* structural anomalies;
* unresolved warnings;
* human corrections required.

### Operating quality

* stale-topic count;
* overdue reviews;
* orphan topics;
* broken links;
* duplicated content;
* ownerless content;
* unpublished approved changes;
* renderer failures.

### Business value

* effort to make a representative change;
* review effort;
* publishing effort;
* number of outputs produced without duplicate editing;
* defect rate;
* author satisfaction;
* reader findability;
* answer quality for knowledge-grounded agents.

AI-generated structured documentation should be treated as a hypothesis rather than a fact, particularly where exceptions and compliance rules are involved.

***

## 15. What is the rollback and disaster-recovery model?

Ask:

* Can a bad publication be rolled back immediately?
* Can canonical content be restored independently from rendered outputs?
* Are release artifacts reproducible from a Git tag?
* Are media files versioned with the content?
* What happens if a renderer version changes the output unexpectedly?
* Can you reproduce exactly what users saw on a given date?
* Are dependencies and templates version-pinned?
* Is there a signed or hashed release manifest?

Your current hashes and atomic promotion are strong foundations, but the release model should identify:

```text
content version
schema version
template version
renderer version
publication-map version
release identity
```

***

## 16. What trust boundary applies to AI-assisted edits?

Ask:

* Which transformations can AI propose?
* Which can be applied deterministically?
* Who approves substantive rewriting?
* Must every AI rewrite retain source provenance?
* How are omissions detected?
* Can an AI classify requirements as guidance incorrectly?
* How are prompt, model, and tool versions recorded?
* Can deterministic and AI-generated changes be distinguished in review?
* Is protected content permitted in the chosen model/service?
* What is the fallback when model output is inconsistent?

Internal AI-governance material emphasizes documenting human involvement, roles, authorities, limitations, and changes in accuracy. 

Use transformation classifications such as:

```text
deterministic cleanup
structural move
AI-proposed rewrite
AI-proposed classification
human-authored change
generated derived element
```

**Tenant-tested evidence added 2026-08-03 (Phase 5 Task 7/8):** on the "model output is
inconsistent" question specifically —
`docs/research/knowledge-discovery-retrieval/field-note-aspx-vs-markdown-grounding.md` documents a real, reproducible
case: two live SharePoint Copilot agents, unmodified, asked the identical cross-topic-relationship
question twice each, gave a hedged/declined answer on the first run and a confident-but-mutually-
contradictory answer on the second (across both agents independently). The same evidence also shows
agents inferring "currency" from SharePoint file-upload timestamps rather than authored review
metadata when no real currency signal exists — a concrete example of the "can an AI classify
requirements as guidance incorrectly" and "what is the fallback when model output is inconsistent"
risks this section already names, not yet a proposed answer to either.

