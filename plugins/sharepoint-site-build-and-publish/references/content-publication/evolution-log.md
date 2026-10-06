# Evolution Log — sharepoint-site-build-and-publish

Append-only record of every self-evolution event. Written by the `self-evolution` skill.
Do not edit manually except to correct a factual error.

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
# Inventory-driven download workflow — 2026-10-05

- Status: RESOLVED — Added the selected bulk download wrapper and source/local manifest. Reuses the canonical downloader; added stored-file REST retrieval, neutral platform detection/config discovery and interactive-default on-prem authentication. Hash directories preserve equal filenames from separate sources.
- Verification: content-publication namespace 58 passed; three focused plan/Online/on-prem adapter tests passed after final downloader changes. Live download performance/authentication remains unverified. Contract: `bulk-download-workflow.md`.
