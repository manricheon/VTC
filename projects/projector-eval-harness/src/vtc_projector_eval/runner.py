"""Command construction for guarded projector eval shell runners."""

from __future__ import annotations


def build_lmms_eval_command(
    *,
    model: str,
    model_args: str,
    task: str,
    output_dir: str,
    limit: int,
    include_path: str,
    nproc: int,
    port: int,
    batch_size: int = 1,
) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    return [
        "uv",
        "run",
        "accelerate",
        "launch",
        "--num_processes",
        str(nproc),
        "--main_process_port",
        str(port),
        "-m",
        "lmms_eval",
        "--model",
        model,
        "--model_args",
        model_args,
        "--tasks",
        task,
        "--batch_size",
        str(batch_size),
        "--limit",
        str(limit),
        "--include_path",
        include_path,
        "--log_samples",
        "--output_path",
        output_dir,
    ]
