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
  NEUTRAL_CONTRACT_DISTRIBUTION, NEUTRAL_RUNTIME_DISTRIBUTION, REPOSITORY_ORCHESTRATION,
  OUT_OF_PHASE_4_5_SCOPE, UNRESOLVED

  NEUTRAL_RUNTIME_DISTRIBUTION added in the Wave 1 correction pass (2026-08-01): the original
  8-value vocabulary above predates the human-approved decision to give atomic_output.py's
  atomicity primitives their own distribution (knowledge-workbench-runtime, spec §13c) rather than
  duplicating them or folding them into knowledge_workbench_contracts — a domain the original
  vocabulary's author could not have anticipated. Extended here, not silently invented; see
  docs/superpowers/plans/phase-4-5-evidence/wave-1-decisions.json's atomic_output_disposition.

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
    "NEUTRAL_RUNTIME_DISTRIBUTION",
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

# Per-script proposed domain ownership. Originally taken from the approved plan's own "Known File
# Inventory" table; updated 2026-08-01 (Wave 1 correction pass) to reflect the human-approved Wave
# 1 decisions in wave-1-decisions.json. THREE files remain UNRESOLVED here on purpose — each was
# approved for a FUNCTION-level split, not a whole-file reassignment to one domain:
#   - analyze_structure.py: see wave-1-analyze-structure-split-decision.md
#   - convert.py: see wave-1-shared-contract-decision.md
#   - atomic_output.py: see wave-1-shared-contract-decision.md and spec §13c —
#     create_staging_dir/promote go to the new NEUTRAL_RUNTIME_DISTRIBUTION, but
#     build_generator_info/write_generator_info (which import dependencies.py) are explicitly
#     NOT part of that distribution and stay duplicated per consuming domain instead, so this
#     file has no single settled owner either.
# A script-level dependency graph cannot represent "part of this file is domain A, part is domain
# B," so each of these three files' proposed_source_domain/proposed_target_domain stays UNRESOLVED
# at this whole-file granularity even though the underlying decision is no longer open — see
# classify_edge()'s disposition logic below, which treats edges touching any of these three as
# PROVISIONALLY_ACCEPTED (decision made, implementation is a later wave's job), not
# REQUIRES_HUMAN_DECISION (which would incorrectly imply the decision itself is still pending).
PROPOSED_OWNER_DOMAIN: dict[str, str] = {
    "scripts/analyze_structure.py": "UNRESOLVED",  # approved split — see wave-1-analyze-structure-split-decision.md
    "scripts/plans.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/topic_grouping.py": "KNOWLEDGE_ANALYSIS",  # plan table
    "scripts/pandoc_validate.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/dependencies.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/emf_convert.py": "SOURCE_DOCUMENT_EXTRACTION",  # plan table
    "scripts/convert.py": "UNRESOLVED",  # approved split — see wave-1-shared-contract-decision.md (run_pandoc_extraction -> source-document-extraction, rest -> canonical-knowledge)
    "scripts/canonical_package.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/chunking.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/dispositions.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/identity.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/media_disposition.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/package.py": "CANONICAL_KNOWLEDGE",  # plan table
    "scripts/validate_canonical.py": "CANONICAL_KNOWLEDGE",  # plan table
    # UNRESOLVED at whole-file granularity like analyze_structure.py/convert.py above — atomic_output.py
    # ALSO functionally splits per the approved decision: create_staging_dir/promote (no
    # dependencies.py dependency) -> NEUTRAL_RUNTIME_DISTRIBUTION; build_generator_info/
    # write_generator_info (which import dependencies.py, hence this file's edge to it) are NOT
    # extracted — each consuming domain implements its own thin wrapper instead. See
    # wave-1-shared-contract-decision.md and spec §13c.
    "scripts/atomic_output.py": "UNRESOLVED",
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
    elif to_domain == "NEUTRAL_RUNTIME_DISTRIBUTION":
        # RESERVED, not currently reachable: no PROPOSED_OWNER_DOMAIN entry maps directly to this
        # value today — atomic_output.py itself stays UNRESOLVED (see the dict's comment above),
        # since part of it goes to knowledge_workbench_runtime and part stays duplicated per-domain.
        # Kept for a future wave that might assign a script wholesale to this distribution (e.g. if
        # runtime/python's own files are ever scanned by this same tool).
        dep_class = "CROSS_DOMAIN_UTILITY"
        disposition = "PROVISIONALLY_ACCEPTED"
        rationale = "Target is wholly owned by the knowledge-workbench-runtime distribution — see spec §13c."
    elif frm_domain == "UNRESOLVED" or to_domain == "UNRESOLVED":
        touched = [f for f in (frm, to) if PROPOSED_OWNER_DOMAIN.get(f) == "UNRESOLVED"]
        dep_class = "CROSS_DOMAIN_UTILITY"
        disposition = "PROVISIONALLY_ACCEPTED"
        rationale = (
            f"{' and '.join(touched)} — approved for a FUNCTION-level split by Wave 1 (see "
            "wave-1-analyze-structure-split-decision.md / wave-1-shared-contract-decision.md) — "
            "the ownership decision is made, but a whole-script dependency graph cannot represent "
            "a per-function split; a later wave's implementation resolves this edge concretely "
            "when the file is physically split."
        )
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
