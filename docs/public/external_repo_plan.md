# External Source Repository Plan

This plan defines how VTC will later collect source snapshots for AutoGaze, LLaVA-OneVision-2, OneVision-Encoder, and `lmms-eval` audits. Do not run these commands until the clone/download task is explicitly requested.

This task does not clone repositories, download weights, install model dependencies, or run inference.

## Source Repositories and Target Paths

| Source | Target path | Purpose |
| --- | --- | --- |
| `NVlabs/AutoGaze` | `external/AutoGaze` | AutoGaze output generation source audit and artifact writer integration. |
| `EvolvingLMMs-Lab/LLaVA-OneVision-2` | `external/LLaVA-OneVision-2` | LLaVA-OV2 repository source audit, processor/backend behavior, codec path review. |
| `EvolvingLMMs-Lab/lmms-eval`, branch `llava-onevision2` | `external/lmms-eval` | Later benchmark adapter and per-sample profiling hook audit. |
| `lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct` Hugging Face custom-code snapshot | `external/LLaVA-OneVision-2-8B-Instruct-code` | Code-only custom model snapshot for LLaVA-OV2; no model weights. |
| OneVision-Encoder source/custom code, if needed | `external/OneVision-Encoder` | OV-Encoder custom-code audit for Project B direct `patch_positions` path. |

`external/` is ignored by Git and must not be committed. Source snapshot metadata will be recorded later in `docs/public/external_snapshot.md`.

## Clone and Download Rules

- Use source-only clones or code-only downloads.
- Do not download model weights, checkpoints, tokenizer weights, safetensors, binary shards, or cached HF model artifacts.
- Keep third-party source repositories under `external/`, not `weights/`.
- Use `weights/` only for Hugging Face weights, checkpoints, and caches in later weight-enabled tasks.
- Prefer shallow clones only if they still allow exact commit hash recording. If a shallow clone prevents accurate branch or commit audit, use a normal source clone.
- Record for every source:
  - remote URL
  - branch or revision
  - commit hash
  - clone/download date in UTC
  - command used
  - any missing repository, missing branch, or access blocker
- Do not edit external source trees for bridge implementation during source audit. If a patch becomes necessary later, document the reason and keep it separate from the source snapshot.

## Commands To Run Later

Run these from the VTC repository root only after the user explicitly requests external source setup.

```bash
mkdir -p external
```

GitHub source clones:

```bash
git clone https://github.com/NVlabs/AutoGaze.git external/AutoGaze
git clone https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2.git external/LLaVA-OneVision-2
git clone --branch llava-onevision2 https://github.com/EvolvingLMMs-Lab/lmms-eval.git external/lmms-eval
```

If shallow clones are acceptable for a specific source snapshot:

```bash
git clone --depth 1 https://github.com/NVlabs/AutoGaze.git external/AutoGaze
git clone --depth 1 https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2.git external/LLaVA-OneVision-2
git clone --depth 1 --branch llava-onevision2 https://github.com/EvolvingLMMs-Lab/lmms-eval.git external/lmms-eval
```

Record clone metadata:

```bash
git -C external/AutoGaze remote -v
git -C external/AutoGaze branch --show-current
git -C external/AutoGaze rev-parse HEAD

git -C external/LLaVA-OneVision-2 remote -v
git -C external/LLaVA-OneVision-2 branch --show-current
git -C external/LLaVA-OneVision-2 rev-parse HEAD

git -C external/lmms-eval remote -v
git -C external/lmms-eval branch --show-current
git -C external/lmms-eval rev-parse HEAD
```

Hugging Face custom-code snapshot options:

```bash
hf download lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct \
  --repo-type model \
  --local-dir external/LLaVA-OneVision-2-8B-Instruct-code \
  --include "*.py" "*.json" "*.txt" "*.md" "configuration*" "modeling*" "processing*" "tokenization*"
```

Equivalent Python `huggingface_hub` approach:

```bash
python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct",
    repo_type="model",
    local_dir="external/LLaVA-OneVision-2-8B-Instruct-code",
    allow_patterns=[
        "*.py",
        "*.json",
        "*.txt",
        "*.md",
        "configuration*",
        "modeling*",
        "processing*",
        "tokenization*",
    ],
    ignore_patterns=[
        "*.bin",
        "*.ckpt",
        "*.gguf",
        "*.h5",
        "*.msgpack",
        "*.onnx",
        "*.pt",
        "*.pth",
        "*.safetensors",
        "*.tflite",
        "*.npz",
        "*.npy",
    ],
)
PY
```

