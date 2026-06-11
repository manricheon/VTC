#!/usr/bin/env python
"""Project A LLaVA-OV2 codec boundary smoke.

This validates the bridge artifact contract only. It does not import LLaVA-OV2,
torch, transformers, AutoGaze, or run generation.
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
from gaze_ov_bridge.project_a_llava_boundary import (
    inspect_llava_codec_source,
    load_project_a_boundary_artifacts,
)
from gaze_ov_bridge.token_metrics import DEFAULT_PATCH_SIZE, DEFAULT_TARGET_SCALES


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
VTC_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "out" / "smoke_project_a_codec_synthetic"
DEFAULT_OUT_DIR = PROJECT_ROOT / "out" / "smoke_project_a_llava_boundary"
DEFAULT_LLAVA_CODE_DIR = VTC_ROOT / "external" / "LLaVA-OneVision-2-8B-Instruct-code"


def _write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_smoke(
    *,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    out_dir: Path = DEFAULT_OUT_DIR,
    source_root: Path = DEFAULT_LLAVA_CODE_DIR,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tracemalloc.start()
    timer = StageTimer()

    with timer.stage("total"):
        with timer.stage("load_artifacts"):
            loaded = load_project_a_boundary_artifacts(source_dir)

        with timer.stage("validate_src_positions"):
            payload = loaded["payload"]
            stats = dict(loaded["stats"])

        with timer.stage("optional_processor_probe"):
            source_probe = inspect_llava_codec_source(source_root)

        stats["llava_codec_source_probe"] = source_probe
        write_stats(stats, out_dir / "stats.json")

    profile = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_a_codec",
        env_name="bridge-core",
        policy_name="llava_boundary_contract",
        input_metadata={
            "video_id": "synthetic_project_a_llava_boundary",
            "num_frames": loaded["profile_fields"]["token_counts"].get("dense_native_raw_patch_tokens", 0) // 256,
            "target_scales": list(DEFAULT_TARGET_SCALES),
            "patch_size": DEFAULT_PATCH_SIZE,
        },
        token_counts=loaded["profile_fields"]["token_counts"],
        compression=loaded["profile_fields"]["compression"],
        timings_s=timer.as_dict(),
        memory_mb=collect_memory_mb(include_torch=False),
        notes=[
            "Project A LLaVA codec boundary validation only.",
            "No model import, weights, generation, torch, or transformers.",
        ],
        git_commit=current_git_commit(VTC_ROOT),
        run_id="smoke_project_a_llava_boundary",
        include_optional_torch_environment=False,
    )
    write_profile_json(profile, out_dir / "profile.json")

    _write_json(
        {
            "selected_blocks": payload["selected_blocks"],
            "src_positions_shape": payload["meta"]["src_positions_shape"],
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

    print("Project A LLaVA codec boundary smoke")
    print(f"source_dir={result['source_dir']}")
    print(f"out_dir={result['out_dir']}")
    print(f"total_s={profile['timings_s']['total']:.6f}")
    print(f"selected_112_blocks={token_counts['selected_112_blocks']}")
    print(f"raw_patch_tokens={token_counts['project_a_raw_patch_tokens']}")
    print(f"llm_visual_tokens={token_counts['project_a_llm_visual_tokens']}")
    print(
        "project_a_vs_dense_raw_ratio="
        f"{_format_optional_float(compression['project_a_vs_dense_raw_ratio'])}"
    )
    print(
        "project_a_vs_dense_visual_ratio="
        f"{_format_optional_float(compression['project_a_vs_dense_visual_ratio'])}"
    )
    print(f"peak_rss_mb={_format_optional_float(memory['process_peak_rss'])}")
    print(f"llava_codec_source_status={result['source_probe']['status']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Project A synthetic artifacts against the LLaVA codec boundary.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing selected_blocks.json and src_positions.npy.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for boundary stats/profile.",
    )
    parser.add_argument(
        "--llava-code-dir",
        type=Path,
        default=DEFAULT_LLAVA_CODE_DIR,
        help="LLaVA-OV2 custom-code source directory for source-only inspection.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_smoke(
        source_dir=args.source_dir.resolve(),
        out_dir=args.out_dir.resolve(),
        source_root=args.llava_code_dir.resolve(),
    )
    print_summary(result)


if __name__ == "__main__":
    main()
