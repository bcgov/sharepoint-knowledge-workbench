"""
Wave 0 Step 6: classify each dependency-graph edge.

Revision 2 (2026-08-01, human review): separates two previously conflated concepts into
independent fields per edge, per reviewer instruction:

  dependency_classification - what kind of coupling the edge represents
  proposed_source_domain    - provisional target-plugin ownership of the "from" script
  proposed_target_domain    - provisional target-plugin ownership of the "to" script
  disposition               - what Wave 0 does with this edge (accept / defer to Wave 1 / etc.)
  rationale                 - one-line human-readable reason

**Provenance note:** the reviewer's instruction states this `dependency_classification`
vocabulary was "already established" in the approved specification. A repository-wide search
(`grep -rl` across every tracked file) found zero occurrences of these value names anywhere in
this repository, including the approved spec and plan — so that specific provenance claim could
not be verified and is not repeated here. The vocabulary below is adopted anyway, on the
reviewer's/user's direct authority in this Wave 0 correction pass, not represented as pre-existing
approved doctrine.

dependency_classification values:
  VALID_FORWARD_DEPENDENCY - source's domain plausibly should depend on target's domain
  CROSS_DOMAIN_UTILITY     - target is a small shared helper used across multiple domains
  SOURCE_FORMAT_COUPLING   - edge concerns raw source-document/extraction concerns
  PRESENTATION_COUPLING    - edge concerns rendering/publication reading canonical internals
  SHARED_CONTRACT          - target is a contracts.py/hashing.py/path_safety.py-style candidate
                              for the neutral contracts distribution
  CLI_ORCHESTRATION        - source is cli.py, orchestrating across all domains
  TEST_ONLY_DEPENDENCY     - edge only appears in test code, not production code (none observed
                              in this graph — the graph is scripts/-only by construction)
  HISTORICAL_OR_DEAD       - edge appears unused / dead code (requires confirmation, never assumed)
  REVERSE_DEPENDENCY       - target's domain conventionally depends on source's, not vice versa
                              (reserved: classify_edge() has no logic to detect this yet, since it
                              would require a settled forward-dependency convention per domain
                              pair, which does not exist until Wave 1's decisions are made; no
                              edge in the current 58-edge graph is assigned this value)

proposed_source_domain / proposed_target_domain values:
  SOURCE_DOCUMENT_EXTRACTION, KNOWLEDGE_ANALYSIS, CANONICAL_KNOWLEDGE, KNOWLEDGE_PUBLICATION,
  NEUTRAL_CONTRACT_DISTRIBUTION, REPOSITORY_ORCHESTRATION, OUT_OF_PHASE_4_5_SCOPE, UNRESOLVED

disposition values:
  PROVISIONALLY_ACCEPTED, REQUIRES_HUMAN_DECISION, OUT_OF_SCOPE_RETAIN_IN_PLACE,
  HISTORICAL_OR_DEAD_REQUIRES_CONFIRMATION
"""
from __future__ import annotations

DEPENDENCY_CLASSIFICATIONS = {
    "VALID_FORWARD_DEPENDENCY",
    "REVERSE_DEPENDENCY",
    "CROSS_DOMAIN_UTILITY",
    "SOURCE_FORMAT_COUPLING",
    "PRESENTATION_COUPLING",
    "SHARED_CONTRACT",
    "CLI_ORCHESTRATION",
    "TEST_ONLY_DEPENDENCY",
    "HISTORICAL_OR_DEAD",
}

PROPOSED_DOMAINS = {
    "SOURCE_DOCUMENT_EXTRACTION",
    "KNOWLEDGE_ANALYSIS",
    "CANONICAL_KNOWLEDGE",
    "KNOWLEDGE_PUBLICATION",
    "NEUTRAL_CONTRACT_DISTRIBUTION",
    "REPOSITORY_ORCHESTRATION",
    "OUT_OF_PHASE_4_5_SCOPE",
    "UNRESOLVED",
}

DISPOSITIONS = {
    "PROVISIONALLY_ACCEPTED",
    "REQUIRES_HUMAN_DECISION",
    "OUT_OF_SCOPE_RETAIN_IN_PLACE",
    "HISTORICAL_OR_DEAD_REQUIRES_CONFIRMATION",
}

