import numpy as np

from gaze_ov_bridge.io_artifacts import (
    read_decoded_entries,
    read_pack_plan,
    read_patch_positions,
    read_patches,
    read_selected_blocks,
    read_src_positions,
    read_stats,
    write_decoded_entries,
    write_pack_plan,
    write_patch_positions,
    write_patches,
    write_selected_blocks,
    write_src_positions,
    write_stats,
)


def test_json_and_npy_artifact_round_trip(tmp_path):
    decoded_entries = [
        {
            "batch_idx": 0,
            "seq_idx": 0,
            "frame_idx": 0,
            "scale": 112,
            "grid": 8,
            "row": 0,
            "col": 1,
            "flat_id": 21,
            "local_id": 21,
        }
    ]
    selected_blocks = [(0, 0, 1), (1, 2, 3)]
    src_positions = np.array([[0, 0, 2], [0, 0, 3]], dtype=np.int64)
    stats = {
        "selected_112_blocks": 2,
        "raw_patch_tokens": 8,
        "llm_visual_tokens": 2,
        "confirms_no_hard_union_default": True,
    }

    write_decoded_entries(decoded_entries, tmp_path / "decoded_entries.json")
    write_selected_blocks(selected_blocks, tmp_path / "selected_blocks.json")
    write_src_positions(src_positions, tmp_path / "src_positions.npy")
    write_stats(stats, tmp_path / "stats.json")

    assert read_decoded_entries(tmp_path / "decoded_entries.json") == decoded_entries
    assert read_selected_blocks(tmp_path / "selected_blocks.json") == selected_blocks
    assert read_src_positions(tmp_path / "src_positions.npy").tolist() == src_positions.tolist()
    assert read_stats(tmp_path / "stats.json") == stats


def test_project_b_artifact_round_trip(tmp_path):
    patch_positions = np.array([[0.0, 3.5, 3.5], [1.0, 0.0, 0.0]], dtype=np.float64)
    patches = np.arange(2 * 14 * 14 * 3, dtype=np.uint8).reshape(2, 14, 14, 3)
    pack_plan = {
        "canvas_size": 224,
        "patch_size": 14,
        "canvas_grid": 16,
        "slots_per_canvas": 256,
        "num_canvases": 1,
        "total_slots": 256,
        "total_padding_slots": 254,
        "tokens": [
            {"token_idx": 0, "canvas_idx": 0, "slot_idx": 0, "row": 0, "col": 0},
            {"token_idx": 1, "canvas_idx": 0, "slot_idx": 1, "row": 0, "col": 1},
        ],
    }

    write_patch_positions(patch_positions, tmp_path / "patch_positions.npy")
    write_patches(patches, tmp_path / "patches.npy")
    write_pack_plan(pack_plan, tmp_path / "pack_plan.json")

    np.testing.assert_array_equal(read_patch_positions(tmp_path / "patch_positions.npy"), patch_positions)
    np.testing.assert_array_equal(read_patches(tmp_path / "patches.npy"), patches)
    assert read_pack_plan(tmp_path / "pack_plan.json") == pack_plan
