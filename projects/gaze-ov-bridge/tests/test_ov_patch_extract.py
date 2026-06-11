from __future__ import annotations

import numpy as np

from gaze_ov_bridge.autogaze_decode import decode_flat_ids
from gaze_ov_bridge.ov_patch_extract import extract_ov_direct_patches


def _coordinate_frame() -> np.ndarray:
    rows = np.arange(224, dtype=np.uint8).reshape(224, 1)
    cols = np.arange(224, dtype=np.uint8).reshape(1, 224)
    frame = np.zeros((224, 224, 3), dtype=np.uint8)
    frame[:, :, 0] = rows
    frame[:, :, 1] = cols
    frame[:, :, 2] = rows + cols
    return frame


def test_extracts_hwc_patches_from_scale_resized_frames():
    frames = np.zeros((2, 224, 224, 3), dtype=np.uint8)
    frames[0] = _coordinate_frame()
    frames[1] = np.asarray([7, 8, 9], dtype=np.uint8)
    entries = decode_flat_ids([
        84 + (1 * 16) + 2,  # frame 0, scale 224, row 1, col 2
        340,  # frame 1, scale 28, row 0, col 0
    ])

    patches = extract_ov_direct_patches(frames, entries)

    assert patches.shape == (2, 14, 14, 3)
    assert patches.dtype == np.uint8
    assert patches[0, 0, 0].tolist() == [14, 28, 42]
    assert patches[0, -1, -1].tolist() == [27, 41, 68]
    assert np.all(patches[1] == np.asarray([7, 8, 9], dtype=np.uint8))


def test_extracts_chw_patches_when_requested():
    frames = np.zeros((1, 224, 224, 3), dtype=np.uint8)
    frames[0] = np.asarray([3, 4, 5], dtype=np.uint8)
    entries = decode_flat_ids([20])

    patches = extract_ov_direct_patches(frames, entries, output_layout="chw")

    assert patches.shape == (1, 3, 14, 14)
    assert patches[:, 0].tolist() == [[[3] * 14 for _ in range(14)]]
    assert patches[:, 1].tolist() == [[[4] * 14 for _ in range(14)]]
    assert patches[:, 2].tolist() == [[[5] * 14 for _ in range(14)]]
