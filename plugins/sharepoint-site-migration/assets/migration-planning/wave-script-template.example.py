"""
DESIGN SCAFFOLD — example shape only, not a working script, not yet wired to
any real generation logic.

This is a STYLE REFERENCE for `scaffold-migration-wave-scripts` to follow —
the agent step reads this to understand the expected shape of a generated
wave script, then produces a NEW script per computed wave using real object
names from that wave's own dependency-matrix.json entries. Nothing below is
meant to be copied verbatim; every {placeholder} must come from the matrix,
never be filled in with content from this template.

Layer: sharepoint-site-migration / assets (template, not shipped code)
"""

from __future__ import annotations

# A generated wave script is expected to call INTO sharepoint-site-build-and-publish's
# existing, already three-gate-safe plan/apply functions -- never open a new,
# parallel write path of its own.
#
# from list_provisioning import ListDef, ProvisioningSchema, CurrentState, plan_provisioning, apply_provisioning
# from content_type_provisioning import ContentTypeDef
# from field_provisioning import FieldDef


def plan_wave_{wave_id}(current_state) -> "ProvisioningPlan":
    """Build the provisioning plan for wave {wave_id}: {list of object names
    from this wave, taken from dependency-matrix.json -- never hardcoded here}."""
    schema = ProvisioningSchema(
        # lists=(...), content_types=(...), fields=(...)  -- populated from the matrix
    )
    return plan_provisioning(schema, current_state)


def main() -> None:
    """Dry-run by default. Requires an explicitly injected executor and a
    plan-derived confirmation token to write anything -- matches
    sharepoint-site-build-and-publish's existing safety gate exactly, does not
    reimplement or weaken it."""
    raise NotImplementedError("template only -- sharepoint-scaffold-migration-wave-scripts fills this in")


if __name__ == "__main__":
    main()
