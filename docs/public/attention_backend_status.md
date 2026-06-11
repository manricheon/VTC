# Attention Backend Status

Status date: `2026-06-11T13:12:23Z`

No model code was patched. No model inference was run. Runtime fallback is not claimed until the matching isolated environment imports successfully.

## Source Audit Summary

Command:

```bash
bash scripts/audit_external_sources.sh
```

| Path | Attention evidence | Runtime status | Classification |
| --- | --- | --- | --- |
| `bridge-core` | no `torch`, `transformers`, or `flash_attn` dependency | tested | not blocked |
| `external/AutoGaze` | `flash_attn` and `attn_implementation` mentions; source mentions `sdpa`/`eager` | no-sync probe only | fallback unknown; CUDA-only if FlashAttention proves mandatory |
| `external/OneVision-Encoder` | guarded `flash_attn` references; `patch_positions` path found; eager mentions found | no-sync probe only | SDPA/eager likely possible but unverified |
| `external/LLaVA-OneVision-2` and HF code | codec, `image_grid_thw`, `patch_positions`, `sdpa`, and `eager` mentions found | no-sync probe only | SDPA/eager likely possible but unverified |
| `external/lmms-eval` | adapter mentions `flash_attention_2`, codec backend, latency/token hooks | no-sync probe only | CUDA-oriented by default unless overridden |
| `envs/mps-probe` | optional no-sync probe ran, but torch absent | no runtime proof | optional only |

## Latest Probe Results

The no-sync probes wrote JSON under `artifacts/compat/` and profile-like JSON under `artifacts/profiles/`.

- AutoGaze: `flash_attn` not importable; source mentions fallback-related settings; runtime fallback unverified.
- OV-Encoder: `patch_positions` path found; source suggests SDPA/eager support; runtime fallback unverified.
- LLaVA-OV2: codec processing and `patch_positions` path found; source suggests SDPA/eager support; runtime fallback unverified.
- lmms-eval: LLaVA-OV2 adapter has latency/token hooks and defaults toward FlashAttention 2.
- MPS: torch absent, so MPS availability is unknown.

## Decision Rules

- `bridge-core` must stay free of `flash_attn`, torch, and transformers.
- If a model path requires `flash_attn` at import/runtime, classify it as Linux/CUDA-only.
- If `attn_implementation="sdpa"` or `"eager"` works in an isolated env, record the exact command and config before using it in worktree tasks.
- MPS results are best-effort diagnostics and do not replace Linux verification.
