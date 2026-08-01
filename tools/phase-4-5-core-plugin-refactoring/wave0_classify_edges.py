"""
Wave 0 Step 6: classify each dependency-graph edge.

Nine-value classification (constructed for this Wave 0 run — the plan's "same nine-value
classification as Revision 2" refers to an earlier plan revision not present in this repository's
history; no authoritative nine-value list could be located, so this classification is built fresh,
grounded in the four active target domain plugins named in CLAUDE.md/the approved spec, and is
explicitly PROVISIONAL pending Wave 1's human decision checkpoint, consistent with the plan's own
decision-deferral pattern):

  SOURCE_EXTRACTION_INTERNAL          - both endpoints proposed-owned by source-document-extraction
  KNOWLEDGE_ANALYSIS_INTERNAL         - both endpoints proposed-owned by knowledge-analysis
  CANONICAL_KNOWLEDGE_INTERNAL        - both endpoints proposed-owned by canonical-knowledge
  KNOWLEDGE_PUBLICATION_INTERNAL      - both endpoints proposed-owned by knowledge-publication
  SHARED_CONTRACT_CANDIDATE           - target is contracts.py/hashing.py/path_safety.py (candidates
                                         for extraction into contracts/python per Wave 1)
  CLI_ORCHESTRATION_EDGE              - source is cli.py (orchestrates all domains; not itself
                                         owned by any one domain)
  SHAREPOINT_DEFERRED_EDGE            - either endpoint is a sharepoint_*.py module (belongs to the
                                         deferred sharepoint-publication plugin per CLAUDE.md, out
                                         of Phase 4.5's active scope)
  CROSS_DOMAIN_REQUIRES_HUMAN_DECISION - endpoints proposed-owned by two different active domains
  UNCLASSIFIED_REQUIRES_HUMAN_DECISION - proposed owner could not be heuristically assigned
"""
from __future__ import annotations

# Provisional per-script domain ownership heuristic — see module docstring. Confirmed/replaced by
# Wave 1 Step 1 (analyze_structure.py split decision) and Step 6 (wave-1-decisions.json).
PROPOSED_OWNER_DOMAIN: dict[str, str] = {
    "scripts/analyze_structure.py": "knowledge-analysis",
    "scripts/plans.py": "knowledge-analysis",
    "scripts/topic_grouping.py": "knowledge-analysis",
    "scripts/pandoc_validate.py": "knowledge-analysis",
    "scripts/dependencies.py": "source-document-extraction",
    "scripts/emf_convert.py": "source-document-extraction",
    "scripts/convert.py": "canonical-knowledge",
    "scripts/canonical_package.py": "canonical-knowledge",
    "scripts/chunking.py": "canonical-knowledge",
    "scripts/dispositions.py": "canonical-knowledge",
    "scripts/identity.py": "canonical-knowledge",
    "scripts/media_disposition.py": "canonical-knowledge",
    "scripts/package.py": "canonical-knowledge",
    "scripts/validate_canonical.py": "canonical-knowledge",
    "scripts/atomic_output.py": "canonical-knowledge",
    "scripts/pandoc_fixes/attrs.py": "canonical-knowledge",
    "scripts/pandoc_fixes/footnotes.py": "canonical-knowledge",
    "scripts/pandoc_fixes/heading_emphasis.py": "canonical-knowledge",
    "scripts/pandoc_fixes/images.py": "canonical-knowledge",
    "scripts/pandoc_fixes/tables.py": "canonical-knowledge",
    "scripts/pandoc_fixes/toc.py": "canonical-knowledge",
    "scripts/publication_map.py": "knowledge-publication",
    "scripts/renderers/multipage_markdown.py": "knowledge-publication",
    "scripts/renderers/protocol.py": "knowledge-publication",
    "scripts/renderers/validate_rendered.py": "knowledge-publication",
    "scripts/contracts.py": "shared-contract-candidate",
    "scripts/hashing.py": "shared-contract-candidate",
    "scripts/path_safety.py": "shared-contract-candidate",
    "scripts/cli.py": "cli-orchestration",
    "scripts/sharepoint_cli.py": "sharepoint-publication-deferred",
    "scripts/sharepoint_dry_run.py": "sharepoint-publication-deferred",
    "scripts/sharepoint_package.py": "sharepoint-publication-deferred",
    "scripts/sharepoint_reconcile.py": "sharepoint-publication-deferred",
}


def classify_edge(edge: dict) -> str:
    frm, to = edge["from"], edge["to"]
    frm_owner = PROPOSED_OWNER_DOMAIN.get(frm)
    to_owner = PROPOSED_OWNER_DOMAIN.get(to)

    if frm == "scripts/cli.py":
        return "CLI_ORCHESTRATION_EDGE"
    if to_owner == "sharepoint-publication-deferred" or frm_owner == "sharepoint-publication-deferred":
        return "SHAREPOINT_DEFERRED_EDGE"
    if to_owner == "shared-contract-candidate":
        return "SHARED_CONTRACT_CANDIDATE"
    if frm_owner is None or to_owner is None:
        return "UNCLASSIFIED_REQUIRES_HUMAN_DECISION"
    if frm_owner == to_owner:
        domain_map = {
            "source-document-extraction": "SOURCE_EXTRACTION_INTERNAL",
            "knowledge-analysis": "KNOWLEDGE_ANALYSIS_INTERNAL",
            "canonical-knowledge": "CANONICAL_KNOWLEDGE_INTERNAL",
            "knowledge-publication": "KNOWLEDGE_PUBLICATION_INTERNAL",
        }
        return domain_map.get(frm_owner, "UNCLASSIFIED_REQUIRES_HUMAN_DECISION")
    return "CROSS_DOMAIN_REQUIRES_HUMAN_DECISION"


def classify_all(graph: dict) -> list[dict]:
    return [{**edge, "classification": classify_edge(edge)} for edge in graph["edges"]]
