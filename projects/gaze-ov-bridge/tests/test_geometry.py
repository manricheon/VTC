import numpy as np

from gaze_ov_bridge.geometry import (
    expand_112_block_to_native_positions,
    scale_token_to_112_blocks,
    selected_blocks_to_src_positions,
)


def test_112_block_maps_to_native_2x2_patch_positions_in_order():
    assert expand_112_block_to_native_positions(3, 2, 5) == [
        (3, 4, 10),
        (3, 4, 11),
        (3, 5, 10),
        (3, 5, 11),
    ]


def test_selected_blocks_to_src_positions_are_integer_rows():
    src_positions = selected_blocks_to_src_positions([(0, 0, 0), (1, 7, 7)])

    assert src_positions.dtype.kind in {"i", "u"}
    assert src_positions.tolist() == [
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 1],
        [1, 14, 14],
        [1, 14, 15],
        [1, 15, 14],
        [1, 15, 15],
    ]


def test_scale_token_to_112_blocks_for_supported_scales():
    assert scale_token_to_112_blocks(112, 3, 4) == [(3, 4)]
    assert scale_token_to_112_blocks(224, 6, 9) == [(3, 4)]
    assert scale_token_to_112_blocks(56, 1, 2) == [(2, 4), (2, 5), (3, 4), (3, 5)]
    assert scale_token_to_112_blocks(28, 1, 1) == [
        (4, 4),
        (4, 5),
        (4, 6),
        (4, 7),
        (5, 4),
        (5, 5),
        (5, 6),
        (5, 7),
        (6, 4),
        (6, 5),
        (6, 6),
        (6, 7),
        (7, 4),
        (7, 5),
        (7, 6),
        (7, 7),
    ]

    empty = selected_blocks_to_src_positions([])
    assert isinstance(empty, np.ndarray)
    assert empty.shape == (0, 3)
