# Phase 4 Deployment Scripts & Verification Utilities

This directory contains PowerShell deployment scripts and hash-verification utilities for deploying candidate native SharePoint skills into target document libraries.

## Contents & Responsibilities
- `scripts/`: PowerShell scripts for uploading skill assets (e.g. `SKILL.md`) to `AgentAssets/Skills/review-manual-topics/` via PnP PowerShell or Graph REST API.
- SHA-256 Readback Verification: All deployment steps must verify 100% byte-for-byte fidelity of uploaded skill definitions against repository sources prior to evaluation.
