# External Source Snapshot

Snapshot date: `2026-06-11T05:00:20Z`

This snapshot records source-only external repositories under `external/`. The `external/` directory is ignored and is not committed. No model inference was run, no heavy dependencies were installed, and no model weight payload files were downloaded.

## Snapshot Table

| Repo name | Local path | Remote URL | Branch | Commit hash | Purpose | Source-only | Weights downloaded |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AutoGaze | `external/AutoGaze` | `https://github.com/NVlabs/AutoGaze.git` | `main` | `ba48d0f94ac2929d6fe3ee4380dc893aa6eed0ab` | AutoGaze source audit for output generation and artifact serialization. | yes | no |
| LLaVA-OneVision-2 | `external/LLaVA-OneVision-2` | `https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2.git` | `main` | `ee337788824119dc1fed9fa5e461867ed01057c0` | LLaVA-OV2 source audit, codec/backend review, and bundled OneVision-Encoder custom-code inspection. | yes | no |
| lmms-eval | `external/lmms-eval` | `https://github.com/EvolvingLMMs-Lab/lmms-eval.git` | `llava-onevision2` | `3997a60cb8e79d9341ac1e4a286f0bb739bcc779` | Later `llava_onevision2` benchmark adapter and profiling hook audit. | yes | no |
| LLaVA-OneVision-2-8B-Instruct custom code | `external/LLaVA-OneVision-2-8B-Instruct-code` | `https://huggingface.co/lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` | `main` | `5a75eaf7d3cd73de6f85e637e45b420f46857d2e` | Code/config-only Hugging Face custom-code snapshot for LLaVA-OV2. | yes | no |

## Setup Notes

- GitHub sources were cloned with `--depth 1`; exact HEAD commit hashes are recorded above.
- `hf` was not available locally, so the Hugging Face custom-code snapshot used Git.
- The first Hugging Face partial clone attempt with `--filter=blob:none` failed during checkout with a promisor remote `expected 'packfile'` error.
- The successful Hugging Face snapshot used `GIT_LFS_SKIP_SMUDGE=1`, `--no-checkout`, sparse checkout patterns for code/config files, and local LFS filter disabling because `git-lfs` is not installed.
- The checked-out Hugging Face snapshot contains code/config/tokenizer metadata files, including `model.safetensors.index.json`, but no `.safetensors`, `.bin`, `.pt`, `.pth`, `.ckpt`, `.npy`, or `.npz` payload files were present after setup.
- `external/OneVision-Encoder` was not created in this pass because `external/LLaVA-OneVision-2/transformers_impl/onevision_encoder/` already provides standalone OneVision-Encoder custom code for source inspection. A separate OneVision-Encoder snapshot remains deferred unless later audit work needs a distinct upstream repository or Hugging Face repo.

## Dependency File Audit

Relevant dependency and requirements files found:

- `external/AutoGaze/pyproject.toml`
- `external/LLaVA-OneVision-2/pyproject.toml`
- `external/LLaVA-OneVision-2/requirements.txt`
- `external/LLaVA-OneVision-2/aiak_megatron/pyproject.toml`
- `external/LLaVA-OneVision-2/aiak_megatron/setup.py`
- `external/LLaVA-OneVision-2/aiak_megatron/megatron/core/requirements.txt`
- `external/lmms-eval/pyproject.toml`
- `external/lmms-eval/setup.py`

Initial findings:

- AutoGaze `pyproject.toml` lists `torch`, `torchvision`, `flash_attn`, `hydra-core`, `timm`, `transformers~=4.51`, `av`, and `imageio`.
- LLaVA-OneVision-2 `requirements.txt` pins `transformers==5.7.0` and includes `accelerate`, `datasets`, `hydra-core`, `megatron-energon`, `qwen_vl_utils`, `timm`, and related training/evaluation utilities.
- `lmms-eval` `pyproject.toml` has broad benchmark dependencies including `torch>=2.1.0`, `torchvision>=0.16.0`, `transformers>=4.39.2`, `opencv-python-headless`, `av<16.0.0`, `qwen-vl-utils>=0.0.14`, optional `video` extras, and many benchmark packages.
- These findings reinforce the existing split-environment decision: keep `bridge-core`, `autogaze`, `llava-ov2`, `ov-encoder`, and `lmms-eval` separate.

## Attention and `flash_attn` Audit

Search terms used:

```bash
rg -n "flash_attn|flash_attention|flash_attention_2|attn_implementation|sdpa|eager" external/...
```

File hit counts:

- AutoGaze: 11 files
- LLaVA-OneVision-2: 37 files
- lmms-eval: 58 files
- LLaVA-OneVision-2-8B-Instruct custom code: 3 files

Initial findings:

