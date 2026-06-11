"""Project B OV-Encoder direct token planning utilities."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from .token_metrics import (
    DEFAULT_PATCH_SIZE,
    DEFAULT_TARGET_SCALES,
    NATIVE_PATCH_GRID,
    build_compression_metrics,
    build_token_counts,
)


def _entry_int(entry: Mapping[str, Any], key: str) -> int:
    return int(entry[key])


def _infer_num_frames(decoded_entries: Sequence[Mapping[str, Any]]) -> int:
    max_frame = max((_entry_int(entry, "frame_idx") for entry in decoded_entries), default=-1)
    return max_frame + 1


def _tokens_by_scale(
    decoded_entries: Sequence[Mapping[str, Any]],
    target_scales: Sequence[int],
) -> dict[str, int]:
    counts = Counter(str(_entry_int(entry, "scale")) for entry in decoded_entries)
    result = {str(scale): int(counts.get(str(scale), 0)) for scale in target_scales}
    extra_scales = sorted(
        scale
        for scale in counts
        if scale not in result
    )
    result.update({scale: int(counts[scale]) for scale in extra_scales})
    return result


def ov_fractional_position(
    *,
    scale: int,
    row: int,
    col: int,
    native_grid: int = NATIVE_PATCH_GRID,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> tuple[float, float]:
    """Map a scale-local AutoGaze patch to fractional OV native-grid coordinates."""

    if scale <= 0:
        raise ValueError("scale must be positive")
    if patch_size <= 0:
        raise ValueError("patch_size must be positive")
    if native_grid <= 0:
        raise ValueError("native_grid must be positive")
    if row < 0 or col < 0:
        raise ValueError("row and col must be non-negative")

    grid = scale // patch_size
    if grid <= 0:
        raise ValueError("scale must be at least one patch")
    if row >= grid or col >= grid:
        raise ValueError("row and col must be inside the scale grid")

    h = (row + 0.5) * (native_grid / grid) - 0.5
    w = (col + 0.5) * (native_grid / grid) - 0.5
    return float(h), float(w)


def ov_token_metadata(
    entry: Mapping[str, Any],
    *,
    token_idx: int,
    native_grid: int = NATIVE_PATCH_GRID,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> dict[str, Any]:
    """Convert one decoded AutoGaze entry into one OV-direct token metadata row."""

    frame_idx = _entry_int(entry, "frame_idx")
    scale = _entry_int(entry, "scale")
    row = _entry_int(entry, "row")
    col = _entry_int(entry, "col")
    h, w = ov_fractional_position(
        scale=scale,
        row=row,
        col=col,
        native_grid=native_grid,
        patch_size=patch_size,
    )

    token: dict[str, Any] = {
        "token_idx": int(token_idx),
        "batch_idx": _entry_int(entry, "batch_idx"),
        "seq_idx": _entry_int(entry, "seq_idx"),
        "frame_idx": frame_idx,
        "scale": scale,
        "grid": _entry_int(entry, "grid"),
        "row": row,
        "col": col,
        "flat_id": _entry_int(entry, "flat_id"),
        "local_id": _entry_int(entry, "local_id"),
        "patch_position": [float(frame_idx), h, w],
    }
    return token


def build_project_b_stats(
    decoded_entries: Sequence[Mapping[str, Any]],
    *,
    num_frames: int | None = None,
    target_scales: Sequence[int] = DEFAULT_TARGET_SCALES,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> dict[str, Any]:
    """Build Project B token/compression stats without expanding coarse tokens."""

    if num_frames is None:
        num_frames = _infer_num_frames(decoded_entries)

    total_tokens = len(decoded_entries)
    token_counts = build_token_counts(
        num_frames=int(num_frames),
        autogaze_valid_tokens_total=total_tokens,
        target_scales=target_scales,
        patch_size=patch_size,
    )
    compression = build_compression_metrics(token_counts)

    return {
        "total_tokens": total_tokens,
        "valid_autogaze_entries": total_tokens,
        "tokens_by_scale": _tokens_by_scale(decoded_entries, target_scales),
        "dense_native_raw_patch_tokens": token_counts["dense_native_raw_patch_tokens"],
        "autogaze_candidate_tokens_total": token_counts["autogaze_candidate_tokens_total"],
        "project_b_ov_direct_tokens": token_counts["project_b_ov_direct_tokens"],
        "confirms_no_native_union": True,
        "token_counts": token_counts,
        "compression": compression,
    }


def build_ov_direct_plan(
    decoded_entries: Sequence[Mapping[str, Any]],
    *,
    num_frames: int | None = None,
    target_scales: Sequence[int] = DEFAULT_TARGET_SCALES,
    patch_size: int = DEFAULT_PATCH_SIZE,
    native_grid: int = NATIVE_PATCH_GRID,
) -> dict[str, Any]:
    """Build metadata for the OV-Encoder direct path without calling an encoder."""

    tokens = [
        ov_token_metadata(
            entry,
            token_idx=token_idx,
            native_grid=native_grid,
            patch_size=patch_size,
        )
        for token_idx, entry in enumerate(decoded_entries)
    ]
    patch_positions = np.asarray(
        [token["patch_position"] for token in tokens],
        dtype=np.float32,
    ).reshape(-1, 3)
    stats = build_project_b_stats(
        decoded_entries,
        num_frames=num_frames,
        target_scales=target_scales,
        patch_size=patch_size,
    )

    return {
        "tokens": tokens,
        "patch_positions": patch_positions,
        "total_tokens": len(tokens),
        "stats": stats,
    }
