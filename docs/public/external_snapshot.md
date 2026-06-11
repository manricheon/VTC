# External Source Snapshot

Snapshot date: `2026-06-11T06:01:56Z`

This snapshot records source-only external repositories and code-only Hugging Face snapshots under `external/`. The `external/` directory is ignored and must not be committed. No model inference was run, no heavy dependencies were installed, and no model weight payload files were downloaded.

## Snapshot Table

| Repo name | Target path | Source URL or HF repo id | Branch/revision | Commit hash or HF revision | Status | Purpose | Source-only | Weights downloaded | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AutoGaze | `external/AutoGaze` | `https://github.com/NVlabs/AutoGaze.git` | `main` | `ba48d0f94ac2929d6fe3ee4380dc893aa6eed0ab` | `already_present` | AutoGaze source audit for output generation and artifact serialization. | yes | no | none |
| LLaVA-OneVision-2 | `external/LLaVA-OneVision-2` | `https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2.git` | `main` | `ee337788824119dc1fed9fa5e461867ed01057c0` | `already_present` | LLaVA-OV2 source audit, processor/backend review, and bundled OneVision-Encoder source inspection. | yes | no | none |
| lmms-eval | `external/lmms-eval` | `https://github.com/EvolvingLMMs-Lab/lmms-eval.git` | `llava-onevision2` | `3997a60cb8e79d9341ac1e4a286f0bb739bcc779` | `already_present` | `llava_onevision2` benchmark adapter and profiling hook audit. | yes | no | none |
| LLaVA-OneVision-2-8B-Instruct custom code | `external/LLaVA-OneVision-2-8B-Instruct-code` | `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | `main` | `5a75eaf7d3cd73de6f85e637e45b420f46857d2e` | `downloaded_code_only` | Code/config/text Hugging Face custom-code snapshot for LLaVA-OV2. | yes | no | none |
| OneVision-Encoder custom code | `external/OneVision-Encoder` | `lmms-lab-encoder/onevision-encoder-large` | `main` | `9908b86a6c651379df4a0b0a7ecfccc6afcd544e` | `downloaded_code_only` | Code/config/text Hugging Face custom-code snapshot for Project B source inspection. | yes | no | none |

The three GitHub clones were fetched with `git fetch --prune` during this pass. Their checked-out commits match their fetched remote branch tips.

File payload check:

- No `.safetensors`, `.bin`, `.pt`, `.pth`, `.gguf`, or `.onnx` files were found under `external/`.
- No `.safetensors`, `.bin`, `.pt`, `.pth`, `.gguf`, or `.onnx` files were found under `weights/`.
- Hugging Face cache paths remain under `weights/hf_home` through `HF_HOME` and `HF_HUB_CACHE`.

## Hugging Face Code Snapshots

`external/LLaVA-OneVision-2-8B-Instruct-code` was refreshed with `scripts/hf_download_code_only.sh`. The target contains code/config/tokenizer text files such as:

- `codec_video_processing_llava_onevision2.py`
- `processing_llava_onevision2.py`
- `video_processing_llava_onevision2.py`
- `modeling_llava_onevision2.py`
- `configuration_llava_onevision2.py`
- `config.json`
- `preprocessor_config.json`
- tokenizer/config text files

It also contains `model.safetensors.index.json`, which is model metadata, not a model weight payload.

`external/OneVision-Encoder` was created from `lmms-lab-encoder/onevision-encoder-large` with code/config/text allow patterns and weight payload ignore patterns. It contains:

- `README.md`
- `__init__.py`
- `config.json`
- `configuration_onevision_encoder.py`
- `modeling_onevision_encoder.py`
- `preprocessor_config.json`

The OneVision-Encoder README also references a GitHub source repo at `https://github.com/EvolvingLMMs-Lab/OneVision-Encoder.git`. That separate GitHub repo was not cloned in this task because the requested HF custom-code snapshot is now sufficient for source inspection. Clone it later only if the HF custom-code snapshot is insufficient.

## AutoGaze Important Paths

AutoGaze source commit: `ba48d0f94ac2929d6fe3ee4380dc893aa6eed0ab`.

Important source paths:

