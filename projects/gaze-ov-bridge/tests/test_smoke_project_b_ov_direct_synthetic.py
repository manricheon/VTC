from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def test_smoke_project_b_ov_direct_synthetic_writes_profiled_artifacts(
    tmp_path: Path,
) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    script_path = (
        repo_root
        / "projects"
        / "gaze-ov-bridge"
        / "scripts"
        / "smoke_project_b_ov_direct_synthetic.py"
    )
    out_dir = tmp_path / "smoke_project_b_ov_direct_synthetic"

    result = subprocess.run(
        [sys.executable, str(script_path), "--out-dir", str(out_dir)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "direct_tokens=5" in result.stdout
    assert "confirms_no_native_union=True" in result.stdout

    stats_path = out_dir / "stats.json"
    profile_path = out_dir / "profile.json"
    decoded_path = out_dir / "decoded_entries.json"
    patch_positions_path = out_dir / "patch_positions.npy"
    patches_path = out_dir / "patches.npy"
    pack_plan_path = out_dir / "pack_plan.json"

    for path in (
        stats_path,
        profile_path,
        decoded_path,
        patch_positions_path,
        patches_path,
        pack_plan_path,
    ):
        assert path.exists(), path

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    decoded_entries = json.loads(decoded_path.read_text(encoding="utf-8"))
    pack_plan = json.loads(pack_plan_path.read_text(encoding="utf-8"))
    patch_positions = np.load(patch_positions_path)
    patches = np.load(patches_path)

    assert len(decoded_entries) == 5
    assert {entry["scale"] for entry in decoded_entries} == {28, 56, 112, 224}
    assert stats["total_tokens"] == len(decoded_entries)
    assert stats["tokens_by_scale"] == {"28": 2, "56": 1, "112": 1, "224": 1}
    assert stats["patch_positions_shape"] == [5, 3]
    assert stats["patches_shape"] == [5, 14, 14, 3]
    assert stats["pack_canvas_count"] == 1
    assert stats["confirms_no_native_union"] is True

    assert patch_positions.dtype == np.float32
    np.testing.assert_allclose(
        patch_positions,
        np.asarray(
            [
                [0.0, 3.5, 3.5],
                [0.0, 1.5, 1.5],
                [0.0, 0.5, 0.5],
                [0.0, 0.0, 0.0],
                [1.0, 3.5, 3.5],
            ],
            dtype=np.float32,
        ),
    )
    assert patches.shape == (5, 14, 14, 3)

    assert len(pack_plan["tokens"]) == 5
    assert pack_plan["total_padding_slots"] == 251
    assert all("padding" not in token for token in pack_plan["tokens"])
    assert [token["token_idx"] for token in pack_plan["tokens"]] == [0, 1, 2, 3, 4]

    assert profile["project"]["track"] == "project_b_ov_direct"
    assert profile["project"]["policy_name"] == "direct_multiscale_no_union"
    for key in ("total", "decode", "patch_extract", "pack"):
        assert profile["timings_s"][key] is not None
        assert profile["timings_s"][key] > 0
    assert "process_peak_rss" in profile["memory_mb"]
    assert "tracemalloc_peak" in profile["memory_mb"]
    assert profile["token_counts"]["autogaze_candidate_tokens_total"] == 680
    assert profile["token_counts"]["autogaze_valid_tokens_total"] == 5
    assert profile["token_counts"]["dense_native_raw_patch_tokens"] == 512
    assert profile["token_counts"]["project_b_ov_direct_tokens"] == 5
    assert profile["compression"]["project_b_vs_autogaze_candidates_ratio"] == 5 / 680
    assert profile["compression"]["project_b_vs_dense_native_ratio"] == 5 / 512
    assert profile["compression"]["project_b_reduction_vs_candidates"] == 1 - (5 / 680)
    assert profile["compression"]["project_b_reduction_vs_dense_native"] == 1 - (5 / 512)
