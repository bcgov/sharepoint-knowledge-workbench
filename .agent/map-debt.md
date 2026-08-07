
### [2026-07-30] PnP.PowerShell Tenant Upload Friction & Execution Discipline Failure

- **Logged Date**: 2026-07-30
- **Artifact Affected**: `tools/phase-3-sharepoint-discovery/run-phase3-tenant-pilot.ps1` and agent execution rules
- **Friction Observed**: 
  1. `Set-PnPPage -Values` is invalid syntax in PnP.PowerShell for custom page metadata (must use `Set-PnPListItem` with item ID).
  2. `Add-PnPPage` fails with "already exists" on rerun unless existence check and update logic are implemented.
  3. `& pandoc` output returns a string array in PowerShell, breaking `Add-PnPPageTextPart -Text` unless joined with `-join "`n"`.
  4. `Resolve-PnPFolder` fails with `Access Denied` on custom Document Libraries (must use `Add-PnPFolder -Name "media" -Folder "LibraryName"` instead).
  5. PnP list binding divergence: SharePoint list Title (`CEIS-Pilot-Knowledge`) vs URL path (`CEISPilotKnowledge`) caused target mismatches until explicit lookup fallback was implemented.
  6. **BEHAVIORAL FAILURE**: Agent repeatedly rushed broken script iterations to the user without doing full line-by-line file verification, failing to read explicit user instructions regarding target paths (`CEISPilotKnowledge`).
- **Prevention Rules (Hard Enforcement)**:
  - **Full-File Audit Gate**: Before asking the user to run any generated script, the agent MUST view the full file content (`view_file`), audit every variable, and verify parameter signatures against authoritative docs.
  - **Instruction Match Verification**: Explicit user inputs (URLs, paths, folder names, library titles) MUST be grep-checked against all script variables before claims of fix completion.
  - **Zero Guessing on PnP API**: PnP.PowerShell cmdlet options must never be inferred; test/verify parameter types locally before outputting instructions.
- **Evidence**: `run-phase3-tenant-pilot.ps1` commits `4323198`, `a530de0`, `65ef41f`, `55a9099`, `dbde503`, `6fd27c2`, `2ca5e76`, `0774cf3`, `97615da`.
- **Severity**: H
- **Repeat**: NO
- **Status**: RESOLVED

### [2026-08-01] Phase 4.5 Wave 6 — `build_wheel()` Alphabetical-Last-Wheel Bug in Combined-Install Harness

- **Logged Date**: 2026-08-01
- **Cycle/Session**: Phase 4.5, Waves 4-8 execution session
- **Artifact Affected**: `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py::build_wheel`, `tools/phase-4-5-core-plugin-refactoring/combined_install_check.py`
- **Friction Observed**: `build_wheel(project_dir, dist_dir)` picks `sorted(dist_dir.glob("*.whl"))[-1]` — correct when called once per fresh `dist_dir`, but `combined_install_check.py` called it four times into ONE shared `dist_dir` (once per plugin). After the first call, every subsequent call's `glob` saw all wheels built so far and picked the alphabetically-LAST one across all of them (`source_document_extraction-...` always won), so three of the four "wheels" installed were actually duplicate copies of the same one plugin. The resulting combined install silently had only one real plugin's code, plus three mismatched dist-info records — surfaced as `ModuleNotFoundError` for bare names that were obviously present in the source tree, which took real debugging to trace back to the wheel-selection logic rather than an actual plugin bug.
- **Why it wasn't caught by any single-plugin isolated-install run**: `isolated_install_check.py` was only ever invoked with a fresh, empty `dist_dir` per call (once per plugin, in its own `tempfile.TemporaryDirectory()`), so the bug in `build_wheel`'s selection logic was latent and untriggered until Wave 6 introduced the first caller that reused one `dist_dir` across multiple `build_wheel` calls.
- **Fix**: `combined_install_check.py` now builds each plugin's wheel into its own `dist_dir / "dist" / <plugin-name>` subdirectory, never a shared one. `build_wheel` itself was left unchanged (still correct for its original single-call-per-directory contract) rather than patched to track "the wheel I just built" — the caller-side fix is simpler and matches how `isolated_install_check.py` already used it correctly.
- **Evidence**: repro'd via a persistent (non-tempfile) dist dir showing all four `build_wheel()` calls returning `source_document_extraction-0.1.0a1-py3-none-any.whl`; fix verified by re-running `combined_install_check.py` and confirming all four plugins' own bare modules import correctly post-install.
- **Severity**: M
- **Repeat**: NO (fixed at the one call site that could trigger it; no other caller reuses a shared `dist_dir`)
- **Status**: RESOLVED

