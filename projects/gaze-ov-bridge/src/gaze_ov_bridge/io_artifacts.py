"""JSON/NPY artifact helpers for Project A."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .profile_schema import json_ready


def _write_json(data: Any, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(json_ready(data), handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def _read_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_decoded_entries(entries: Sequence[Mapping[str, Any]], path: str | Path) -> None:
    _write_json(list(entries), path)


def read_decoded_entries(path: str | Path) -> list[dict[str, Any]]:
    data = _read_json(path)
    if not isinstance(data, list):
        raise ValueError("decoded_entries artifact must contain a list")
    return [dict(item) for item in data]


def write_selected_blocks(blocks: Sequence[Sequence[int]], path: str | Path) -> None:
    _write_json([[int(frame), int(row), int(col)] for frame, row, col in blocks], path)


def read_selected_blocks(path: str | Path) -> list[tuple[int, int, int]]:
    data = _read_json(path)
    if not isinstance(data, list):
        raise ValueError("selected_blocks artifact must contain a list")
    return [(int(frame), int(row), int(col)) for frame, row, col in data]


def write_src_positions(src_positions: np.ndarray | Sequence[Sequence[int]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_path, np.asarray(src_positions, dtype=np.int64))


def read_src_positions(path: str | Path) -> np.ndarray:
    return np.load(Path(path)).astype(np.int64, copy=False)


def write_stats(stats: Mapping[str, Any], path: str | Path) -> None:
    _write_json(dict(stats), path)


def read_stats(path: str | Path) -> dict[str, Any]:
    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError("stats artifact must contain an object")
    return dict(data)
