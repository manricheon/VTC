#!/usr/bin/env python
"""Synthetic Project B OV-direct smoke with profiling.

This script does not import AutoGaze, OneVision-Encoder, torch, transformers,
or run model inference. It exercises the pure-Python bridge path from
synthetic AutoGaze flat ids to OV-direct patches, fractional patch_positions,
and pack metadata.
"""

from __future__ import annotations

import argparse
import json
import tracemalloc
from pathlib import Path
from typing import Any

import numpy as np

from gaze_ov_bridge.autogaze_decode import decode_flat_ids
from gaze_ov_bridge.io_artifacts import (
    write_decoded_entries,
    write_pack_plan,
    write_patch_positions,
    write_patches,
    write_stats,
)
from gaze_ov_bridge.memory_probe import collect_memory_mb
from gaze_ov_bridge.ov_direct import build_ov_direct_plan
from gaze_ov_bridge.ov_pack import build_ov_pack_plan
from gaze_ov_bridge.ov_patch_extract import extract_ov_direct_patches
from gaze_ov_bridge.profile_schema import (
    create_profile_record,
    current_git_commit,
    write_profile_json,
)
from gaze_ov_bridge.profiling import StageTimer
from gaze_ov_bridge.token_metrics import DEFAULT_PATCH_SIZE, DEFAULT_TARGET_SCALES


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
VTC_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_OUT_DIR = PROJECT_ROOT / "out" / "smoke_project_b_ov_direct_synthetic"


def _synthetic_autogaze_output() -> tuple[np.ndarray, np.ndarray, int]:
    """Return gazing_pos, padding mask, and num_frames for a deterministic smoke."""

    # Per-frame layout at patch size 14:
    # 28: ids 0..3, 56: 4..19, 112: 20..83, 224: 84..339.
    # id 85 is a padded 224-scale token and must be skipped.
    gazing_pos = np.asarray([[0, 4, 20, 84, 85, 340]], dtype=np.int64)
    if_padded_gazing = np.asarray([[False, False, False, False, True, False]], dtype=bool)
    num_frames = 2
    return gazing_pos, if_padded_gazing, num_frames


def _synthetic_frames(num_frames: int) -> np.ndarray:
    """Create simple [T, 224, 224, 3] uint8 frames for synthetic patch extraction."""

    rows = np.arange(224, dtype=np.uint8).reshape(224, 1)
    cols = np.arange(224, dtype=np.uint8).reshape(1, 224)
    frames = np.zeros((num_frames, 224, 224, 3), dtype=np.uint8)
    frames[0, :, :, 0] = rows
    frames[0, :, :, 1] = cols
    frames[0, :, :, 2] = rows + cols
    if num_frames > 1:
        frames[1:] = np.asarray([17, 23, 31], dtype=np.uint8)
    return frames


def _expected_positions_by_scale() -> dict[int, list[float]]:
    return {
        28: [0.0, 3.5, 3.5],
        56: [0.0, 1.5, 1.5],
        112: [0.0, 0.5, 0.5],
        224: [0.0, 0.0, 0.0],
    }


def _validate_smoke_outputs(
    *,
    decoded_entries: list[dict[str, int]],
    direct_plan: dict[str, Any],
    patches: np.ndarray,
    pack_plan: dict[str, Any],
    stats: dict[str, Any],
    profile: dict[str, Any],
    profile_path: Path,
) -> None:
    total_tokens = len(decoded_entries)

    assert stats["total_tokens"] == total_tokens
    assert direct_plan["total_tokens"] == total_tokens
    assert len(direct_plan["tokens"]) == total_tokens
    assert direct_plan["patch_positions"].shape[0] == total_tokens
    assert patches.shape[0] == total_tokens
    assert len(pack_plan["tokens"]) == total_tokens
    assert stats["project_b_ov_direct_tokens"] == total_tokens
    assert stats["confirms_no_native_union"] is True
    assert all("covered_112_blocks" not in token for token in direct_plan["tokens"])
    assert all("native_positions" not in token for token in direct_plan["tokens"])
    assert all("padding" not in token for token in pack_plan["tokens"])

    positions_by_scale: dict[int, list[float]] = {}
    for token in direct_plan["tokens"]:
        positions_by_scale.setdefault(int(token["scale"]), token["patch_position"])
    for scale, expected_position in _expected_positions_by_scale().items():
        np.testing.assert_allclose(positions_by_scale[scale], expected_position)

    with profile_path.open("r", encoding="utf-8") as handle:
        reloaded_profile = json.load(handle)

    assert reloaded_profile["project"]["track"] == "project_b_ov_direct"
    assert reloaded_profile["project"]["policy_name"] == "direct_multiscale_no_union"
    for key in ("total", "decode", "patch_extract", "pack"):
        assert reloaded_profile["timings_s"][key] is not None
        assert reloaded_profile["timings_s"][key] > 0
    for key in ("process_peak_rss", "tracemalloc_peak"):
        assert key in reloaded_profile["memory_mb"]
    for key in (
        "autogaze_candidate_tokens_total",
        "autogaze_valid_tokens_total",
        "autogaze_tokens_by_scale",
        "dense_native_raw_patch_tokens",
        "project_b_ov_direct_tokens",
    ):
        assert key in reloaded_profile["token_counts"]
    for key in (
        "project_b_vs_autogaze_candidates_ratio",
        "project_b_vs_dense_native_ratio",
        "project_b_reduction_vs_candidates",
        "project_b_reduction_vs_dense_native",
    ):
        assert key in reloaded_profile["compression"]
    assert profile == reloaded_profile


