#!/usr/bin/env python3
"""Print compact summaries for profile JSON/JSONL files."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Iterator[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    elif isinstance(data, dict):
        yield data


def _load_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            data = json.loads(stripped)
            if isinstance(data, dict):
                yield data


def load_profiles(paths: Iterable[str | Path]) -> Iterator[dict[str, Any]]:
    for raw_path in paths:
        path = Path(raw_path)
        if path.suffix == ".jsonl":
            yield from _load_jsonl(path)
        else:
            yield from _load_json(path)


def _get(profile: Mapping[str, Any], section: str, key: str, default: Any = None) -> Any:
    value = profile.get(section, {})
    if not isinstance(value, Mapping):
        return default
    return value.get(key, default)


def _fmt(value: Any, precision: int = 4) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{precision}f}"
    return str(value)


def _selected_tokens(profile: Mapping[str, Any]) -> Any:
    token_counts = profile.get("token_counts", {})
    if not isinstance(token_counts, Mapping):
        return "-"
    for key in (
        "project_a_llm_visual_tokens",
        "project_b_ov_direct_tokens",
        "selected_112_blocks",
    ):
        value = token_counts.get(key)
        if value not in (None, 0):
            return value
    return token_counts.get("selected_112_blocks", "-")


def _row(profile: Mapping[str, Any]) -> list[str]:
    return [
        str(profile.get("run_id", "-")),
        _fmt(_get(profile, "project", "track")),
        _fmt(_get(profile, "project", "policy_name")),
        _fmt(_get(profile, "timings_s", "total")),
        _fmt(_selected_tokens(profile)),
        _fmt(_get(profile, "compression", "project_a_vs_dense_raw_ratio")),
        _fmt(_get(profile, "compression", "project_a_vs_dense_visual_ratio")),
        _fmt(_get(profile, "compression", "project_b_vs_autogaze_candidates_ratio")),
        _fmt(_get(profile, "compression", "project_b_vs_dense_native_ratio")),
        _fmt(_get(profile, "memory_mb", "process_peak_rss"), precision=1),
        _fmt(_get(profile, "task_metrics", "score")),
    ]


def print_table(profiles: Iterable[Mapping[str, Any]]) -> None:
    headers = [
        "run_id",
        "track",
        "policy",
        "total_s",
        "selected",
        "a_raw",
        "a_visual",
        "b_candidates",
        "b_dense",
        "peak_rss",
        "score",
    ]
    rows = [_row(profile) for profile in profiles]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows)) if rows else len(header)
        for index, header in enumerate(headers)
    ]

    def format_row(row: list[str]) -> str:
        return "  ".join(value.ljust(widths[index]) for index, value in enumerate(row))

    print(format_row(headers))
    print(format_row(["-" * width for width in widths]))
    for row in rows:
        print(format_row(row))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", nargs="+", help="Profile JSON or JSONL files.")
    args = parser.parse_args()

    print_table(load_profiles(args.profiles))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
