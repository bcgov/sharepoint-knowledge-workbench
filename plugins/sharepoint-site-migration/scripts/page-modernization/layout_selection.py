"""
layout_selection.py
====================

Purpose: Stage 3 of the page-modernization pipeline -- data-driven modern
layout selection. Evaluates rules (first-match-wins, packaged
`assets/layout-rules.json` by default) against component counts derived
from a classified component model. A rule's `condition` is data, not code:
it is evaluated with a restricted AST evaluator that only permits name
lookups, comparisons, boolean/arithmetic operators and literals -- never a
function call -- so a malformed or hostile rule is recorded in
`skippedRules` with a reason, never silently skipped or executed.

Layer: CLI entry point, invoked as a real subprocess by the pipeline (and by
this plugin's own tests).

Key Input Dependencies:
    - Component-model JSON supplied with --input.
    - Layout rules JSON supplied with --rules or bundled in assets/layout-rules.json.

Function Index:
    _eval_boolean, _eval_comparison, _eval_binary, _eval_name,
    _eval_constant, _eval_node, safe_eval_condition, _compute_counts,
    select_layout, main
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

import outcomes

_AND_OR_RE = re.compile(r"\b(AND|OR)\b")
_AND_OR_MAP = {"AND": "and", "OR": "or"}

_PACKAGED_RULES = Path(__file__).resolve().parent / "assets" / "layout-rules.json"

_BOOL_OPS = {ast.And: lambda a, b: a and b, ast.Or: lambda a, b: a or b}
_CMP_OPS = {
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
}
_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
}


class UnsafeConditionError(ValueError):
    """Raised when a rule condition contains a node this evaluator refuses to evaluate."""


def _eval_boolean(node: ast.BoolOp, variables: dict):
    """Evaluate supported boolean operands using the existing eager semantics."""
    op = _BOOL_OPS.get(type(node.op))
    if op is None:
        raise UnsafeConditionError(f"unsupported boolean operator: {type(node.op).__name__}")
    values = [_eval_node(value, variables) for value in node.values]
    result = values[0]
    for value in values[1:]:
        result = op(result, value)
    return result


def _eval_comparison(node: ast.Compare, variables: dict):
    """Evaluate a chained comparison, stopping after its first false pair."""
    left = _eval_node(node.left, variables)
    for operator, comparator in zip(node.ops, node.comparators):
        compare = _CMP_OPS.get(type(operator))
        if compare is None:
            raise UnsafeConditionError(f"unsupported comparison operator: {type(operator).__name__}")
        right = _eval_node(comparator, variables)
        if not compare(left, right):
            return False
        left = right
    return True


def _eval_binary(node: ast.BinOp, variables: dict):
    """Evaluate an explicitly supported arithmetic expression."""
    op = _BIN_OPS.get(type(node.op))
    if op is None:
        raise UnsafeConditionError(f"unsupported binary operator: {type(node.op).__name__}")
    return op(_eval_node(node.left, variables), _eval_node(node.right, variables))


def _eval_name(node: ast.Name, variables: dict):
    """Resolve a rule variable or reject an undeclared name."""
    if node.id not in variables:
        raise UnsafeConditionError(f"unknown variable: {node.id}")
    return variables[node.id]


def _eval_constant(node: ast.Constant):
    """Return a primitive literal accepted by the rule-expression grammar."""
    if isinstance(node.value, (int, float, bool, str)) or node.value is None:
        return node.value
    raise UnsafeConditionError(f"unsupported constant type: {type(node.value).__name__}")


def _eval_node(node: ast.AST, variables: dict):
    """Dispatch a parsed expression node to its restricted evaluator."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)
    if isinstance(node, ast.BoolOp):
        return _eval_boolean(node, variables)
    if isinstance(node, ast.Compare):
        return _eval_comparison(node, variables)
    if isinstance(node, ast.BinOp):
        return _eval_binary(node, variables)
    if isinstance(node, ast.Name):
        return _eval_name(node, variables)
    if isinstance(node, ast.Constant):
        return _eval_constant(node)
    raise UnsafeConditionError(f"unsupported expression node: {type(node).__name__}")


