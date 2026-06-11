from gaze_ov_bridge.autogaze_decode import decode_flat_ids
from gaze_ov_bridge.selector_112_anchor import select_112_anchor_blocks
from gaze_ov_bridge.stats import build_project_a_stats


def test_112_scale_direct_selections_become_selected_blocks():
    entries = decode_flat_ids([20, 21])

    result = select_112_anchor_blocks(entries)

    assert result["selected_blocks"] == [(0, 0, 0), (0, 0, 1)]
    assert result["stats"]["selected_112_blocks"] == 2
    assert result["stats"]["confirms_no_hard_union_default"] is True


def test_224_scale_adds_fine_vote_to_containing_112_block():
    entries = decode_flat_ids([84 + (3 * 16) + 5])

    result = select_112_anchor_blocks(entries)

    assert result["fine_votes"] == [
        {
            "frame_idx": 0,
            "scale": 224,
            "row": 3,
            "col": 5,
            "r112": 1,
            "c112": 2,
        }
    ]
    assert result["selected_blocks"] == [(0, 1, 2)]


def test_56_and_28_do_not_hard_union_by_default():
    entries = decode_flat_ids([4, 0])

    result = select_112_anchor_blocks(entries)

    assert result["selected_blocks"] == []
    assert result["region_priors_56"][0]["covered_112_blocks"] == [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]
    assert len(result["frame_priors_28"][0]["covered_112_blocks"]) == 16
    assert result["stats"]["confirms_no_hard_union_default"] is True


def test_hard_union_ablation_expands_coarse_priors():
    entries = decode_flat_ids([4, 0])

    result = select_112_anchor_blocks(entries, hard_union=True)

    assert len(result["selected_blocks"]) == 16
    assert (0, 0, 0) in result["selected_blocks"]
    assert (0, 3, 3) in result["selected_blocks"]
    assert result["stats"]["confirms_no_hard_union_default"] is False


def test_duplicate_entries_are_counted_but_selected_blocks_are_unique():
    entries = decode_flat_ids([20, 20, 84])

    result = select_112_anchor_blocks(entries)

    assert result["selected_blocks"] == [(0, 0, 0)]
    assert result["stats"]["decoded_entries_total"] == 3
    assert result["stats"]["duplicate_selected_blocks"] == 2


def test_project_a_stats_use_token_metrics_consistently():
    stats = build_project_a_stats(
        decoded_entries=decode_flat_ids([20, 84, 340]),
        selected_blocks=[(0, 0, 0), (1, 0, 0)],
        num_frames=2,
    )

    assert stats["autogaze_tokens_by_scale"] == {"28": 8, "56": 32, "112": 128, "224": 512}
    assert stats["selected_112_blocks"] == 2
    assert stats["raw_patch_tokens"] == 8
    assert stats["llm_visual_tokens"] == 2
    assert stats["token_counts"]["project_a_raw_patch_tokens"] == 8
    assert stats["token_counts"]["project_a_llm_visual_tokens"] == 2
    assert stats["compression"]["project_a_vs_dense_raw_ratio"] == 8 / 512
