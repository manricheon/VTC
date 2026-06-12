# CUDA/Linux Machine Setup

This guide is for a fresh CUDA/Linux checkout where `external/`, `weights/`,
`artifacts/`, and project `out/` directories are empty or missing. That is
expected: those paths are ignored by Git and are not pushed to GitHub.

Use this guide before real AutoGaze inference, real LLaVA-OV2 generation, real
OV-Encoder forward, or `lmms-eval`.

## 0. Clone The Working Branch

```bash
git clone --branch feature/gaze-ov-bridge-local git@github.com:manricheon/VTC.git VTC
cd VTC
git status --short
```

Expected:

- branch is `feature/gaze-ov-bridge-local`
- working tree is clean

## 1. Read Order

Read these first:

1. `README.md`
2. `docs/public/cuda_machine_setup.md`
3. `docs/public/quickstart.md`
4. `docs/public/external_repo_plan.md`
5. `docs/public/hf_downloads.md`
6. `docs/public/architecture.md`
7. `docs/public/benchmarking.md`
8. `docs/public/troubleshooting.md`

The current bridge is boundary-ready. Runtime readiness still requires Linux
system checks, external source setup, weights, model env sync, CUDA attention
backend checks, and import/runtime probes.

## 2. System And Bridge-Core Gate

```bash
bash scripts/install_uv_linux.sh
source scripts/env_weights.sh
bash scripts/check_system_deps.sh
bash scripts/setup_bridge_core.sh
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
```

If `ffmpeg` is missing, install it before codec or benchmark work:

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

Fedora/RHEL:

```bash
sudo dnf install -y ffmpeg
```

## 3. Set Up External Source Trees

`external/` is source-only. Do not put model weights here.

```bash
mkdir -p external
```

Clone GitHub source repos:

```bash
git clone https://github.com/NVlabs/AutoGaze.git external/AutoGaze
git clone https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2.git external/LLaVA-OneVision-2
git clone --branch llava-onevision2 https://github.com/EvolvingLMMs-Lab/lmms-eval.git external/lmms-eval
```

Download the LLaVA-OV2 custom-code snapshot only. This excludes model payload
files:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv sync
cd ../..
bash scripts/hf_download_code_only.sh
```

Download the OneVision-Encoder code/config snapshot only:

```bash
source scripts/env_weights.sh
VTC_ROOT="$(pwd)"
cd envs/hf-tools
uv sync
uv run python ../../scripts/hf_download_snapshot.py \
  --repo-id "lmms-lab-encoder/onevision-encoder-large" \
  --repo-type model \
  --local-dir "${VTC_ROOT}/external/OneVision-Encoder" \
  --cache-dir "${HF_HUB_CACHE}" \
  --allow-pattern "*.py" \
  --allow-pattern "*.json" \
  --allow-pattern "*.md" \
  --allow-pattern "*.txt" \
  --allow-pattern "configuration*" \
  --allow-pattern "modeling*" \
  --allow-pattern "processing*" \
  --allow-pattern "tokenization*" \
  --ignore-pattern "*.safetensors" \
  --ignore-pattern "*.bin" \
  --ignore-pattern "*.pt" \
  --ignore-pattern "*.pth" \
  --ignore-pattern "*.gguf" \
  --ignore-pattern "*.onnx"
cd ../..
```

Audit external source status:

```bash
bash scripts/audit_external_sources.sh
```

Expected paths:

- `external/AutoGaze`
- `external/LLaVA-OneVision-2`
- `external/lmms-eval`
- `external/LLaVA-OneVision-2-8B-Instruct-code`
- `external/OneVision-Encoder`

## 4. Set Up Hugging Face Cache And Weights

All HF cache and checkpoint files must stay under `weights/`.

```bash
source scripts/env_weights.sh
bash scripts/check_hf_assets.sh
```

If auth is needed, do not write tokens to files. Use one of:

```bash
export HF_TOKEN=<token value from Hugging Face settings>
```

or:

```bash
source scripts/env_weights.sh
cd envs/hf-tools
uv run hf auth login
cd ../..
```

Download selected weights explicitly:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
bash scripts/setup_hf_assets.sh
```

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_OV_ENCODER=1 \
bash scripts/setup_hf_assets.sh
```

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_LLAVA_OV2=1 \
VTC_ALLOW_LLAVA_OV2_DOWNLOAD=1 \
bash scripts/setup_hf_assets.sh
```

Check again:

```bash
bash scripts/check_hf_assets.sh
```

Expected checkpoint paths:

- `weights/checkpoints/AutoGaze`
- `weights/checkpoints/onevision-encoder-large`
- `weights/checkpoints/LLaVA-OneVision-2-8B-Instruct`

## 5. Re-run Boundary And Readiness Checks

```bash
bash scripts/vtc_doctor.sh
bash scripts/run_all_smokes.sh
bash scripts/run_profile_summaries.sh
bash scripts/check_benchmark_readiness.sh
```

At this stage `READY_FOR_BENCHMARK=1` means the repository has the required
source/weight paths and boundary artifacts for the guarded benchmark skeleton.
It still does not mean real generation has been validated.

## 6. Sync And Probe Model Environments

Run model env sync only when ready for heavy dependencies:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
bash scripts/run_compat_probes.sh
```

Check CUDA in the relevant envs. Example for LLaVA-OV2:

```bash
cd envs/llava-ov2
uv run python - <<'PY'
import torch
print("torch", torch.__version__)
print("cuda", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0))
PY
cd ../..
```

Repeat the same kind of import/CUDA check for `envs/autogaze` and
`envs/ov-encoder` after those envs sync.

## 7. Runtime Gate Order

Do not jump to full benchmark. Use this order:

1. bridge-core tests and smokes
2. external source audit
3. weight presence checks
4. model env sync/import probes
5. CUDA and attention backend check
6. Project A real LLaVA-OV2 generation smoke
7. Project B real OV-Encoder forward smoke
8. `lmms-eval --limit 1`
9. small benchmark subset
10. full benchmark

The first guarded lmms-eval command is dry-run by default:

```bash
bash scripts/run_lmms_eval_autogaze_limit1.sh
```

Only after runtime blockers are resolved:

```bash
RUN_LMMS_EVAL=1 TASK=JumpScore TC=128 TS=2 bash scripts/run_lmms_eval_autogaze_limit1.sh
```

## 8. If Something Is Missing

Use these diagnostics:

```bash
bash scripts/vtc_doctor.sh
bash scripts/check_system_deps.sh
bash scripts/audit_external_sources.sh
bash scripts/check_hf_assets.sh
bash scripts/check_benchmark_readiness.sh
```

Common meanings:

- `external/* missing`: follow section 3.
- `weights/checkpoints/* empty`: follow section 4.
- `ffmpeg missing`: install system `ffmpeg`.
- `READY_FOR_BENCHMARK=0`: inspect missing source/weight/boundary paths.
- `flash_attn missing`: not a bridge-core issue; verify in model env on CUDA.
- `torch.cuda.is_available() == False`: CUDA runtime or PyTorch install is not ready.

## 9. Do Not Commit Runtime Payloads

Do not commit these paths:

- `external/`
- `weights/`
- `artifacts/`
- `projects/gaze-ov-bridge/out/`
- `envs/*/.venv/`

Only commit source, tests, scripts, and public docs unless a task explicitly
asks for local guidance files.
