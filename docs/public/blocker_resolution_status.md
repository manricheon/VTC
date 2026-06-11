# Blocker Resolution Status

Status date: `2026-06-11T06:21:15Z`

No model weights were downloaded, no model inference was run, no heavy Python dependencies were installed, and no push was performed.

## Status Table

| Blocker | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| External GitHub source repos | resolved | `external/AutoGaze`, `external/LLaVA-OneVision-2`, and `external/lmms-eval` are present and match fetched remote branch tips. | Keep `external/` uncommitted. |
| LLaVA-OV2 HF custom code | resolved | Code/config/text snapshot exists at `external/LLaVA-OneVision-2-8B-Instruct-code`, revision `5a75eaf7d3cd73de6f85e637e45b420f46857d2e`; no payload weights found. | Use for source audit and later processor import probes. |
| OneVision-Encoder custom code | resolved for source inspection | Code/config/text snapshot exists at `external/OneVision-Encoder`, revision `9908b86a6c651379df4a0b0a7ecfccc6afcd544e`; no payload weights found. | Clone standalone GitHub source later only if the HF custom-code snapshot is insufficient. |
| AutoGaze HF repo verification | resolved | `nvidia/AutoGaze` is public, ungated, `model_type=autogaze`, and has `config.json`, `preprocessor_config.json`, and `model.safetensors`. | Use `VTC_AUTOGAZE_REPO=nvidia/AutoGaze` in the weight-download task. |
| `bfshi/AutoGaze` ambiguity | partially resolved | Source quick-start references it, but public HF metadata/listing returned model not found / 401 with no token. | Treat as stale/private/renamed unless user provides access or new evidence. |
| HF token/access | still blocked for private/gated repos | `HF_TOKEN` is not set; HF CLI login under `HF_HOME` is unauthenticated. Public metadata/code snapshots worked. No gated blocker was hit in the weight pass because downloads were skipped by policy flags before payload fetch. | User must authenticate before any private/gated repo download. Public repos may still download without auth, subject to rate limits. |
| Weight downloads | still blocked / needs manual decision | `VTC_ALLOW_WEIGHT_DOWNLOAD` was not set, so no weights were downloaded. Target checkpoint directories exist but are empty: AutoGaze `0B`, OneVision-Encoder `0B`, LLaVA-OV2 `0B`. | Set explicit allow and target flags, then rerun. Commands are recorded in `docs/public/weights_snapshot.md`. |
| Linux ffmpeg/system dependency | still blocked / needs ffmpeg install | Current host is Darwin and has no `ffmpeg` on `PATH`; `/etc/os-release` is unavailable; Linux target not yet verified. `ALLOW_SYSTEM_INSTALL` was not set, so no system install was attempted. | Install/verify `ffmpeg` on Linux before codec/backend tests. Use `bash scripts/check_system_deps.sh` to report status, or `REQUIRED_SYSTEM_DEPS=1 bash scripts/check_system_deps.sh` for a failing gate. |
| Model-env import probes | partially resolved | Best-effort `uv run --no-sync` probes ran for AutoGaze, OV-Encoder, LLaVA-OV2, `lmms-eval`, and optional MPS. JSON outputs are under `artifacts/compat/*_probe.json`; profiles are under `artifacts/profiles/compat_*.json`. Heavy deps were not synced, so model runtime imports remain unavailable. | Sync/probe each isolated env when ready, starting with `envs/ov-encoder` and `envs/llava-ov2`; keep `lmms-eval` last. |
| `flash_attn` requirements | partially resolved | bridge-core does not require it. AutoGaze declares it and `flash_attn` is absent in unsynced probe. LLaVA-OV2 and OneVision source show SDPA/eager fallback indicators, but runtime fallback is unverified. `lmms-eval` adapter defaults to `flash_attention_2`. | Confirm `sdpa`/`eager` import and runtime behavior after isolated env sync; classify mandatory FlashAttention paths as Linux/CUDA-only if fallback fails. |
| CUDA availability | still blocked / target-dependent | No CUDA checks were run; official model runs remain Linux/CUDA-oriented where FlashAttention is mandatory. | Verify on Linux CUDA machine after dependencies and weights are available. |
| MPS optional probes | partially resolved / optional | Optional MPS probe ran on Darwin, but `torch` is not installed, so MPS availability and memory metrics are unavailable. This does not affect Linux target status. | Sync optional `envs/mps-probe` with torch extras only if Mac/MPS diagnostics are needed. |
| lmms-eval benchmark | still blocked / deferred | Source adapter exists and has timing/token hooks. Import-only probe finds `lmms_eval` source importable, but adapter import is blocked by missing deps such as `loguru`; no datasets, weights, or full benchmark run. | Keep isolated in `envs/lmms-eval`; do not run full benchmark until model paths are validated. |

## Can Proceed to Weight Downloads?

Public weight download readiness:

- AutoGaze: yes, use `nvidia/AutoGaze`.
- OneVision-Encoder: yes, public HF repo is visible.
- LLaVA-OV2: yes, public HF repo is visible.

Required before actual downloads:

- User must explicitly request the weight-download task and set the allow/target flags.
- `VTC_ALLOW_WEIGHT_DOWNLOAD=1` must be set.
- Sufficient disk space must be confirmed.
- `HF_TOKEN` is optional for the currently visible public repos but may still be useful for rate limits.

Required before codec/backend inference:

- Verify/install `ffmpeg` on Linux.
- Run isolated model-env dependency/import probes.
- Resolve any `flash_attn`/attention backend failures in the relevant isolated env.

Manual `ffmpeg` install commands are documented in `docs/public/system_dependencies.md`.
