"""Project A stats assembly."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .token_metrics import (
    DEFAULT_PATCH_SIZE,
    DEFAULT_TARGET_SCALES,
    build_compression_metrics,
    build_token_counts,
    project_a_token_counts,
)


def _count_entries_by_scale(decoded_entries: list[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter(str(int(entry["scale"])) for entry in decoded_entries)
    return {str(scale): int(counts.get(str(scale), 0)) for scale in DEFAULT_TARGET_SCALES}


def build_project_a_stats(
    *,
    decoded_entries: list[Mapping[str, Any]],
    selected_blocks: Sequence[Sequence[int]],
    num_frames: int | None = None,
    hard_union: bool = False,
    target_scales: Sequence[int] = DEFAULT_TARGET_SCALES,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> dict[str, Any]:
    if num_frames is None:
        max_frame = max((int(entry["frame_idx"]) for entry in decoded_entries), default=-1)
        num_frames = max_frame + 1

    selected_count = len({(int(frame), int(row), int(col)) for frame, row, col in selected_blocks})
    project_a_counts = project_a_token_counts(selected_count)
    token_counts = build_token_counts(
        num_frames=int(num_frames),
        selected_112_blocks=selected_count,
        autogaze_valid_tokens_total=len(decoded_entries),
        target_scales=target_scales,
        patch_size=patch_size,
    )
    compression = build_compression_metrics(token_counts)

    return {
        "decoded_entries_total": len(decoded_entries),
        "valid_autogaze_entries": len(decoded_entries),
        "selected_112_blocks": selected_count,
        "raw_patch_tokens": project_a_counts["project_a_raw_patch_tokens"],
        "llm_visual_tokens": project_a_counts["project_a_llm_visual_tokens"],
        "autogaze_tokens_by_scale": token_counts["autogaze_tokens_by_scale"],
        "decoded_entries_by_scale": _count_entries_by_scale(decoded_entries),
        "confirms_no_hard_union_default": not hard_union,
        "hard_union": bool(hard_union),
        "token_counts": token_counts,
        "compression": compression,
    }
