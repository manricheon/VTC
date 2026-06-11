# Project B OV-Encoder Direct Boundary

Project B validates this bridge contract before any OneVision-Encoder forward:

```text
decoded_entries -> patches + patch_positions + pack_plan -> OV-direct payload
```

This step is artifact-contract validation only. It does not import AutoGaze,
OneVision-Encoder, torch, transformers, or model weights.

## Bridge Payload

The bridge-side payload is:

```python
{
    "decoded_entries": [...],
    "patches": np.ndarray,           # [K, 14, 14, 3] by default
    "patch_positions": np.ndarray,   # float32 [K, 3]
    "pack_plan": {...},
    "meta": {
        "contract": "project_b_ov_direct_boundary",
        "total_tokens": K,
        "patches_shape": [...],
        "patch_positions_shape": [K, 3],
        "pack_canvas_count": int,
        "confirms_no_native_union": True,
    },
}
```

Validation rules:

- One valid decoded AutoGaze entry maps to exactly one OV token.
- Coarse scales are not expanded into native-grid union.
- `patch_positions` must have shape `[K, 3]`.
- Fractional coordinates follow the direct OV formula:
  `h = (row + 0.5) * (16 / grid) - 0.5`,
  `w = (col + 0.5) * (16 / grid) - 0.5`.
- Expected first-row offsets:
  - scale `224`: `0.0`
  - scale `112`: `0.5`
  - scale `56`: `1.5`
  - scale `28`: `3.5`
- Pack-plan token metadata preserves input order and excludes padding slots.

## OneVision-Encoder Source Contract

The code-only OneVision-Encoder snapshot contains the direct-path hooks:

- `external/OneVision-Encoder/configuration_onevision_encoder.py`
  - default `image_size=224`
  - default `patch_size=14`
  - RoPE configuration fields
- `external/OneVision-Encoder/modeling_onevision_encoder.py`
  - `forward_from_positions(patch_positions)` consumes explicit
    `[batch_size, seq_len, 3]` positions.
  - `forward(... visible_indices=None, patch_positions=None)` exposes both
    sparse-token and explicit-position paths.
  - source contains `_attn_implementation`, `flash_attention_2`, and an eager
    fallback indicator.
- `external/OneVision-Encoder/README.md`
  - documents `224x224` video input, `patch_size=14`, 256 tokens per frame, and
    `patch_positions`.

The bridge boundary smoke source-inspects these files. It does not import model
code because runtime import can require torch, transformers, and attention
backend dependencies outside `bridge-core`.

## Current Blockers

- OneVision-Encoder runtime import is not proven in `bridge-core`.
- Heavy `envs/ov-encoder` sync is not fully proven here.
- `flash_attn`/CUDA readiness is not proven.
- SDPA/eager fallback is source-indicated but not runtime-proven.
- Real OV-Encoder forward remains deferred.

## Smoke Command

```bash
cd envs/bridge-core
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_direct_synthetic.py
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_b_ov_boundary.py
uv run python ../../scripts/profile_summary.py ../../projects/gaze-ov-bridge/out/smoke_project_b_ov_boundary/profile.json
```
