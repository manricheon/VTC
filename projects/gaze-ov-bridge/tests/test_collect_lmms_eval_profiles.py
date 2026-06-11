from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_collect_lmms_eval_profiles_summarizes_backend_means(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    profile_path = tmp_path / "profiles.jsonl"
    rows = [
        {
            "backend": "autogaze_codec_anchor112",
            "total_time": 2.0,
            "model_time": 1.0,
            "llm_visual_tokens": 10,
            "project_a_vs_dense_visual_ratio": 0.25,
            "score": 1,
        },
        {
            "backend": "autogaze_codec_anchor112",
            "total_time": 4.0,
            "model_time": 3.0,
            "llm_visual_tokens": 20,
            "project_a_vs_dense_visual_ratio": 0.5,
            "score": 0,
        },
        {
            "backend": "frames",
            "total_time": 6.0,
            "model_time": 5.0,
            "llm_visual_tokens": 64,
            "project_a_vs_dense_visual_ratio": 1.0,
        },
    ]
    profile_path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts/collect_lmms_eval_profiles.py"), str(profile_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "autogaze_codec_anchor112" in result.stdout
    assert "frames" in result.stdout
    assert "3.0000" in result.stdout
    assert "2.0000" in result.stdout
    assert "15.0000" in result.stdout
    assert "0.5000" in result.stdout


def test_collect_lmms_eval_profiles_handles_missing_profiles(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts/collect_lmms_eval_profiles.py"), str(tmp_path / "missing.jsonl")],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "no profiles found" in result.stdout.lower()
