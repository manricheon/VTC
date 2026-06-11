import numpy as np

from gaze_ov_bridge.autogaze_decode import decode_flat_ids


def test_flat_id_examples_decode_to_scale_grid_and_frame():
    entries = decode_flat_ids([0, 4, 20, 84, 340])

    assert [
        (entry["frame_idx"], entry["scale"], entry["row"], entry["col"], entry["local_id"])
        for entry in entries
    ] == [
        (0, 28, 0, 0, 0),
        (0, 56, 0, 0, 4),
        (0, 112, 0, 0, 20),
        (0, 224, 0, 0, 84),
        (1, 28, 0, 0, 0),
    ]
    assert entries[0]["grid"] == 2
    assert entries[2]["grid"] == 8
    assert entries[3]["grid"] == 16


def test_decode_accepts_2d_batch_and_removes_padding():
    flat_ids = np.array([[0, 4, 20], [84, 340, 341]])
    if_padded = np.array([[False, True, False], [False, False, True]])

    entries = decode_flat_ids(flat_ids, if_padded_gazing=if_padded)

    assert [(entry["batch_idx"], entry["seq_idx"], entry["flat_id"]) for entry in entries] == [
        (0, 0, 0),
        (0, 2, 20),
        (1, 0, 84),
        (1, 1, 340),
    ]


def test_decode_preserves_duplicate_valid_entries():
    entries = decode_flat_ids([20, 20], if_padded_gazing=[False, False])

    assert len(entries) == 2
    assert [entry["flat_id"] for entry in entries] == [20, 20]
    assert [entry["row"] for entry in entries] == [0, 0]
