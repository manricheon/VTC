"""Markdown report generation for projector eval benchmark runs."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .matrix import DEFAULT_PRESETS, build_matrix, parse_limit
from .profiles import summarize_profiles
from .results import collect_result_rows, summarize_result_rows
from .sources import audit_sources


DEFAULT_FOURIER_CKPT = Path("weights/checkpoints/llava-v1.5-7b")
DEFAULT_DIVT_CKPT = Path("weights/checkpoints/llava-v1.5-divt-0.65-7b")


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _status(ok: bool) -> str:
    return "ok" if ok else "blocked"


def _format(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def checkpoint_blockers(
    repo_root: str | Path,
    *,
    fourier_ckpt: str | Path = DEFAULT_FOURIER_CKPT,
    divt_ckpt: str | Path = DEFAULT_DIVT_CKPT,
) -> list[str]:
    root = Path(repo_root)
    blockers: list[str] = []
    checks = (
        ("Fourier/LLaVA-1.5", Path(fourier_ckpt)),
        ("DiVT", Path(divt_ckpt)),
    )
    for label, relative_path in checks:
        path = relative_path if relative_path.is_absolute() else root / relative_path
        if not path.exists():
            blockers.append(f"missing checkpoint for {label}: {relative_path}")
    return blockers


def _source_table(source_records: dict[str, dict[str, Any]]) -> list[str]:
    lines = [
        "| Source | Status | Branch | Commit | Required files | Terms |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in source_records.values():
        terms_ok = all(bool(value) for value in record["terms"].values())
        commit = str(record.get("commit_actual") or "-")[:12]
        lines.append(
            "| {name} | {status} | {branch} | `{commit}` | {files} | {terms} |".format(
                name=record["name"],
                status=_status(
                    record["status"] == "present"
                    and record["required_files_present"]
                    and record["commit_matches_expected"]
                ),
                branch=record.get("branch_actual") or "-",
                commit=commit,
                files=_status(bool(record["required_files_present"])),
                terms=_status(terms_ok),
            )
        )
    return lines


def _matrix_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Model | Task | Limit | Model args |",
        "| --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{model}` | `{task}` | {limit} | `{model_args}` |".format(
                model=row["model"],
                task=row["task"],
                limit="none" if row["limit"] is None else row["limit"],
                model_args=row["model_args"],
            )
        )
    return lines


def _profile_table(summary: dict[str, dict[str, Any]]) -> list[str]:
    if not summary:
        return ["No profile rows were found."]
    lines = [
        "| Model task | Count | Mean score | Mean total time | Mean model time | Mean visual tokens | Mean visual ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, values in summary.items():
        lines.append(
            "| `{key}` | {count} | {score} | {total} | {model} | {tokens} | {ratio} |".format(
                key=key,
                count=values["count"],
                score=_format(values["mean_score"]),
                total=_format(values["mean_total_time"]),
                model=_format(values["mean_model_time"]),
                tokens=_format(values["mean_visual_tokens"]),
                ratio=_format(values["mean_visual_ratio"]),
            )
        )
    return lines


def _result_table(summary: list[dict[str, Any]]) -> list[str]:
    if not summary:
        return ["No lmms-eval result rows were found."]
    lines = [
        "| Task | Metric | Fourier score | DiVT score | DiVT - Fourier |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in summary:
        lines.append(
            "| `{task}` | `{metric}` | {fourier} | {divt} | {delta} |".format(
                task=row["task"],
                metric=row["metric"],
                fourier=_format(row["fourier_score"]),
                divt=_format(row["divt_score"]),
                delta=_format(row["delta_divt_minus_fourier"]),
            )
        )
    return lines


def _result_file_list(summary: list[dict[str, Any]]) -> list[str]:
    paths = sorted(
        {
            str(path)
            for row in summary
            for path in (row["fourier_path"], row["divt_path"])
            if path
        }
    )
    if not paths:
        return ["No result files were found."]
    return [f"- {path}" for path in paths]


def build_report(
    *,
    repo_root: str | Path,
    profiles: list[str | Path],
    result_paths: list[str | Path] | None = None,
    run_id: str,
    preset: str = "smoke",
    tasks: str | None = None,
    limit: int | None = 1,
    fourier_ckpt: str | Path = DEFAULT_FOURIER_CKPT,
    divt_ckpt: str | Path = DEFAULT_DIVT_CKPT,
    created_at_utc: str | None = None,
) -> str:
    source_records = audit_sources(repo_root)
    blockers = checkpoint_blockers(
        repo_root,
        fourier_ckpt=fourier_ckpt,
        divt_ckpt=divt_ckpt,
    )
    rows = build_matrix(preset=preset, projector_model="all", tasks=tasks, limit=limit)
    profile_summary = summarize_profiles(profiles)
    result_rows = collect_result_rows(result_paths or [])
    result_summary = summarize_result_rows(result_rows)
    task_label = tasks or ",".join(DEFAULT_PRESETS[preset])
    limit_label = "none" if limit is None else str(limit)

    lines = [
        "# Projector Eval Benchmark Report",
        "",
        f"- run_id: `{run_id}`",
        f"- created_at_utc: `{created_at_utc or _utc_now()}`",
        f"- preset: `{preset}`",
        f"- tasks: `{task_label}`",
        f"- limit: `{limit_label}`",
        f"- profiles: `{', '.join(str(path) for path in profiles) if profiles else '-'}`",
        f"- results: `{', '.join(str(path) for path in result_paths or []) if result_paths else '-'}`",
        "",
        "## Status",
        "",
    ]
    if blockers:
        lines.append("Benchmark execution is blocked for real runs.")
        lines.append("")
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append(
            "Checkpoint paths are present. Dataset/env readiness must still be "
            "verified on the target machine."
        )

    lines.extend(
        [
            "",
            "## Source Snapshots",
            "",
            *_source_table(source_records),
            "",
            "## Benchmark Matrix",
            "",
            *_matrix_table(rows),
            "",
            "## Result Summary",
            "",
            *_result_table(result_summary),
            "",
            "## Runtime Profile Summary",
            "",
            *_profile_table(profile_summary),
            "",
            "## Result Files",
            "",
            *_result_file_list(result_summary),
            "",
            "## Run Commands",
            "",
            "Dry-run:",
            "",
            "```bash",
            "bash scripts/run_projector_eval_limit1.sh",
            "```",
            "",
            "Execution after blockers are cleared:",
            "",
            "```bash",
            f"RUN_PROJECTOR_EVAL=1 PROJECTOR_MODEL=all TASK=mme LIMIT={limit_label} \\",
            "  bash scripts/run_projector_eval_limit1.sh",
            "```",
            "",
            "Summarize profiles:",
            "",
            "```bash",
            "bash scripts/summarize_projector_eval_profiles.sh \\",
            "  artifacts/profiles/projector_eval_<run_id>.jsonl",
            "```",
            "",
            "Write report:",
            "",
            "```bash",
            "bash scripts/write_projector_eval_report.sh \\",
            f"  --run-id {run_id} \\",
            f"  --preset {preset} \\",
            f"  --limit {limit_label} \\",
            "  --result artifacts/profiles/projector_eval_<run_id>_<projector>_<task> \\",
            "  --output-md docs/public/projector_eval_current_report.md \\",
            "  artifacts/profiles/projector_eval_<run_id>.jsonl",
            "```",
            "",
            "## Notes",
            "",
            "- Upstream source trees under `external/` are not modified or committed.",
            "- `weights/` and `artifacts/` remain local/generated storage.",
            "- Score fields are unavailable until real `lmms-eval` task result records exist.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(markdown: str, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write a projector eval benchmark report.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--run-id", default="current")
    parser.add_argument("--preset", default="smoke", choices=sorted(DEFAULT_PRESETS))
    parser.add_argument("--tasks", default=None)
    parser.add_argument("--limit", type=parse_limit, default=1)
    parser.add_argument("--result", dest="result_paths", action="append", default=[], type=Path)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--fourier-ckpt", default=str(DEFAULT_FOURIER_CKPT))
    parser.add_argument("--divt-ckpt", default=str(DEFAULT_DIVT_CKPT))
    parser.add_argument("profiles", nargs="*", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(
        repo_root=args.repo_root,
        profiles=args.profiles,
        result_paths=args.result_paths,
        run_id=args.run_id,
        preset=args.preset,
        tasks=args.tasks,
        limit=args.limit,
        fourier_ckpt=args.fourier_ckpt,
        divt_ckpt=args.divt_ckpt,
    )
    if args.output_md:
        write_report(report, args.output_md)
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