### [2026-08-01] Phase 4.5 Wave 8 — `sharepoint_*.py` Outside the Migration's Known File Inventory

- **Logged Date**: 2026-08-01
- **Cycle/Session**: Phase 4.5, Wave 8 execution
- **Artifact Affected**: `plugins/docx-to-content/scripts/sharepoint_{cli,dry_run,package,reconcile}.py` (Phase 3's real, tenant-verified SharePoint publication tooling)
- **Friction Observed**: Wave 8's plan step was a literal `git rm -r plugins/docx-to-content/`. Before executing it, a full-directory listing (per the new Hard Gate #13 this session added) surfaced four `sharepoint_*.py` scripts and their tests that were never part of the four-plugin Known File Inventory from Wave 0/1 — `sharepoint-publication` is explicitly listed as deferred/out-of-scope in `CLAUDE.md`. A literal wholesale deletion would have destroyed working, tenant-tested code with no migration path.
- **Why it wasn't caught earlier**: the Known File Inventory was built once, early (Wave 0), scoped to the four domains being extracted; it was never re-diffed against the directory's actual full contents at the point of final deletion, seven waves later.
- **Fix**: flagged to the user before deleting anything (via `AskUserQuestion`); user chose to relocate. The four scripts, their four test files, and one doc file were `git mv`'d wholesale to a new `plugins/sharepoint-publication/` holding location (given its own minimal `.claude-plugin/plugin.json`/`plugin.yaml` and README documenting its provisional, not-yet-decomposed status) before the rest of `docx-to-content/` was removed. Non-contract reference docs/templates with no per-plugin home were relocated to `docs/architecture/docx-to-content-legacy-references/` the same way, rather than deleted.
- **Evidence**: `docs/superpowers/plans/phase-4-5-evidence/wave-8-removal-gate-checklist.md`, `docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`, commit `82c92b7`.
- **Severity**: H (would have been an unrecoverable-in-the-working-tree loss of real, tenant-verified functionality, recoverable only via git history archaeology)
- **Repeat**: NO (new Hard Gate #13 in `self-evolution-policy.md` makes this check mandatory before any future wholesale directory deletion)
- **Status**: RESOLVED

### [2026-08-01] Phase 4.5 Wave 8 wrap-up — Marketplace/plugin.json Gap Not Investigated Until User Repeated the Instruction

- **Logged Date**: 2026-08-01
- **Cycle/Session**: Phase 4.5 Wave 8 wrap-up
- **Artifact Affected**: `.claude-plugin/marketplace.json` (repo root, did not exist), `plugins/sharepoint-publication/.claude-plugin/plugin.json` (did not exist)
- **Friction Observed**: User said "remember at end of these phases you might need to update marketplace.json, use the marketplace manager skill." The agent manually `grep`'d for `marketplace.json` instead of invoking the actual `manage-marketplace` skill, concluded "not needed" from that manual proxy check, and reported that conclusion as final. The user had to say "i know what it's for" and then explicitly "create the marketplace file" before the real work happened — the agent's own conclusion was substituted for the user's stated intent instead of being used as one input alongside it.
- **Fix**: ran the actual `manage-marketplace` skill this time (not a manual proxy), created `.claude-plugin/marketplace.json` listing all real plugins, validated with `claude plugin validate .`, and added the missing `plugin.json`/`plugin.yaml` for `sharepoint-publication` (the one plugin that didn't have one) once the user pointed out only 4 of 5 plugins had been covered.
- **Evidence**: `.claude-plugin/marketplace.json`, `plugins/sharepoint-publication/.claude-plugin/plugin.json`, `plugins/sharepoint-publication/plugin.yaml`.
- **Severity**: S
- **Repeat**: NO (new Hard Gate #14 in `self-evolution-policy.md`)
- **Status**: RESOLVED

### [2026-08-02] Phase 4/5 — Reusable SharePoint Capability Written Into `tools/phase-N-*` Instead of an Already-Designed Plugin

- **Logged Date**: 2026-08-02
- **Cycle/Session**: Phase 4 native-skills work (prior session) + Phase 5 CEIS grounding prototype (this session)
- **Artifact Affected**: `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` (a real skill implementation, not phase evidence); `tools/phase-5-sharepoint-knowledge-agent-pilot/{upload-rendered-markdown.ps1, backup-existing-agents.ps1, backup-skills-and-templates.ps1}` (agent creation/backup, native-skill backup, content upload — all reusable operational capability).
- **Friction Observed**: `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` (lines ~230-269) already proposes a plugin named `sharepoint-knowledge` with skill groups explicitly named `native-skills/`, `agents/`, `deployment/`, `governance/`, `health/` — exactly the destination for this capability. The agent never read this document before or during either phase's execution, and instead (a) let a real skill implementation live inside a `tools/phase-4-*` folder, then (b) repeated the same mistake in Phase 5 by writing three new reusable `.ps1` scripts directly into `tools/phase-5-*` rather than checking the vision's plugin boundary first. When the user first raised it ("why are there skills inside tools/..."), the agent produced an inventory/migration-analysis document but proposed *inventing new plugin names* (`sharepoint-agents`, `sharepoint-native-skills`, `workbench-setup`) rather than checking whether the vision had already named the correct one — confirming the check still hadn't happened even after being directly prompted twice. Only stopped, and the real cause named, on the user's third direct challenge ("do you not understand the purpose of this repo and architecture even now?").
- **Why it wasn't caught earlier**: no step in this session's (or the referenced prior session's) workflow included "check `docs/vision/` for an existing plugin-boundary decision" before creating a new script or skill file. The `tools/phase-N-*` convention was inherited from earlier sessions and treated as settled precedent rather than re-checked against the vision each time new capability was added.
- **Fix**: **DESIGN_COMPLETE.** The domain and plugin name are now decided —
  `sharepoint-agents-and-skills` (not `sharepoint-knowledge`, rejected as too vague; not split
  into two plugins). Full migration design: `docs/superpowers/specs/
  2026-08-02-sharepoint-agents-and-skills-plugin-design.md` — final artifact disposition matrix,
  plugin tree, skill list, script parameter matrix, phase-wrapper strategy, evidence-preservation
  strategy, and 6 migration waves. **IMPLEMENTATION_NOT_AUTHORIZED. MIGRATION_NOT_STARTED.** Reusable
  agent/native-skill capability (`review-manual-topics/SKILL.md` and the scripts/backups listed in
  Artifact Affected above) is still mixed with Phase 3-5 phase evidence in `tools/`, unresolved
  until a migration wave is separately authorized and executed. New rule added (see `CLAUDE.md`
  Section 0): before creating any new script/skill file for SharePoint-facing capability, or before
  proposing a plugin name for a migration, read the vision doc's proposed-plugin-set section (and
  now this design doc) first.
- **Evidence**: this session's transcript; `docs/reports/multi-document-destination-config/{script-inventory-and-plugin-migration-candidates.md, complete-artifact-classification.md}` (the full artifact-level evidence inventory, still valid and reused by the design doc); `docs/superpowers/specs/2026-08-02-sharepoint-agents-and-skills-plugin-design.md` (the accepted domain model).
- **Severity**: M (no data loss or tenant damage, but real rework risk and repeated user correction across two phases)
- **Repeat**: YES — happened in Phase 4, then again in Phase 5 within the same architecture area. Per the aging rule, must escalate immediately on next encounter, not be deferred a third time.
- **Status**: OPEN (design complete; do not mark RESOLVED until a migration wave actually executes — see the design doc's Section 7)

### [2026-08-03] Phase 6 Task 0.17 — `workbench-setup` Wrongly Assigned Cross-Repository Ownership, Then Executed On Before the User Caught It

- **Logged Date**: 2026-08-03
- **Cycle/Session**: Phase 6 Task 0.16 wrap-up → Task 0.17 start (same session)
- **Artifact Affected**: `start-here.md`, `docs/superpowers/plans/phase-6-multi-runtime-capability-model-plan-scaffold.md` (Task 0.17 section), `docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md` (Section 8), `docs/superpowers/plans/2026-08-02-multi-document-destination-configuration.md`, `docs/architecture/complete-plugin-skill-catalog-after-phase-9.{json,md}` (`workbench-setup`'s `authoring_constraint` field) — all wrongly stated `workbench-setup`'s three skills must be authored in the sibling `agent-plugins-skills` monorepo as "Category 1 (marketplace-style)" skills, per `CLAUDE.md`'s Skill Development Protocol. A `git worktree`/branch was actually created in `agent-plugins-skills` under this wrong premise before the user caught it (3 untracked `.psd1.example` files, never committed/pushed — cleaned up, that repo otherwise unaffected, verified via `git status`/`git log` before and after cleanup).
- **Friction Observed**: the user's actual, prior instruction was to **use** the `marketplace-manager` skill (installed *from* `agent-plugins-skills` into this repo's `.agents/skills/`) as the *procedure/tool* for the applicable `marketplace.json` registration step — not to author `workbench-setup`'s plugin code *inside* `agent-plugins-skills`. The agent (in an earlier planning pass, not caught during the user's own plan review either) conflated "this skill's source-of-truth repo" with "where a plugin using/consulting that skill's procedure must itself be authored," and inserted the wrong conclusion into the Phase 6 plan as a stated cross-repository authoring constraint. That wrong constraint then survived unchallenged through plan review and start-here.md handoffs until this session began actually executing it (creating the worktree, generating the three canonical `.psd1.example` templates there) before the user interrupted and corrected it directly.
- **Why Hard Gate #14 did not prevent this**: gate #14 ("Don't Self-Conclude 'Not Needed' on a Capability the User Named Unprompted") covers the *inverse* failure — ignoring or dismissing a named capability. This incident is a different, related failure in the same conceptual area: correctly recognizing the named capability (`marketplace-manager`) but **misattributing its scope** — treating "consult skill X's procedure" as "adopt skill X's repository as this new plugin's home." Gate #14's check ("did I run the actual tool instead of a manual proxy") does not catch a scope-misattribution error, only a dismissal error.
- **Fix**: added Hard Gate #15 to `self-evolution-policy.md` (see below) generalizing this distinction — a named skill/tool's own source repository is never, by itself, evidence for where a *different* artifact (a new plugin, a new file, a new capability) that merely *uses* that skill must be authored. Corrected every false ownership statement listed under Artifact Affected above (each now carries an explicit correction record naming this incident), deleted the stray `agent-plugins-skills` worktree/branch, and confirmed via `git status`/`git log` that no other file in that sibling repo was touched.
- **Evidence**: this session's transcript (the user's exact correction message); commit `c8275c4` ("docs: correct false workbench-setup cross-repository ownership claim") in `sharepoint-knowledge-workbench`.
- **Severity**: M (no tenant/data impact, no code shipped under the wrong premise — but a real architecture-plan error that survived one full human plan review before being caught, plus wasted a session-start on the wrong repo)
- **Repeat**: NO (new Hard Gate #15 in `self-evolution-policy.md`)
- **Disposition of the wrong-repository attempt**: `ABANDONED_WRONG_REPOSITORY`.
- **Status**: RESOLVED

### [2026-08-03] Phase 6 native-runtime evaluation prep — `reconcile-deployed-skill.ps1` Falsely Reported Zero Deployed Skills

- **Logged Date**: 2026-08-03
- **Cycle/Session**: Phase 6 remediation round 2 — native-sharepoint runbook prep (live tenant verification)
- **Artifact Affected**: `plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1`
- **Friction Observed**: ran this existing, previously-untested-live script against the real tenant (`AG-CSB-INTRANET-DEV`) to verify the `review-manual-topics` deployment precondition before running Phase 6's native-runtime evaluation cases. It reported `DISPOSITION: TASK_8_NO_SKILLS_DEPLOYED` — zero skill folders found in `AgentAssets/Skills/`. This was reported to the user as fact. The user pushed back ("you are wrong") and provided a screenshot showing `AgentAssets/Skills/` actually contains two real folders (`ceis-test-skill`, `review-manual-topics`, both modified 3 days prior). The script was wrong, not the tenant — a false-negative live-tenant read that was initially reported as ground truth without the skepticism it deserved for a script that had never actually been run against a live tenant before (only ever exercised, if at all, as inert code).
- **Root causes, three real bugs found by direct cmdlet investigation, not guessing**:
  1. `Get-PnPFolderInFolder -FolderSiteRelativeUrl` was passed a SERVER-relative path (built from `$agentAssetsLib.RootFolder.ServerRelativeUrl`, e.g. `/sites/AG-CSB-INTRANET-DEV/AgentAssets/Skills`) but that parameter requires a SITE-relative path (e.g. `AgentAssets/Skills`) — silently resolved to zero folders instead of erroring.
  2. `Get-PnPFile -Url ... -AsFile` (no `-Path`) selected the "Save to local path" parameter set, which requires `-Path`, causing an interactive prompt this session's non-interactive invocation couldn't answer, silently failing that lookup too.
  3. A second `Get-PnPFile ... -Path $tempPath -AsFile` call passed a full file path to `-Path`, but that parameter expects a directory with `-Filename` supplied separately — a second interactive-prompt failure.
- **Why this wasn't caught in Task 0's original completion**: `reconcile-deployed-skill.ps1` had no automated test coverage (verified: `grep` for its name across `tests/` returns nothing) and, per its own history, had likely never been run against a real live tenant end-to-end before this session — only ever validated by code review / synthetic reasoning. A cmdlet-parameter-set bug like #2/#3 (silently switching to a different parameter set that then prompts interactively) is exactly the kind of defect that only surfaces on a real, live, non-interactive run — never in a mocked or manually-reasoned-through review.
- **Fix**: fixed all three at the cmdlet-parameter level (switched to `-Identity` for folder enumeration, `-AsFileObject` for the no-save lookup, explicit `-Path`/`-Filename` split for the save-to-disk lookup). Verified fixed with a real, non-interactive (`< /dev/null`) re-run against the live tenant: correctly found both real deployed skill folders, computed real SHA-256 hashes, and correctly surfaced a genuine, separate finding (`DISPOSITION: DEPLOYED_ARTIFACT_DRIFT_DETECTED` — the deployed `review-manual-topics` hash does not match this repo's current `SKILL.md`).
- **Evidence**: commit `5e05893` ("fix(sharepoint-agents-and-skills): 3 real bugs in reconcile-deployed-skill.ps1"); the user's screenshot (this session, not persisted to the repo); before/after script output in this session's transcript.
- **Severity**: M (no tenant/data impact — read-only script — but a false negative that, if trusted without the user's own independent verification, would have led to an incorrect "skill not deployed, redeploy from scratch" action against a tenant that already had the correct artifact, and more broadly would have blocked Phase 6's native-runtime evaluation on a fabricated premise)
- **Repeat**: NO (fixed at the source; no other script in this repo shares this exact `reconcile-deployed-skill.ps1` code path). Generalizable lesson, not yet codified as a new Hard Gate: **a live-tenant script's first-ever real run should be treated as unverified until independently cross-checked (e.g. against the actual SharePoint UI), especially when it reports a negative/empty result** — a script silently returning "nothing found" due to a parameter-set bug looks identical to a script correctly reporting "nothing found," and only external verification (the user's screenshot here) distinguished them. Considered for a future Hard Gate if this pattern recurs.
- **Status**: RESOLVED

### [2026-08-03] Phase 6 native-runtime redeploy — `deploy-and-verify-skill.ps1` `Add-PnPFile` Parameter-Set Bug

- **Logged Date**: 2026-08-03
- **Cycle/Session**: Same session as the `reconcile-deployed-skill.ps1` fixes above — continuation, redeploying `review-manual-topics/SKILL.md` to resolve the `DEPLOYED_ARTIFACT_DRIFT_DETECTED` finding those fixes surfaced.
- **Artifact Affected**: `plugins/sharepoint-agents-and-skills/scripts/deploy-and-verify-skill.ps1`
- **Friction Observed**: real `-Execute` run against the live tenant failed with `Parameter set cannot be resolved using the specified named parameters` immediately upon attempting the upload.
- **Root cause**: `Add-PnPFile -Path $sourcePath -Folder $targetFolderUrl -FileName $targetFilename -Values @{...}` — `-Path` selects the "Upload file" parameter set, which provides `-NewFileName` for renaming on upload; `-FileName` belongs to a different, stream-based parameter set ("Upload file from stream"/"from text") that has no `-Path`. Mixing the two is invalid and PowerShell correctly rejected it (unlike the three `reconcile-deployed-skill.ps1` bugs, this one errored loudly rather than silently returning a wrong empty result — a better failure mode, caught immediately on the real execution attempt rather than needing external cross-checking).
- **Why not caught earlier**: same as the sibling script — no test coverage, and `-Execute` (the only code path that exercises this line) had apparently never been run against a real tenant before this session; the script's own preflight (`-Execute` omitted) never reaches this line at all.
- **Fix**: `-FileName` → `-NewFileName`. Verified fixed with a real `-Execute` run: upload succeeded, pre/post-deployment SHA-256 readback matched 100% (`bb327348...`), and the sibling reconciliation script (already fixed) confirmed `DISPOSITION: TASK_8_ARTIFACT_ALREADY_PRESENT_AND_RECONCILED` afterward — the drift this session found earlier is now resolved on the real tenant, not just in this repo's expectations.
- **Evidence**: commit `0345b5f`; live-tenant command output in this session's transcript (upload URL, matching SHA-256 readback, reconciliation re-run).
- **Severity**: L (errored loudly and immediately rather than silently misbehaving; no partial/corrupt write occurred — PnP rejects an invalid parameter combination before any tenant call is made)
- **Repeat**: NO (fixed at the source)
- **Status**: RESOLVED

### [2026-08-07] Phase 9 Wave 2 — `audit_plugin_structure.py` (Hard Gate #12) Does Not Exist in This Repository

- **Logged Date**: 2026-08-07
- **Cycle/Session**: Phase 9 Wave 2 — agent extraction into `plugins/sharepoint-agents-and-skills/`
- **Artifact Affected**: `.agent/rules/self-evolution-policy.md` Hard Gate #12; `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §9a (both name `audit_plugin_structure.py <plugin>` as a mandatory pre-completion check)
- **Friction Observed**: Hard Gate #12 and spec §9a both mandate running `audit_plugin_structure.py <plugin>` before any new skill/agent is considered complete, and explicitly distinguish it from `audit.py` ("it catches real files living inside skill dirs that the compliance audit does not flag as an error"). The script does not exist anywhere in this repository or in any installed skill — `find . -name 'audit_plugin_structure.py'` returns nothing; `.agents/skills/audit-plugin/scripts/` contains `audit.py`, `audit_marketplace_sources.py`, `run_eval.py`, `run_loop.py`, and helpers, but no structure auditor. A mandatory gate therefore cannot be satisfied as written.
- **Why it was not fixed now**: writing the missing auditor is a new capability in a different domain (plugin-structure tooling, owned by the `audit-plugin` skill from the sibling `agent-plugins-skills` monorepo per `CLAUDE.md`'s Category 1 protocol), not part of Wave 2's authorized scope, and Category 1 artifacts must be authored in the sibling repo under its own PR/review protocol — not created here.
- **Workaround used, and its limits**: ran `.agents/skills/audit-plugin/scripts/audit.py --path plugins/sharepoint-agents-and-skills` instead (result: `AUDIT PASSED`, only pre-existing `references/`-directory warnings). This is explicitly the weaker of the two checks per Hard Gate #12's own text. Wave 2's specific exposure is nil — it added no files inside any skill directory at all (agents are plugin-root peers of `skills/`) — but a future extraction that does add skill-internal files will hit a real, unguarded drift risk.
- **Recommended fix**: author `audit_plugin_structure.py` in `agent-plugins-skills` under the `audit-plugin` skill (real-file-inside-skill-dir detection, per ADR-002/ADR-003), merge via that repo's PR protocol, reinstall here — then update Hard Gate #12 and spec §9a with the resolved invocation path. Until then, Hard Gate #12's second sentence should be treated as aspirational and any Phase 9 wave that writes files into a skill directory must state explicitly which check it actually ran.
- **Evidence / reproduction**: `find /Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench -name 'audit_plugin_structure.py'` → no results (repository and `.agents/` both searched, 2026-08-07).
- **Severity**: M (a mandatory hard gate is unsatisfiable as written; the drift class it exists to catch has already occurred once undetected across 16 files per the 2026-07-25 entry it cites)
- **Repeat**: YES — this gate will be unsatisfiable for every subsequent Phase 9 wave until the script exists. Must escalate on next encounter rather than being deferred again.
- **Status**: OPEN

### [2026-08-07] Phase 9 Wave 2 — `plugin_add.py` (Hard Gate #10) Writes a Worktree-Absolute Path into Tracked `plugin-sources.json`

- **Logged Date**: 2026-08-07
- **Cycle/Session**: Phase 9 Wave 2 — agent extraction into `plugins/sharepoint-agents-and-skills/`
- **Artifact Affected**: `plugin-sources.json`, `skills-lock.json` (both tracked); `.agents/skills/plugin-installer/scripts/plugin_add.py` (Category 1, sibling-repo owned)
- **Friction Observed**: Hard Gate #10 requires `plugin_add.py <plugin-path> -y` after any modification under `plugins/`. Running it from a git worktree (the standard per-phase workflow since Phase 2, per `CLAUDE.md`) appended an absolute worktree path — `/Users/.../.claude/worktrees/agent-aa349c7aac745b79c` — as a permanent `source` entry in tracked `plugin-sources.json`, and added 15 `installedAt` records to tracked `skills-lock.json` describing an install into a throwaway worktree-local `.agents/` directory that will not exist after the worktree is removed. Committing either would have shipped a dead machine-specific path into `main`.
- **Fix applied inline**: reverted both files (`git checkout -- plugin-sources.json skills-lock.json`) after confirming the installer's real verification value had already been obtained — it reported the destination as `.agents/ (skills + agents + commands + hooks)` and successfully installed all four new agent files, which is exactly the evidence Wave 2 needed to confirm `plugins/<plugin>/agents/` is the tool-recognized component location. The gate was run; only its tracked-file side effects were discarded. Nothing under `plugins/` was altered by the revert.
- **Recommended durable fix**: `plugin_add.py` should record the source as a repository-root-relative path (or the canonical repo URL it already knows — it writes `https://github.com/richfrem/sharepoint-knowledge-workbench` into `skills-lock.json` while writing an absolute worktree path into `plugin-sources.json`, so the two manifests disagree). Owned by `agent-plugins-skills`; fix belongs there, not here. Until then, Hard Gate #10 should carry a worktree caveat: run the installer, then verify `git status` and revert manifest churn that encodes the worktree path.
- **Evidence / reproduction**: `git diff plugin-sources.json` immediately after `python3 .agents/skills/plugin-installer/scripts/plugin_add.py . --plugins sharepoint-agents-and-skills -y` from the Wave 2 worktree, 2026-08-07.
- **Severity**: M (silently commits a machine- and worktree-specific absolute path into a tracked manifest; the per-phase worktree workflow means every future phase hits this)
- **Repeat**: YES — inherent to running Hard Gate #10 from any worktree, which is the mandated workflow. Escalate on next encounter.
- **Status**: RESOLVED (this occurrence reverted; underlying installer defect OPEN in the sibling repo)

### [2026-08-07] Phase 9 Wave 2 — Extracted Agents Were Pure Routers Over Nonexistent Skills

- **Logged Date**: 2026-08-07
- **Cycle/Session**: Phase 9 Wave 2 — agent extraction into `plugins/sharepoint-agents-and-skills/`
- **Artifact Affected**: `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/task-2a-symlink-resolution-and-task-3a-agent-classification.md` (Task 3a classification); `docs/superpowers/specs/phase-9-reusable-sharepoint-plugin-extraction-spec.md` §8f (agent classification axes)
- **Friction Observed**: Task 3a classified these four agents as zero-cost on genericity ("completely free of project literals... the cleanest extraction candidates found anywhere in this audit") based on a literal-density scan. That held on read — zero literals, confirmed. But the scan measured the wrong cost axis for agents: all four are *pure routers* whose entire body is a table of source-plugin skill names (`sp-extracting-links`, `sp-auditing-schema`, `sp-converting-aspx-pages`, …). Those names are not project literals and pass every §8h/§9 check, yet a verbatim copy would have produced four agents routing to roughly fifteen capabilities that do not exist in this repository. The real extraction work was rebuilding each routing table against this repo's actual capability inventory — not scrubbing literals, of which there were none.
- **Fix applied inline**: rewrote each routing table against verified real skills, added a mandatory `## Not available in this workbench` section to every agent, and made dangling references *mechanically impossible to reintroduce* — `tests/unit/test_agent_definitions.py` resolves every hyphenated inline-code token in every agent against the real set of skill/plugin/agent names under `plugins/`, failing unless the token exists or is explicitly declared unavailable. Task 3a's classification is not wrong and was not amended; the cost model behind it is incomplete.
- **Recommended fix**: spec §8f's agent-classification axes should gain a fifth axis alongside literal density — **routing-target resolvability**: the count of source capabilities an agent routes to that have no destination equivalent. For a router, that number *is* the extraction cost, and it is uncorrelated with literal density. Recommended before Wave 3 classifies `sp-discovery-agent`/`sp-migration-agent` (3 literals each — i.e. they will look cheap on the same incomplete axis that made these four look free).
- **Evidence / reproduction**: the four source files at `78d6bb9` are 17–18 lines each and name 15 distinct `sp-*` skills between them, of which zero exist in this repository (`ls plugins/*/skills/`); provenance Records 3–6 list the per-agent re-targeting.
- **Severity**: M (no defect shipped — caught during Wave 2 execution and guarded by test — but the same incomplete cost model is about to be applied to the remaining five agents in a later wave)
- **Repeat**: NO for these four (resolved and test-guarded); YES as a classification-model gap for Wave 3+ unless §8f gains the axis.
- **Status**: RESOLVED (Wave 2 artifacts); recommendation for §8f is OPEN
