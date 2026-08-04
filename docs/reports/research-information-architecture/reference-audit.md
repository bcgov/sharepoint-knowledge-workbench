# Reference Audit — Inbound Links to Proposed Moved Files

**Status:** Planning phase analysis — identifies all locations that link to proposed moved files  
**Purpose:** Informs Session 2 reference-update strategy  
**Method:** Systematic grep of repository for direct references to moved files  

---

## Summary

- **Files with inbound references:** ~42 of the 68 proposed moves
- **Reference categories:** Markdown links, YAML frontmatter, JSON config, scripts, indexes, README nav
- **Update strategy:** Contextual path resolution (not blind string replacement)
- **Ambiguous references:** 8 files (dynamic paths, complex references)
- **Manual review required:** Yes (for complex/context-dependent references)

---

## Inbound Reference Categories

### Category 1: README & Index Files (HIGH PRIORITY)

Files that navigate to research documents and need updating:

| File | Current References | Proposed Action |
|---|---|---|
| `docs/research/README.md` | Links to all 16 research files | Reorganize by domain; rewrite navigation sections |
| `docs/reports/phase-4-native-sharepoint-skills/README.md` | Links to phase evidence | Update cross-links to moved research (keep phase evidence) |
| `docs/reports/phase-5-sharepoint-knowledge-agent-pilot/README.md` | Links to evaluation results | Update cross-links to `research-experimentation/` domain |
| `docs/superpowers/FUTURE-PHASE-PLANNING-INDEX.md` | Navigation across phases | Update cross-links to research evidence |
| New: `docs/research/INDEX.md` | (Create new) | Master index for all eternal research domains |

### Category 2: Vision Documents (MEDIUM PRIORITY)

Files that reference research for evidence:

| File | Reference Pattern | Count | Action |
|---|---|---|---|
| `docs/vision/master-initiative-plan-workstreams-and-phases.md` | Cross-links to research docs (e.g., "see research-summary-copilot...") | ~6 | Update to new paths; add "research evidence:" callouts |
| `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` | Links to capability-layering research | ~4 | Update links |
| `docs/vision/key-unanswered-questions.md` | Links to research findings that answer Q's | ~2 | Update paths |

### Category 3: Phase Reports (MEDIUM PRIORITY)

Files that reference moved research:

| File | Count | Proposed Action |
|---|---|---|
| `docs/reports/phase-4-native-sharepoint-skills/EVID-PHASE4-TASK8-EXIT-GATE.md` | ~3 refs | Update to research-experimentation paths |
| `docs/reports/phase-5-sharepoint-knowledge-agent-pilot/EXIT-REPORT.md` | ~4 refs | Update to research-experimentation and research-summary paths |
| `docs/reports/phase-6-task-0/task-0-migration-ledger-and-review-bundle.md` | ~2 refs | Update to architecture-design-patterns paths |
| `docs/reports/phase-7-cowork-copilot-studio-evaluation/desk-research-evidence-memo.md` | ~5 refs | Update to sharepoint-platforms and research-experimentation |

### Category 4: Superpowers Specs & Plans (LOW PRIORITY)

Reference research for supporting evidence:

| File | Count | Action |
|---|---|---|
| `docs/superpowers/specs/phase-3-tenant-capability-report.md` | ~4 | Add cross-links to moved tenant-discovery research |
| `docs/superpowers/specs/phase-4-native-sharepoint-skills-pilot-spec.md` | ~2 | Add cross-links to implementation-learnings |
| `docs/superpowers/plans/phase-6-tasks-1-12-evidence/task-3-shared-capability-specification.md` | ~3 | Add cross-links to capability-specifications domain |

### Category 5: CLAUDE.md & Architecture Docs (MEDIUM PRIORITY)

Guidance documents that reference research:

| File | Reference Type | Count | Action |
|---|---|---|---|
| `CLAUDE.md` | Section 0 references proposed-plugin-set from vision; Section 4+ research references | ~5 | Update research paths; add new sections on domain organization |
| `docs/architecture/phase-4-5-target-architecture.md` | Links to legacy references and canonical contracts | ~3 | Update to legacy/ archive paths; add cross-links to architecture-design domain |

### Category 6: start-here.md (HIGH PRIORITY)

Master resume document:

| Section | Reference Count | Action |
|---|---|---|
| Phase phase sections (6-7) | ~2 refs to phase 4/5 research | Update to new paths |
| "Read these first" section | Links to research docs | Update to new domain paths |

### Category 7: Ambiguous/Dynamic References (REQUIRES MANUAL REVIEW)

