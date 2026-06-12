"""Runtime profile JSONL writer used by lmms-eval plugin wrappers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _request_metadata(request: object) -> dict[str, Any]:
    args = getattr(request, "args", ())
    if not isinstance(args, tuple) or len(args) < 6:
        return {"sample_id": None, "task": "unknown", "split": None}
    return {
        "sample_id": args[3],
        "task": str(args[4]),
        "split": args[5],
    }


def _json_ready(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if hasattr(value, "item"):
        try:
            return _json_ready(value.item())
        except Exception as exc:  # noqa: BLE001 - exact error is serialized below.
            return f"unserializable_item:{type(exc).__name__}:{exc}"
    return str(value)


def record_generation_profiles(
    *,
    path: str | Path | None,
    model: str,
    policy_name: str,
    requests: list[object],
    outputs: list[str],
    total_time_s: float,
    token_counts: dict[str, Any],
) -> None:
    if path is None:
        return
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    per_sample_time = float(total_time_s) / max(1, len(requests))
    with output_path.open("a", encoding="utf-8") as handle:
        for request, output in zip(requests, outputs):
            metadata = _request_metadata(request)
            record = {
                "model": model,
                "policy_name": policy_name,
                "task": metadata["task"],
                "sample_id": metadata["sample_id"],
                "split": metadata["split"],
                "output_text": output,
                "timings_s": {"total": per_sample_time},
                "token_counts": dict(token_counts),
                "task_metrics": {"score": None},
                "notes": ["score unavailable at model wrapper stage"],
            }
            handle.write(json.dumps(_json_ready(record), sort_keys=True, allow_nan=False))
            handle.write("\n")
