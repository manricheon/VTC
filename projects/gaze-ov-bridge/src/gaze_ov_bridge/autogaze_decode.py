"""Decode AutoGaze flat token ids into scale/grid entries."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np

from .token_metrics import DEFAULT_PATCH_SIZE, DEFAULT_TARGET_SCALES


def scale_layout(
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> list[dict[str, int]]:
    if patch_size <= 0:
        raise ValueError("patch_size must be positive")

    layout: list[dict[str, int]] = []
    offset = 0
    for scale in (DEFAULT_TARGET_SCALES if target_scales is None else tuple(target_scales)):
        if scale < 0:
            raise ValueError("target scales must be non-negative")
        grid = scale // patch_size
        count = grid * grid
        layout.append(
            {
                "scale": int(scale),
                "grid": int(grid),
                "count": int(count),
                "start": int(offset),
                "end": int(offset + count),
            }
        )
        offset += count
    return layout


def tokens_per_frame(
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> int:
    return sum(item["count"] for item in scale_layout(target_scales, patch_size))


def _as_2d_array(values: Any, name: str) -> np.ndarray:
    array = np.asarray(values)
    if array.ndim == 1:
        return array.reshape(1, -1)
    if array.ndim == 2:
        return array
    raise ValueError(f"{name} must be a 1D or 2D array/list")


def _decode_local_id(
    local_id: int,
    layout: list[dict[str, int]],
) -> tuple[int, int, int, int]:
    for item in layout:
        if item["start"] <= local_id < item["end"]:
            within_scale = local_id - item["start"]
            grid = item["grid"]
            if grid <= 0:
                raise ValueError(f"scale {item['scale']} has zero grid for this patch size")
            row = within_scale // grid
            col = within_scale % grid
            return item["scale"], grid, row, col
    raise ValueError(f"local_id {local_id} is outside the per-frame token layout")


def decode_flat_id(
    flat_id: int,
    *,
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> dict[str, int]:
    if flat_id < 0:
        raise ValueError("flat_id must be non-negative")

    layout = scale_layout(target_scales, patch_size)
    per_frame = sum(item["count"] for item in layout)
    if per_frame <= 0:
        raise ValueError("per-frame token count must be positive")

    frame_idx = flat_id // per_frame
    local_id = flat_id % per_frame
    scale, grid, row, col = _decode_local_id(local_id, layout)

    return {
        "frame_idx": int(frame_idx),
        "scale": int(scale),
        "grid": int(grid),
        "row": int(row),
        "col": int(col),
        "flat_id": int(flat_id),
        "local_id": int(local_id),
    }


def decode_flat_ids(
    gazing_pos: Any,
    if_padded_gazing: Any | None = None,
    *,
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> list[dict[str, int]]:
    flat_ids = _as_2d_array(gazing_pos, "gazing_pos")
    if if_padded_gazing is None:
        padded = np.zeros(flat_ids.shape, dtype=bool)
    else:
        padded = _as_2d_array(if_padded_gazing, "if_padded_gazing").astype(bool)
        if padded.shape != flat_ids.shape:
            raise ValueError("if_padded_gazing must have the same shape as gazing_pos")

    entries: list[dict[str, int]] = []
    for batch_idx in range(flat_ids.shape[0]):
        for seq_idx in range(flat_ids.shape[1]):
            if bool(padded[batch_idx, seq_idx]):
                continue
            decoded = decode_flat_id(
                int(flat_ids[batch_idx, seq_idx]),
                target_scales=target_scales,
                patch_size=patch_size,
            )
            decoded.update({"batch_idx": int(batch_idx), "seq_idx": int(seq_idx)})
            entries.append(
                {
                    "batch_idx": decoded["batch_idx"],
                    "seq_idx": decoded["seq_idx"],
                    "frame_idx": decoded["frame_idx"],
                    "scale": decoded["scale"],
                    "grid": decoded["grid"],
                    "row": decoded["row"],
                    "col": decoded["col"],
                    "flat_id": decoded["flat_id"],
                    "local_id": decoded["local_id"],
                }
            )
    return entries
