# Semantic Components

Authored content signals meaning using semantic callouts, not ad-hoc bold
text or emoji. A semantic callout uses GitHub-style alert syntax:

```markdown
> [!WARNING]
> Disconnect power before opening the panel.
```

The first line inside the blockquote is `[!TYPE]`; every following
blockquoted line is the callout body.

## Approved semantic components

| Component | Callout tag | Use for |
|---|---|---|
| Note | `[!NOTE]` | Supplementary information that is helpful but not critical. |
| Warning | `[!WARNING]` | A hazard or action that could cause harm, data loss, or a serious error if ignored. |
| Important | `[!IMPORTANT]` | Information the reader must not skip to succeed at the task. |
| Example | `[!EXAMPLE]` | A worked example illustrating the surrounding content. |
| Prerequisite | `[!PREREQUISITE]` | Something the reader must have or know before proceeding. |
| Procedure step | (ordinary ordered list item under `## Procedure`) | One discrete, numbered action in a procedure. |
| Expected result | `[!EXPECTED RESULT]` (or the `## Expected Result` section) | What the reader should observe once a step or procedure succeeds. |
| Decision | `[!DECISION]` | A branch point where the reader must choose between options. |
| Exception | `[!EXCEPTION]` (or the `## Exceptions and Special Cases` section) | A case where the standard procedure does not apply. |
| Troubleshooting item | `[!TROUBLESHOOTING]` (or the `## Troubleshooting` section) | A known problem and its resolution. |
| Definition | `[!DEFINITION]` | A term the reader may not already know. |
| Reference | `[!REFERENCE]` | A pointer to related, non-topic material (a policy, a standard, an external document). |
| Knowledge check | `[!KNOWLEDGE CHECK]` | A short self-check question for the reader. |

## Guidance

- Use exactly one callout type per block — do not nest callouts.
- Prefer the dedicated template section (`## Procedure`, `## Expected
  Result`, `## Exceptions and Special Cases`, `## Troubleshooting`) over an
  inline callout when the content is a whole section's worth of material;
  use the inline callout tag for a single aside within running text.
- Do not invent new callout tags — if none of the above fit, the content
  probably belongs in ordinary prose instead.
