# gaze-ov-bridge

`gaze-ov-bridge` is the first VTC subproject. It will rebuild prior AutoGaze, OneVision-Encoder, and LLaVA-OV2 experiments through small, auditable stages.

The package starts with CPU-safe Python scaffolding only. Heavy model dependencies, external repositories, and model weights are intentionally excluded from the initial setup.

## Initial Constraints

- Python `>=3.11`.
- Managed with `uv`.
- Runtime dependencies are limited to `numpy` and `pillow`.
- Test dependency is limited to `pytest`.
- Do not add `torch`, `transformers`, AutoGaze, OneVision-Encoder, LLaVA-OV2, `lmms-eval`, or `flash_attn` yet.
