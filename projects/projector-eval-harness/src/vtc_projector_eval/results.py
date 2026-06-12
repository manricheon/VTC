"""Readers for aggregated lmms-eval result JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FOURIER_MODEL = "vtc_fourier_llava15"
DIVT_MODEL = "vtc_divt_llava15"

_IGNORED_METRIC_PREFIXES = ("paired_",)
_IGNORED_METRIC_SUFFIXES = (
    "_stderr",
    "_stderr_clt",
    "_stderr_clustered",
    "_expected_accuracy",
    "_consensus_accuracy",
    "_internal_variance",
    "_consistency_rate",
)


def find_result_files(paths: list[str | Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"result path does not exist: {path}")
        candidates = sorted(path.rglob("*_results.json")) if path.is_dir() else [path]
        for candidate in candidates:
            resolved = candidate.resolve()
            if candidate.suffix == ".json" and resolved not in seen:
                seen.add(resolved)
                files.append(candidate)
    return files


def _metric_parts(metric_key: str) -> tuple[str, str]:
    metric, _, filter_name = metric_key.partition(",")
    return metric, filter_name or "-"


def _stderr_key(metric: str, filter_name: str) -> str:
    if filter_name == "-":
        return f"{metric}_stderr"
    return f"{metric}_stderr,{filter_name}"


def _is_score_metric(metric_key: str, value: Any) -> bool:
    if not isinstance(value, (int, float)):
        return False
    metric, _ = _metric_parts(metric_key)
    if any(metric.startswith(prefix) for prefix in _IGNORED_METRIC_PREFIXES):
        return False
    return not any(metric.endswith(suffix) for suffix in _IGNORED_METRIC_SUFFIXES)


def _model_name(data: dict[str, Any], path: Path) -> str:
    config = data.get("config", {})
    if isinstance(config, dict) and config.get("model"):
        return str(config["model"])
    model_configs = data.get("model_configs", {})
    if isinstance(model_configs, dict) and model_configs.get("model"):
        return str(model_configs["model"])
    return path.parent.name


def _limit_for_task(data: dict[str, Any], task: str) -> int | float | str | None:
    config = data.get("config", {})
    if isinstance(config, dict) and "limit" in config:
        return config["limit"]
    sample_counts = data.get("n-samples", {})
    if isinstance(sample_counts, dict):
        task_counts = sample_counts.get(task, {})
        if isinstance(task_counts, dict):
            return task_counts.get("effective")
    return None


def collect_result_rows(paths: list[str | Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result_file in find_result_files(paths):
        data = json.loads(result_file.read_text(encoding="utf-8"))
        task_results = data.get("results", {})
        if not isinstance(task_results, dict):
            continue
        model = _model_name(data, result_file)
        for task, metrics in sorted(task_results.items()):
            if not isinstance(metrics, dict):
                continue
            for metric_key, score in sorted(metrics.items()):
                if not _is_score_metric(metric_key, score):
                    continue
                metric, filter_name = _metric_parts(metric_key)
                stderr = metrics.get(_stderr_key(metric, filter_name))
                rows.append(
                    {
                        "model": model,
                        "task": task,
                        "metric": metric,
                        "filter": filter_name,
                        "score": float(score),
                        "stderr": float(stderr) if isinstance(stderr, (int, float)) else None,
                        "limit": _limit_for_task(data, task),
                        "path": str(result_file),
                    }
                )
    return rows


def _metric_rank(row: dict[str, Any]) -> tuple[int, str]:
    metric = str(row["metric"])
    if metric in {"score", "acc", "accuracy", "exact_match", "f1"}:
        return (0, metric)
    if "overall" in metric or "total" in metric:
        return (1, metric)
    if metric.endswith("_score"):
        return (2, metric)
    return (3, metric)


def _primary_by_model_task(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for row in sorted(rows, key=_metric_rank):
        key = (str(row["task"]), str(row["model"]))
        selected.setdefault(key, row)
    return selected


def summarize_result_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = _primary_by_model_task(rows)
    tasks = sorted({task for task, _ in selected})
    summary: list[dict[str, Any]] = []
    for task in tasks:
        fourier = selected.get((task, FOURIER_MODEL))
        divt = selected.get((task, DIVT_MODEL))
        fourier_metric = str(fourier["metric"]) if fourier else None
        divt_metric = str(divt["metric"]) if divt else None
        metric = fourier_metric or divt_metric or "-"
        if fourier_metric and divt_metric and fourier_metric != divt_metric:
            metric = f"{fourier_metric}/{divt_metric}"

        delta = None
        if fourier and divt and fourier_metric == divt_metric:
            delta = round(float(divt["score"]) - float(fourier["score"]), 10)

        summary.append(
            {
                "task": task,
                "metric": metric,
                "fourier_score": fourier["score"] if fourier else None,
                "divt_score": divt["score"] if divt else None,
                "delta_divt_minus_fourier": delta,
                "fourier_path": fourier["path"] if fourier else None,
                "divt_path": divt["path"] if divt else None,
            }
        )
    return summary
