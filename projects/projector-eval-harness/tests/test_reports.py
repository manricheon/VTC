from __future__ import annotations

import json
from pathlib import Path

from vtc_projector_eval.reports import build_report, checkpoint_blockers, write_report


def _make_minimal_sources(repo_root: Path) -> None:
    fourier = repo_root / "external" / "Fourier-Compressor"
    divt = repo_root / "external" / "DiVT"
    (fourier / "fourier_compressor" / "integrations" / "llava").mkdir(parents=True)
    (divt / "llava" / "model" / "multimodal_projector").mkdir(parents=True)
    (divt / "llava" / "model" / "language_model").mkdir(parents=True)
    (fourier / "pyproject.toml").write_text("[project]\nname='Fourier-Compressor'\n", encoding="utf-8")
    (fourier / "fourier_compressor" / "integrations" / "llava" / "monkey_patch.py").write_text(
        "def apply_to_llava(reserve=12): pass\n",
        encoding="utf-8",
    )
    (fourier / "fourier_compressor" / "compress.py").write_text(
        "def compress_square(features, reserve=12): pass\n",
        encoding="utf-8",
    )
    (divt / "pyproject.toml").write_text("[project]\nname='llava'\n", encoding="utf-8")
    (divt / "llava" / "model" / "multimodal_projector" / "builder.py").write_text(
        "class DiVT: pass\nthreshold = 0.65\n",
        encoding="utf-8",
    )
    (divt / "llava" / "model" / "language_model" / "llava_llama.py").write_text(
        "def generate(threshold=0.65): pass\n",
        encoding="utf-8",
    )


def test_checkpoint_blockers_report_missing_default_checkpoints(tmp_path: Path):
    blockers = checkpoint_blockers(tmp_path)

    assert any("whyisverysmart/Fourier-LLaVA-v1.5-7B-144" in blocker for blocker in blockers)
    assert any("weights/checkpoints/Fourier-LLaVA-v1.5-7B-144" in blocker for blocker in blockers)
    assert any("hyunlee86/llava-v1.5-7b-divt-0.65" in blocker for blocker in blockers)
    assert any("weights/checkpoints/llava-v1.5-7b-divt-0.65" in blocker for blocker in blockers)


def test_build_report_includes_sources_matrix_profiles_and_blockers(tmp_path: Path):
    _make_minimal_sources(tmp_path)
    profile_path = tmp_path / "profiles.jsonl"
    profile_path.write_text(
        json.dumps(
            {
                "model": "vtc_fourier_llava15",
                "task": "mme",
                "score": 1.0,
                "timings_s": {"total": 2.0},
                "token_counts": {"llm_visual_tokens": 144},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_report(
        repo_root=tmp_path,
        profiles=[profile_path],
        run_id="unit",
        preset="smoke",
        tasks="mme",
    )

    assert "# Projector Eval Benchmark Report" in report
    assert "run_id: `unit`" in report
    assert "Fourier-Compressor" in report
    assert "DiVT" in report
    assert "whyisverysmart/Fourier-LLaVA-v1.5-7B-144" in report
    assert "hyunlee86/llava-v1.5-7b-divt-0.65" in report
    assert "vtc_fourier_llava15" in report
    assert "vtc_divt_llava15" in report
    assert "vtc_fourier_llava15::mme" in report
    assert "missing checkpoint" in report


def test_build_report_marks_none_limit_for_full_runs(tmp_path: Path):
    _make_minimal_sources(tmp_path)

    report = build_report(
        repo_root=tmp_path,
        profiles=[],
        run_id="full",
        preset="full",
        tasks="mme",
        limit=None,
    )

    assert "| `vtc_fourier_llava15` | `mme` | none |" in report
    assert "| `vtc_divt_llava15` | `mme` | none |" in report


def test_build_report_includes_lmms_eval_result_scores(tmp_path: Path):
    _make_minimal_sources(tmp_path)
    result_path = tmp_path / "outputs" / "vtc_fourier_llava15" / "run_results.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps(
            {
                "config": {"model": "vtc_fourier_llava15", "limit": 1},
                "results": {"mme": {"acc,none": 0.75, "acc_stderr,none": 0.01}},
                "n-samples": {"mme": {"original": 10, "effective": 1}},
            }
        ),
        encoding="utf-8",
    )

    report = build_report(
        repo_root=tmp_path,
        profiles=[],
        result_paths=[tmp_path / "outputs"],
        run_id="unit",
        preset="smoke",
        tasks="mme",
    )

    assert "| `mme` | `acc` | 0.7500 | - | - |" in report
    assert f"- {result_path}" in report


def test_write_report_creates_parent_directory(tmp_path: Path):
    output_path = tmp_path / "docs" / "report.md"

    write_report("# Title\n", output_path)

    assert output_path.read_text(encoding="utf-8") == "# Title\n"
