#!/usr/bin/env python3
"""Compare profile JSON/JSONL files without pandas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
        return rows
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _get(record: dict[str, Any], *keys: str) -> Any:
    value: Any = record
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _num(record: dict[str, Any], *paths: tuple[str, ...]) -> float | None:
    for path in paths:
        value = _get(record, *path)
        if isinstance(value, bool) or value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _row(path: Path, record: dict[str, Any]) -> list[str]:
    return [
        str(path),
        str(record.get("run_id", "-")),
        _fmt(_get(record, "project", "track") or record.get("track")),
        _fmt(_get(record, "project", "policy_name") or record.get("policy_name")),
        _fmt(_num(record, ("timings_s", "total"), ("total_time",), ("total_time_s",))),
        _fmt(_num(record, ("token_counts", "project_a_llm_visual_tokens"), ("token_counts", "project_b_ov_direct_tokens"), ("llm_visual_tokens",))),
        _fmt(_num(record, ("compression", "project_a_vs_dense_visual_ratio"), ("compression", "project_b_vs_dense_native_ratio"), ("compression_ratio",))),
        _fmt(_num(record, ("memory_mb", "process_peak_rss"), ("peak_rss",), ("peak_rss_mb",))),
        _fmt(_num(record, ("task_metrics", "score"), ("score",))),
    ]


def print_table(rows: list[list[str]]) -> None:
    headers = ["file", "run_id", "track", "policy", "total_s", "tokens", "compression", "peak_rss", "score"]
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    print("  ".join(header.ljust(width) for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", nargs="+", type=Path, help="Profile JSON/JSONL files.")
    args = parser.parse_args()

    rows: list[list[str]] = []
    for path in args.profiles:
        for record in _records(path):
            rows.append(_row(path, record))
    if not rows:
        print("no profiles found")
        return 0
    print_table(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
