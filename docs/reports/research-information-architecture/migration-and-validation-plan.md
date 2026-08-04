# Migration and Validation Plan — Session 2 Execution Blueprint

**Status:** Planning phase — specifies how Session 2 will execute the approved migration  
**Authorization:** Requires user approval of taxonomy and inventory before execution begins  
**Scope:** 68 file moves + 15 legacy archive + reference updates + validation  

---

## Phase 1: Pre-Migration Setup (Start of Session 2)

### Step 1.1: Verify Preconditions
```bash
# Confirm we're in correct worktree and branch
git branch -v  # Should show docs/research-information-architecture
pwd            # Should show .../sharepoint-knowledge-workbench/.worktrees/research-information-architecture

# Confirm no uncommitted changes
git status --short  # Should be empty (or only new discovery artifacts from Session 1)

# Confirm main is clean
git checkout main && git pull --ff-only origin main && git rev-parse HEAD
# Should match origin/main
```

### Step 1.2: Load Approved Manifest
- Read user-approved `research-path-migration.proposed.json` (Session 1 output)
- Verify 68 moves, 15 legacy archiving operations defined
- Load move list into migration script

### Step 1.3: Baseline Reference Scan
```bash
# For each of 68 files being moved, find all inbound references
# Output: raw grep results + analyzed reference map
python3 migration_tools/baseline_reference_scan.py \
  --manifest research-path-migration.proposed.json \
  --output reference-baseline.json
```

**Produces:** `reference-baseline.json` (all locations that link to moving files)

### Step 1.4: Validate Migration Manifest
```bash
python3 migration_tools/validate_manifest.py \
  --manifest research-path-migration.proposed.json
```

**Checks:**
- All `old_path` entries exist on disk
- No `new_path` collisions (two moves target same location)
- No file would be orphaned
- All paths are repository-relative (no `/Users/...`)
- `old_path` and `new_path` use POSIX forward slashes

**Output:** `validation-report-manifest.txt` (PASS/FAIL + issues)

---

## Phase 2: Execute File Moves (Session 2 Main)

### Step 2.1: Create Domain Directories
```bash
mkdir -p docs/research/sharepoint-platforms-capabilities/{sharepoint-agents,copilot-in-sharepoint,copilot-cowork,copilot-studio,content-permissions-governance}
mkdir -p docs/research/structured-content-engineering/{document-extraction-analysis,content-models-contracts,content-cleanup-chunking,multi-format-rendering,legacy}
mkdir -p docs/research/publication-delivery/{sharepoint-publishing,markdown-publishing,publication-lifecycle,multi-target-strategy,rendering-architecture}
mkdir -p docs/research/knowledge-discovery-retrieval/{agent-grounding,search-retrieval,knowledge-curation,human-ai-collaboration,citation-verification}
mkdir -p docs/research/capability-specifications/{native-sharepoint-skills,sharepoint-agents,hybrid-workflows,governance-policies}
mkdir -p docs/research/architecture-design-patterns/{plugin-architecture,skill-design-patterns,data-models,deployment-patterns}
mkdir -p docs/research/research-experimentation/{tenant-discovery,format-comparison,platform-evaluation,implementation-learnings,experiments-closed}
mkdir -p docs/research/strategic-planning-vision/{master-roadmap,capability-vision,initiative-governance,risk-analysis}
```

### Step 2.2: Move Files (Git-Aware)
```bash
python3 migration_tools/execute_migration.py \
  --manifest research-path-migration.proposed.json \
  --method git-mv \
  --commit-per-domain true \
  --output migration-execution-log.txt
```

**For each move:**
```bash
git mv <old_path> <new_path>
```

**Grouped commits** (one per domain):
```
git commit -m "docs(research-ia): move sharepoint-platforms docs to enduring research domain"
git commit -m "docs(research-ia): move structured-content-engineering docs to enduring research domain"
# ... etc
```

**Output:** 
- Executed moves recorded in git log
- Migration execution log with all operations
- `git status` should show all moves staged/committed

### Step 2.3: Archive Legacy Files
```bash
# Move docx-to-content legacy references
git mv docs/architecture/docx-to-content-legacy-references \
       docs/research/structured-content-engineering/legacy/docx-to-content

# Add README to legacy folder
cat > docs/research/structured-content-engineering/legacy/README.md << 'EOF'
# Legacy References

These documents are historical references from the docx-to-content plugin's initial design phase (before Phase 1). They are preserved for reference but are not current documentation.

For current structured-content-engineering guidance, see the parent directory's active documents.

**Why archived:** These predate the canonical-contract hardening (Phase 2) and plugin decomposition (Phase 4.5). They remain valid as historical context but are superseded by Phase 1+ implementation.

**Files:**
- canonical-contract.md
- content-authoring-guide.md
- extraction-triggers.md
- ... (full list)
EOF

git add docs/research/structured-content-engineering/legacy/README.md
git commit -m "docs(research-ia): archive docx-to-content legacy references with README"
```

