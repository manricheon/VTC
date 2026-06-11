#!/usr/bin/env python
"""Project B OV-Encoder direct boundary smoke.

This validates OV-direct artifacts only. It does not import OneVision-Encoder,
torch, transformers, AutoGaze, or run model forward.
"""

from __future__ import annotations

import argparse
import json
import tracemalloc
from pathlib import Path
from typing import Any

from gaze_ov_bridge.io_artifacts import write_stats
from gaze_ov_bridge.memory_probe import collect_memory_mb
from gaze_ov_bridge.profile_schema import (
    create_profile_record,
    current_git_commit,
    write_profile_json,
)
from gaze_ov_bridge.profiling import StageTimer
from gaze_ov_bridge.project_b_ov_boundary import (
    inspect_ov_encoder_source,
    load_project_b_boundary_artifacts,
)
from gaze_ov_bridge.token_metrics import DEFAULT_PATCH_SIZE, DEFAULT_TARGET_SCALES


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
VTC_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "out" / "smoke_project_b_ov_direct_synthetic"
DEFAULT_OUT_DIR = PROJECT_ROOT / "out" / "smoke_project_b_ov_boundary"
DEFAULT_OV_CODE_DIR = VTC_ROOT / "external" / "OneVision-Encoder"


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_smoke(
    *,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    out_dir: Path = DEFAULT_OUT_DIR,
    source_root: Path = DEFAULT_OV_CODE_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tracemalloc.start()
    timer = StageTimer()

    with timer.stage("total"):
        with timer.stage("load_artifacts"):
            loaded = load_project_b_boundary_artifacts(source_dir)

        with timer.stage("validate_patches"):
            payload = loaded["payload"]
            stats = dict(loaded["stats"])

        with timer.stage("validate_positions"):
            # Position validation is performed in load_project_b_boundary_artifacts.
            stats["validated_patch_positions"] = True

        with timer.stage("optional_import_probe"):
            source_probe = inspect_ov_encoder_source(source_root)

        stats["ov_encoder_source_probe"] = source_probe
        write_stats(stats, out_dir / "stats.json")

    profile = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_b_ov_direct",
        env_name="bridge-core",
        policy_name="ov_boundary_no_union",
        input_metadata={
            "video_id": "synthetic_project_b_ov_boundary",
            "num_frames": loaded["profile_fields"]["token_counts"].get("dense_native_raw_patch_tokens", 0) // 256,
            "target_scales": list(DEFAULT_TARGET_SCALES),
            "patch_size": DEFAULT_PATCH_SIZE,
        },
        token_counts=loaded["profile_fields"]["token_counts"],
        compression=loaded["profile_fields"]["compression"],
        timings_s=timer.as_dict(),
        memory_mb=collect_memory_mb(include_torch=False),
        notes=[
            "Project B OV-direct boundary validation only.",
            "No model import, weights, forward pass, torch, or transformers.",
        ],
        git_commit=current_git_commit(VTC_ROOT),
        run_id="smoke_project_b_ov_boundary",
        include_optional_torch_environment=False,
    )
    write_profile_json(profile, out_dir / "profile.json")

    _write_json(
        {
            "patch_positions_shape": payload["meta"]["patch_positions_shape"],
            "patches_shape": payload["meta"]["patches_shape"],
            "pack_canvas_count": payload["meta"]["pack_canvas_count"],
            "meta": payload["meta"],
        },
        out_dir / "payload_summary.json",
    )

    return {
        "out_dir": out_dir,
        "source_dir": source_dir,
        "source_probe": source_probe,
        "payload": payload,
        "stats": stats,
        "profile": profile,
    }


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return "None"
    return f"{value:.6f}"


def print_summary(result: dict[str, Any]) -> None:
    profile = result["profile"]
    token_counts = profile["token_counts"]
    compression = profile["compression"]
    memory = profile["memory_mb"]

    print("Project B OV boundary smoke")
    print(f"source_dir={result['source_dir']}")
    print(f"out_dir={result['out_dir']}")
    print(f"total_s={profile['timings_s']['total']:.6f}")
    print(f"direct_tokens={token_counts['project_b_ov_direct_tokens']}")
    print(
        "project_b_vs_autogaze_candidates_ratio="
        f"{_format_optional_float(compression['project_b_vs_autogaze_candidates_ratio'])}"
    )
    print(
        "project_b_vs_dense_native_ratio="
        f"{_format_optional_float(compression['project_b_vs_dense_native_ratio'])}"
    )
    print(f"peak_rss_mb={_format_optional_float(memory['process_peak_rss'])}")
    print(f"confirms_no_native_union={result['stats']['confirms_no_native_union']}")
    print(f"ov_encoder_source_status={result['source_probe']['status']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Project B synthetic OV-direct artifacts at the OV-Encoder boundary.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing Project B synthetic artifacts.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for boundary stats/profile.",
    )
    parser.add_argument(
        "--ov-code-dir",
        type=Path,
        default=DEFAULT_OV_CODE_DIR,
        help="OneVision-Encoder code snapshot for source-only inspection.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_smoke(
        source_dir=args.source_dir.resolve(),
        out_dir=args.out_dir.resolve(),
        source_root=args.ov_code_dir.resolve(),
    )
    print_summary(result)


if __name__ == "__main__":
    main()
