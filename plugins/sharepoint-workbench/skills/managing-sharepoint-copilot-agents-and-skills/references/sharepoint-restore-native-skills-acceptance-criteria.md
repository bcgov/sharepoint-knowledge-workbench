# Acceptance Criteria: sharepoint-restore-native-skills

## Goal
Validate that the Sharepoint Restore Native Skills skill performs its documented SharePoint Copilot work without mutating tenant state beyond its stated scope.

## Required behavior
- Run the skill using the parameters documented in its SKILL.md quick start.
- Supply the correct SharePoint connection/config values or a valid local sample fixture.
- Only write to the intended output directory, local backup folder, or target artifact path declared by the skill.
- When the skill is read-only, leave the tenant unchanged.
- When the skill write path is expected, confirm the output file or object is created exactly once and matches the requested target.

## Pass conditions
- The command exits successfully with a clear result.
- Every required output artifact exists at the expected path.
- Any validation message or summary reflects the actual output count or target created.
- The skill does not create unrelated SharePoint objects or mutate adjacent content.
- The result can be reproduced by rerunning the same command with the same inputs.

## Evidence to keep
- Command and parameter set used.
- Output path or file names created.
- Validation counts or checksums, if applicable.
- Confirmation that no unexpected write happened outside the declared scope.
