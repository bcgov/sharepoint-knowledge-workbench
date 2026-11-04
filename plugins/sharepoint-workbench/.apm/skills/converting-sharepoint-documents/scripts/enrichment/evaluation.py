"""Evaluation mode for the enrichment layer: compare four retrieval arms on the same questions (agent-mediated).

Purpose: measure whether structure and AI navigation aids help an agent reach the smallest authoritative unit. This
module writes task files, validates the run records a host agent writes, scores them deterministically from recorded
facts (no model judges anything) and summarises per arm. Results show this corpus and agent only.

Key Input Dependencies: a questions file, run records written by the host agent, page provenance from the page map.

Key Functions Index:
    - build_tasks()
    - validate_run()
    - is_authoritative()
    - score_run()
    - summarize()
    - render_report()
"""

import json
from pathlib import Path

ARMS = ("native_pdf", "large_markdown", "topic_markdown", "topic_markdown_with_navigation")

TASK_INSTRUCTIONS = (
    "Answer the question using only the materials allowed for this arm. Record every file you opened in `retrieved` "
    "(path and, when known, source pages [first, last]), cite sources in `citations`, and write the run record JSON to "
    "`runs/<arm>__<question id>.json`. Prefer authoritative extracted content or the original PDF as the factual basis; "
    "AI-generated navigation aids are for finding content, not for citing facts."
)


def _page_overlap(a, b) -> bool:
    return bool(a and b) and a[0] <= b[1] and b[0] <= a[1]


def build_tasks(eval_dir: Path, questions: list, materials: dict, arms=ARMS) -> list:
    """Write `tasks/<arm>__<id>.json` for every question and arm. `materials` maps arm to a description of what the
    agent may open (paths). Questions: {id, question, expected_pages: [first, last], expected_facts: [str]}."""
    eval_dir = Path(eval_dir)
    (eval_dir / "tasks").mkdir(parents=True, exist_ok=True)
    tasks = []
    for q in questions:
        for arm in arms:
            task = {"arm": arm, "question_id": q["id"], "question": q["question"],
                    "allowed_materials": materials.get(arm, []), "instructions": TASK_INSTRUCTIONS}
            (eval_dir / "tasks" / f"{arm}__{q['id']}.json").write_text(json.dumps(task, indent=2), encoding="utf-8")
            tasks.append(task)
    return tasks


def validate_run(run) -> list:
    """Problems with one run record; empty when it can be scored."""
    if not isinstance(run, dict):
        return ["run must be an object"]
    problems = []
    if run.get("arm") not in ARMS:
        problems.append(f"arm must be one of {ARMS}")
    if not run.get("question_id"):
        problems.append("question_id is missing")
    if not isinstance(run.get("answer", ""), str):
        problems.append("answer must be text")
    for field in ("retrieved", "citations"):
        items = run.get(field, [])
        if not isinstance(items, list) or not all(isinstance(i, dict) and isinstance(i.get("path"), str) for i in items):
            problems.append(f"{field} must be a list of objects with a path")
    for field in ("tokens", "latency_s"):
        value = run.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
            problems.append(f"{field} must be a non-negative number or null")
    return problems


def is_authoritative(path: str) -> bool:
    """The original PDF or deterministic extraction, never anything under `ai-navigation/`."""
    p = path.replace("\\", "/").lower()
    return "ai-navigation/" not in p and p.endswith((".pdf", ".md"))


def score_run(question: dict, run: dict) -> dict:
    """Metrics for one run from recorded facts only (substring and page overlap; no model judging)."""
    expected = question.get("expected_pages")
    retrieved, citations = run.get("retrieved", []), run.get("citations", [])
    reached = any(is_authoritative(r["path"]) and _page_overlap(r.get("pages"), expected) for r in retrieved)
    good = [c for c in citations if is_authoritative(c["path"]) and _page_overlap(c.get("pages"), expected)]
    facts = question.get("expected_facts", [])
    answer = run.get("answer", "")
    found = [f for f in facts if f.lower() in answer.lower()]
    return {
        "arm": run["arm"], "question_id": run["question_id"],
        "retrieval_accuracy": 1.0 if reached else 0.0,
        "answer_completeness": len(found) / len(facts) if facts else None,
        "citation_correctness": len(good) / len(citations) if citations else 0.0,
        "citations": len(citations),
        "tokens": run.get("tokens"), "latency_s": run.get("latency_s"),
        "files_retrieved": len(retrieved), "answer_length": len(answer),
        "failed_to_reach_source": not reached,
        "error": run.get("error"),
    }


def _mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 3) if values else None


def summarize(questions: list, runs: list) -> dict:
    """Per-arm means over scored runs; invalid runs are counted, not scored. Missing runs show in `runs` vs `questions`."""
    by_id = {q["id"]: q for q in questions}
    arms = {}
    for run in runs:
        arm = run.get("arm") if isinstance(run, dict) else None
        bucket = arms.setdefault(arm, {"scores": [], "invalid": 0})
        if validate_run(run) or run["question_id"] not in by_id:
            bucket["invalid"] += 1
            continue
        bucket["scores"].append(score_run(by_id[run["question_id"]], run))
    summary = {}
    for arm, bucket in arms.items():
        s = bucket["scores"]
        summary[arm] = {
            "runs": len(s), "invalid_runs": bucket["invalid"], "questions": len(questions),
            "retrieval_accuracy": _mean(x["retrieval_accuracy"] for x in s),
            "answer_completeness": _mean(x["answer_completeness"] for x in s),
            "citation_correctness": _mean(x["citation_correctness"] for x in s),
            "mean_tokens": _mean(x["tokens"] for x in s),
            "mean_latency_s": _mean(x["latency_s"] for x in s),
            "mean_files_retrieved": _mean(x["files_retrieved"] for x in s),
            "mean_answer_length": _mean(x["answer_length"] for x in s),
            "failures_to_reach_source": sum(1 for x in s if x["failed_to_reach_source"]),
        }
    return summary


def render_report(summary: dict) -> str:
    """Markdown table of the summary. Ends with the caveat that results apply to this corpus and agent only."""
    cols = ["runs", "invalid_runs", "retrieval_accuracy", "answer_completeness", "citation_correctness", "mean_tokens",
            "mean_latency_s", "mean_files_retrieved", "mean_answer_length", "failures_to_reach_source"]
    lines = ["| arm | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for arm in [a for a in ARMS if a in summary] + [a for a in summary if a not in ARMS]:
        lines.append(f"| {arm} | " + " | ".join("n/a" if summary[arm][c] is None else str(summary[arm][c]) for c in cols) + " |")
    lines.append("\nResults describe this corpus, question set and agent only; they are not general claims.")
    return "\n".join(lines) + "\n"
