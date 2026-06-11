# Project A LLaVA-OV2 Codec Boundary

Project A validates this bridge contract before any LLaVA-OV2 generation:

```text
decoded_entries -> selected_112_blocks -> src_positions -> codec-compatible payload
```

This step is artifact-contract validation only. It does not import AutoGaze,
LLaVA-OV2, torch, transformers, or model weights.

## Bridge Payload

The bridge-side payload is:

```python
{
    "src_positions": np.ndarray,       # int64 [N, 3]
    "selected_blocks": [(frame, r112, c112), ...],
    "meta": {
        "contract": "project_a_llava_codec_boundary",
        "selected_112_blocks": int,
        "raw_patch_tokens": int,
        "llm_visual_tokens": int,
        "src_positions_shape": [N, 3],
        "native_patch_grid": 16,
    },
}
```

Validation rules:

- `src_positions` must have shape `[N, 3]`.
- Rows are integer `[frame_idx, native_h, native_w]`.
- `native_h` and `native_w` must be within `0..15`.
- `N == selected_112_blocks * 4`.
- Each selected 112 block maps to native 2x2 order:
  `[2*r, 2*c]`, `[2*r, 2*c+1]`, `[2*r+1, 2*c]`, `[2*r+1, 2*c+1]`.

## LLaVA-OV2 Source Contract

The code-only HF custom-code snapshot contains the codec boundary:

- `external/LLaVA-OneVision-2-8B-Instruct-code/codec_video_processing_llava_onevision2.py`
  - `process_codec_video(video_url, cfg)` returns a payload with `images`,
    `src_positions`, `fps`, `out_dir`, and `meta`.
  - `drop_padding_canvases(images, src_positions)` rejects half-padding canvases.
  - `codec_positions_for_processor(src_positions, image_grid_thw, device)` checks
    that `src_positions` length matches `image_grid_thw` patch count and converts
    positions into processor block layout.
  - `codec_image_processor_outputs(image_processor, images, max_pixels)` runs the
    image processor without resizing codec canvases in a way that would desync
    `image_grid_thw` and `src_positions`.
- `external/LLaVA-OneVision-2-8B-Instruct-code/processing_llava_onevision2.py`
  - `video_backend="codec"` enters the codec branch.
  - The codec branch calls `process_codec_video`, `drop_padding_canvases`,
    `codec_image_processor_outputs`, and `codec_positions_for_processor`.
  - It emits `pixel_values`, `image_grid_thw`, and `patch_positions`.

The bridge boundary smoke source-inspects these files. It does not import them,
because importing processor/model code may require heavy dependencies or
attention backends that are not part of `bridge-core`.

## Current Blockers

- Runtime LLaVA-OV2 processor import is not proven in `bridge-core`.
- `flash_attn`/CUDA readiness is not proven.
- SDPA/eager fallback is source-indicated but not runtime-proven.
- Real generation and lmms-eval remain deferred.

## Smoke Command

```bash
cd envs/bridge-core
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_codec_synthetic.py
uv run python ../../projects/gaze-ov-bridge/scripts/smoke_project_a_llava_boundary.py
uv run python ../../scripts/profile_summary.py ../../projects/gaze-ov-bridge/out/smoke_project_a_llava_boundary/profile.json
```
