"""
link_rules.py
=============

Purpose:
    Loads and applies a caller-supplied URL rewrite ruleset. This module is the
    ONLY place source/target URLs are permitted to exist in this plugin, and it
    ships no built-in rules, no default hosts, and no default site paths -- a
    ruleset is always provided by the operator for their own environment.

Layer: sharepoint-site-migration / rules

Key Input Dependencies:
    - a JSON ruleset file: {"rules": [{"match": ..., "replacement": ..., "description": ...}]}

Usage:
    from link_rules import load_ruleset
    ruleset = load_ruleset("my-environment-rules.json")
    new_url, applied = ruleset.apply(old_url)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


class RulesetError(ValueError):
    """Raised when a ruleset is missing, unreadable, or structurally invalid."""


@dataclass(frozen=True)
class RewriteRule:
    """One literal (not regular-expression) find/replace pair.

    ``match`` is matched case-insensitively and escaped before use, so operators
    can paste real URL fragments without worrying about regex metacharacters.
    """

    match: str
    replacement: str
    description: str = ""

    def apply(self, url: str) -> tuple[str, bool]:
        pattern = re.compile(re.escape(self.match), re.IGNORECASE)
        rewritten, count = pattern.subn(self.replacement, url)
        return rewritten, count > 0

    def to_dict(self) -> dict[str, str]:
        return {"match": self.match, "replacement": self.replacement, "description": self.description}


@dataclass(frozen=True)
class RewriteRuleset:
    """An ordered collection of rules. Order is significant: declare the most
    specific rule first, exactly as the operator intends it to be applied."""

    rules: Sequence[RewriteRule] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "RewriteRuleset":
        if not isinstance(payload, Mapping):
            raise RulesetError("ruleset must be an object with a 'rules' list")
        raw_rules = payload.get("rules")
        if not isinstance(raw_rules, list):
            raise RulesetError("ruleset must contain a 'rules' list")
        if not raw_rules:
            raise RulesetError("ruleset must declare at least one rule")

        rules: list[RewriteRule] = []
        for index, entry in enumerate(raw_rules):
            if not isinstance(entry, Mapping):
                raise RulesetError(f"rule {index} must be an object")
            match = entry.get("match")
            replacement = entry.get("replacement")
            if not isinstance(match, str) or not match.strip():
                raise RulesetError(f"rule {index} needs a non-empty string 'match'")
            if not isinstance(replacement, str):
                raise RulesetError(f"rule {index} needs a string 'replacement'")
            rules.append(
                RewriteRule(
                    match=match,
                    replacement=replacement,
                    description=str(entry.get("description", "")),
                )
            )
        return cls(rules=tuple(rules))

    def apply(self, text: str) -> tuple[str, list[RewriteRule]]:
        """Apply every rule in declared order. Returns the rewritten text and
        the rules that actually changed something."""
        result = text
        applied: list[RewriteRule] = []
        for rule in self.rules:
            result, changed = rule.apply(result)
            if changed:
                applied.append(rule)
        return result, applied

    def matches(self, text: str) -> list[RewriteRule]:
        """Rules that would still change ``text`` -- the residual-legacy test."""
        return [rule for rule in self.rules if rule.apply(text)[1]]

    def to_dict(self) -> dict[str, Any]:
        return {"rules": [rule.to_dict() for rule in self.rules]}


def load_ruleset(path: str | Path) -> RewriteRuleset:
    """Load a ruleset from a real file on disk."""
    resolved = Path(path)
    if not resolved.is_file():
        raise RulesetError(f"rewrite ruleset not found: {resolved}")
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RulesetError(f"rewrite ruleset is not valid JSON: {resolved} ({exc})") from exc
    return RewriteRuleset.from_dict(payload)
