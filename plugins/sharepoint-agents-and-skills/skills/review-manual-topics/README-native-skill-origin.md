# Candidate Skill: review-manual-topics

This directory contains the candidate native SharePoint agent skill definition (`SKILL.md`) for Phase 4.

## Overview
`review-manual-topics` is designed to run natively within Microsoft 365 Copilot / SharePoint Agent contexts. It provides strict topic-scoped technical review capabilities over modern SharePoint Site Pages derived from Phase 3 conversion.

## Boundary Enforcement
- **Primary Subject**: Exactly 1 target topic page per query.
- **Related Evidence**: Up to 2 directly linked/referenced topic pages max as secondary context.
- **Non-Interference**: Must not alter source content, perform site-wide unconstrained searches, or access unauthorized pages.
