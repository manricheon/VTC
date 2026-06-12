from __future__ import annotations

import json
from pathlib import Path

from vtc_projector_eval.profiles import summarize_profiles


def test_summarize_profiles_groups_by_model_and_task(tmp_path: Path):
    path = tmp_path / "profiles.jsonl"
    rows = [
        {
            "model": "vtc_fourier_llava15",
            "task": "mme",
            "score": 1.0,
            "timings_s": {"total": 4.0, "model_forward": 2.0},
            "token_counts": {"llm_visual_tokens": 144},
            "compression": {"visual_ratio": 0.25},
        },
        {
            "model": "vtc_fourier_llava15",
            "task": "mme",
            "score": 0.0,
            "total_time": 2.0,
            "llm_visual_tokens": 100,
        },
        {
            "model": "vtc_divt_llava15",
            "task": "pope",
            "score": 0.5,
            "total_time": 6.0,
        },
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    summary = summarize_profiles([path])

    assert summary["vtc_fourier_llava15::mme"]["count"] == 2
    assert summary["vtc_fourier_llava15::mme"]["mean_score"] == 0.5
    assert summary["vtc_fourier_llava15::mme"]["mean_total_time"] == 3.0
    assert summary["vtc_fourier_llava15::mme"]["mean_visual_tokens"] == 122.0
    assert summary["vtc_divt_llava15::pope"]["count"] == 1


def test_summarize_profiles_ignores_missing_paths(tmp_path: Path):
    summary = summarize_profiles([tmp_path / "missing.jsonl"])

    assert summary == {}
