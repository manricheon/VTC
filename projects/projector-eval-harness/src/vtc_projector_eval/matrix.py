"""Benchmark matrix construction for projector eval guarded runners."""

from __future__ import annotations

import argparse
import json
from typing import Any


DEFAULT_PRESETS: dict[str, list[str]] = {
    "smoke": [
        "mme",
        "pope",
        "textvqa_val_lite",
        "vqav2_val_lite",
        "scienceqa_img",
        "mmbench_en_dev_lite",
        "gqa_lite",
    ],
    "full": [
        "mme",
        "pope",
        "textvqa_val",
        "vqav2_val",
        "scienceqa_img",
        "mmbench_en_dev",
        "gqa",
        "mmvet",
    ],
}

MODEL_ALIASES = {
    "fourier": "vtc_fourier_llava15",
    "divt": "vtc_divt_llava15",
}


def _split_tasks(tasks: str | None, preset: str) -> list[str]:
    if tasks:
        parsed = [task.strip() for task in tasks.split(",") if task.strip()]
        if not parsed:
            raise ValueError("tasks override must contain at least one task")
        return parsed
    if preset not in DEFAULT_PRESETS:
        raise ValueError(f"preset must be one of: {', '.join(sorted(DEFAULT_PRESETS))}")
    return list(DEFAULT_PRESETS[preset])


def _selected_models(projector_model: str) -> list[str]:
    if projector_model == "all":
        return [MODEL_ALIASES["fourier"], MODEL_ALIASES["divt"]]
    if projector_model not in MODEL_ALIASES:
        raise ValueError("projector_model must be one of: all, fourier, divt")
    return [MODEL_ALIASES[projector_model]]


def _model_args(model: str, fourier_reserve: int, divt_threshold: float) -> str:
    if model == "vtc_fourier_llava15":
        return (
            "pretrained=${FOURIER_CKPT},device_map=auto,use_flash_attention_2=False,"
            f"fourier_reserve={fourier_reserve}"
        )
    if model == "vtc_divt_llava15":
        return (
            "pretrained=${DIVT_CKPT},device_map=auto,use_flash_attention_2=False,"
            f"divt_threshold={divt_threshold}"
        )
    raise ValueError(f"unknown model: {model}")


def parse_limit(value: str) -> int | None:
    if value in {"none", "all", "full"}:
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "limit must be a positive integer, none, all, or full"
        ) from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            "limit must be a positive integer, none, all, or full"
        )
    return parsed


def build_matrix(
    *,
    preset: str,
    projector_model: str = "all",
    tasks: str | None = None,
    limit: int | None = 1,
    fourier_reserve: int = 12,
    divt_threshold: float = 0.65,
) -> list[dict[str, Any]]:
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive")
    rows: list[dict[str, Any]] = []
    for model in _selected_models(projector_model):
        for task in _split_tasks(tasks, preset):
            rows.append(
                {
                    "model": model,
                    "task": task,
                    "limit": int(limit) if limit is not None else None,
                    "model_args": _model_args(model, fourier_reserve, divt_threshold),
                }
            )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build projector eval benchmark matrix.")
    parser.add_argument("--preset", default="smoke", choices=sorted(DEFAULT_PRESETS))
    parser.add_argument("--projector-model", default="all", choices=("all", "fourier", "divt"))
    parser.add_argument("--tasks", default=None)
    parser.add_argument("--limit", type=parse_limit, default=1)
    parser.add_argument("--fourier-reserve", type=int, default=12)
    parser.add_argument("--divt-threshold", type=float, default=0.65)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_matrix(
        preset=args.preset,
        projector_model=args.projector_model,
        tasks=args.tasks,
        limit=args.limit,
        fourier_reserve=args.fourier_reserve,
        divt_threshold=args.divt_threshold,
    )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
