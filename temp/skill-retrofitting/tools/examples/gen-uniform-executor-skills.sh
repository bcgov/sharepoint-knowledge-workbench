#!/bin/bash
# usage: gen-prov-skills.sh <dat> ; run from plugins/sharepoint-provisioning/skills
while IFS='|' read -r skill title script token desc purpose extra verify; do
  cat > "$skill/SKILL.md" <<EOT
---
name: $skill
plugin: sharepoint-provisioning
description: $desc
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/$script -PlanPath plan.json"
  - "pwsh -File scripts/$script -PlanPath plan.json -Execute -ConfirmToken $token"
---

# $title

$purpose

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without \`-Execute\` it prints a structured JSON action summary and changes nothing.
- A real write needs \`-Execute -ConfirmToken $token\`, exactly. The plan's own \`confirmation_token\` field is a different value. A real run is a live tenant write that the user runs.
- $extra
- Read the "Plan JSON shape" block in \`scripts/$script\`'s header and do not invent plan keys. When running an installed copy, pass \`-ConfigPath\` (or \`-SiteUrl\`, \`-ClientId\`, \`-TenantId\`).

## Quick start

\`\`\`bash
pwsh -File scripts/$script -PlanPath path/to/plan.json
\`\`\`

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with \`-Execute -ConfirmToken $token\`.
4. Report the result and check it as described below.

## Verification

$verify

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
EOT
done < "$1"
