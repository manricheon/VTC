from __future__ import annotations

import json
from pathlib import Path

from vtc_projector_eval.results import collect_result_rows, summarize_result_rows


def _write_lmms_result(
    path: Path,
    *,
    model: str,
    task: str,
    metric: str,
    score: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "config": {
                    "model": model,
                    "model_args": "pretrained=/weights/example",
                    "limit": 1,
                },
                "results": {
                    task: {
                        "alias": task.upper(),
                        metric: score,
                        metric.replace(",", "_stderr,"): 0.01,
                        "paired_baseline": "ignored",
                    }
                },
                "n-samples": {task: {"original": 10, "effective": 1}},
            }
        ),
        encoding="utf-8",
    )


def test_collect_result_rows_reads_lmms_eval_result_files_under_directories(tmp_path: Path):
    output_dir = tmp_path / "projector_eval_smoke_mme_fourier_mme"
    result_path = output_dir / "vtc_fourier_llava15" / "2026-06-12T10-00-00_results.json"
    _write_lmms_result(
        result_path,
        model="vtc_fourier_llava15",
        task="mme",
        metric="acc,none",
        score=0.75,
    )
    (output_dir / "vtc_fourier_llava15" / "2026_samples_mme.jsonl").write_text(
        "{}\n",
        encoding="utf-8",
    )

    rows = collect_result_rows([output_dir])

    assert rows == [
        {
            "model": "vtc_fourier_llava15",
            "task": "mme",
            "metric": "acc",
            "filter": "none",
            "score": 0.75,
            "stderr": 0.01,
            "limit": 1,
            "path": str(result_path),
        }
    ]


def test_summarize_result_rows_pivots_scores_by_task_and_model(tmp_path: Path):
    fourier_path = tmp_path / "fourier" / "vtc_fourier_llava15" / "run_results.json"
    divt_path = tmp_path / "divt" / "vtc_divt_llava15" / "run_results.json"
    _write_lmms_result(
        fourier_path,
        model="vtc_fourier_llava15",
        task="mme",
        metric="acc,none",
        score=0.70,
    )
    _write_lmms_result(
        divt_path,
        model="vtc_divt_llava15",
        task="mme",
        metric="acc,none",
        score=0.80,
    )

    summary = summarize_result_rows(collect_result_rows([tmp_path]))

    assert summary == [
        {
            "task": "mme",
            "metric": "acc",
            "fourier_score": 0.70,
            "divt_score": 0.80,
            "delta_divt_minus_fourier": 0.10,
            "fourier_path": str(fourier_path),
            "divt_path": str(divt_path),
        }
    ]
