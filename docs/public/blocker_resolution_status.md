# Blocker Resolution Status

Status date: `2026-06-11T06:10:32Z`

No model weights were downloaded, no model inference was run, no heavy Python dependencies were installed, and no push was performed.

## Status Table

| Blocker | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| External GitHub source repos | resolved | `external/AutoGaze`, `external/LLaVA-OneVision-2`, and `external/lmms-eval` are present and match fetched remote branch tips. | Keep `external/` uncommitted. |
| LLaVA-OV2 HF custom code | resolved | Code/config/text snapshot exists at `external/LLaVA-OneVision-2-8B-Instruct-code`, revision `5a75eaf7d3cd73de6f85e637e45b420f46857d2e`; no payload weights found. | Use for source audit and later processor import probes. |
| OneVision-Encoder custom code | resolved for source inspection | Code/config/text snapshot exists at `external/OneVision-Encoder`, revision `9908b86a6c651379df4a0b0a7ecfccc6afcd544e`; no payload weights found. | Clone standalone GitHub source later only if the HF custom-code snapshot is insufficient. |
| AutoGaze HF repo verification | resolved | `nvidia/AutoGaze` is public, ungated, `model_type=autogaze`, and has `config.json`, `preprocessor_config.json`, and `model.safetensors`. | Use `VTC_AUTOGAZE_REPO=nvidia/AutoGaze` in the weight-download task. |
| `bfshi/AutoGaze` ambiguity | partially resolved | Source quick-start references it, but public HF metadata/listing returned model not found / 401 with no token. | Treat as stale/private/renamed unless user provides access or new evidence. |
| HF token/access | still blocked for private/gated repos | `HF_TOKEN` is not set; HF CLI login under `HF_HOME` is unauthenticated. Public metadata/code snapshots worked. | User must authenticate before any private/gated repo download. |
| Weight downloads | intentionally deferred | No `.safetensors`, `.bin`, `.pt`, `.pth`, `.gguf`, or `.onnx` files found under `weights/` or `external/`. | Run explicit weight-download task with `VTC_ALLOW_WEIGHT_DOWNLOAD=1`. |
| Linux ffmpeg/system dependency | still blocked / needs ffmpeg install | Current host is Darwin and has no `ffmpeg` on `PATH`; `/etc/os-release` is unavailable; Linux target not yet verified. `ALLOW_SYSTEM_INSTALL` was not set, so no system install was attempted. | Install/verify `ffmpeg` on Linux before codec/backend tests. Use `bash scripts/check_system_deps.sh` to report status, or `REQUIRED_SYSTEM_DEPS=1 bash scripts/check_system_deps.sh` for a failing gate. |
| Model-env import probes | still blocked / pending | Source-only audits completed, but no `uv sync` or import probe was run for heavy model envs in this task. | Run isolated probes for `envs/autogaze`, `envs/ov-encoder`, `envs/llava-ov2`, `envs/lmms-eval`, and optional `envs/mps-probe`. |
| `flash_attn` requirements | partially resolved | bridge-core does not require it. AutoGaze declares it. LLaVA-OV2 and OneVision source show fallback-capable code paths, but defaults/examples are FlashAttention-oriented. | Confirm `sdpa`/`eager` import behavior in isolated model env probes. |
| CUDA availability | still blocked / target-dependent | No CUDA checks were run; official model runs remain Linux/CUDA-oriented where FlashAttention is mandatory. | Verify on Linux CUDA machine after dependencies and weights are available. |
| MPS optional probes | still blocked / optional | No MPS model-env probes were run. | Run only as best-effort after dependencies allow it; do not treat as official support. |
| lmms-eval benchmark | still blocked / deferred | Source adapter exists and has timing/token hooks, but environment, datasets, weights, and runner probes remain deferred. | Keep isolated in `envs/lmms-eval`; do not run full benchmark until model paths are validated. |

## Can Proceed to Weight Downloads?

Public weight download readiness:

- AutoGaze: yes, use `nvidia/AutoGaze`.
- OneVision-Encoder: yes, public HF repo is visible.
- LLaVA-OV2: yes, public HF repo is visible.

Required before actual downloads:

- User must explicitly request the weight-download task.
- `VTC_ALLOW_WEIGHT_DOWNLOAD=1` must be set.
- Sufficient disk space must be confirmed.
- `HF_TOKEN` is optional for the currently visible public repos but may still be useful for rate limits.

Required before codec/backend inference:

- Verify/install `ffmpeg` on Linux.
- Run isolated model-env dependency/import probes.
- Resolve any `flash_attn`/attention backend failures in the relevant isolated env.

Manual `ffmpeg` install commands are documented in `docs/public/system_dependencies.md`.
