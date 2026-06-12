"""Profile JSONL summary helpers for projector eval runs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def _nested(record: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = record
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _numeric(record: dict[str, Any], paths: tuple[tuple[str, ...], ...]) -> float | None:
    for path in paths:
        value = _nested(record, path)
        if isinstance(value, bool) or value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _label(record: dict[str, Any], paths: tuple[tuple[str, ...], ...], default: str) -> str:
    for path in paths:
        value = _nested(record, path)
        if value:
            return str(value)
    return default


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no} is not valid JSON: {exc}") from exc
        if isinstance(value, dict):
            rows.append(value)
    return rows


def summarize_profiles(paths: list[str | Path]) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "score": [],
            "total_time": [],
            "model_time": [],
            "visual_tokens": [],
            "visual_ratio": [],
        }
    )
    for input_path in paths:
        for record in _read_jsonl(Path(input_path)):
            model = _label(record, (("model",), ("project", "model")), "unknown_model")
            task = _label(record, (("task",), ("task_name",), ("input", "task_name")), "unknown_task")
            key = f"{model}::{task}"
            group = groups[key]
            group["count"] += 1
            fields = {
                "score": (("score",), ("task_metrics", "score")),
                "total_time": (("total_time",), ("timings_s", "total")),
                "model_time": (("model_time",), ("timings_s", "model_forward")),
                "visual_tokens": (
                    ("llm_visual_tokens",),
                    ("token_counts", "llm_visual_tokens"),
                    ("token_counts", "project_a_llm_visual_tokens"),
                ),
                "visual_ratio": (
                    ("visual_ratio",),
                    ("compression", "visual_ratio"),
                    ("compression", "project_a_vs_dense_visual_ratio"),
                ),
            }
            for name, candidates in fields.items():
                value = _numeric(record, candidates)
                if value is not None:
                    group[name].append(value)

    summary: dict[str, dict[str, Any]] = {}
    for key, group in sorted(groups.items()):
        summary[key] = {
            "count": group["count"],
            "mean_score": _mean(group["score"]),
            "mean_total_time": _mean(group["total_time"]),
            "mean_model_time": _mean(group["model_time"]),
            "mean_visual_tokens": _mean(group["visual_tokens"]),
            "mean_visual_ratio": _mean(group["visual_ratio"]),
        }
    return summary


def _format(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def print_summary(summary: dict[str, dict[str, Any]]) -> None:
    if not summary:
        print("no profiles found")
        return
    headers = (
        "model_task",
        "count",
        "mean_score",
        "mean_total_time",
        "mean_model_time",
        "mean_visual_tokens",
        "mean_visual_ratio",
    )
    rows = []
    for key, values in summary.items():
        rows.append((key, *(_format(values[header]) for header in headers[1:])))
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize projector eval profile JSONL files.")
    parser.add_argument("profiles", nargs="*", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print_summary(summarize_profiles(args.profiles))


if __name__ == "__main__":
    main()
