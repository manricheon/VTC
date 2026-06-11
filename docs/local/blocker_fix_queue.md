# Blocker Fix Queue

This is the short ordered queue before external source or weight-download work continues.

- [ ] Source `scripts/env_weights.sh` and rerun `cd envs/bridge-core && uv run python ../../scripts/check_linux_env.py`.
- [ ] Run an HF auth/access-only probe for required model repos, with no weight download.
- [ ] Confirm Linux system prerequisites, especially `ffmpeg`.
- [ ] Run no-weight isolated import probes, one env at a time: `llava-ov2`, `ov-encoder`, `autogaze`, `lmms-eval`.
- [ ] Classify `flash_attn` paths from probe evidence: optional fallback vs Linux/CUDA-only.
- [ ] Decide whether `external/LLaVA-OneVision-2/transformers_impl/onevision_encoder/` is sufficient for Project B or whether a standalone OneVision-Encoder source snapshot is required.
- [ ] Run optional `envs/mps-probe` only as a best-effort Mac diagnostic.
- [ ] Plan weight downloads only after HF access, cache paths, and environment import probes are resolved.
