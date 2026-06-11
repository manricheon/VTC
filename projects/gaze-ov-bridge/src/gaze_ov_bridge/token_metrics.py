"""Token count and compression helpers for bridge profiling."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


DEFAULT_TARGET_SCALES = (28, 56, 112, 224)
DEFAULT_PATCH_SIZE = 14
NATIVE_PATCH_GRID = 16
LLAVA_OV2_MERGED_GRID = 8

TOKEN_COUNT_KEYS = (
    "autogaze_candidate_tokens_total",
    "autogaze_valid_tokens_total",
    "autogaze_tokens_by_scale",
    "dense_native_raw_patch_tokens",
    "dense_native_merged_visual_tokens",
    "selected_112_blocks",
    "project_a_raw_patch_tokens",
    "project_a_llm_visual_tokens",
    "project_b_ov_direct_tokens",
)

COMPRESSION_KEYS = (
    "project_a_vs_dense_raw_ratio",
    "project_a_vs_dense_visual_ratio",
    "project_a_raw_reduction",
    "project_a_visual_reduction",
    "project_b_vs_autogaze_candidates_ratio",
    "project_b_vs_dense_native_ratio",
    "project_b_reduction_vs_candidates",
    "project_b_reduction_vs_dense_native",
)


def _require_non_negative_int(name: str, value: int) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def _target_scales_tuple(target_scales: Iterable[int] | None) -> tuple[int, ...]:
    scales = tuple(DEFAULT_TARGET_SCALES if target_scales is None else target_scales)
    for scale in scales:
        _require_non_negative_int("scale", scale)
    return scales


def safe_ratio(numerator: float | int | None, denominator: float | int | None) -> float | None:
    """Return numerator / denominator, or None when the denominator is zero/null."""

    if numerator is None or denominator in (None, 0):
        return None
    return float(numerator) / float(denominator)


def reduction_from_ratio(ratio: float | None) -> float | None:
    if ratio is None:
        return None
    return 1.0 - ratio


def autogaze_tokens_by_scale(
    num_frames: int = 1,
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> dict[str, int]:
    _require_non_negative_int("num_frames", num_frames)
    if patch_size <= 0:
        raise ValueError("patch_size must be positive")

    return {
        str(scale): num_frames * (scale // patch_size) ** 2
        for scale in _target_scales_tuple(target_scales)
    }


def autogaze_candidate_tokens_per_frame(
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> int:
    if patch_size <= 0:
        raise ValueError("patch_size must be positive")
    return sum((scale // patch_size) ** 2 for scale in _target_scales_tuple(target_scales))


def autogaze_candidate_tokens_total(
    num_frames: int,
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> int:
    _require_non_negative_int("num_frames", num_frames)
    return num_frames * autogaze_candidate_tokens_per_frame(target_scales, patch_size)


def dense_native_raw_patch_tokens(
    num_frames: int,
    native_grid: int = NATIVE_PATCH_GRID,
) -> int:
    _require_non_negative_int("num_frames", num_frames)
    if native_grid <= 0:
        raise ValueError("native_grid must be positive")
    return num_frames * native_grid * native_grid


def dense_native_merged_visual_tokens(
    num_frames: int,
    merged_grid: int = LLAVA_OV2_MERGED_GRID,
) -> int:
    _require_non_negative_int("num_frames", num_frames)
    if merged_grid <= 0:
        raise ValueError("merged_grid must be positive")
    return num_frames * merged_grid * merged_grid


def project_a_token_counts(selected_112_blocks: int) -> dict[str, int]:
    _require_non_negative_int("selected_112_blocks", selected_112_blocks)
    return {
        "project_a_raw_patch_tokens": selected_112_blocks * 4,
        "project_a_llm_visual_tokens": selected_112_blocks,
    }


def project_b_token_count(valid_autogaze_entries: int) -> int:
    _require_non_negative_int("valid_autogaze_entries", valid_autogaze_entries)
    return valid_autogaze_entries


def empty_token_counts() -> dict[str, int | dict[str, int]]:
    return {
        "autogaze_candidate_tokens_total": 0,
        "autogaze_valid_tokens_total": 0,
        "autogaze_tokens_by_scale": {},
        "dense_native_raw_patch_tokens": 0,
        "dense_native_merged_visual_tokens": 0,
        "selected_112_blocks": 0,
        "project_a_raw_patch_tokens": 0,
        "project_a_llm_visual_tokens": 0,
        "project_b_ov_direct_tokens": 0,
    }


def build_token_counts(
    num_frames: int,
    selected_112_blocks: int = 0,
    autogaze_valid_tokens_total: int = 0,
    target_scales: Iterable[int] | None = None,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> dict[str, int | dict[str, int]]:
    _require_non_negative_int("autogaze_valid_tokens_total", autogaze_valid_tokens_total)

    project_a = project_a_token_counts(selected_112_blocks)
    return {
        "autogaze_candidate_tokens_total": autogaze_candidate_tokens_total(
            num_frames=num_frames,
            target_scales=target_scales,
            patch_size=patch_size,
        ),
        "autogaze_valid_tokens_total": autogaze_valid_tokens_total,
        "autogaze_tokens_by_scale": autogaze_tokens_by_scale(
            num_frames=num_frames,
            target_scales=target_scales,
            patch_size=patch_size,
        ),
        "dense_native_raw_patch_tokens": dense_native_raw_patch_tokens(num_frames),
        "dense_native_merged_visual_tokens": dense_native_merged_visual_tokens(num_frames),
        "selected_112_blocks": selected_112_blocks,
        "project_a_raw_patch_tokens": project_a["project_a_raw_patch_tokens"],
        "project_a_llm_visual_tokens": project_a["project_a_llm_visual_tokens"],
        "project_b_ov_direct_tokens": project_b_token_count(autogaze_valid_tokens_total),
    }


def build_compression_metrics(
    token_counts: Mapping[str, int | dict[str, int]],
) -> dict[str, float | None]:
    project_a_raw_ratio = safe_ratio(
        token_counts.get("project_a_raw_patch_tokens"),
        token_counts.get("dense_native_raw_patch_tokens"),
    )
    project_a_visual_ratio = safe_ratio(
        token_counts.get("project_a_llm_visual_tokens"),
        token_counts.get("dense_native_merged_visual_tokens"),
    )
    project_b_candidates_ratio = safe_ratio(
        token_counts.get("project_b_ov_direct_tokens"),
        token_counts.get("autogaze_candidate_tokens_total"),
    )
    project_b_dense_ratio = safe_ratio(
        token_counts.get("project_b_ov_direct_tokens"),
        token_counts.get("dense_native_raw_patch_tokens"),
    )

    return {
        "project_a_vs_dense_raw_ratio": project_a_raw_ratio,
        "project_a_vs_dense_visual_ratio": project_a_visual_ratio,
        "project_a_raw_reduction": reduction_from_ratio(project_a_raw_ratio),
        "project_a_visual_reduction": reduction_from_ratio(project_a_visual_ratio),
        "project_b_vs_autogaze_candidates_ratio": project_b_candidates_ratio,
        "project_b_vs_dense_native_ratio": project_b_dense_ratio,
        "project_b_reduction_vs_candidates": reduction_from_ratio(project_b_candidates_ratio),
        "project_b_reduction_vs_dense_native": reduction_from_ratio(project_b_dense_ratio),
    }


def empty_compression_metrics() -> dict[str, None]:
    return {key: None for key in COMPRESSION_KEYS}