- `external/AutoGaze/README.md`: lists `nvidia/AutoGaze` as the official pre-trained AutoGaze model.
- `external/AutoGaze/QUICK_START.md`: documents runtime output fields and currently references `bfshi/AutoGaze` in sample code.
- `external/AutoGaze/autogaze/models/autogaze/modeling_autogaze.py`: returns `gazing_pos`, `num_gazing_each_frame`, and `if_padded_gazing`.
- `external/AutoGaze/autogaze/models/autogaze/autogaze.py`: returns `gazing_pos`, `gazing_mask`, `scales`, `num_gazing_each_frame`, and `if_padded_gazing`.
- `external/AutoGaze/autogaze/datasets/collate.py`: collates `gazing_pos`, `if_padded_gazing`, and `num_gazing_each_frame`.
- `external/AutoGaze/autogaze/utils.py`: contains gazing-position utility code.

Dependency finding:

- `external/AutoGaze/pyproject.toml` declares `torch`, `torchvision`, `flash_attn`, `hydra-core`, `wandb`, `loguru`, `timm`, `transformers~=4.51`, `pillow`, `numpy`, `omegaconf`, `matplotlib`, `einops`, `av`, and `imageio`.

## AutoGaze HF Repo Verification

Candidate checks were run in public-only mode with no `HF_TOKEN` set.

Verified candidate:

- `nvidia/AutoGaze`
- HF metadata status: public, `gated=false`, `private=false`
- HF revision: `5100fae739ec1bf3f875914fa1b703846a18943a`
- HF config summary: `model_type="autogaze"`
- Listed files: `.gitattributes`, `LICENSE.md`, `README.md`, `config.json`, `model.safetensors`, `preprocessor_config.json`

Rejected or unresolved candidate:

- `bfshi/AutoGaze`
- `hf models info` returned model not found.
- `list_repo_files` through the snapshot wrapper returned a 401 repository-not-found/auth error with no token configured.
- The AutoGaze quick-start still references `bfshi/AutoGaze`, but the README model table identifies `nvidia/AutoGaze` as the official pre-trained model.

Decision:

- Use `nvidia/AutoGaze` for the first AutoGaze weight-download attempt.
- Keep `bfshi/AutoGaze` recorded as a stale, private, renamed, or otherwise inaccessible reference unless the user later provides evidence or HF access that proves it is required.

## LLaVA-OV2 Important Paths

GitHub source commit: `ee337788824119dc1fed9fa5e461867ed01057c0`.

HF custom-code revision: `5a75eaf7d3cd73de6f85e637e45b420f46857d2e`.

Important source paths:

- `external/LLaVA-OneVision-2/requirements.txt`: pins `transformers==5.7.0` and includes LLaVA-OV2 development dependencies.
- `external/LLaVA-OneVision-2/transformers_impl/onevision_encoder/modeling_onevision_encoder.py`: bundled OneVision-Encoder implementation with `patch_positions` handling.
- `external/LLaVA-OneVision-2/transformers_impl/llavaonevision2/modeling_llava_onevision2.py`: LLaVA-OV2 model implementation.
- `external/LLaVA-OneVision-2-8B-Instruct-code/codec_video_processing_llava_onevision2.py`: codec video preprocessing, `process_codec_video`, and `src_positions` to processor-position conversion.
- `external/LLaVA-OneVision-2-8B-Instruct-code/processing_llava_onevision2.py`: processor codec branch that produces `pixel_values`, `image_grid_thw`, and `patch_positions`.
- `external/LLaVA-OneVision-2-8B-Instruct-code/video_processing_llava_onevision2.py`: frame backend dense `patch_positions`.
- `external/LLaVA-OneVision-2-8B-Instruct-code/modeling_llava_onevision2.py`: model path that consumes `patch_positions` and preserves them through generation expansion.

Codec finding:

- The HF custom-code codec module says the codec path invokes `cv-preinfer` / `codec-video-prep` and requires `ffmpeg` on `PATH`.
- The codec branch returns `pixel_values`, `image_grid_thw`, and `patch_positions`, matching the Project A codec-compatible artifact target.

## OneVision-Encoder Important Paths

HF custom-code revision: `9908b86a6c651379df4a0b0a7ecfccc6afcd544e`.

Important source paths:

- `external/OneVision-Encoder/README.md`: documents 224 video input usage, 14 patch size, `patch_positions`, and example `attn_implementation="flash_attention_2"`.
- `external/OneVision-Encoder/config.json`: model config for `onevision_encoder`.
- `external/OneVision-Encoder/modeling_onevision_encoder.py`: model implementation.

Project B finding:

