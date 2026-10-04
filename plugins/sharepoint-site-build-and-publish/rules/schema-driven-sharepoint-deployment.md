# Schema-Driven SharePoint Deployment

## Core principle

Every schema/deployment-object definition (site columns, content types,
lists, or any other deployable object type) lives in a caller-supplied JSON
structure -- never hardcoded inline in a deployment script or an
orchestrator. Deploy logic and validation logic both read the SAME
structure, so they cannot drift from each other: if a field, content type,
or list is renamed, added, or removed in the schema, both the code that
deploys it and the code that verifies it see the change on the very next
run, not on a separately-maintained copy someone forgot to update.

## The dependency-annotation standard

Any object that needs ordered deployment relative to other objects
declares its dependencies **by name**, in the same shared schema structure
used for planning and validation (this plugin's generalized
`DeploymentObject.depends_on`, see `plugins/sharepoint-site-migration/scripts/migration-planning/wave_planning.py`) -- never by
having its position hand-encoded into a separate, fixed-order orchestrator
step list. A dependency is "this object depends on that named object," not
"this object belongs in stage N" -- the latter requires a human to keep the
stage number in sync with reality every time the object set changes, which
is exactly the kind of coupling this rule exists to eliminate.

## Why this rule exists

A hand-maintained deployment step list is a duplicate source of truth: it
encodes, by hand, an ordering that a dependency graph could instead compute.
The moment the underlying set of deployable objects changes -- one is
renamed, several are consolidated into a single script, or a new one is
introduced -- the hand-maintained list can silently fall out of sync with
that reality. Nothing catches the drift until the orchestrator is actually
run: it may reference an object or script that no longer exists, or it may
run everything in an order that no longer reflects real dependencies. A
schema-driven, dependency-annotated approach -- where deployment order is
computed via topological sort over declared dependencies, not typed out by
a human -- turns that class of bug into a planning-time failure (an
unresolved dependency or a cycle, reported honestly) rather than a
run-time surprise against a live tenant.

## Deliberately out of scope for this rule

This rule governs *schema/dependency structure and where it lives*, not any
project-specific field-naming convention, migration-source-vs-destination
naming scheme, or incident-specific war story from any one deployment
target. Those remain specific to whatever project encounters them and are
not generalized here.