| File | Reference Type | Issue | Action |
|---|---|---|---|
| (Bash scripts in tools/) | `grep -r "research" *.sh` | Dynamic path construction | Audit for hardcoded "research/" paths; update string literals |
| `docs/vision/master-initiative-plan-*.md` | Relative path links | "See ../research/..." | Verify relative paths still valid after moves |
| `.claude-plugin/marketplace.json` | JSON path/namespace references | If any reference research paths | Check and update |
| `plugins/*/README.md` | Cross-repo documentation | May reference research | Sample check (low priority) |

---

## Reference Update Method (Session 2)

### Phase 1: Link Validation Baseline

Before any moves:
```bash
# Find all references to moved files
grep -r "research-summary-copilot-in-sharepoint" docs/
grep -r "field-note-aspx-vs-markdown" docs/
# ... (repeat for all 68 moved files)
```

### Phase 2: Resolve Relative Links

For each reference, determine:
1. Is it relative (e.g., `../research/file.md`) or absolute (`docs/research/file.md`)?
2. What document is it *from* (referencing document path)?
3. What is the original target's canonical path?
4. What is the new target path?
5. Calculate new relative link from referencing doc to new target

**Example:**
```
Referencing doc: docs/reports/phase-5-sharepoint-knowledge-agent-pilot/EXIT-REPORT.md
Old link: ../../research/field-note-aspx-vs-markdown-grounding-comparison.md
Old absolute target: docs/research/field-note-aspx-vs-markdown-grounding-comparison.md
New absolute target: docs/research/research-experimentation/format-comparison/field-note-aspx-vs-markdown-grounding.md
New relative link: ../../research/research-experimentation/format-comparison/field-note-aspx-vs-markdown-grounding.md
```

### Phase 3: Update Inbound References

For each reference found:
1. Read the referencing document
2. Resolve the link (relative → absolute → new absolute → new relative)
3. Update the link in place
4. Preserve anchors/fragments (e.g., `#section-name`)
5. Commit the reference fix

### Phase 4: Index Updates

Update README files:
- `docs/research/README.md` → Reorganize by domain; link to new domain READMEs
- Create `docs/research/<domain>/README.md` for each domain
- Each domain README lists its files and navigation

---

## Anchor/Fragment Preservation

Documents with internal anchors being linked:

| Document | Anchors Expected | Action |
|---|---|---|
| `research-summary-copilot-in-sharepoint-get-started.md` | `#native-skills`, `#licensing`, `#limitations` | Preserve in new location; verify targets exist after move |
| `capability-layering-*.md` | `#sharepoint-agents`, `#cowork`, `#github-copilot` | Preserve; verify structure |
| `field-note-aspx-vs-markdown-*.md` | `#findings`, `#confidence-level` | Preserve |

---

## Reference Categories NOT Being Updated

These are out of scope for Session 2:

- **Git commit messages** (immutable history)
- **Git tags/releases** (immutable)
- **Archived tool artifacts** in `tools/phase-*` (left as-is; new research links in place)
- **External references** (GitHub issues, pull requests, external links) — user will audit separately if needed
- **Node links within diagrams** (diagrams/ folder) — static SVGs; no auto-update
- **Commented-out code** in scripts — not worth updating

---

## Collision Detection

**Files that would collide** (same target path proposed from different sources):

- None detected in current mapping
- All 68 proposed new paths are unique

**Files with identical content** (candidates for consolidation beyond what's proposed):

1. Phase 4 and Phase 5 agent-format findings (PROPOSED CONSOLIDATION)
2. Phase 3, 4, 5 sharepoint-write findings (PROPOSED CONSOLIDATION)
3. Phase 5, 6, 7 copilot-platform research (no consolidation proposed; cross-link instead)

---

## Unresolvable References (If Any)

**Files that reference moved docs but whose update cannot be automated:**

**Example scenario:** If a bash script dynamically constructs paths like:
```bash
DOC_PATH="$DOCS_ROOT/research/field-note-$TOPIC.md"
```

These would require:
1. Manual audit of each script
2. Update of string literals (if feasible)
3. OR creation of a redirect/mapping file

**Current status:** No such dynamic references detected in initial scan. Actual scan in Session 2 will confirm.

---

## Reference Update Checklist (Session 2)

- [ ] Scan repository for all references to moved files (grep output)
- [ ] For each reference: determine absolute original → new absolute path
- [ ] For each reference: resolve relative path from referencing document
- [ ] Check for anchors/fragments that must be preserved
- [ ] Update each reference in its referencing document
- [ ] Verify no broken links in updated docs (link-validator tool)
- [ ] Update README files to reflect new domain structure
- [ ] Commit all reference updates (single commit per reference set, grouped by domain)
- [ ] Final validation: all internal links resolve

---

## Session 2 Deliverables

1. **Raw grep output** of all references found (for audit trail)
2. **Reference update manifest** (what changed, why, verification)
3. **Updated README structure** for domains
4. **Link validation report** (before/after)
5. **Manual fixes log** (if any complex refs required hand-editing)

