# Phase 4 Evaluation Test Suite & Case Definitions

This directory contains structured JSON test cases for evaluating candidate native SharePoint agent skills against strict boundary, accuracy, security, and baseline requirements.

## Evaluation Categories
- `normal/`: Standard topic review queries within primary subject boundary.
- `negative/`: Out-of-scope or non-existent topic queries to test graceful refusal / non-hallucination.
- `ambiguous/`: Broad or multi-topic queries to test scope clamping (single primary + max 2 related).
- `permission/`: Access control test cases across 4 test identity classes (`OWNER_EDITOR`, `INTENDED_READER`, `RESTRICTED_READER`, `NO_SOURCE_ACCESS`).
- `safety/`: Prompt injection, jailbreak, data exfiltration, and writing/modification attempt test cases.
