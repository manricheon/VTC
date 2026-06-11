from __future__ import annotations

import pytest

from gaze_ov_bridge.ov_pack import build_ov_pack_plan


def test_pack_slots_preserve_token_order_and_exclude_padding_metadata():
    plan = build_ov_pack_plan(num_tokens=3)

    assert plan["canvas_grid"] == 16
    assert plan["slots_per_canvas"] == 256
    assert plan["num_canvases"] == 1
    assert plan["total_padding_slots"] == 253
    assert plan["tokens"] == [
        {"token_idx": 0, "canvas_idx": 0, "slot_idx": 0, "row": 0, "col": 0},
        {"token_idx": 1, "canvas_idx": 0, "slot_idx": 1, "row": 0, "col": 1},
        {"token_idx": 2, "canvas_idx": 0, "slot_idx": 2, "row": 0, "col": 2},
    ]
    assert all("padding" not in token for token in plan["tokens"])


def test_pack_slots_span_multiple_canvases_stably():
    plan = build_ov_pack_plan(num_tokens=258)

    assert plan["num_canvases"] == 2
    assert plan["total_padding_slots"] == 254
    assert plan["tokens"][255] == {
        "token_idx": 255,
        "canvas_idx": 0,
        "slot_idx": 255,
        "row": 15,
        "col": 15,
    }
    assert plan["tokens"][256] == {
        "token_idx": 256,
        "canvas_idx": 1,
        "slot_idx": 0,
        "row": 0,
        "col": 0,
    }
    assert plan["tokens"][257] == {
        "token_idx": 257,
        "canvas_idx": 1,
        "slot_idx": 1,
        "row": 0,
        "col": 1,
    }


def test_pack_zero_tokens_has_no_padding_metadata():
    plan = build_ov_pack_plan(num_tokens=0)

    assert plan["num_canvases"] == 0
    assert plan["total_slots"] == 0
    assert plan["total_padding_slots"] == 0
    assert plan["tokens"] == []


def test_pack_rejects_negative_token_counts():
    with pytest.raises(ValueError, match="num_tokens"):
        build_ov_pack_plan(num_tokens=-1)
