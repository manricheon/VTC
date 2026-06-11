# CLI Sequential A/B/C Plan

Date: 2026-06-11

Current branch: `feature/gaze-ov-bridge-local`

Current commit before A/B/C work: `f66c182 Record model environment lockfiles`

## Task A Summary

Project A LLaVA-OV2 codec-compatible boundary validation.

Add a pure Python bridge-side validation module and smoke script for the contract:

```text
selected_blocks.json + src_positions.npy -> LLaVA-compatible payload boundary
```

This must not run LLaVA-OV2 generation, import AutoGaze into LLaVA runtime, or require model execution.

## Task B Summary

Project B OV-Encoder direct boundary validation.

Add a pure Python bridge-side validation module and smoke script for the contract:

```text
decoded_entries.json + patches.npy + patch_positions.npy + pack_plan.json -> OV-direct payload boundary
```

This must not run real OV-Encoder forward or import AutoGaze.

## Task C Summary

lmms-eval integration planning and limit-one runner skeleton.

Create a public plan and a guarded `--limit 1` runner skeleton for future `autogaze_codec` evaluation. The script must not run the benchmark unless explicitly enabled.

## Deferred Blockers

- `ffmpeg` is missing on the Mac probe host and must be verified on Linux.
- Heavy model envs still need isolated sync/import probes.
- `flash_attn`, CUDA, and SDPA/eager runtime fallback remain unverified.
- MPS is best-effort only.
- Real LLaVA-OV2 generation waits.
- Real OV-Encoder forward waits.
- Full lmms-eval benchmark waits.

## Commit Plan

1. Local guidance commit: `Plan CLI sequential A/B/C tasks`.
2. Public Task A commit: `Add Project A LLaVA codec boundary validation`.
3. Public Task B commit: `Add Project B OV direct boundary validation`.
4. Public Task C commit: `Add lmms-eval autogaze profiling plan`.
5. Public completion-status commit: `Record CLI A/B/C completion status`.
