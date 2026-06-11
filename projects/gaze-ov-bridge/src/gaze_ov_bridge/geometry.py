"""Project A grid geometry helpers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np


Block112 = tuple[int, int, int]
Block112NoFrame = tuple[int, int]


def scale_token_to_112_blocks(scale: int, row: int, col: int) -> list[Block112NoFrame]:
    if row < 0 or col < 0:
        raise ValueError("row and col must be non-negative")

    if scale == 112:
        return [(row, col)]
    if scale == 224:
        return [(row // 2, col // 2)]
    if scale == 56:
        r0 = row * 2
        c0 = col * 2
        return [(r, c) for r in range(r0, r0 + 2) for c in range(c0, c0 + 2)]
    if scale == 28:
        r0 = row * 4
        c0 = col * 4
        return [(r, c) for r in range(r0, r0 + 4) for c in range(c0, c0 + 4)]
    raise ValueError(f"unsupported scale for 112 anchor mapping: {scale}")


def expand_112_block_to_native_positions(
    frame_idx: int,
    r112: int,
    c112: int,
) -> list[tuple[int, int, int]]:
    if frame_idx < 0 or r112 < 0 or c112 < 0:
        raise ValueError("frame_idx, r112, and c112 must be non-negative")

    native_h = 2 * r112
    native_w = 2 * c112
    return [
        (frame_idx, native_h, native_w),
        (frame_idx, native_h, native_w + 1),
        (frame_idx, native_h + 1, native_w),
        (frame_idx, native_h + 1, native_w + 1),
    ]


def normalize_selected_blocks(blocks: Iterable[Sequence[int]]) -> list[Block112]:
    normalized = {(int(frame), int(row), int(col)) for frame, row, col in blocks}
    return sorted(normalized)


def selected_blocks_to_src_positions(blocks: Iterable[Sequence[int]]) -> np.ndarray:
    rows: list[tuple[int, int, int]] = []
    for frame_idx, r112, c112 in normalize_selected_blocks(blocks):
        rows.extend(expand_112_block_to_native_positions(frame_idx, r112, c112))
    return np.asarray(rows, dtype=np.int64).reshape(-1, 3)
