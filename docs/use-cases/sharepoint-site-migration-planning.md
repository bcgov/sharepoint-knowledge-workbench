# Use Case: Migration Wave Planning

Dependency-graph analysis and deployment wave-order computation across a multi-object SharePoint
migration project — the missing middle layer between site discovery/schema analysis (read-only,
single-site) and provisioning (executes one already-ordered target schema).

## When to use this

A migration touches many interdependent objects (lists, content types, columns) and the order
they get created/migrated in matters — you need a computed dependency graph and wave sequence, not
a hand-maintained stage list that goes stale when things get reordered.

## Workflow at a glance

> **Status: partially implemented.** Only `analyze-migration-dependencies` is real, tested,
> and installs standalone. `initialize-migration-project`,
> `normalize-migration-inventory`, and `scaffold-migration-wave-scripts` remain design
> scaffolds — their `SKILL.md` files describe intended, not current, behavior. Don't invoke those
> three expecting a working result.

- `analyze-migration-dependencies` — derives wave order via topological sort from declared
  dependencies (never a human-maintained sequence of stage numbers).
- `plan-migration-waves` — consumes the computed graph to produce a wave plan.

`sharepoint-site-build-and-publish` consumes this plugin's computed wave plan as an input to its own gated
apply — it does not compute wave order itself.

## Full detail

[`plugins/sharepoint-site-migration/README.md`](../../plugins/sharepoint-site-migration/README.md)
