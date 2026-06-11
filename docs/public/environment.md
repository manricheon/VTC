# Bridge-Core Environment

VTC is Linux-first and uv-managed. The initial `bridge-core` environment supports pure Python bridge development, synthetic tests, and profiling schema work without installing model stacks.

## Official Target

Linux is the official development and compatibility target. Use `uv sync` and `uv run` for environment management. Do not use `python -m venv` or `pip install -e .` for bridge-core setup.

## Mac/MPS

MacBook/MPS may run bridge-core only as a best-effort lightweight probe:

```bash
ALLOW_NON_LINUX=1 bash scripts/bootstrap_bridge_core.sh
```

MPS results are not official compatibility results.

## Install uv

From the VTC repository root:

```bash
bash scripts/install_uv_linux.sh
```

If `uv` is already available, the script prints the installed version and exits. It does not install project dependencies or model dependencies.

## Set Weights and Cache Paths

Source the weights environment helper before any future Hugging Face operation:

```bash
source scripts/env_weights.sh
```

This sets:

- `VTC_ROOT=<repo root>`
- `HF_HOME=<VTC_ROOT>/weights/hf_home`
- `HF_HUB_CACHE=<VTC_ROOT>/weights/hf_home/hub`

It also creates checkpoint directories under `weights/checkpoints/` without downloading weights.

## Bootstrap bridge-core

From the VTC repository root:

```bash
bash scripts/bootstrap_bridge_core.sh
```

On non-Linux systems:

```bash
ALLOW_NON_LINUX=1 bash scripts/bootstrap_bridge_core.sh
```

The bootstrap script runs:

```bash
cd envs/bridge-core
uv sync --group dev
uv run python -m compileall ../../projects/gaze-ov-bridge/src
uv run pytest -q ../../projects/gaze-ov-bridge/tests
```

It does not call `pip`, manually create a virtualenv, install `torch`, install `transformers`, clone repositories, download weights, or run model inference.

## Check Environment

From the VTC repository root:

```bash
cd envs/bridge-core
uv run python ../../scripts/check_linux_env.py
cd ../..
```

The check reports Python, platform, machine, root paths, cache environment variables, `uv`, `git`, `ffmpeg`, required Level 1 imports, and optional model/video imports.

## Level 1 Supports

- Project A pure Python selector tests.
- Project A synthetic codec `src_positions` smoke tests.
- Project B pure Python OV-direct geometry tests.
- Project B synthetic patch extraction smoke tests.
- Profiling schema and synthetic profiling.

## Level 1 Does Not Support

- Real AutoGaze inference.
- Real OV-Encoder forward.
- Real LLaVA-OV2 generation.
- Full `lmms-eval` benchmark runs.
- Model weight downloads.

## Later Levels

Later integration levels may add:

- External source clone steps.
- Compatibility probes under `artifacts/compat/`.
- Model-specific environments.
- CUDA benchmark runs on Linux.

Each later level should remain isolated in its matching `envs/*` environment and should exchange JSON/NPY artifacts instead of importing model packages across environments.

## Weights Policy

All Hugging Face caches and checkpoints must live under `weights/`.

Use:

```bash
source scripts/env_weights.sh
```

before any later download-enabled workflow so `HF_HOME` and `HF_HUB_CACHE` point inside the repository workspace. The helper creates directories only; it does not download weights.
