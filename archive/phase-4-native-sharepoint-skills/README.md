# Phase 4 — Native SharePoint Skills Pilot Assets

This directory contains executable, deployable, and evaluation assets for Phase 4 of the AI-Assisted Structured Knowledge Workbench.

## Scope & Purpose
- Candidate Skill: `review-manual-topics`
- Primary Subject Boundary: Exactly 1 explicitly selected CEIS topic page.
- Related Evidence Boundary: Up to 2 directly referenced topics max (evidence inputs only).
- Source of Truth: `skills/review-manual-topics/SKILL.md` (reviewed repo copy).
- Target Deployment Path: `AgentAssets/Skills/review-manual-topics/SKILL.md` with 100% SHA-256 readback verification.
- Configuration: Copy `config.psd1.example` to `config.psd1` (ignored in git) for local tenant execution using ClientId, TenantId, and SiteUrl.
- Evaluation: 5 categories (Normal, Negative, Ambiguous, Permission across 4 identity classes, Safety) against a No-Skill Control baseline.
- Non-Goals: No automated deployment, no agent-initiated writes, no plugin boundary extraction.
