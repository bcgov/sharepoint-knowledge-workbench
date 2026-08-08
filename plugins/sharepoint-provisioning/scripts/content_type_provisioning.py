"""
content_type_provisioning.py
=============================

Purpose:
    Caller-declared site-content-type provisioning: create-if-missing content
    types, add/hide/show/unlink field links, and content-type-to-list attach
    planning. Reconcile semantics throughout -- an existing content type is
    left alone except for the specific drift the declared schema calls out;
    a field link's hidden-flag drift against the schema is surfaced in the
    plan (not silently fixed without being named), and a field no longer
    declared on the content type is explicitly unlinked rather than left as
    orphaned live state.

    Pure planning only. This module performs no write of any kind -- see
    ``list_provisioning`` for the gated apply step that actually executes a
    plan.

Layer: sharepoint-provisioning / content-type planning

Key Input Dependencies:
    - none (standard library only)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ContentTypeFieldSpec:
    """One field a content type declares, and whether it should be hidden
    on that content type's forms."""

    field_name: str
    hidden: bool = False


@dataclass(frozen=True)
class ContentTypeDef:
    """A caller-declared content type. ``unlink_fields`` names fields that
    must be explicitly unlinked if still present -- e.g. a field that was
    declared in an earlier version of the schema and has since been
    superseded."""

    name: str
    parent: str = "Item"
    fields: Sequence[ContentTypeFieldSpec] = field(default_factory=tuple)
    unlink_fields: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ContentTypeState:
    """Caller-supplied observation of a content type's current live state.
    ``field_links`` maps a linked field's name to its current hidden flag."""

    name: str
    exists: bool
    field_links: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class ContentTypeAction:
    """One planned step. ``already_correct`` distinguishes 'nothing to do'
    from a real change, without dropping the step from the plan -- reviewers
    see the full reconciliation, not just the diff."""

    step: str  # create_content_type | link_field | hide_field | show_field | unlink_field
    detail: str
    already_correct: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"step": self.step, "detail": self.detail, "already_correct": self.already_correct}


def plan_content_type(
    ct_def: ContentTypeDef, current: ContentTypeState | None
) -> list[ContentTypeAction]:
    """Plan every action needed to reconcile one content type's declared
    schema against its caller-supplied observed current state."""
    actions: list[ContentTypeAction] = []
    exists = bool(current and current.exists)

    if exists:
        actions.append(
            ContentTypeAction(
                "create_content_type",
                f"'{ct_def.name}' already exists",
                already_correct=True,
            )
        )
    else:
        actions.append(
            ContentTypeAction(
                "create_content_type",
                f"create '{ct_def.name}' (parent '{ct_def.parent}')",
            )
        )

    links: Mapping[str, bool] = current.field_links if (current and exists) else {}

    for spec in ct_def.fields:
        if spec.field_name not in links:
            actions.append(
                ContentTypeAction(
                    "link_field",
                    f"link '{spec.field_name}' to '{ct_def.name}'",
                )
            )
            hide_step = "hide_field" if spec.hidden else "show_field"
            actions.append(
                ContentTypeAction(
                    hide_step,
                    f"set hidden={spec.hidden} for '{spec.field_name}' on '{ct_def.name}' (new link)",
                )
            )
            continue

        currently_hidden = links[spec.field_name]
        hide_step = "hide_field" if spec.hidden else "show_field"
        if currently_hidden != spec.hidden:
            actions.append(
                ContentTypeAction(
                    hide_step,
                    f"reconcile hidden={spec.hidden} for '{spec.field_name}' on "
                    f"'{ct_def.name}' (drift: was {currently_hidden})",
                )
            )
        else:
            actions.append(
                ContentTypeAction(
                    hide_step,
                    f"'{spec.field_name}' already hidden={spec.hidden} on '{ct_def.name}'",
                    already_correct=True,
                )
            )

    for name in ct_def.unlink_fields:
        if name in links:
            actions.append(
                ContentTypeAction(
                    "unlink_field",
                    f"unlink '{name}' from '{ct_def.name}' (no longer declared in schema)",
                )
            )

    return actions


def plan_add_content_type_to_list(
    list_title: str,
    content_type_name: str,
    current_list_content_types: Sequence[str],
) -> ContentTypeAction:
    """Plan attaching a content type to a list, create-if-missing."""
    if content_type_name in current_list_content_types:
        return ContentTypeAction(
            "attach_content_type",
            f"'{content_type_name}' already attached to '{list_title}'",
            already_correct=True,
        )
    return ContentTypeAction(
        "attach_content_type",
        f"attach '{content_type_name}' to '{list_title}'",
    )
