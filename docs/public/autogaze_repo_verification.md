# AutoGaze Repository Verification

Verification date: `2026-06-11T06:01:56Z`

No model weights were downloaded during this verification. Checks used public Hugging Face metadata/listing calls with no `HF_TOKEN` set.

## Source Evidence

AutoGaze source:

- Path: `external/AutoGaze`
- Remote: `https://github.com/NVlabs/AutoGaze.git`
- Branch: `main`
- Commit: `ba48d0f94ac2929d6fe3ee4380dc893aa6eed0ab`

Relevant source evidence:

- `external/AutoGaze/README.md` links to the `bfshi/autogaze` collection and `bfshi/AutoGaze` Space.
- `external/AutoGaze/README.md` lists `nvidia/AutoGaze` as the official pre-trained AutoGaze model.
- `external/AutoGaze/QUICK_START.md` currently uses `bfshi/AutoGaze` in example `from_pretrained(...)` calls.
- `external/AutoGaze/QUICK_START.md` documents the expected output keys `gazing_pos`, `if_padded_gazing`, and `num_gazing_each_frame`.

The source docs therefore contain a stale or ambiguous reference: the README table points to `nvidia/AutoGaze`, while the quick-start code points to `bfshi/AutoGaze`.

## Candidate Checks

| Candidate | Metadata result | File listing result | Auth required | Looks like AutoGaze weights/config | Decision |
| --- | --- | --- | --- | --- | --- |
| `nvidia/AutoGaze` | success | success, 6 files | no | yes: `config.json`, `preprocessor_config.json`, `model.safetensors`, `model_type=autogaze` | chosen |
| `bfshi/AutoGaze` | model not found | 401 repository-not-found/auth error | unknown; token absent | not verifiable in public-only mode | not chosen |

## `nvidia/AutoGaze`

HF metadata summary:

- Repo id: `nvidia/AutoGaze`
- Public/private: public
- Gated: false
- Revision: `5100fae739ec1bf3f875914fa1b703846a18943a`
- Config model type: `autogaze`
- Listed files:
  - `.gitattributes`
  - `LICENSE.md`
  - `README.md`
  - `config.json`
  - `model.safetensors`
  - `preprocessor_config.json`

This repo matches the AutoGaze README model table and has the expected Hugging Face model/preprocessor files.

## `bfshi/AutoGaze`

HF metadata/listing result:

- `hf models info bfshi/AutoGaze` returned model not found.
- The snapshot-wrapper list call returned a 401 repository-not-found/auth error.
- `HF_TOKEN` was not set, so this could mean private/gated access, a renamed repo, or a stale quick-start reference.

Because `nvidia/AutoGaze` is public and explicitly listed as the official pre-trained model, `bfshi/AutoGaze` is not required for the first weight-download attempt.

## Decision

Use `nvidia/AutoGaze` as the AutoGaze weight repo.

Confidence: high.

Evidence:

- AutoGaze README identifies `nvidia/AutoGaze` as the official pre-trained model.
- Hugging Face metadata reports `model_type=autogaze`.
- Public file listing contains `config.json`, `preprocessor_config.json`, and `model.safetensors`.
- The alternative candidate is not available in public-only mode.

## Weight Download Command

Run only in an explicit weight-download task:

```bash
source scripts/env_weights.sh
VTC_ALLOW_WEIGHT_DOWNLOAD=1 \
VTC_DOWNLOAD_AUTOGAZE=1 \
VTC_AUTOGAZE_REPO=nvidia/AutoGaze \
bash scripts/hf_download_weights.sh
```

Expected target:

```text
weights/checkpoints/AutoGaze
```

Do not commit `weights/`.
