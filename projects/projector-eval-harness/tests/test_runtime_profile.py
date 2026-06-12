from __future__ import annotations

import json
from pathlib import Path

from vtc_projector_eval.runtime_profile import record_generation_profiles


class FakeRequest:
    def __init__(self, args):
        self.args = args


def test_record_generation_profiles_writes_one_record_per_request(tmp_path: Path):
    path = tmp_path / "profiles" / "run.jsonl"
    requests = [
        FakeRequest(("prompt", {"max_new_tokens": 4}, None, 7, "mme", "test")),
        FakeRequest(("prompt", {"max_new_tokens": 4}, None, 8, "pope", "test")),
    ]

    record_generation_profiles(
        path=path,
        model="vtc_fourier_llava15",
        policy_name="fourier_reserve_12",
        requests=requests,
        outputs=["yes", "no"],
        total_time_s=3.0,
        token_counts={"llm_visual_tokens": 144},
    )

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [row["task"] for row in rows] == ["mme", "pope"]
    assert rows[0]["sample_id"] == 7
    assert rows[0]["timings_s"]["total"] == 1.5
    assert rows[0]["token_counts"]["llm_visual_tokens"] == 144
    assert rows[0]["notes"] == ["score unavailable at model wrapper stage"]


def test_record_generation_profiles_skips_none_path(tmp_path: Path):
    record_generation_profiles(
        path=None,
        model="vtc_divt_llava15",
        policy_name="divt_threshold_0.65",
        requests=[],
        outputs=[],
        total_time_s=0.0,
        token_counts={},
    )

    assert list(tmp_path.iterdir()) == []
