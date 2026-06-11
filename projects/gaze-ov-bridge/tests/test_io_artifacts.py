import numpy as np

from gaze_ov_bridge.io_artifacts import (
    read_decoded_entries,
    read_selected_blocks,
    read_src_positions,
    read_stats,
    write_decoded_entries,
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
