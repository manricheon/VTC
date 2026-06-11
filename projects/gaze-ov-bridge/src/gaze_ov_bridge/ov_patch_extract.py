"""Synthetic patch extraction for Project B OV-Encoder direct artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from PIL import Image

from .token_metrics import DEFAULT_PATCH_SIZE


NATIVE_FRAME_SIZE = 224


def _entry_int(entry: Mapping[str, Any], key: str) -> int:
    return int(entry[key])


def _validate_frames(frames: Any) -> np.ndarray:
    array = np.asarray(frames)
    if array.ndim != 4:
        raise ValueError("frames must have shape [T, H, W, C]")
    if array.shape[1] != NATIVE_FRAME_SIZE or array.shape[2] != NATIVE_FRAME_SIZE:
        raise ValueError("frames must have H=W=224 for OV direct synthetic extraction")
    if array.shape[3] <= 0:
        raise ValueError("frames must have at least one channel")
    return array


def _resampling_nearest() -> Image.Resampling:
    return Image.Resampling.NEAREST


def _resize_frame(frame: np.ndarray, scale: int) -> np.ndarray:
    image = Image.fromarray(frame)
    resized = image.resize((int(scale), int(scale)), resample=_resampling_nearest())
    return np.asarray(resized)


def _extract_one_patch(
    frames: np.ndarray,
    entry: Mapping[str, Any],
    *,
    patch_size: int,
) -> np.ndarray:
    frame_idx = _entry_int(entry, "frame_idx")
    scale = _entry_int(entry, "scale")
    row = _entry_int(entry, "row")
    col = _entry_int(entry, "col")

    if patch_size <= 0:
        raise ValueError("patch_size must be positive")
    if frame_idx < 0 or frame_idx >= frames.shape[0]:
        raise ValueError("entry frame_idx is outside the frames array")
    if scale <= 0:
        raise ValueError("entry scale must be positive")

    grid = scale // patch_size
    if grid <= 0:
        raise ValueError("entry scale must contain at least one patch")
    if row < 0 or col < 0 or row >= grid or col >= grid:
        raise ValueError("entry row/col is outside the scale grid")

    resized = _resize_frame(frames[frame_idx], scale)
    top = row * patch_size
    left = col * patch_size
    patch = resized[top : top + patch_size, left : left + patch_size]
    if patch.shape[:2] != (patch_size, patch_size):
        raise ValueError("extracted patch has an unexpected shape")
    return patch


def extract_ov_direct_patches(
    frames: Any,
    decoded_entries: Sequence[Mapping[str, Any]],
    *,
    patch_size: int = DEFAULT_PATCH_SIZE,
    output_layout: str = "hwc",
) -> np.ndarray:
    """Extract one 14x14 patch per decoded AutoGaze entry.

    The default output layout is `[K, 14, 14, C]`. Set `output_layout="chw"`
    for `[K, C, 14, 14]`.
    """

    frames_array = _validate_frames(frames)
    if output_layout not in {"hwc", "chw"}:
        raise ValueError('output_layout must be "hwc" or "chw"')

    patches = [
        _extract_one_patch(frames_array, entry, patch_size=patch_size)
        for entry in decoded_entries
    ]
    if not patches:
        channels = frames_array.shape[3]
        if output_layout == "hwc":
            return np.empty((0, patch_size, patch_size, channels), dtype=frames_array.dtype)
        return np.empty((0, channels, patch_size, patch_size), dtype=frames_array.dtype)

    stacked = np.stack(patches, axis=0)
    if output_layout == "chw":
        return np.transpose(stacked, (0, 3, 1, 2))
    return stacked
