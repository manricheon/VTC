#!/usr/bin/env python
"""Summarize lmms-eval per-sample profile JSONL files without pandas."""

from __future__ import annotations

import argparse
import glob
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


def _backend(record: dict[str, Any]) -> str:
    for path in (("backend",), ("policy_name",), ("project", "policy_name")):
        value = _nested(record, path)
        if value:
            return str(value)
    return "unknown"


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _format(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.4f}"


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


def _default_paths() -> list[Path]:
    return [Path(path) for path in sorted(glob.glob("artifacts/profiles/lmms_eval_*.jsonl"))]


def summarize_profiles(paths: list[Path]) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "total_time": [],
            "model_time": [],
            "visual_tokens": [],
            "compression_ratio": [],
            "score": [],
        }
    )

    for path in paths:
        for record in _read_jsonl(path):
            backend = _backend(record)
            group = groups[backend]
            group["count"] += 1
            fields = {
                "total_time": (
                    ("total_time",),
                    ("total_time_s",),
                    ("timings_s", "total"),
                ),
                "model_time": (
                    ("model_time",),
                    ("model_time_s",),
                    ("timings_s", "model_forward"),
                ),
                "visual_tokens": (
                    ("llm_visual_tokens",),
                    ("project_a_llm_visual_tokens",),
                    ("token_counts", "project_a_llm_visual_tokens"),
                ),
                "compression_ratio": (
                    ("project_a_vs_dense_visual_ratio",),
                    ("compression_ratio",),
                    ("compression", "project_a_vs_dense_visual_ratio"),
                ),
                "score": (
                    ("score",),
                    ("task_metrics", "score"),
                ),
            }
            for name, candidates in fields.items():
                value = _numeric(record, candidates)
                if value is not None:
                    group[name].append(value)

    summary: dict[str, dict[str, Any]] = {}
    for backend, group in sorted(groups.items()):
        summary[backend] = {
            "count": group["count"],
            "mean_total_time": _mean(group["total_time"]),
            "mean_model_time": _mean(group["model_time"]),
            "mean_visual_tokens": _mean(group["visual_tokens"]),
            "mean_compression_ratio": _mean(group["compression_ratio"]),
            "mean_score": _mean(group["score"]),
        }
    return summary


def print_summary(summary: dict[str, dict[str, Any]]) -> None:
    if not summary:
        print("no profiles found")
        return

    headers = (
        "backend",
        "count",
        "mean_total_time",
        "mean_model_time",
        "mean_visual_tokens",
        "mean_compression_ratio",
        "mean_score",
    )
    rows = []
    for backend, values in summary.items():
        rows.append(
            (
                backend,
                str(values["count"]),
                _format(values["mean_total_time"]),
                _format(values["mean_model_time"]),
                _format(values["mean_visual_tokens"]),
                _format(values["mean_compression_ratio"]),
                _format(values["mean_score"]),
            )
        )
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]

    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize lmms-eval profile JSONL files.")
    parser.add_argument(
        "profiles",
        nargs="*",
        type=Path,
        help="Profile JSONL paths. Defaults to artifacts/profiles/lmms_eval_*.jsonl.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = args.profiles or _default_paths()
    existing = [path for path in paths if path.exists()]
    if not existing:
        print("no profiles found")
        return
    print_summary(summarize_profiles(existing))


if __name__ == "__main__":
    main()
