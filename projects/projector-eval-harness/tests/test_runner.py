from __future__ import annotations

from vtc_projector_eval.runner import build_lmms_eval_command


def test_build_lmms_eval_command_uses_plugin_and_include_path():
    command = build_lmms_eval_command(
        model="vtc_fourier_llava15",
        model_args="pretrained=/weights/llava,device_map=auto,fourier_reserve=12",
        task="mme",
        output_dir="/tmp/out",
        limit=1,
        include_path="projects/projector-eval-harness/tasks",
        nproc=1,
        port=29840,
    )

    joined = " ".join(command)
    assert command[:3] == ["uv", "run", "accelerate"]
    assert "--model" in command
    assert "vtc_fourier_llava15" in command
    assert "--include_path" in command
    assert "projects/projector-eval-harness/tasks" in command
    assert "--limit" in command
    assert "1" in command
    assert "LMMS_EVAL_PLUGINS" not in joined


def test_build_lmms_eval_command_can_omit_limit_for_full_runs():
    command = build_lmms_eval_command(
        model="vtc_divt_llava15",
        model_args="pretrained=/weights/divt,device_map=auto,divt_threshold=0.65",
        task="pope",
        output_dir="/tmp/out",
        limit=None,
        include_path="projects/projector-eval-harness/tasks",
        nproc=1,
        port=29840,
    )

    assert "--limit" not in command
    assert "None" not in command
