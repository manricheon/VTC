"""Project A LLaVA-OV2 codec boundary validation.

This module validates bridge artifacts only. It does not import LLaVA-OV2,
AutoGaze, torch, transformers, or model weights.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .io_artifacts import read_selected_blocks, read_src_positions, read_stats
from .token_metrics import (
    NATIVE_PATCH_GRID,
    build_compression_metrics,
    build_token_counts,
)


def _normalize_selected_blocks(
    selected_blocks: Sequence[Sequence[int]] | None,
) -> list[tuple[int, int, int]]:
    if selected_blocks is None:
        return []
    normalized: list[tuple[int, int, int]] = []
    for block in selected_blocks:
        if len(block) != 3:
            raise ValueError("selected_blocks entries must be [frame_idx, r112, c112]")
        frame_idx, row, col = block
        normalized.append((int(frame_idx), int(row), int(col)))
    return normalized


def _as_integer_src_positions(src_positions: Any) -> np.ndarray:
    array = np.asarray(src_positions)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("src_positions must have shape [N, 3]")
    if np.issubdtype(array.dtype, np.integer):
        return array.astype(np.int64, copy=False)
    if not np.all(np.isfinite(array)):
        raise ValueError("src_positions must contain finite integer values")
    if not np.all(array == np.floor(array)):
        raise ValueError("src_positions must contain integer [frame_idx, native_h, native_w] values")
    return array.astype(np.int64)


def expected_src_positions_for_blocks(
    selected_blocks: Sequence[Sequence[int]],
) -> np.ndarray:
    rows: list[list[int]] = []
    for frame_idx, r112, c112 in _normalize_selected_blocks(selected_blocks):
        rows.extend(
            [
                [frame_idx, 2 * r112, 2 * c112],
                [frame_idx, 2 * r112, 2 * c112 + 1],
                [frame_idx, 2 * r112 + 1, 2 * c112],
                [frame_idx, 2 * r112 + 1, 2 * c112 + 1],
            ]
        )
    return np.asarray(rows, dtype=np.int64).reshape(-1, 3)


def validate_src_positions(
    src_positions: Any,
    *,
    selected_blocks: Sequence[Sequence[int]] | None = None,
    native_grid: int = NATIVE_PATCH_GRID,
) -> np.ndarray:
    """Validate integer [frame_idx, native_h, native_w] src_positions."""

    if native_grid <= 0:
        raise ValueError("native_grid must be positive")

    positions = _as_integer_src_positions(src_positions)
    if positions.shape[0] == 0:
        return positions
    if np.any(positions[:, 0] < 0):
        raise ValueError("src_positions frame_idx values must be non-negative")
    spatial = positions[:, 1:3]
    if np.any(spatial < 0) or np.any(spatial >= native_grid):
        raise ValueError(f"src_positions native_h/native_w values must be within 0..{native_grid - 1}")

    blocks = _normalize_selected_blocks(selected_blocks)
    if blocks:
        expected_len = len(blocks) * 4
        if positions.shape[0] != expected_len:
            raise ValueError(
                "src_positions length must equal selected_blocks * 4 "
                f"(got {positions.shape[0]}, expected {expected_len})"
            )
        expected = expected_src_positions_for_blocks(blocks)
        if not np.array_equal(positions, expected):
            raise ValueError("src_positions must follow native 2x2 ordering for each selected 112 block")

    return positions


def build_llava_codec_payload(
    *,
    selected_blocks: Sequence[Sequence[int]],
    src_positions: Any,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blocks = _normalize_selected_blocks(selected_blocks)
    positions = validate_src_positions(src_positions, selected_blocks=blocks)
    payload_meta = {
        "contract": "project_a_llava_codec_boundary",
        "selected_112_blocks": len(blocks),
        "raw_patch_tokens": int(positions.shape[0]),
        "llm_visual_tokens": len(blocks),
        "src_positions_shape": list(positions.shape),
        "native_patch_grid": NATIVE_PATCH_GRID,
    }
    if meta:
        payload_meta.update(dict(meta))

    return {
        "src_positions": positions,
        "selected_blocks": blocks,
        "meta": payload_meta,
    }


def _infer_num_frames(src_positions: np.ndarray, upstream_stats: Mapping[str, Any] | None) -> int:
    token_counts = (upstream_stats or {}).get("token_counts")
    if isinstance(token_counts, Mapping):
        dense_raw = token_counts.get("dense_native_raw_patch_tokens")
        if isinstance(dense_raw, int) and dense_raw > 0:
            return max(1, dense_raw // (NATIVE_PATCH_GRID * NATIVE_PATCH_GRID))
    if src_positions.size == 0:
        return 0
    return int(src_positions[:, 0].max()) + 1


def _profile_fields(
    payload: Mapping[str, Any],
    upstream_stats: Mapping[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    upstream_stats = dict(upstream_stats or {})
    token_counts = upstream_stats.get("token_counts")
    compression = upstream_stats.get("compression")
    if isinstance(token_counts, Mapping) and isinstance(compression, Mapping):
        return {"token_counts": dict(token_counts), "compression": dict(compression)}

    selected_count = int(payload["meta"]["selected_112_blocks"])
    valid_tokens = int((token_counts or {}).get("autogaze_valid_tokens_total", 0)) if isinstance(token_counts, Mapping) else 0
    num_frames = _infer_num_frames(payload["src_positions"], upstream_stats)
    built_counts = build_token_counts(
        num_frames=num_frames,
        selected_112_blocks=selected_count,
        autogaze_valid_tokens_total=valid_tokens,
    )
    return {
        "token_counts": built_counts,
        "compression": build_compression_metrics(built_counts),
    }


def load_project_a_boundary_artifacts(source_dir: str | Path) -> dict[str, Any]:
    source_path = Path(source_dir)
    missing = [
        name
        for name in ("selected_blocks.json", "src_positions.npy")
        if not (source_path / name).exists()
    ]
    if missing:
        raise FileNotFoundError(
            "Project A boundary artifacts are missing: "
            + ", ".join(missing)
            + ". Run smoke_project_a_codec_synthetic.py first."
        )

    selected_blocks = read_selected_blocks(source_path / "selected_blocks.json")
    src_positions = read_src_positions(source_path / "src_positions.npy")
    stats = read_stats(source_path / "stats.json") if (source_path / "stats.json").exists() else {}
    payload = build_llava_codec_payload(
        selected_blocks=selected_blocks,
        src_positions=src_positions,
        meta={"source_dir": str(source_path)},
    )
    profile_fields = _profile_fields(payload, stats)
    boundary_stats = {
        "contract": "project_a_llava_codec_boundary",
        "selected_112_blocks": payload["meta"]["selected_112_blocks"],
        "raw_patch_tokens": payload["meta"]["raw_patch_tokens"],
        "llm_visual_tokens": payload["meta"]["llm_visual_tokens"],
        "src_positions_shape": payload["meta"]["src_positions_shape"],
        "valid_src_positions": True,
        "token_counts": profile_fields["token_counts"],
        "compression": profile_fields["compression"],
    }

    return {
        "payload": payload,
        "stats": boundary_stats,
        "profile_fields": profile_fields,
    }


def _file_contains(path: Path, names: Sequence[str]) -> dict[str, bool]:
    if not path.exists():
        return {name: False for name in names}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {name: name in text for name in names}


def inspect_llava_codec_source(source_root: str | Path) -> dict[str, Any]:
    """Inspect LLaVA-OV2 custom-code source without importing it."""

    root = Path(source_root)
    codec_file = root / "codec_video_processing_llava_onevision2.py"
    processor_file = root / "processing_llava_onevision2.py"
    codec_terms = _file_contains(
        codec_file,
        (
            "process_codec_video",
            "drop_padding_canvases",
            "codec_positions_for_processor",
            "codec_image_processor_outputs",
            "src_positions",
            "fps",
            "meta",
        ),
    )
    processor_terms = _file_contains(
        processor_file,
        (
            "video_backend",
            "codec",
            "image_grid_thw",
            "patch_positions",
            "process_codec_video",
        ),
    )
    status = "present" if codec_file.exists() and processor_file.exists() else "missing"

    return {
        "source_root": str(root),
        "codec_processing_file": str(codec_file) if codec_file.exists() else None,
        "processor_file": str(processor_file) if processor_file.exists() else None,
        "status": status,
        "has_process_codec_video": codec_terms["process_codec_video"],
        "has_drop_padding_canvases": codec_terms["drop_padding_canvases"],
        "has_codec_positions_for_processor": codec_terms["codec_positions_for_processor"],
        "has_codec_image_processor_outputs": codec_terms["codec_image_processor_outputs"],
        "has_src_positions": codec_terms["src_positions"],
        "has_fps": codec_terms["fps"],
        "has_meta": codec_terms["meta"],
        "processor_has_video_backend": processor_terms["video_backend"],
        "processor_has_codec_branch": processor_terms["codec"],
        "processor_has_image_grid_thw": processor_terms["image_grid_thw"],
        "processor_has_patch_positions": processor_terms["patch_positions"],
        "processor_calls_process_codec_video": processor_terms["process_codec_video"],
    }