def safe_eval_condition(condition: str, variables: dict):
    """Parse `condition` as a Python expression and evaluate it using only a
    restricted subset of AST nodes -- no attribute access, no subscripting,
    and above all no Call node is ever evaluated, so arbitrary code
    execution embedded in a rules file is structurally impossible."""
    normalized = _AND_OR_RE.sub(lambda m: _AND_OR_MAP[m.group(1)], condition)
    tree = ast.parse(normalized, mode="eval")
    return _eval_node(tree, variables)


def _compute_counts(components: "list[dict]") -> dict:
    """Count component roles and types used by the layout-rule variables."""
    primary_count = sum(1 for c in components if c.get("role") == "Primary")
    secondary_count = sum(1 for c in components if c.get("role") == "Secondary")
    child_count = sum(1 for c in components if c.get("role") == "Child")
    banner_count = sum(1 for c in components if c.get("role") == "Banner")
    content_editor_count = sum(1 for c in components if c.get("type") == "ContentEditor")
    summary_links_count = sum(1 for c in components if c.get("type") == "SummaryLinks")
    non_primary_count = secondary_count + child_count + banner_count
    return {
        "primaryCount": primary_count,
        "secondaryCount": secondary_count,
        "childCount": child_count,
        "bannerCount": banner_count,
        "contentEditorCount": content_editor_count,
        "summaryLinksCount": summary_links_count,
        "nonPrimaryCount": non_primary_count,
    }


def select_layout(components: "list[dict]", rules: dict, rules_source: str) -> dict:
    """Choose the first safe matching layout rule and report skipped rules."""
    counts = _compute_counts(components)
    skipped_rules = []
    selected = None

    for rule in rules.get("rules", []):
        try:
            matched = bool(safe_eval_condition(rule["condition"], counts))
        except (UnsafeConditionError, SyntaxError, TypeError, ValueError, ZeroDivisionError) as exc:
            skipped_rules.append({"id": rule.get("id"), "reason": str(exc)})
            continue
        if matched:
            selected = rule
            break

    if selected is None:
        decision = {
            "selectedLayout": "Home",
            "sectionTemplate": "OneColumn",
            "ruleApplied": "DEFAULT",
            "rationale": "No rule matched; falling back to the default Home/OneColumn layout.",
        }
    else:
        decision = {
            "selectedLayout": selected["layout"],
            "sectionTemplate": selected["sectionTemplate"],
            "ruleApplied": selected["id"],
            "rationale": selected["rationale"],
        }

    decision["pnpFlag"] = f"-LayoutType {decision['selectedLayout']}"
    decision["rulesSource"] = rules_source
    decision["skippedRules"] = skipped_rules

    if not components:
        outcome = outcomes.make_outcome("Empty", "No components to select a layout from")
    elif skipped_rules:
        outcome = outcomes.make_outcome(
            "Partial",
            f"{len(skipped_rules)} rule(s) skipped as malformed/unsafe: "
            f"{', '.join(str(s['id']) for s in skipped_rules)}",
        )
    else:
        outcome = outcomes.make_outcome("Observed", f"layout selected via rule {decision['ruleApplied']}")

    decision["outcome"] = outcome
    return decision


def main(argv: "list[str] | None" = None) -> int:
    """Read a component model and rules, then write one layout decision."""
    parser = argparse.ArgumentParser(description="Select a modern layout for a classified component model.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--rules")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Unavailable: input component model file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        model = json.loads(input_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed: could not parse input component model file: {exc}", file=sys.stderr)
        return 1

    rules_path = Path(args.rules) if args.rules else _PACKAGED_RULES
    if not rules_path.is_file():
        print(f"Unavailable: layout rules file not found: {rules_path}", file=sys.stderr)
        return 1

    try:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed: could not parse layout rules file: {exc}", file=sys.stderr)
        return 1

    decision = select_layout(model.get("components", []), rules, str(rules_path))

    output_path = Path(args.output)
    output_path.write_text(json.dumps(decision, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
