from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_smoke_projector_eval_synthetic_writes_profile_report_and_stats(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    script_path = (
        repo_root
        / "projects"
        / "projector-eval-harness"
        / "scripts"
        / "smoke_projector_eval_synthetic.py"
    )
    out_dir = tmp_path / "smoke_projector_eval_synthetic"
    env = {
        **os.environ,
        "PYTHONPATH": (
            f"{repo_root / 'projects' / 'projector-eval-harness' / 'src'}"
            f"{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
        ),
    }

    result = subprocess.run(
        [sys.executable, str(script_path), "--out-dir", str(out_dir)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert "projector_models=2" in result.stdout
    assert "model_inference=not_run" in result.stdout
    assert "downloads=not_run" in result.stdout

    stats_path = out_dir / "stats.json"
    profile_path = out_dir / "profile.json"
    report_path = out_dir / "report.md"
    for path in (stats_path, profile_path, report_path):
        assert path.exists(), path

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")

    assert stats["projector_models"] == 2
    assert stats["smoke_tasks"] == 7
    assert stats["smoke_matrix_rows"] == 14
    assert stats["checkpoint_blockers"] == 2
    assert stats["downloads"] == "not_run"
    assert stats["model_inference"] == "not_run"
    assert stats["source_audit"]["fourier"]["status"] == "present"
    assert stats["source_audit"]["divt"]["status"] == "present"

    assert profile["project"]["track"] == "projector_eval"
    assert profile["project"]["policy_name"] == "synthetic_source_matrix_report"
    assert profile["token_counts"]["projector_models"] == 2
    assert profile["token_counts"]["smoke_matrix_rows"] == 14
    assert profile["task_metrics"]["score"] is None
    assert profile["timings_s"]["total"] > 0
    assert profile["notes"] == [
        "Synthetic projector eval smoke.",
        "No checkpoint download, dataset access, CUDA runtime, or model inference.",
    ]

    assert "# Projector Eval Benchmark Report" in report
    assert "Benchmark execution is blocked for real runs." in report
