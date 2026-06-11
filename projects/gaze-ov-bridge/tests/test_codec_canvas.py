from gaze_ov_bridge.codec_canvas import build_src_positions


def test_src_positions_rows_are_frame_native_h_native_w_integers():
    src_positions = build_src_positions([(2, 1, 3)])

    assert src_positions.dtype.kind in {"i", "u"}
    assert src_positions.tolist() == [
        [2, 2, 6],
        [2, 2, 7],
        [2, 3, 6],
        [2, 3, 7],
    ]
