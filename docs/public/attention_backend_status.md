# Attention Backend Status

Status date: `2026-06-11T07:28:02Z`

This source audit searched external source code for:

```text
flash_attn
flash_attention
flash_attention_2
attn_implementation
sdpa
eager
```

No model code was patched. No model inference was run. Runtime fallback is not claimed until an import/probe verifies it in the matching isolated environment.

## Summary

| Path | Source status | Runtime status | Current classification |
| --- | --- | --- | --- |
| bridge-core | no `torch`, `transformers`, or `flash_attn` dependency | verified by tests | pure Python, not blocked |
| AutoGaze | declares `flash_attn`; source has `sdpa`/`eager` settings and `use_flash_attn` config | not synced/probed | fallback unknown; Linux/CUDA if FlashAttention proves mandatory |
| OneVision-Encoder | guarded `flash_attn` import; eager class exists; default appears FlashAttention-oriented | not synced/probed | eager fallback appears possible but unverified |
| LLaVA-OV2 | declares `_supports_flash_attn` and `_supports_sdpa`; eager attention path exists | not synced/probed | SDPA/eager appears possible but unverified |
| lmms-eval LLaVA-OV2 adapter | defaults `attn_implementation="flash_attention_2"` | not synced/probed | CUDA-oriented by default unless overridden |
| MPS | source fallback may make import probes possible | not synced/probed with torch | optional only, not official |

## Source Findings

AutoGaze:

- `external/AutoGaze/pyproject.toml` declares `flash_attn`.
- `external/AutoGaze/autogaze/models/autogaze/configuration_autogaze.py` sets `attn_mode` to `"flash_attention_2"` when `use_flash_attn=True`, otherwise `"sdpa"`.
- `external/AutoGaze/autogaze/configs/model/autogaze.yaml` currently contains `use_flash_attn: False`.
- QUICK_START examples use `attn_implementation="sdpa"` for SigLIP paths.
- Conclusion: source suggests non-FlashAttention paths may exist, but AutoGaze runtime is not verified.

OneVision-Encoder:

- `external/OneVision-Encoder/modeling_onevision_encoder.py` imports `flash_attn` inside `try/except`.
- It defines attention classes for `"eager"` and `"flash_attention_2"`.
- If the configured implementation is unknown and FlashAttention is unavailable, source contains a fallback toward eager in one branch.
- README examples use `attn_implementation="flash_attention_2"` and CUDA.
- Conclusion: eager fallback appears possible but must be verified by `envs/ov-encoder` import/probe.

LLaVA-OV2:

- `external/LLaVA-OneVision-2-8B-Instruct-code/modeling_llava_onevision2.py` includes `eager_attention_forward`.
- The model declares `_supports_flash_attn = True` and `_supports_sdpa = True`.
- The model chooses attention implementation through `config._attn_implementation`.
- Conclusion: SDPA/eager fallback appears possible but must be verified by `envs/llava-ov2`.

lmms-eval:

- `external/lmms-eval/lmms_eval/models/chat/llava_onevision2.py` defaults `attn_implementation` to `"flash_attention_2"`.
- Example scripts use `attn_implementation=flash_attention_2`.
- Conclusion: benchmark path is CUDA-oriented by default unless a later probe confirms a safe override.

## MPS Feasibility

MPS is best-effort only:

- bridge-core works without torch and does not need MPS.
- model import probes may be possible only if the selected env can avoid mandatory `flash_attn`.
- MPS results must not be treated as official Linux compatibility.

## Next Probe Commands

No-weight import probes after explicit env sync:

```bash
VTC_ALLOW_HEAVY_ENV_SYNC=1 bash scripts/setup_model_envs_best_effort.sh
```

If fallback works, record exact `attn_implementation` values in the relevant model-env status doc before any real model inference.
