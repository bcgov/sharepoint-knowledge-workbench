"""Tests for the evaluation mode: task files, run validation, deterministic scoring, per-arm summaries and report.

Purpose: scoring uses recorded facts (page overlap, substrings, counts); nothing depends on generated wording quality.

Key Input Dependencies: scripts/enrichment/evaluation.py.
"""
import json
import sys
from pathlib import Path

_plugin_dir = Path(__file__).resolve().parents[1]
_skill = (_plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills") \
    / "converting-sharepoint-documents"
sys.path.insert(0, str(_skill / "scripts" / "enrichment"))

import evaluation as ev  # noqa: E402

Q = {"id": "q1", "question": "Notice for annual leave?", "expected_pages": [2, 2], "expected_facts": ["10 days", "annual"]}


def _run(arm="topic_markdown", **changes):
    run = {"arm": arm, "question_id": "q1", "answer": "Annual leave needs 10 days notice.",
           "retrieved": [{"path": "Criminal_md/doc/02-leave.md", "pages": [2, 3]}],
           "citations": [{"path": "Criminal_md/doc/02-leave.md", "pages": [2, 2]}], "tokens": 1200, "latency_s": 4.5}
    run.update(changes)
    return run


def test_tasks_cover_every_question_and_arm(tmp_path):
    tasks = ev.build_tasks(tmp_path, [Q, {**Q, "id": "q2"}], {"native_pdf": ["m.pdf"]})
    assert len(tasks) == 2 * len(ev.ARMS)
    first = json.loads((tmp_path / "tasks" / "native_pdf__q1.json").read_text())
    assert first["allowed_materials"] == ["m.pdf"] and "authoritative" in first["instructions"]


def test_scoring_from_recorded_facts():
    score = ev.score_run(Q, _run())
    assert score["retrieval_accuracy"] == 1.0 and score["answer_completeness"] == 1.0
    assert score["citation_correctness"] == 1.0 and not score["failed_to_reach_source"]
    assert score["files_retrieved"] == 1 and score["tokens"] == 1200


def test_ai_navigation_files_do_not_count_as_authoritative_source():
    nav_only = _run("topic_markdown_with_navigation",
                    retrieved=[{"path": "doc/ai-navigation/index.md", "pages": [1, 3]}],
                    citations=[{"path": "doc/ai-navigation/topics/01-x.md", "pages": [2, 2]}])
    score = ev.score_run(Q, nav_only)
    assert score["failed_to_reach_source"] is True and score["citation_correctness"] == 0.0
    assert ev.is_authoritative("source-documents/m.pdf") and not ev.is_authoritative("a\\ai-navigation\\index.md")


def test_wrong_pages_missing_facts_and_no_citations():
    wrong = _run(answer="Not sure.", retrieved=[{"path": "doc/05.md", "pages": [9, 9]}], citations=[])
    score = ev.score_run(Q, wrong)
    assert (score["retrieval_accuracy"], score["answer_completeness"], score["citation_correctness"]) == (0.0, 0.0, 0.0)
    assert score["failed_to_reach_source"] is True


def test_run_validation_rejects_malformed_records():
    assert ev.validate_run(_run()) == []
    assert ev.validate_run("x") and ev.validate_run(_run(arm="other"))
    assert ev.validate_run(_run(retrieved=[{"pages": [1, 1]}])) and ev.validate_run(_run(tokens=-1))


def test_summary_counts_invalid_runs_and_model_failures_per_arm_and_report():
    runs = [_run("native_pdf"), _run("topic_markdown"), _run("topic_markdown", question_id="q9"),
            _run("topic_markdown", error="timeout", answer="", retrieved=[], citations=[], tokens=None)]
    summary = ev.summarize([Q], runs)
    assert summary["topic_markdown"]["runs"] == 2 and summary["topic_markdown"]["invalid_runs"] == 1
    assert summary["topic_markdown"]["failures_to_reach_source"] == 1
    assert summary["native_pdf"]["retrieval_accuracy"] == 1.0
    report = ev.render_report(summary)
    assert "| native_pdf |" in report and "this corpus" in report
    assert ev.summarize([Q], []) == {}
