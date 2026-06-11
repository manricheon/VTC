# Quickstart

This quickstart runs the current boundary-ready bridge-core workflow. It does
not run real model inference, LLaVA-OV2 generation, OV-Encoder forward, or full
lmms-eval.

## 1. Install uv

From the VTC repository root:

```bash
bash scripts/install_uv_linux.sh
```

If `uv` is already installed, this prints the version and exits.

## 2. Set Weights And Cache Paths

```bash
source scripts/env_weights.sh
```

This sets `HF_HOME` and `HF_HUB_CACHE` under `weights/` and creates expected
checkpoint directories. It does not download weights.

## 3. Bootstrap bridge-core

```bash
bash scripts/setup_bridge_core.sh
```

This uses `uv sync` and `uv run`. It installs only bridge-core dependencies and
runs tests/compile checks. It does not install model stacks.

## 4. Check Repository Readiness

```bash
bash scripts/vtc_doctor.sh
bash scripts/pre_worktree_gate.sh
```

`READY_FOR_WORKTREE=1` means the artifact-boundary work is ready. It does not
mean model runtime is ready.

## 5. Run All Safe Examples

```bash
bash scripts/run_all_smokes.sh
```

This runs:

- Project A synthetic codec smoke
- Project A LLaVA boundary smoke
- Project B synthetic OV-direct smoke
- Project B OV boundary smoke

## 6. Summarize Profiles

```bash
bash scripts/run_profile_summaries.sh
```

## What This Validates

- Project A synthetic codec contract.
- Project A LLaVA boundary contract, if the boundary script exists.
- Project B synthetic OV-direct contract.
- Project B OV boundary contract, if the boundary script exists.
- Profile output shape, token counts, compression ratios, timings, and process memory.

## What This Does Not Validate Yet

- Real AutoGaze inference.
- Real LLaVA-OV2 generation.
- Real OV-Encoder forward.
- Full lmms-eval benchmark execution.
- CUDA or FlashAttention runtime.
