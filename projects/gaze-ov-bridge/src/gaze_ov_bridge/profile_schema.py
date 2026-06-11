"""Profile schema construction and JSON writers."""

from __future__ import annotations

import json
import math
import platform
import subprocess
import sys
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .memory_probe import MEMORY_KEYS
from .token_metrics import (
    COMPRESSION_KEYS,
    TOKEN_COUNT_KEYS,
    build_compression_metrics,
    empty_compression_metrics,
    empty_token_counts,
)


SCHEMA_VERSION = "1.0.0"
ALLOWED_TRACKS = {
    "project_a_codec",
    "project_b_ov_direct",
    "autogaze",
    "llava_ov2",
    "ov_encoder",
    "lmms_eval",
    "compat_probe",
}

TIMING_KEYS = (
    "total",
    "decode",
    "selector",
    "src_positions",
    "patch_extract",
    "pack",
    "processor",
    "model_forward",
    "generate",
    "eval",
)

TASK_METRIC_KEYS = (
    "score",
    "accuracy",
    "benchmark_name",
)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _package_version(distribution_name: str) -> str | None:
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version(distribution_name)
    except PackageNotFoundError:
        return None


def _optional_torch_environment() -> tuple[bool | None, bool | None, str | None]:
    torch_version = _package_version("torch")
    if torch_version is None:
        return None, None, None

    try:
        import torch
    except Exception:  # noqa: BLE001 - optional diagnostic path.
        return None, None, torch_version

    cuda_available: bool | None
    mps_available: bool | None

    try:
        cuda_available = bool(torch.cuda.is_available())
    except Exception:  # noqa: BLE001 - optional diagnostic path.
        cuda_available = None

    try:
        mps_backend = getattr(torch.backends, "mps", None)
        mps_available = bool(mps_backend and mps_backend.is_available())
    except Exception:  # noqa: BLE001 - optional diagnostic path.
        mps_available = None

    return cuda_available, mps_available, torch_version


def current_git_commit(cwd: str | Path | None = None) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def create_environment_record(env_name: str) -> dict[str, Any]:
    cuda_available, mps_available, torch_version = _optional_torch_environment()
    return {
        "env_name": env_name,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.replace("\n", " "),
        "cuda_available": cuda_available,
        "mps_available": mps_available,
        "torch_version": torch_version,
        "transformers_version": _package_version("transformers"),
    }


def _input_defaults() -> dict[str, Any]:
    return {
        "video_id": None,
        "num_frames": None,
        "target_scales": [28, 56, 112, 224],
        "patch_size": 14,
    }


def _timing_defaults() -> dict[str, float | None]:
    return {key: None for key in TIMING_KEYS}


def _memory_defaults() -> dict[str, float | None]:
    return {key: None for key in MEMORY_KEYS}


def _task_metric_defaults() -> dict[str, Any]:
    return {key: None for key in TASK_METRIC_KEYS}


def _merge_defaults(defaults: dict[str, Any], values: Mapping[str, Any] | None) -> dict[str, Any]:
    merged = dict(defaults)
    if values:
        merged.update(values)
    return merged


def create_profile_record(
    *,
    project_name: str,
    track: str,
    env_name: str,
    policy_name: str | None = None,
    input_metadata: Mapping[str, Any] | None = None,
    token_counts: Mapping[str, Any] | None = None,
    compression: Mapping[str, Any] | None = None,
    timings_s: Mapping[str, Any] | None = None,
    memory_mb: Mapping[str, Any] | None = None,
    task_metrics: Mapping[str, Any] | None = None,
    notes: str | list[str] | None = None,
    git_commit: str | None = None,
    run_id: str | None = None,
    created_at_utc: str | None = None,
    environment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if track not in ALLOWED_TRACKS:
        allowed = ", ".join(sorted(ALLOWED_TRACKS))
        raise ValueError(f"track must be one of: {allowed}")

    merged_token_counts = _merge_defaults(empty_token_counts(), token_counts)
    if compression is None:
        if token_counts is None:
            merged_compression = empty_compression_metrics()
        else:
            merged_compression = build_compression_metrics(merged_token_counts)
    else:
        merged_compression = _merge_defaults(
            {key: None for key in COMPRESSION_KEYS},
            compression,
        )

    if isinstance(notes, str):
        normalized_notes: list[str] = [notes]
    elif notes is None:
        normalized_notes = []
    else:
        normalized_notes = list(notes)

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id or str(uuid.uuid4()),
        "created_at_utc": created_at_utc or _utc_now(),
        "git_commit": git_commit,
        "project": {
            "project_name": project_name,
            "track": track,
            "policy_name": policy_name,
        },
        "environment": _merge_defaults(create_environment_record(env_name), environment),
        "input": _merge_defaults(_input_defaults(), input_metadata),
        "token_counts": merged_token_counts,
        "compression": merged_compression,
        "timings_s": _merge_defaults(_timing_defaults(), timings_s),
        "memory_mb": _merge_defaults(_memory_defaults(), memory_mb),
        "task_metrics": _merge_defaults(_task_metric_defaults(), task_metrics),
        "notes": normalized_notes,
    }


def json_ready(value: Any) -> Any:
    """Convert common Python/NumPy-like values into strict JSON values."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, set):
        return [json_ready(item) for item in sorted(value)]
    if hasattr(value, "item"):
        try:
            return json_ready(value.item())
        except Exception:  # noqa: BLE001 - best-effort serialization helper.
            pass
    if hasattr(value, "tolist"):
        try:
            return json_ready(value.tolist())
        except Exception:  # noqa: BLE001 - best-effort serialization helper.
            pass
    return str(value)


def write_profile_json(record: Mapping[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(json_ready(record), handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def append_profile_jsonl(record: Mapping[str, Any], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(json_ready(record), sort_keys=True, allow_nan=False))
        handle.write("\n")
