# Structured Content Pipeline Diagrams

Diagrams 01–05 describe the implemented document-conversion workflow. The
owning plugin and current skills are:

| Workflow | Diagram | Current skills |
|---|---|---|
| End-to-end conversion | `01-phase1-overview.mmd` | `content-extract-docx`, `content-analyze-document-structure`, `content-assemble-structured-content`, `content-render-markdown-pages`, `content-render-sharepoint-pages` |
| Extract, analyze, and confirm | `02-analyze-and-confirm.mmd` | `content-extract-docx`, `content-analyze-document-structure` |
| Assemble structured content | `03-create-canonical-content.mmd` | `content-assemble-structured-content` |
| Render and validate output | `04-generate-and-render.mmd` | `content-render-markdown-pages`, `content-render-sharepoint-pages`, `content-validate-rendered-output`, `content-compare-rendered-output` |
| Validation and human review | `05-validation-and-evidence.mmd` | `content-validate-rendered-output`, `content-compare-rendered-output`, `content-review-manual-topic` |

These skills are packaged in
[`sharepoint-document-conversion`](../../plugins/sharepoint-document-conversion/README.md).
The same plugin also provides rendering-template authoring and validation skills.

Diagrams 06–09 are future-state workflow concepts, not descriptions of a
built end-to-end authoring, approval, or republishing workflow. Some individual
skills they could use already exist; the diagrams now identify those skills
without implying that the broader workflows are implemented.

- `06-phase3-editing-workflow-hybrid-candidate.mmd` — proposed governed editing.
- `07-phase3-publisher-triggered-render-workflow.mmd` — proposed publisher flow.
- `08-phase3-editor-submission-and-approval-workflow.mmd` — proposed business approval flow.
- `09-phase6-5-ongoing-authoring-and-republishing-loop.mmd` — proposed continuous maintenance loop.
- `high-level.mmd` — broad knowledge-conversion vision beyond current outputs.