- `modeling_onevision_encoder.py` implements `VideoRotaryEmbeddingSplit466.forward_from_positions(patch_positions)`.
- `OneVisionEncoderModel.forward(...)` accepts `visible_indices` and `patch_positions`.
- If `patch_positions` is provided, the model computes RoPE from the explicit `[t, h, w]` table.
- This supports the Project B decision to preserve one AutoGaze selected token as one OV direct token with fractional/explicit positions prepared by bridge-core.

## lmms-eval Important Paths

Source commit: `3997a60cb8e79d9341ac1e4a286f0bb739bcc779`.

Important source paths:

- `external/lmms-eval/pyproject.toml`: broad benchmark dependencies including `torch`, `torchvision`, `transformers>=4.39.2`, `opencv-python-headless`, `av<16.0.0`, `qwen-vl-utils`, and optional video extras.
- `external/lmms-eval/lmms_eval/models/chat/llava_onevision2.py`: registered `llava_onevision2` adapter.
- `external/lmms-eval/examples/llava_onevision2_repro/run_frames.sh`: frame backend example.
- `external/lmms-eval/examples/llava_onevision2_repro/run_codec.sh`: codec backend example.

Adapter finding:

- The `llava_onevision2` adapter defaults `attn_implementation` to `flash_attention_2`.
- It supports `video_backend="frames"` and `video_backend="codec"`.
- The codec backend imports `process_codec_video`, `drop_padding_canvases`, `codec_positions_for_processor`, and `codec_image_processor_outputs` from the checkpoint custom code.
- It passes `patch_positions` through the processor output into generation.
- It already accumulates `e2e_latency` and `total_tokens`, then logs `avg_speed`.

## Attention and flash_attn Findings

AutoGaze:

- `flash_attn` is declared in `pyproject.toml`.
- QUICK_START SigLIP examples use `attn_implementation="sdpa"` for the customized SigLIP path.
- This still needs an isolated `envs/autogaze` import probe before assuming CPU/MPS or non-FlashAttention operation.

LLaVA-OV2:

- The HF custom-code model declares `_supports_flash_attn = True` and `_supports_sdpa = True`.
- The model accepts explicit `patch_positions` and keeps them in generation expansion.
- `lmms-eval` defaults to `attn_implementation="flash_attention_2"`, so non-CUDA probes must explicitly test `sdpa` or `eager` rather than relying on defaults.

OneVision-Encoder:

- The HF custom-code model imports `flash_attn` inside a guarded `try/except`, so module import itself should not require `flash_attn`.
- Attention classes include `eager` and `flash_attention_2`.
- The README examples use `attn_implementation="flash_attention_2"` and `.to("cuda")`.
- The default/config path appears FlashAttention-oriented; a later import probe must explicitly test `attn_implementation="eager"` for CPU/MPS viability.

bridge-core:

- No `flash_attn`, `torch`, `transformers`, AutoGaze, LLaVA-OV2, OneVision-Encoder, or `lmms-eval` dependency is required.

## Profiling Hook Findings

AutoGaze:

- Export points should be near the returned `gazing_pos`, `if_padded_gazing`, `gazing_mask`, and `num_gazing_each_frame` fields.
- Token counts by scale can be computed after serialized artifacts are produced; do not import AutoGaze into bridge-core.

LLaVA-OV2:

- Codec preprocessing can be timed around `process_codec_video`, `drop_padding_canvases`, `codec_positions_for_processor`, and processor image output conversion.
- Model profiling can use stages for `processor`, `model_forward`, and `generate`.
- Token counts should be taken from bridge artifacts and processor/model inputs, not inferred from text output alone.

OneVision-Encoder:

- Project B profiling can time `patch_extract`, `pack`, and later `model_forward`.
- The explicit `patch_positions` path is the key hook for preserving sparse multiscale tokens.

lmms-eval:

- The `llava_onevision2` adapter already measures generation latency and output token counts.
- A later benchmark integration can append per-sample or per-batch `profile.jsonl` records near `generate_until`.

## Remaining Deferred Work

- Download model weights under `weights/checkpoints/...`.
- Install or verify `ffmpeg` on the official Linux target.
- Run isolated model-environment uv sync/import probes.
- Verify `flash_attn`, `sdpa`, and `eager` behavior in actual model environments.
- Run real AutoGaze output generation.
- Run real LLaVA-OV2 codec/generation.
- Run real OneVision-Encoder direct forward.
- Run `lmms-eval`.
