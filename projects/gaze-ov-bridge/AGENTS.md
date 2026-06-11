# gaze-ov-bridge Agent Guidance

## Project A, Priority 1: AutoGaze -> LLaVA-OV2 Codec-Compatible Backend

- Goal: obtain answer-level score and later lmms-eval results.
- Keep LLaVA-OV2 model code as unchanged as possible.
- Convert AutoGaze outputs into 112-anchor native 2x2 block selections.
- 112 scale is the canonical anchor.
- 224 scale is fine evidence for the containing 112 block.
- 56 scale is region prior, not full union by default.
- 28 scale is frame/global prior, not spatial union by default.
- Final LLaVA-OV2 selected units are 112 blocks: `(frame_id, r112, c112)`.
- Each 112 block maps to 4 native 14x14 patches in 2x2 order.
- `src_positions` must be integer `[frame_id, native_h, native_w]`.
- Avoid half-padding canvases.
- Hard union should exist only as an explicit ablation option.
- Do not import AutoGaze inside LLaVA-OV2 runtime. Consume JSON/NPY artifacts.
- Always profile token counts, compression ratios, latency, and memory where possible.

## Project B, Priority 2: AutoGaze -> OneVision-Encoder Direct

- Goal: preserve AutoGaze multi-scale selected patches as individual tokens.
- Do not expand coarse tokens into native-grid union.
- Extract actual 14x14 patches from scale-resized frames.
- Generate fractional `patch_positions = [t, h, w]`.
- Do not apply RoPE frequency scaling.
- AutoGaze selected token 1개는 OV-Encoder token 1개로 유지한다.
- OV native grid is `224 / 14 = 16`.
- For scale grid = `scale / 14`:
  - `h = (row + 0.5) * (16 / grid) - 0.5`
  - `w = (col + 0.5) * (16 / grid) - 0.5`
- Do not import AutoGaze inside OV-Encoder runtime. Consume JSON/NPY artifacts.
- Always profile direct token counts, dense comparison tokens, latency, and memory where possible.

## Attention and flash_attn Policy

- Do not assume `flash_attn` is available.
- Audit whether `flash_attn` is a hard requirement or optional performance dependency.
- Check whether sdpa or eager attention fallback is possible for any model that supports it.
- MPS tests may run only if dependencies and attention backend allow it.
- Linux remains the official target.

## Profiling Policy

- Every smoke script and real integration script must produce `stats.json`.
- Every real model script should produce `profile.json` or `profile.jsonl`.
- Profiling must include:
  - wall-clock timings by stage
  - token counts
  - compression ratios
  - peak CPU memory where possible
  - CUDA/MPS memory where possible
  - environment metadata
  - git commit
  - run_id
- Profiling should use stdlib first.
- Optional torch-specific memory metrics should be collected only when torch is installed.