# Per-script proposed domain ownership, taken directly from the approved plan's own "Known File
# Inventory" table (docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-
# refactoring.md, "Provisional domain" column) rather than invented fresh — that table already
# exists as real project data and takes precedence over any heuristic. Three files the plan itself
# marks as split/duplicated across domains (analyze_structure.py, convert.py, atomic_output.py)
# are mapped to UNRESOLVED here, matching the plan's own statement that their domain is pending a
# Wave 1 decision (Step 1 for analyze_structure.py; convert.py and atomic_output.py are not yet
# split by any wave, so a single owner cannot be asserted). Confirmed/replaced by Wave 1 Step 1
# and Step 6 (wave-1-decisions.json).
PROPOSED_OWNER_DOMAIN: dict[str, str] = {
    "scripts/analyze_structure.py": "UNRESOLVED",  # plan: "split — Wave 1 Step 1"
    "scripts/plans.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/topic_grouping.py": "KNOWLEDGE_ANALYSIS",  # plan table
    "scripts/pandoc_validate.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/dependencies.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/emf_convert.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/convert.py": "UNRESOLVED",  # plan: "split source-extraction/canonical-knowledge"
    "scripts/canonical_package.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/chunking.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/dispositions.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/identity.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/media_disposition.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/package.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/validate_canonical.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/atomic_output.py": "UNRESOLVED",  # plan: "duplicated: canonical-knowledge + knowledge-publication"
    "scripts/pandoc_fixes/attrs.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan: "pandoc_fixes/ (6 modules) -> source-document-extraction"
    "scripts/pandoc_fixes/footnotes.py": "SOURCE_DOCUMENT_EXTRACTION",
    "scripts/pandoc_fixes/heading_emphasis.py": "SOURCE_DOCUMENT_EXTRACTION",
    "scripts/pandoc_fixes/images.py": "SOURCE_DOCUMENT_EXTRACTION",
    "scripts/pandoc_fixes/tables.py": "SOURCE_DOCUMENT_EXTRACTION",
    "scripts/pandoc_fixes/toc.py": "SOURCE_DOCUMENT_EXTRACTION",
    "scripts/publication_map.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/renderers/multipage_markdown.py": "KNOWLEDGE_PUBLICATION",  # plan: "renderers/ (3 modules) -> knowledge-publication"
    "scripts/renderers/protocol.py": "KNOWLEDGE_PUBLICATION",
    "scripts/renderers/validate_rendered.py": "KNOWLEDGE_PUBLICATION",
    # NOTE: the plan's table also calls contracts.py "split" (like analyze_structure.py/convert.py/
    # atomic_output.py, which are mapped to UNRESOLVED below) — but unlike those three, its split
    # destination is a single, already-named target domain (NEUTRAL_CONTRACT_DISTRIBUTION), not an
    # ambiguous choice between two active domains. Deliberately mapped to a concrete domain rather
    # than UNRESOLVED for that reason, not an oversight.
    "scripts/contracts.py": "NEUTRAL_CONTRACT_DISTRIBUTION",
    "scripts/hashing.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/path_safety.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/cli.py": "REPOSITORY_ORCHESTRATION",  # plan: "compatibility orchestrator (not moved)"
    "scripts/sharepoint_cli.py": "OUT_OF_PHASE_4_5_SCOPE",  # plan table
    "scripts/sharepoint_dry_run.py": "OUT_OF_PHASE_4_5_SCOPE",  # plan table
    "scripts/sharepoint_package.py": "OUT_OF_PHASE_4_5_SCOPE",  # plan table
    "scripts/sharepoint_reconcile.py": "OUT_OF_PHASE_4_5_SCOPE",  # plan table
}

_INTRA_DOMAIN_CLASSIFICATION = {
    "SOURCE_DOCUMENT_EXTRACTION": "VALID_FORWARD_DEPENDENCY",
    "KNOWLEDGE_ANALYSIS": "VALID_FORWARD_DEPENDENCY",
    "CANONICAL_KNOWLEDGE": "VALID_FORWARD_DEPENDENCY",
    "KNOWLEDGE_PUBLICATION": "VALID_FORWARD_DEPENDENCY",
}


