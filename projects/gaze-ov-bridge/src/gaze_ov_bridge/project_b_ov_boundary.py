"""Project B OV-Encoder direct boundary validation.

This module validates OV-direct artifacts only. It does not import
OneVision-Encoder, AutoGaze, torch, transformers, or model weights.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .io_artifacts import (
    read_decoded_entries,
    read_pack_plan,
    read_patch_positions,
    read_patches,
    read_stats,
)
from .ov_direct import ov_fractional_position
from .token_metrics import (
    DEFAULT_PATCH_SIZE,
    NATIVE_PATCH_GRID,
    build_compression_metrics,
    build_token_counts,
)


def _entry_int(entry: Mapping[str, Any], key: str) -> int:
    return int(entry[key])


def validate_patches(
    patches: Any,
    *,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> np.ndarray:
    array = np.asarray(patches)
    if array.ndim != 4:
        raise ValueError("patches must have shape [K, 14, 14, C] or [K, C, 14, 14]")
    hwc = array.shape[1] == patch_size and array.shape[2] == patch_size
    chw = array.shape[2] == patch_size and array.shape[3] == patch_size
    if not hwc and not chw:
        raise ValueError("patches must contain 14x14 spatial patches")
    return array


def validate_no_native_union(
    decoded_entries: Sequence[Mapping[str, Any]],
    patch_positions: Any,
) -> None:
    positions = np.asarray(patch_positions)
    if len(decoded_entries) != positions.shape[0]:
        raise ValueError(
            "Project B requires one OV token per valid AutoGaze entry; "
            f"got {len(decoded_entries)} entries and {positions.shape[0]} patch_positions"
        )


def validate_patch_positions(
    patch_positions: Any,
    *,
    decoded_entries: Sequence[Mapping[str, Any]] | None = None,
    native_grid: int = NATIVE_PATCH_GRID,
    patch_size: int = DEFAULT_PATCH_SIZE,
) -> np.ndarray:
    positions = np.asarray(patch_positions, dtype=np.float32)
    if positions.ndim != 2 or positions.shape[1] != 3:
        raise ValueError("patch_positions must have shape [K, 3]")
    if not np.all(np.isfinite(positions)):
        raise ValueError("patch_positions must contain finite values")
    if decoded_entries is None:
        return positions

    validate_no_native_union(decoded_entries, positions)
    expected_rows: list[list[float]] = []
    for entry in decoded_entries:
        h, w = ov_fractional_position(
            scale=_entry_int(entry, "scale"),
            row=_entry_int(entry, "row"),
            col=_entry_int(entry, "col"),
            native_grid=native_grid,
            patch_size=patch_size,
        )
        expected_rows.append([float(_entry_int(entry, "frame_idx")), h, w])
    expected = np.asarray(expected_rows, dtype=np.float32).reshape(-1, 3)
    if not np.allclose(positions, expected):
        raise ValueError("patch_positions do not match expected fractional OV positions")
    return positions


def validate_pack_plan(pack_plan: Mapping[str, Any], *, num_tokens: int) -> dict[str, Any]:
    tokens = list(pack_plan.get("tokens", []))
    if len(tokens) != num_tokens:
        raise ValueError(f"pack_plan token count must equal {num_tokens}")
    for expected_idx, token in enumerate(tokens):
        if "padding" in token:
            raise ValueError("pack_plan token metadata must exclude padding slots")
        if int(token.get("token_idx", -1)) != expected_idx:
            raise ValueError("pack_plan token_idx values must preserve input order")
        slot_idx = int(token.get("slot_idx", -1))
        canvas_grid = int(pack_plan.get("canvas_grid", 0))
        if canvas_grid <= 0:
            raise ValueError("pack_plan canvas_grid must be positive")
        expected_row = slot_idx // canvas_grid
        expected_col = slot_idx % canvas_grid
        if int(token.get("row", -1)) != expected_row or int(token.get("col", -1)) != expected_col:
            raise ValueError("pack_plan row/col values must match slot_idx")
    return dict(pack_plan)


def build_ov_boundary_payload(
    *,
    decoded_entries: Sequence[Mapping[str, Any]],
    patches: Any,
    patch_positions: Any,
    pack_plan: Mapping[str, Any],
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    validated_patches = validate_patches(patches)
    positions = validate_patch_positions(patch_positions, decoded_entries=decoded_entries)
    validate_no_native_union(decoded_entries, positions)
    validated_pack = validate_pack_plan(pack_plan, num_tokens=positions.shape[0])

    if validated_patches.shape[0] != positions.shape[0]:
        raise ValueError(
            "patches and patch_positions must have the same token count "
            f"(got {validated_patches.shape[0]} and {positions.shape[0]})"
        )

    payload_meta = {
        "contract": "project_b_ov_direct_boundary",
        "total_tokens": int(positions.shape[0]),
        "patches_shape": list(validated_patches.shape),
        "patch_positions_shape": list(positions.shape),
        "pack_canvas_count": int(validated_pack.get("num_canvases", 0)),
        "confirms_no_native_union": True,
    }
    if meta:
        payload_meta.update(dict(meta))

    return {
        "decoded_entries": [dict(entry) for entry in decoded_entries],
        "patches": validated_patches,
        "patch_positions": positions,
        "pack_plan": validated_pack,
        "meta": payload_meta,
    }


def _infer_num_frames(decoded_entries: Sequence[Mapping[str, Any]], upstream_stats: Mapping[str, Any]) -> int:
    token_counts = upstream_stats.get("token_counts")
    if isinstance(token_counts, Mapping):
        dense_raw = token_counts.get("dense_native_raw_patch_tokens")
        if isinstance(dense_raw, int) and dense_raw > 0:
            return max(1, dense_raw // (NATIVE_PATCH_GRID * NATIVE_PATCH_GRID))
    max_frame = max((_entry_int(entry, "frame_idx") for entry in decoded_entries), default=-1)
    return max_frame + 1


def _profile_fields(
    payload: Mapping[str, Any],
    upstream_stats: Mapping[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    stats = dict(upstream_stats or {})
    token_counts = stats.get("token_counts")
    compression = stats.get("compression")
    if isinstance(token_counts, Mapping) and isinstance(compression, Mapping):
        return {"token_counts": dict(token_counts), "compression": dict(compression)}

    decoded_entries = payload["decoded_entries"]
    num_frames = _infer_num_frames(decoded_entries, stats)
    built_counts = build_token_counts(
        num_frames=num_frames,
        autogaze_valid_tokens_total=int(payload["meta"]["total_tokens"]),
    )
    return {
        "token_counts": built_counts,
        "compression": build_compression_metrics(built_counts),
    }


def load_project_b_boundary_artifacts(source_dir: str | Path) -> dict[str, Any]:
    source_path = Path(source_dir)
    required = ("decoded_entries.json", "patches.npy", "patch_positions.npy", "pack_plan.json")
    missing = [name for name in required if not (source_path / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Project B boundary artifacts are missing: "
            + ", ".join(missing)
            + ". Run smoke_project_b_ov_direct_synthetic.py first."
        )

    decoded_entries = read_decoded_entries(source_path / "decoded_entries.json")
    patches = read_patches(source_path / "patches.npy")
    patch_positions = read_patch_positions(source_path / "patch_positions.npy")
    pack_plan = read_pack_plan(source_path / "pack_plan.json")
    stats = read_stats(source_path / "stats.json") if (source_path / "stats.json").exists() else {}
    payload = build_ov_boundary_payload(
        decoded_entries=decoded_entries,
        patches=patches,
        patch_positions=patch_positions,
        pack_plan=pack_plan,
        meta={"source_dir": str(source_path)},
    )
    profile_fields = _profile_fields(payload, stats)
    boundary_stats = {
        "contract": "project_b_ov_direct_boundary",
        "total_tokens": payload["meta"]["total_tokens"],
        "patch_positions_shape": payload["meta"]["patch_positions_shape"],
        "patches_shape": payload["meta"]["patches_shape"],
        "pack_canvas_count": payload["meta"]["pack_canvas_count"],
        "confirms_no_native_union": True,
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


def inspect_ov_encoder_source(source_root: str | Path) -> dict[str, Any]:
    """Inspect OneVision-Encoder source without importing model code."""

    root = Path(source_root)
    modeling_file = root / "modeling_onevision_encoder.py"
    config_file = root / "configuration_onevision_encoder.py"
    readme_file = root / "README.md"
    model_terms = _file_contains(
        modeling_file,
        (
            "patch_positions",
            "visible_indices",
            "forward_from_positions",
            "_attn_implementation",
            "flash_attention_2",
            "eager",
        ),
    )
    config_terms = _file_contains(config_file, ("image_size", "patch_size", "rope"))
    readme_terms = _file_contains(readme_file, ("224", "patch_positions", "flash_attention_2"))
    status = "present" if modeling_file.exists() and config_file.exists() else "missing"

    return {
        "source_root": str(root),
        "modeling_file": str(modeling_file) if modeling_file.exists() else None,
        "config_file": str(config_file) if config_file.exists() else None,
        "readme_file": str(readme_file) if readme_file.exists() else None,
        "status": status,
        "has_patch_positions": model_terms["patch_positions"],
        "has_visible_indices": model_terms["visible_indices"],
        "has_forward_from_positions": model_terms["forward_from_positions"],
        "has_attn_implementation": model_terms["_attn_implementation"],
        "has_flash_attention_2": model_terms["flash_attention_2"] or readme_terms["flash_attention_2"],
        "has_eager_fallback_indicator": model_terms["eager"],
        "config_has_image_size": config_terms["image_size"],
        "config_has_patch_size": config_terms["patch_size"],
        "config_has_rope": config_terms["rope"],
        "readme_mentions_224": readme_terms["224"],
        "readme_mentions_patch_positions": readme_terms["patch_positions"],
    }
