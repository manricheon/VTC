#!/usr/bin/env python
"""Synthetic Project A codec-compatible smoke with profiling.

This script does not import AutoGaze, LLaVA-OV2, torch, transformers, or run
model inference. It exercises the pure-Python bridge path from synthetic
AutoGaze flat ids to LLaVA-OV2 codec-compatible src_positions artifacts.
"""

from __future__ import annotations

import argparse
import json
import tracemalloc
from pathlib import Path
from typing import Any

import numpy as np

from gaze_ov_bridge.autogaze_decode import decode_flat_ids
from gaze_ov_bridge.codec_canvas import build_src_positions
from gaze_ov_bridge.io_artifacts import (
    write_decoded_entries,
    write_selected_blocks,
    write_src_positions,
    write_stats,
)
from gaze_ov_bridge.memory_probe import collect_memory_mb
from gaze_ov_bridge.profile_schema import (
    create_profile_record,
    current_git_commit,
    write_profile_json,
)
from gaze_ov_bridge.profiling import StageTimer
from gaze_ov_bridge.selector_112_anchor import select_112_anchor_blocks
from gaze_ov_bridge.token_metrics import DEFAULT_PATCH_SIZE, DEFAULT_TARGET_SCALES


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
VTC_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_OUT_DIR = PROJECT_ROOT / "out" / "smoke_project_a_codec_synthetic"


def _synthetic_autogaze_output() -> tuple[np.ndarray, np.ndarray, int]:
    """Return gazing_pos, padding mask, and num_frames for a deterministic smoke."""

    # Per-frame layout at patch size 14:
    # 28: ids 0..3, 56: 4..19, 112: 20..83, 224: 84..339.
    # id 137 is 224-scale row 3 col 5, which votes for 112 block row 1 col 2.
    gazing_pos = np.asarray([[0, 4, 20, 137, 85, 340]], dtype=np.int64)
    if_padded_gazing = np.asarray([[False, False, False, False, True, False]], dtype=bool)
    num_frames = 2
    return gazing_pos, if_padded_gazing, num_frames


def _validate_smoke_outputs(
    *,
    decoded_entries: list[dict[str, int]],
    selected_blocks: list[tuple[int, int, int]],
    stats: dict[str, Any],
    profile: dict[str, Any],
    profile_path: Path,
) -> None:
    selected_block_lists = [[frame, row, col] for frame, row, col in selected_blocks]

    assert {entry["scale"] for entry in decoded_entries} == {28, 56, 112, 224}
    assert stats["raw_patch_tokens"] == stats["selected_112_blocks"] * 4
    assert stats["llm_visual_tokens"] == stats["selected_112_blocks"]
    assert stats["confirms_no_hard_union_default"] is True

    # Under the default 112-anchor policy, 56/28 entries remain priors and do
    # not add their covered 112 blocks by hard union.
    assert selected_block_lists == [[0, 0, 0], [0, 1, 2]]
    assert [0, 0, 1] not in selected_block_lists
    assert [0, 3, 3] not in selected_block_lists

    with profile_path.open("r", encoding="utf-8") as handle:
        reloaded_profile = json.load(handle)

    assert reloaded_profile["project"]["track"] == "project_a_codec"
    assert reloaded_profile["project"]["policy_name"] == "anchor112_default"
    for key in ("total", "decode", "selector", "src_positions"):
        assert reloaded_profile["timings_s"][key] is not None
        assert reloaded_profile["timings_s"][key] > 0
    for key in (
        "autogaze_candidate_tokens_total",
        "autogaze_valid_tokens_total",
        "autogaze_tokens_by_scale",
        "dense_native_raw_patch_tokens",
        "dense_native_merged_visual_tokens",
        "selected_112_blocks",
        "project_a_raw_patch_tokens",
        "project_a_llm_visual_tokens",
    ):
        assert key in reloaded_profile["token_counts"]
    assert profile == reloaded_profile


def run_smoke(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tracemalloc.start()

    gazing_pos, if_padded_gazing, num_frames = _synthetic_autogaze_output()
    timer = StageTimer()

    with timer.stage("total"):
        with timer.stage("decode"):
            decoded_entries = decode_flat_ids(gazing_pos, if_padded_gazing)

        with timer.stage("selector"):
            selection = select_112_anchor_blocks(
                decoded_entries,
                hard_union=False,
                num_frames=num_frames,
            )
            selected_blocks = selection["selected_blocks"]
            stats = selection["stats"]

        with timer.stage("src_positions"):
            src_positions = build_src_positions(selected_blocks)

        write_decoded_entries(decoded_entries, out_dir / "decoded_entries.json")
        write_selected_blocks(selected_blocks, out_dir / "selected_blocks.json")
        write_src_positions(src_positions, out_dir / "src_positions.npy")
        write_stats(stats, out_dir / "stats.json")

    profile = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_a_codec",
        env_name="bridge-core",
        policy_name="anchor112_default",
        input_metadata={
            "video_id": "synthetic_project_a_codec",
            "num_frames": num_frames,
            "target_scales": list(DEFAULT_TARGET_SCALES),
            "patch_size": DEFAULT_PATCH_SIZE,
        },
        token_counts=stats["token_counts"],
        compression=stats["compression"],
        timings_s=timer.as_dict(),
        memory_mb=collect_memory_mb(include_torch=False),
        notes=[
            "Synthetic Project A codec smoke.",
            "No AutoGaze, LLaVA-OV2, torch, transformers, weights, or inference.",
        ],
        git_commit=current_git_commit(VTC_ROOT),
        run_id="smoke_project_a_codec_synthetic",
        include_optional_torch_environment=False,
    )
    profile_path = out_dir / "profile.json"
    write_profile_json(profile, profile_path)

    _validate_smoke_outputs(
        decoded_entries=decoded_entries,
        selected_blocks=selected_blocks,
        stats=stats,
        profile=profile,
        profile_path=profile_path,
    )

    return {
        "out_dir": out_dir,
        "stats": stats,
        "profile": profile,
        "decoded_entries": decoded_entries,
        "selected_blocks": selected_blocks,
        "src_positions": src_positions,
    }


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.6f}"


def print_summary(result: dict[str, Any]) -> None:
    stats = result["stats"]
    profile = result["profile"]
    token_counts = profile["token_counts"]
    compression = profile["compression"]
    memory = profile["memory_mb"]

    print("Project A codec synthetic smoke")
    print(f"out_dir={result['out_dir']}")
    print(f"total_s={profile['timings_s']['total']:.6f}")
    print(f"valid_autogaze_tokens={token_counts['autogaze_valid_tokens_total']}")
    print(f"selected_112_blocks={stats['selected_112_blocks']}")
    print(f"raw_patch_tokens={stats['raw_patch_tokens']}")
    print(f"llm_visual_tokens={stats['llm_visual_tokens']}")
    print(
        "project_a_vs_dense_raw_ratio="
        f"{_format_optional_float(compression['project_a_vs_dense_raw_ratio'])}"
    )
    print(
        "project_a_vs_dense_visual_ratio="
        f"{_format_optional_float(compression['project_a_vs_dense_visual_ratio'])}"
    )
    print(f"peak_rss_mb={_format_optional_float(memory['process_peak_rss'])}")
    print(
        "confirms_no_hard_union_default="
        f"{stats['confirms_no_hard_union_default']}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run synthetic Project A codec-compatible smoke with profiling.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for stats, profile, and synthetic bridge artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_smoke(args.out_dir.resolve())
    print_summary(result)


if __name__ == "__main__":
    main()