def classify_edge(edge: dict) -> dict:
    frm, to = edge["from"], edge["to"]
    # Distinguish two different reasons a script has no single settled domain:
    #  - not present in PROPOSED_OWNER_DOMAIN at all -> genuinely unrecognized (HISTORICAL_OR_DEAD)
    #  - present, mapped to "UNRESOLVED" -> the plan itself flags this file as split/duplicated,
    #    pending a real Wave 1 decision (analyze_structure.py, convert.py, atomic_output.py)
    frm_known = frm in PROPOSED_OWNER_DOMAIN
    to_known = to in PROPOSED_OWNER_DOMAIN
    frm_domain = PROPOSED_OWNER_DOMAIN.get(frm, "UNRESOLVED")
    to_domain = PROPOSED_OWNER_DOMAIN.get(to, "UNRESOLVED")

    if frm == "scripts/cli.py":
        dep_class = "CLI_ORCHESTRATION"
        disposition = "PROVISIONALLY_ACCEPTED"
        rationale = "cli.py orchestrates across all domains by design; not itself domain-owned."
    elif not frm_known or not to_known:
        dep_class = "HISTORICAL_OR_DEAD"
        disposition = "HISTORICAL_OR_DEAD_REQUIRES_CONFIRMATION"
        rationale = "One or both endpoints are not present in the plan's Known File Inventory table; confirm whether this edge is live before Wave 1."
    elif to_domain == "OUT_OF_PHASE_4_5_SCOPE" or frm_domain == "OUT_OF_PHASE_4_5_SCOPE":
        dep_class = "CROSS_DOMAIN_UTILITY"
        disposition = "OUT_OF_SCOPE_RETAIN_IN_PLACE"
        rationale = "Touches a sharepoint_*.py module; sharepoint-publication is a deferred plugin per CLAUDE.md, out of Phase 4.5's active scope."
    elif to_domain == "NEUTRAL_CONTRACT_DISTRIBUTION":
        dep_class = "SHARED_CONTRACT"
        disposition = "PROVISIONALLY_ACCEPTED"
        rationale = "Target is a contracts.py-style candidate for the neutral contracts distribution."
    elif frm_domain == "UNRESOLVED" or to_domain == "UNRESOLVED":
        dep_class = "CROSS_DOMAIN_UTILITY"
        disposition = "REQUIRES_HUMAN_DECISION"
        rationale = "One or both endpoints are explicitly flagged in the plan's Known File Inventory as split/duplicated across domains (analyze_structure.py, convert.py, or atomic_output.py); domain cannot be asserted until that Wave 1 decision is made."
    elif frm_domain == to_domain:
        dep_class = _INTRA_DOMAIN_CLASSIFICATION[frm_domain]
        disposition = "PROVISIONALLY_ACCEPTED"
        rationale = f"Both endpoints proposed-owned by {frm_domain}; intra-domain dependency."
    elif frm_domain == "KNOWLEDGE_PUBLICATION" and to_domain == "CANONICAL_KNOWLEDGE":
        dep_class = "PRESENTATION_COUPLING"
        disposition = "REQUIRES_HUMAN_DECISION"
        rationale = "Renderer currently accesses canonical implementation rather than a public contract."
    elif to_domain == "SOURCE_DOCUMENT_EXTRACTION" or frm_domain == "SOURCE_DOCUMENT_EXTRACTION":
        dep_class = "SOURCE_FORMAT_COUPLING"
        disposition = "REQUIRES_HUMAN_DECISION"
        rationale = "Edge crosses into/out of source-document-extraction's proposed domain; needs an explicit Wave 1 boundary decision."
    else:
        dep_class = "CROSS_DOMAIN_UTILITY"
        disposition = "REQUIRES_HUMAN_DECISION"
        rationale = f"Crosses proposed domains {frm_domain} -> {to_domain}; needs an explicit Wave 1 boundary decision (move code, or promote target to a shared contract)."

    return {
        **edge,
        "dependency_classification": dep_class,
        "proposed_source_domain": frm_domain,
        "proposed_target_domain": to_domain,
        "disposition": disposition,
        "rationale": rationale,
    }


def classify_all(graph: dict) -> list[dict]:
    return [classify_edge(edge) for edge in graph["edges"]]


def validate_classified_edges(classified: list[dict]) -> list[str]:
    """Returns a list of validation error strings; empty list means all checks passed."""
    errors: list[str] = []
    for i, e in enumerate(classified):
        if e.get("dependency_classification") not in DEPENDENCY_CLASSIFICATIONS:
            errors.append(f"edge {i} ({e.get('from')} -> {e.get('to')}): invalid dependency_classification {e.get('dependency_classification')!r}")
        if e.get("proposed_source_domain") not in PROPOSED_DOMAINS:
            errors.append(f"edge {i} ({e.get('from')} -> {e.get('to')}): invalid proposed_source_domain {e.get('proposed_source_domain')!r}")
        if e.get("proposed_target_domain") not in PROPOSED_DOMAINS:
            errors.append(f"edge {i} ({e.get('from')} -> {e.get('to')}): invalid proposed_target_domain {e.get('proposed_target_domain')!r}")
        if e.get("disposition") not in DISPOSITIONS:
            errors.append(f"edge {i} ({e.get('from')} -> {e.get('to')}): invalid disposition {e.get('disposition')!r}")
        if not e.get("rationale"):
            errors.append(f"edge {i} ({e.get('from')} -> {e.get('to')}): missing rationale")
    return errors