def run_smoke(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tracemalloc.start()

    gazing_pos, if_padded_gazing, num_frames = _synthetic_autogaze_output()
    frames = _synthetic_frames(num_frames)
    timer = StageTimer()

    with timer.stage("total"):
        with timer.stage("decode"):
            decoded_entries = decode_flat_ids(gazing_pos, if_padded_gazing)
            direct_plan = build_ov_direct_plan(decoded_entries, num_frames=num_frames)
            patch_positions = direct_plan["patch_positions"]

        with timer.stage("patch_extract"):
            patches = extract_ov_direct_patches(frames, decoded_entries)

        with timer.stage("pack"):
            pack_plan = build_ov_pack_plan(num_tokens=direct_plan["total_tokens"])

        stats = dict(direct_plan["stats"])
        stats.update(
            {
                "patch_positions_shape": list(patch_positions.shape),
                "patches_shape": list(patches.shape),
                "pack_canvas_count": pack_plan["num_canvases"],
            }
        )

        write_decoded_entries(decoded_entries, out_dir / "decoded_entries.json")
        write_stats(stats, out_dir / "stats.json")
        write_patch_positions(patch_positions, out_dir / "patch_positions.npy")
        write_patches(patches, out_dir / "patches.npy")
        write_pack_plan(pack_plan, out_dir / "pack_plan.json")

    profile = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_b_ov_direct",
        env_name="bridge-core",
        policy_name="direct_multiscale_no_union",
        input_metadata={
            "video_id": "synthetic_project_b_ov_direct",
            "num_frames": num_frames,
            "target_scales": list(DEFAULT_TARGET_SCALES),
            "patch_size": DEFAULT_PATCH_SIZE,
        },
        token_counts=stats["token_counts"],
        compression=stats["compression"],
        timings_s=timer.as_dict(),
        memory_mb=collect_memory_mb(include_torch=False),
        notes=[
            "Synthetic Project B OV-direct smoke.",
            "No AutoGaze, OneVision-Encoder, torch, transformers, weights, or inference.",
        ],
        git_commit=current_git_commit(VTC_ROOT),
        run_id="smoke_project_b_ov_direct_synthetic",
        include_optional_torch_environment=False,
    )
    profile_path = out_dir / "profile.json"
    write_profile_json(profile, profile_path)

    _validate_smoke_outputs(
        decoded_entries=decoded_entries,
        direct_plan=direct_plan,
        patches=patches,
        pack_plan=pack_plan,
        stats=stats,
        profile=profile,
        profile_path=profile_path,
    )

    return {
        "out_dir": out_dir,
        "decoded_entries": decoded_entries,
        "direct_plan": direct_plan,
        "patches": patches,
        "pack_plan": pack_plan,
        "stats": stats,
        "profile": profile,
    }


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.6f}"


def print_summary(result: dict[str, Any]) -> None:
    stats = result["stats"]
    profile = result["profile"]
    compression = profile["compression"]
    memory = profile["memory_mb"]

    print("Project B OV-direct synthetic smoke")
    print(f"out_dir={result['out_dir']}")
    print(f"total_s={profile['timings_s']['total']:.6f}")
    print(f"direct_tokens={stats['total_tokens']}")
    print(f"tokens_by_scale={stats['tokens_by_scale']}")
    print(
        "project_b_vs_autogaze_candidates_ratio="
        f"{_format_optional_float(compression['project_b_vs_autogaze_candidates_ratio'])}"
    )
    print(
        "project_b_vs_dense_native_ratio="
        f"{_format_optional_float(compression['project_b_vs_dense_native_ratio'])}"
    )
    print(f"peak_rss_mb={_format_optional_float(memory['process_peak_rss'])}")
    print(f"confirms_no_native_union={stats['confirms_no_native_union']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run synthetic Project B OV-direct smoke with profiling.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for stats, profile, and synthetic OV-direct artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_smoke(args.out_dir.resolve())
    print_summary(result)


if __name__ == "__main__":
    main()