- AutoGaze declares `flash_attn` as a dependency in `pyproject.toml`. Its quick-start examples instantiate SigLIP models with `attn_implementation="sdpa"`, which suggests an SDPA path exists for at least the shown SigLIP usage, but source import requirements still need a model-environment import probe.
- LLaVA-OneVision-2 GitHub source includes `transformers_impl/onevision_encoder/modeling_onevision_encoder.py`, which dispatches attention through `config._attn_implementation`, defines `eager_attention_forward`, and declares `_supports_flash_attn = True` and `_supports_sdpa = True`.
- LLaVA-OneVision-2 GitHub source also includes `transformers_impl/llavaonevision2/modeling_llava_onevision2.py`, which references `eager`, `sdpa`, and `flash_attention_2` through Transformers attention interfaces.
- The Hugging Face custom-code snapshot `modeling_llava_onevision2.py` imports `is_flash_attention_requested`, defines an eager attention fallback, dispatches via `ALL_ATTENTION_FUNCTIONS`, and declares `_supports_flash_attn = True` and `_supports_sdpa = True`.
- The `lmms-eval` `llava_onevision2` chat adapter defaults `attn_implementation` to `"flash_attention_2"` when loading the model. Other adapters in the tree accept `sdpa` and `eager`, but the LLaVA-OV2 adapter default should be overridden or audited before CPU/MPS probes.

Current classification:

- `bridge-core`: no `flash_attn` requirement.
- AutoGaze: likely Linux/CUDA-oriented until import probe proves SDPA/eager operation without `flash_attn`.
- LLaVA-OV2 custom code: source suggests SDPA/eager support exists, but `lmms-eval` defaults to `flash_attention_2`; use a later import-only probe before any patching.
- OneVision-Encoder direct path: source supports `patch_positions` and attention dispatch with SDPA support in the GitHub custom code; verify in `envs/ov-encoder`.

## Profiling and Token Audit

Search terms used:

```bash
rg -n "profiling|benchmark|latency|token|memory|max_memory|generate|codec|image_grid_thw|patch_positions" external/...
```

File hit counts:

- AutoGaze: 21 files
- LLaVA-OneVision-2: 642 files
- lmms-eval: 991 files
- LLaVA-OneVision-2-8B-Instruct custom code: 15 files

Initial findings by source:

- AutoGaze:
  - Relevant source areas include `autogaze/models/autogaze/`, `autogaze/datasets/collate.py`, and training/task files.
  - Next audit should locate the exact production of `gazing_pos` and `if_padded_gazing` and add/export token counts by scale.
- LLaVA-OneVision-2 GitHub source:
  - `tools/frame_extraction/core/run_cut_frames.py` writes `patch_positions.npy` and metadata for extracted video frames.
  - `transformers_impl/onevision_encoder/modeling_onevision_encoder.py` accepts `patch_positions` as `[batch_size, seq_len, 3]` and computes RoPE from `[t, h, w]`.
  - `transformers_impl/llavaonevision2/modeling_llava_onevision2.py` threads `patch_positions` through image/video feature extraction and generation prep paths.
- Hugging Face LLaVA-OV2 custom code:
  - `codec_video_processing_llava_onevision2.py` documents the codec backend, calls `codec-video-prep`, validates `image_grid_thw` against `src_patch_position`, converts codec positions to block layout, and rewrites visual text spans based on `patch_positions`.
  - `video_processing_llava_onevision2.py` builds dense frame-based `patch_positions` for the non-codec backend.
  - `modeling_llava_onevision2.py` uses explicit `patch_positions` for 3D RoPE and forwards them through image/video feature paths.
- `lmms-eval`:
  - `lmms_eval/models/chat/llava_onevision2.py` registers `llava_onevision2`, supports `video_backend="frames"` or `"codec"`, passes `attn_implementation` into `from_pretrained`, and wraps `self.model.generate`.
  - The same adapter already accumulates `e2e_latency`, `total_tokens`, and `avg_speed` in `generate_until`.
  - `lmms_eval/evaluator.py` dispatches request types through `getattr(lm, reqtype)(cloned_reqs)`, which is the likely outer hook for per-sample or per-request profile records.
  - Other chat adapters such as `qwen2_5_vl.py`, `vllm.py`, and `vllm_generate.py` also record latency and token counts, useful as implementation references.

Profiling implications:

- Project A LLaVA-OV2 profiling can attach at processor codec preprocessing, model forward, and generate boundaries.
- Project B OV-Encoder profiling can attach at direct `patch_positions` preparation and vision model forward boundaries.
- `lmms-eval` profiling can likely append per-sample `profile.jsonl` records inside the model adapter or around evaluator request dispatch.
- Memory profiling still needs model-environment probes; use torch metrics only after torch is installed in the relevant isolated env.

## Missing Blockers and Deferred Items

- No required GitHub repo or branch was missing. The `llava-onevision2` branch cloned successfully.
- `hf` CLI was unavailable, so the Hugging Face snapshot used Git sparse checkout instead.
- `git-lfs` is unavailable. LFS filters were disabled locally for the Hugging Face code-only checkout; no weight payload files were checked out.
- `external/OneVision-Encoder` was not created because the LLaVA-OneVision-2 source tree includes `transformers_impl/onevision_encoder/`. A separate standalone source snapshot remains deferred until a distinct authoritative source is required.
- No dependency installs, model downloads, import probes, or inference runs were performed.