OneVision-Encoder source/custom code should be downloaded only after identifying the authoritative source. If the custom code is hosted only in Hugging Face model repos, use the same code-only `hf download` or `snapshot_download` pattern into `external/OneVision-Encoder`.

## Post-Clone Audit

Run source searches after external sources exist:

```bash
rg -n "flash_attn|flash_attention|flash_attention_2|attn_implementation|sdpa|eager" external/AutoGaze external/LLaVA-OneVision-2 external/lmms-eval external/LLaVA-OneVision-2-8B-Instruct-code external/OneVision-Encoder
```

For each source tree, inspect dependency files:

```bash
rg --files external/AutoGaze external/LLaVA-OneVision-2 external/lmms-eval external/LLaVA-OneVision-2-8B-Instruct-code external/OneVision-Encoder \
  | rg "(pyproject.toml|requirements.*\\.txt|setup.py|setup.cfg|environment.*\\.ya?ml|uv.lock|poetry.lock|README.*|INSTALL.*)"
```

Audit questions:

- Is `flash_attn` imported at module import time?
- Is FlashAttention declared only in package metadata or required by executed code?
- Does the code support `attn_implementation="sdpa"` or `attn_implementation="eager"`?
- Is `"flash_attention_2"` hard-coded?
- Which `transformers`, `torch`, video, codec, and evaluation packages are pinned?
- Which package constraints conflict with the planned split environments?
- Which source files are responsible for AutoGaze token output, LLaVA-OV2 codec input, OV-Encoder `patch_positions`, and `lmms-eval` model adapter execution?

Record findings in `docs/public/dependency_compatibility.md` when they change compatibility decisions. Record immutable source snapshot metadata in `docs/public/external_snapshot.md`.

## Profiling-Related Source Audit

For each external repo, identify existing profiling or benchmark hooks before adding new instrumentation.

Search for profiling and timing code:

```bash
rg -n "profile|profiling|benchmark|latency|throughput|time\\.|perf_counter|cuda.*memory|max_memory|token_count|num_tokens|generate|forward" external/AutoGaze external/LLaVA-OneVision-2 external/lmms-eval external/LLaVA-OneVision-2-8B-Instruct-code external/OneVision-Encoder
```

Audit additions:

- AutoGaze:
  - Locate where `gazing_pos` and `if_padded_gazing` are produced.
  - Identify where selected token counts by scale can be exported.
  - Identify decode/frame preprocessing timing boundaries.
- LLaVA-OV2:
  - Locate codec backend preprocessing and canvas packing.
  - Identify whether codec-selected token counts are already logged.
  - Identify where processor, model forward, and generate latency can be measured.
  - Identify how visual token counts reach the language model.
- OneVision-Encoder:
  - Locate the custom-code path that accepts or constructs `patch_positions`.
  - Identify model forward timing boundaries.
  - Confirm whether sparse, irregular token layouts are accepted without RoPE frequency scaling.
- `lmms-eval`:
  - Locate the `llava-onevision2` model adapter.
  - Identify per-sample hooks for latency, memory, token counts, and score output.
  - Determine how to attach `profile.jsonl` records without breaking benchmark outputs.
- Shared:
  - Map external timing stages to the bridge schema: `decode`, `selector`, `patch_extract`, `pack`, `processor`, `model_forward`, `generate`, `eval`.
  - Record where CPU, CUDA, and optional MPS memory can be measured.
  - Prefer stdlib timing and bridge profile writers first; use torch memory metrics only in environments where torch is already installed.

## Failure Handling

- If a repository is missing, private, renamed, or inaccessible, record the blocker in `docs/public/external_snapshot.md`.
- If branch `llava-onevision2` is missing from `EvolvingLMMs-Lab/lmms-eval`, record the blocker and do not silently fall back to another branch.
- If a Hugging Face custom-code snapshot cannot be fetched without weights, stop and record the exact command and failure.
- If OneVision-Encoder source location is ambiguous, record candidate sources and defer the clone/download until the authoritative source is confirmed.
- Do not invent source files, function names, APIs, or integration hooks.
- Do not patch around missing dependencies such as `flash_attn` until the source audit identifies the safest path.

## Deferred Work

- Actually clone or download external sources.
- Record source snapshots in `docs/public/external_snapshot.md`.
- Run dependency lock/import probes in model-specific `envs/*` environments.
- Download weights into `weights/`.
- Run real AutoGaze, LLaVA-OV2, OneVision-Encoder, or `lmms-eval` inference.
