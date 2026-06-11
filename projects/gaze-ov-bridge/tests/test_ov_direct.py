from __future__ import annotations

import numpy as np

from gaze_ov_bridge.autogaze_decode import decode_flat_ids
from gaze_ov_bridge.ov_direct import (
    build_ov_direct_plan,
    ov_fractional_position,
)
from gaze_ov_bridge.token_metrics import build_token_counts


def test_fractional_positions_for_all_autogaze_scales():
    assert ov_fractional_position(scale=224, row=0, col=0) == (0.0, 0.0)
    assert ov_fractional_position(scale=112, row=0, col=0) == (0.5, 0.5)
    assert ov_fractional_position(scale=56, row=0, col=0) == (1.5, 1.5)
    assert ov_fractional_position(scale=28, row=0, col=0) == (3.5, 3.5)


def test_ov_direct_plan_preserves_one_autogaze_entry_as_one_token():
    entries = decode_flat_ids(
        [[0, 4, 20, 84, 85]],
        if_padded_gazing=[[False, False, False, False, True]],
    )

    plan = build_ov_direct_plan(entries, num_frames=1)

    assert plan["total_tokens"] == 4
    assert plan["stats"]["project_b_ov_direct_tokens"] == 4
    assert plan["stats"]["confirms_no_native_union"] is True
    assert plan["stats"]["tokens_by_scale"] == {"28": 1, "56": 1, "112": 1, "224": 1}
    assert len(plan["tokens"]) == len(entries)
    assert [token["token_idx"] for token in plan["tokens"]] == [0, 1, 2, 3]
    assert plan["patch_positions"].dtype == np.float32
    assert plan["patch_positions"].tolist() == [
        [0.0, 3.5, 3.5],
        [0.0, 1.5, 1.5],
        [0.0, 0.5, 0.5],
        [0.0, 0.0, 0.0],
    ]


def test_project_b_stats_use_shared_token_metrics():
    entries = decode_flat_ids([20, 84, 340])

    plan = build_ov_direct_plan(entries, num_frames=2)
    expected_token_counts = build_token_counts(
        num_frames=2,
        autogaze_valid_tokens_total=3,
    )

    assert plan["stats"]["total_tokens"] == 3
    assert plan["stats"]["dense_native_raw_patch_tokens"] == 512
    assert plan["stats"]["autogaze_candidate_tokens_total"] == 680
    assert plan["stats"]["project_b_ov_direct_tokens"] == 3
    assert plan["stats"]["token_counts"] == expected_token_counts
    assert plan["stats"]["compression"]["project_b_vs_autogaze_candidates_ratio"] == 3 / 680
    assert plan["stats"]["compression"]["project_b_vs_dense_native_ratio"] == 3 / 512