---

## Phase 3: Update Inbound References

### Step 3.1: Reference Resolution
```bash
python3 migration_tools/resolve_references.py \
  --baseline reference-baseline.json \
  --manifest research-path-migration.proposed.json \
  --output reference-resolution-plan.json
```

**For each reference found:**
1. Determine original absolute path (resolve relative links)
2. Match against `old_path` in manifest
3. Calculate new absolute path from `new_path`
4. Recalculate relative link from referencing document to new target
5. Preserve anchors/fragments

**Output:** `reference-resolution-plan.json` with updates for each reference

### Step 3.2: Update References in Documents
```bash
python3 migration_tools/update_references.py \
  --resolution-plan reference-resolution-plan.json \
  --verify-links true \
  --output reference-updates-log.txt
```

**For each reference to update:**
1. Read referencing document
2. Locate reference (search by old_path pattern)
3. Replace with new relative link
4. Verify new link targets a valid file
5. Commit update

**Grouped commits** (by reference category):
```
git commit -m "docs(research-ia-refs): update research references in vision docs"
git commit -m "docs(research-ia-refs): update research references in phase reports"
git commit -m "docs(research-ia-refs): update research references in superpowers specs"
```

### Step 3.3: Update README Files

**Create domain README files:**
```bash
for domain in sharepoint-platforms-capabilities structured-content-engineering publication-delivery knowledge-discovery-retrieval architecture-design-patterns research-experimentation strategic-planning-vision; do
  cat > docs/research/$domain/README.md << 'EOF'
# [Domain Name]

[Description]

## Files

[Auto-generated listing of files in domain]

## Navigation

[Cross-links to related domains]

## Phase Provenance

See `.provenance.json` for phase-source metadata on each file.
EOF
done
```

**Update master index:**
```bash
cat > docs/research/INDEX.md << 'EOF'
# Research Knowledge Index

Navigate enduring research domains (organized by subject, not phase).

[Auto-generated navigation tree]

[Per-domain listings]
EOF
```

---

## Phase 4: Validation

### Step 4.1: Link Validation
```bash
python3 migration_tools/validate_links.py \
  --search-root docs/research docs/vision docs/reports docs/superpowers \
  --output link-validation-report.md
```

**Checks:**
- All markdown links resolve (files exist at targets)
- No broken anchors (targets have matching headers)
- No circular references
- No dangling references (old paths no longer exist)

**Output:** Link validation report (format: `.../target.md:line N: broken link`)

### Step 4.2: Hash Verification
```bash
python3 migration_tools/verify_move_hashes.py \
  --manifest research-path-migration.proposed.json \
  --baseline-hashes pre-migration-hashes.json \
  --output hash-verification-report.txt
```

**For each moved file:**
1. Calculate SHA256 before move (from baseline)
2. Calculate SHA256 after move at new location
3. Confirm they match (move-only, no content changed)
4. Report any mismatches

**Output:** Hash report (all moves verified or flagged)

### Step 4.3: Completeness Check
```bash
python3 migration_tools/verify_completeness.py \
  --manifest research-path-migration.proposed.json \
  --old-paths-should-not-exist docs/research \
  --new-paths-should-exist docs/research
```

**Checks:**
- All `new_path` files exist
- All `old_path` files no longer exist (or only redirect stubs)
- No orphaned files in research directories
- No unexpected files created

**Output:** Completeness report

### Step 4.4: Reference Audit
```bash
grep -r "docs/research/research-" docs/ tools/ | grep -v "Binary" > reference-audit-final.txt
# Manually scan for any lingering old paths
```

---

## Phase 5: Documentation and Closure

