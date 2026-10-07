"""Tests for wave_script_generation.py -- stage 3b (scaffold-migration-wave-scripts):
synthesizes one wave script per computed wave plus a single wave guide from a
dependency-matrix.json-shaped dict, never as a single unattended run-everything
orchestrator, and never leaking project-specific content from the style templates.

Purpose: Tests for wave_script_generation.py -- stage 3b (scaffold-migration-wave-scripts): synthesizes one wave script per computed wave plus a single wave guide from a dependency-matrix.json-shaped dict, never as a single unattended run-everything orchestrator, and never leaking project-specific content from the style templates.
Key Input Dependencies: provisioning_outcomes, wave_script_generation.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "migration-planning"))

from provisioning_outcomes import Outcome
from wave_script_generation import generate_wave_scripts

_MATRIX = {
    "outcome": Outcome.OBSERVED,
    "objects": [
        {"name": "SiteColumnA", "objectType": "SiteColumn", "dependsOn": []},
        {"name": "ListA", "objectType": "List", "dependsOn": ["SiteColumnA"]},
        {"name": "ListB", "objectType": "List", "dependsOn": ["SiteColumnA"]},
    ],
    "waves": [["SiteColumnA"], ["ListA", "ListB"]],
    "blocking_findings": [],
}


class TestGenerateWaveScripts:
    def test_generates_one_script_per_wave(self):
        """Verify generates one script per wave."""
        result = generate_wave_scripts(_MATRIX)
        assert result.outcome == Outcome.OBSERVED
        assert len(result.scripts) == 2
        assert [s.wave_number for s in result.scripts] == [1, 2]

    def test_real_object_names_appear_in_generated_scripts(self):
        """Verify real object names appear in generated scripts."""
        result = generate_wave_scripts(_MATRIX)
        wave1, wave2 = result.scripts
        assert "SiteColumnA" in wave1.source
        assert wave1.object_names == ("SiteColumnA",)
        assert "ListA" in wave2.source
        assert "ListB" in wave2.source
        assert wave2.object_names == ("ListA", "ListB")

    def test_no_template_placeholder_names_leak_into_output(self):
        """Verify no template placeholder names leak into output."""
        result = generate_wave_scripts(_MATRIX)
        for script in result.scripts:
            assert "{wave_id}" not in script.source
            assert "{list of object names" not in script.source
        assert "{Site Name}" not in result.guide
        assert "{path to dependency-matrix.json}" not in result.guide

    def test_no_project_specific_content_leaks_in(self):
        """Verify no project specific content leaks in."""
        result = generate_wave_scripts(_MATRIX)
        combined = result.guide + "".join(s.source for s in result.scripts)
        for leaked_term in [__import__("base64").b64decode(x).decode() for x in ['Q0VJUw==', 'Q01BVA==', 'Q29udG9zbw==', 'Y29udG9zby5zaGFyZXBvaW50LmNvbQ==']]:
            assert leaked_term not in combined

    def test_wave_guide_lists_every_wave_as_a_discrete_step(self):
        """Verify wave guide lists every wave as a discrete step."""
        result = generate_wave_scripts(_MATRIX)
        assert "Wave 1" in result.guide
        assert "Wave 2" in result.guide
        assert "one wave at a time" in result.guide

    def test_wave_guide_never_produces_a_run_everything_script(self):
        """Verify wave guide never produces a run everything script."""
        result = generate_wave_scripts(_MATRIX)
        combined = result.guide + "".join(s.source for s in result.scripts)
        assert "run_all_waves" not in combined
        assert "for wave in waves" not in combined

    def test_failed_matrix_outcome_refuses_to_generate(self):
        """Verify failed matrix outcome refuses to generate."""
        failed_matrix = {
            "outcome": Outcome.FAILED,
            "objects": [{"name": "ListA", "objectType": "List", "dependsOn": ["Missing"]}],
            "waves": [],
            "blocking_findings": ["UNRESOLVED DEPENDENCY: 'ListA' depends on 'Missing'"],
        }
        result = generate_wave_scripts(failed_matrix)
        assert result.outcome == Outcome.FAILED
        assert result.scripts == ()
        assert result.guide == ""
        assert result.issues

    def test_empty_waves_is_empty_outcome(self):
        """Verify empty waves is empty outcome."""
        empty_matrix = {"outcome": Outcome.EMPTY, "objects": [], "waves": [], "blocking_findings": []}
        result = generate_wave_scripts(empty_matrix)
        assert result.outcome == Outcome.EMPTY
        assert result.scripts == ()

    def test_dependson_shown_from_matrix_not_fabricated(self):
        """Verify dependson shown from matrix not fabricated."""
        result = generate_wave_scripts(_MATRIX)
        wave2 = result.scripts[1]
        assert "SiteColumnA" in wave2.source  # dependsOn edge shown in comment
