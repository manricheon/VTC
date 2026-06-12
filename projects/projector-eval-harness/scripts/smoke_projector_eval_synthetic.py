#!/usr/bin/env python
"""Synthetic projector-eval smoke with profiling and report generation.

This script does not download checkpoints, access datasets, initialize CUDA, or
run model inference. It exercises the guarded public contracts: source audit,
asset mapping, benchmark matrix construction, checkpoint blockers, and report
generation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tracemalloc
from pathlib import Path
from time import perf_counter
from typing import Any

from vtc_projector_eval.assets import PROJECTOR_ASSETS
from vtc_projector_eval.matrix import DEFAULT_PRESETS, build_matrix
from vtc_projector_eval.reports import build_report, checkpoint_blockers, write_report
from vtc_projector_eval.sources import audit_sources


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
VTC_ROOT = SCRIPT_PATH.parents[3]
DEFAULT_OUT_DIR = PROJECT_ROOT / "out" / "smoke_projector_eval_synthetic"


def _current_git_commit(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _memory_mb() -> dict[str, float | None]:
    current, peak = tracemalloc.get_traced_memory()
    return {
        "process_peak_rss": None,
        "tracemalloc_current": current / (1024 * 1024),
        "tracemalloc_peak": peak / (1024 * 1024),
    }


def run_smoke(out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tracemalloc.start()
    start = perf_counter()

    source_audit = audit_sources(VTC_ROOT)
    matrix_rows = build_matrix(preset="smoke", projector_model="all", limit=1)
    blockers = checkpoint_blockers(VTC_ROOT)

    stats = {
        "projector_models": len(PROJECTOR_ASSETS),
        "smoke_tasks": len(DEFAULT_PRESETS["smoke"]),
        "smoke_matrix_rows": len(matrix_rows),
        "checkpoint_blockers": len(blockers),
        "downloads": "not_run",
        "model_inference": "not_run",
        "source_audit": source_audit,
    }
    _write_json(out_dir / "stats.json", stats)

    report = build_report(
        repo_root=VTC_ROOT,
        profiles=[],
        result_paths=[],
        run_id="smoke_projector_eval_synthetic",
        preset="smoke",
        limit=1,
        created_at_utc="synthetic",
    )
    report_path = out_dir / "report.md"
    write_report(report, report_path)

    elapsed = perf_counter() - start
    profile = {
        "run_id": "smoke_projector_eval_synthetic",
        "git_commit": _current_git_commit(VTC_ROOT),
        "project": {
            "name": "projector-eval-harness",
            "track": "projector_eval",
            "env_name": "bridge-core",
            "policy_name": "synthetic_source_matrix_report",
        },
        "input_metadata": {
            "preset": "smoke",
            "tasks": list(DEFAULT_PRESETS["smoke"]),
            "report_path": str(report_path),
        },
        "token_counts": {
            "projector_models": len(PROJECTOR_ASSETS),
            "smoke_tasks": len(DEFAULT_PRESETS["smoke"]),
            "smoke_matrix_rows": len(matrix_rows),
            "checkpoint_blockers": len(blockers),
        },
        "compression": {
            "visual_ratio": None,
        },
        "timings_s": {
            "total": elapsed,
            "source_audit_matrix_report": elapsed,
        },
        "memory_mb": _memory_mb(),
        "task_metrics": {
            "score": None,
        },
        "notes": [
            "Synthetic projector eval smoke.",
            "No checkpoint download, dataset access, CUDA runtime, or model inference.",
        ],
    }
    _write_json(out_dir / "profile.json", profile)
    return {"out_dir": out_dir, "stats": stats, "profile": profile, "report_path": report_path}


def print_summary(result: dict[str, Any]) -> None:
    stats = result["stats"]
    profile = result["profile"]
    print("Projector eval synthetic smoke")
    print(f"out_dir={result['out_dir']}")
    print(f"total_s={profile['timings_s']['total']:.6f}")
    print(f"projector_models={stats['projector_models']}")
    print(f"smoke_tasks={stats['smoke_tasks']}")
    print(f"smoke_matrix_rows={stats['smoke_matrix_rows']}")
    print(f"checkpoint_blockers={stats['checkpoint_blockers']}")
    print(f"downloads={stats['downloads']}")
    print(f"model_inference={stats['model_inference']}")
    print(f"report_path={result['report_path']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Output directory for stats, profile, and report artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_smoke(args.out_dir.resolve())
    print_summary(result)


if __name__ == "__main__":
    main()
