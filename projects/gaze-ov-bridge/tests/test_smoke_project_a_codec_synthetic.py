from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def test_smoke_project_a_codec_synthetic_writes_profiled_artifacts(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    script_path = (
        repo_root
        / "projects"
        / "gaze-ov-bridge"
        / "scripts"
        / "smoke_project_a_codec_synthetic.py"
    )
    out_dir = tmp_path / "smoke_project_a_codec_synthetic"

    result = subprocess.run(
        [sys.executable, str(script_path), "--out-dir", str(out_dir)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "selected_112_blocks=2" in result.stdout
    assert "confirms_no_hard_union_default=True" in result.stdout

    stats_path = out_dir / "stats.json"
    profile_path = out_dir / "profile.json"
    decoded_path = out_dir / "decoded_entries.json"
    selected_blocks_path = out_dir / "selected_blocks.json"
    src_positions_path = out_dir / "src_positions.npy"

    for path in (
        stats_path,
        profile_path,
        decoded_path,
        selected_blocks_path,
        src_positions_path,
    ):
        assert path.exists(), path

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    decoded_entries = json.loads(decoded_path.read_text(encoding="utf-8"))
    selected_blocks = json.loads(selected_blocks_path.read_text(encoding="utf-8"))
    src_positions = np.load(src_positions_path)

    assert {entry["scale"] for entry in decoded_entries} == {28, 56, 112, 224}
    assert len(decoded_entries) == 5
    assert selected_blocks == [[0, 0, 0], [0, 1, 2]]
    assert stats["selected_112_blocks"] == 2
    assert stats["raw_patch_tokens"] == 8
    assert stats["llm_visual_tokens"] == 2
    assert stats["raw_patch_tokens"] == stats["selected_112_blocks"] * 4
    assert stats["llm_visual_tokens"] == stats["selected_112_blocks"]
    assert stats["confirms_no_hard_union_default"] is True
    assert [0, 0, 1] not in selected_blocks
    assert [0, 3, 3] not in selected_blocks

    assert src_positions.dtype.kind in {"i", "u"}
    assert src_positions.tolist() == [
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 1],
        [0, 2, 4],
        [0, 2, 5],
        [0, 3, 4],
        [0, 3, 5],
    ]

    assert profile["project"]["track"] == "project_a_codec"
    assert profile["project"]["policy_name"] == "anchor112_default"
    assert profile["timings_s"]["total"] > 0
    assert profile["timings_s"]["decode"] > 0
    assert profile["timings_s"]["selector"] > 0
    assert profile["timings_s"]["src_positions"] > 0
    assert profile["token_counts"]["autogaze_valid_tokens_total"] == 5
    assert profile["token_counts"]["selected_112_blocks"] == 2
    assert profile["token_counts"]["project_a_raw_patch_tokens"] == 8
    assert profile["token_counts"]["project_a_llm_visual_tokens"] == 2
    assert profile["compression"]["project_a_vs_dense_raw_ratio"] == 0.015625
    assert profile["compression"]["project_a_vs_dense_visual_ratio"] == 0.015625
    assert "process_peak_rss" in profile["memory_mb"]
    assert "tracemalloc_peak" in profile["memory_mb"]