### Step 5.1: Produce Audit Report
```bash
cat > docs/reports/research-information-architecture/EXECUTION-REPORT.md << 'EOF'
# Research Information Architecture Migration — Execution Report

**Session:** 2  
**Date:** [Session 2 date]  
**Status:** COMPLETE

## Summary

- **Files moved:** 68
- **Files archived:** 15 (legacy)
- **References updated:** [count from log]
- **Links validated:** [count]
- **Hash mismatches:** [count] (should be 0)
- **Manual fixes required:** [count]

## Moves Executed

[Table: old_path | new_path | commit hash | status]

## References Updated

[Table: referencing_file | old_ref | new_ref | commit_hash]

## Validations Passed

- ✅ All moved files exist at new locations
- ✅ All old locations empty or redirect stubs
- ✅ All hashes match (move-only, no content loss)
- ✅ All internal links resolve
- ✅ No broken anchors
- ✅ No orphaned files

## Blockers Encountered

[List any issues, how resolved]

## Manual Fixes Applied

[List any hand-edits required outside automation]

## Next Steps

1. User verification of moved content
2. External reference audit (GitHub links, etc.) — separate session
3. Announcement of new research navigation structure

EOF
```

### Step 5.2: Create Redirect Stubs (Optional)

If external references to research docs are expected:
```bash
# For each moved file, optionally create a redirect stub at old location
cat > docs/research/research-summary-copilot-in-sharepoint-get-started.md << 'EOF'
# MOVED

This document moved to:
`docs/research/sharepoint-platforms-capabilities/copilot-in-sharepoint/research-copilot-in-sharepoint-preview.md`

[Auto-redirect or manual link]
EOF
```

**Decision:** User decides whether to retain redirect stubs or delete old paths entirely.

### Step 5.3: Final Verification
```bash
# Confirm git state
git log --oneline -20  # Should show all IA migration commits
git status --short     # Should be empty
git diff --stat origin/main..HEAD  # Shows all changes
```

### Step 5.4: Commit to Branch and Push
```bash
git push -u origin docs/research-information-architecture
```

---

## Rollback Plan (If Needed)

If any validation fails and rollback is needed:

```bash
# Hard reset to pre-migration state
git reset --hard <commit-before-migrations>

# Verify restored
git status --short  # Should show only Session 1 discovery artifacts
```

**What triggers rollback:**
- Validation shows broken links that can't be fixed
- Hash mismatches detected (indicates content corruption)
- Unresolvable reference issues (>10% of references)
- Collision detected (two moves to same path)

**Escalation:** If rollback needed, report issues to user and iterate.

---

## Execution Timeline (Estimated)

| Phase | Task | Time |
|---|---|---|
| 1.1-1.4 | Setup, baseline scan, validation | 15 min |
| 2.1-2.3 | Create dirs, execute 68 moves, archive legacy | 10 min |
| 3.1-3.3 | Resolve references, update docs, create READMEs | 30 min |
| 4.1-4.4 | Link validation, hash verify, completeness, audit | 20 min |
| 5.1-5.4 | Produce reports, redirect stubs, push | 15 min |
| **Total** | | **~90 minutes** |

---

## Success Criteria

By end of Session 2:

- ✅ All 68 files moved to enduring research domains
- ✅ 15 legacy files archived with README
- ✅ All inbound references updated and validated
- ✅ New domain README files created and populated
- ✅ Master research index created/updated
- ✅ Hash verification shows all moves are content-identical
- ✅ Link validation report shows 0 broken links
- ✅ Execution report documents all changes
- ✅ Branch pushed and ready for merge review

---

## Appendix: Tools Required

### Temporary Python Scripts (Session 2 Only)

1. `baseline_reference_scan.py` — Find all references to moved files
2. `validate_manifest.py` — Pre-migration manifest validation
3. `execute_migration.py` — Execute git mv in correct order
4. `resolve_references.py` — Calculate updated link paths
5. `update_references.py` — Apply reference updates to files
6. `validate_links.py` — Post-migration link checker
7. `verify_move_hashes.py` — Content integrity verification
8. `verify_completeness.py` — File organization audit

**All tools:** Designed to be run once; delete after session if ephemeral artifacts, retain in `tools/migration/` if reusable.

---

## Deviations from Standard Pattern

**Why Session 2 is different from typical git workflows:**

1. **Grouped moves per domain** rather than per-task commits — reduces commit count and makes domain structure clear
2. **Reference updates after all moves** rather than per-file — ensures all new paths exist before updates
3. **Link validation mandatory before completion** — research is discoverable only if links work
4. **Hash verification required** — proves no content was lost or corrupted during moves
5. **Redirect stubs optional** — depends on whether external links are expected

---

## Next Session (Session 3)

Once Session 2 completes and branch is merged:

1. User verifies new domain structure in main
2. External reference audit (if GitHub links to research exist)
3. Announcement of new navigation structure
4. Optionally: create cross-domain linking/tagging for research discoverability

