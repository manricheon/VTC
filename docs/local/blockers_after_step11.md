# Post-Step-11 Blocker Audit

Date: 2026-06-11

This is a local guidance report. It should not be included in any later public branch.

## Repository State

- Branch: `feature/gaze-ov-bridge-local`
- Latest commit: `631177fb084c26923b010be303a7e0abbab12975`
- Short HEAD: `631177f Add isolated environment compatibility probes`
- Initial `git status --short`: clean
- Final pre-report status before writing this document: clean

Recent history:

```text
631177f Add isolated environment compatibility probes
a7bbfed Record external source repository snapshot
df5f437 Add external source repository plan
dae08a6 Add Project B OV direct synthetic smoke profiling
7e06e44 Implement Project B OV direct utilities
b42d474 Add Project A codec synthetic smoke profiling
6c59b80 Implement Project A codec-compatible selector utilities
a7934fe Add profiling schema and utilities
168b90f Add Linux uv bridge-core environment scripts
3ff05af Add dependency compatibility audit plan
9b9c69f Add local Codex guidance for gaze-ov-bridge
35b40d0 Initialize VTC with gaze-ov-bridge skeleton
```

## Directory Structure Summary

Top-level development environments:

```text
envs/autogaze/.python-version
envs/autogaze/pyproject.toml
envs/bridge-core/.python-version
envs/bridge-core/.venv/
envs/bridge-core/pyproject.toml
envs/bridge-core/uv.lock
envs/llava-ov2/.python-version
envs/llava-ov2/pyproject.toml
envs/lmms-eval/.python-version
envs/lmms-eval/pyproject.toml
envs/mps-probe/.python-version
envs/mps-probe/pyproject.toml
envs/ov-encoder/.python-version
envs/ov-encoder/pyproject.toml
```

External source snapshot present:

```text
external/AutoGaze
external/LLaVA-OneVision-2
external/LLaVA-OneVision-2-8B-Instruct-code
external/lmms-eval
```

Deferred external source:

```text
external/OneVision-Encoder
```

This was intentionally not created because `external/LLaVA-OneVision-2/transformers_impl/onevision_encoder/` currently provides OneVision-Encoder custom code for source inspection.

Weights/cache directories present:

```text
weights/checkpoints/AutoGaze
weights/checkpoints/LLaVA-OneVision-2-8B-Instruct
weights/checkpoints/onevision-encoder-large
weights/hf_home
weights/hf_home/hub
```

Artifacts currently present:

```text
artifacts/profiles/
projects/gaze-ov-bridge/out/smoke_project_a_codec_synthetic/
projects/gaze-ov-bridge/out/smoke_project_b_ov_direct_synthetic/
```

Public docs present:

```text
docs/public/compatibility_probe_plan.md
docs/public/dependency_compatibility.md
docs/public/environment.md
docs/public/external_repo_plan.md
docs/public/external_snapshot.md
docs/public/profiling.md
```

## Previous Steps That Appear Complete

- Step 1 public VTC skeleton and `gaze-ov-bridge` package skeleton.
- Local guidance docs committed separately.
- Dependency compatibility audit plan.
- Linux-first uv bridge-core environment.
- Profiling schema and pure-Python profiling utilities.
- Project A pure-Python codec-compatible selector utilities.
- Project A synthetic smoke script with profile/stat artifacts.
- Project B pure-Python OV-direct utilities.
- Project B synthetic smoke script with profile/stat artifacts.
- External source repository plan.
- Source-only external snapshot for AutoGaze, LLaVA-OneVision-2, lmms-eval, and LLaVA-OV2 HF custom code.
- Isolated compatibility probe scaffolding for AutoGaze, OV-Encoder, LLaVA-OV2, lmms-eval, and optional MPS.

## Missing Or Incomplete Previous Work

- No model weights have been downloaded. This is intentional so far.
- No heavy model environment has been synced or locked yet.
- Isolated model env import probes have not been run in synced model environments.
- `external/OneVision-Encoder` is not present as a separate snapshot. Current source inspection relies on the OneVision-Encoder custom code inside `external/LLaVA-OneVision-2`.
- Hugging Face auth/access state is not verified.
- `HF_HOME` and `HF_HUB_CACHE` were not set in the shell used for `check_linux_env.py`.
- `ffmpeg` is not installed or not on PATH in the current local environment.
- `hf` CLI and `git-lfs` were previously unavailable during source snapshot work.
- The official target remains Linux, but current checks were run on macOS arm64.

## Lightweight Checks

### Passing Checks

Command:

```bash
cd envs/bridge-core && uv run pytest ../../projects/gaze-ov-bridge/tests
```

Result:

```text
35 passed in 0.52s
```

Command:

```bash
cd envs/bridge-core && uv run python -m compileall ../../projects/gaze-ov-bridge/src
```

Result:

```text
Listing '../../projects/gaze-ov-bridge/src'...
Listing '../../projects/gaze-ov-bridge/src/gaze_ov_bridge'...
Listing '../../projects/gaze-ov-bridge/src/gaze_ov_bridge.egg-info'...
```

Command:

```bash
bash -n scripts/*.sh
```

Result: exit code 0.

Fallback command:

```bash
./envs/bridge-core/.venv/bin/python -m py_compile scripts/*.py
```

Result: exit code 0.

Escalated rerun after sandbox uv-cache failure:

```bash
cd envs/bridge-core && uv run python ../../scripts/check_linux_env.py
```

Result:

```text
Python version: 3.11.15
platform: macOS-26.4.1-arm64-arm-64bit
machine: arm64
HF_HOME: not set
HF_HUB_CACHE: not set
uv: uv 0.10.10
git: git version 2.39.5 (Apple Git-154)
ffmpeg: not found
numpy import status: importable (2.4.6)
PIL import status: importable (12.2.0)
pytest import status: importable (9.0.3)
torch import status: not importable: ModuleNotFoundError: No module named 'torch'
transformers import status: not importable: ModuleNotFoundError: No module named 'transformers'
flash_attn import status: not importable: ModuleNotFoundError: No module named 'flash_attn'
decord import status: not importable: ModuleNotFoundError: No module named 'decord'
opencv import status: not importable: ModuleNotFoundError: No module named 'cv2'
Level 1 status: ok
```

### Reproduced Failing Commands

Command:

```bash
cd envs/bridge-core && uv run python ../../scripts/check_linux_env.py
```

Failure snippet in sandbox:

```text
error: Failed to initialize cache at `/Users/mrc/.cache/uv`
  Caused by: failed to open file `/Users/mrc/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
```

Command:

```bash
python -m py_compile scripts/*.py
```

Failure snippet:

```text
zsh:1: command not found: python
```

Command:

```bash
python3 -m py_compile scripts/*.py
```

Failure snippet:

```text
Python 3.9.6
PermissionError: [Errno 1] Operation not permitted: '/Users/mrc/Library/Caches/com.apple.python/Users/mrc/Documents/VTC'
```

## Blocker Register

### B01: HF cache environment is unset

- Classification: `unknown`
- Severity: critical: prevents downloads or core tests
- Evidence: `check_linux_env.py` reported `HF_HOME: not set` and `HF_HUB_CACHE: not set`.
- Impact: Any later HF command could place cache/download material outside `weights/`, violating repository policy.
- Proposed fix: source `scripts/env_weights.sh` before any HF access or download-enabled workflow.
- Requires user HF token: no
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: no

### B02: Hugging Face authentication and gated repo access are unverified

- Classification: `hf_auth_required`, `hf_gated_repo`
- Severity: critical: prevents downloads or core tests
- Evidence: No HF auth/access probe has been run. Weight download remains deferred. HF custom code was collected source-only via git sparse checkout.
- Impact: LLaVA-OV2 and OneVision-Encoder weights may require user token, license acceptance, or gated repo approval.
- Proposed fix: before downloads, run an auth-only/access-only probe that does not download weights. Confirm token, repo visibility, and license state for all required HF repos.
- Requires user HF token: likely yes
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: maybe a small public/auth probe script later

### B03: `ffmpeg` is missing locally

- Classification: `dependency_resolution_failure`
- Severity: high: prevents Project A/LLaVA path
- Evidence: `check_linux_env.py` reported `ffmpeg: not found`.
- Impact: LLaVA-OV2 codec/video preprocessing and later `codec-video-prep` workflows likely need system `ffmpeg`.
- Proposed fix: install system `ffmpeg` on the Linux target before codec/backend tests. On macOS this is only optional local diagnostic support.
- Requires user HF token: no
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: no

### B04: `flash_attn` and CUDA requirements are unresolved

- Classification: `flash_attn_blocker`, `torch_cuda_blocker`
- Severity: high: prevents Project A/LLaVA path
- Evidence: AutoGaze metadata declares `flash_attn`; `lmms-eval` LLaVA-OV2 adapter defaults to `attn_implementation="flash_attention_2"`; local bridge-core correctly does not install `torch` or `flash_attn`.
- Impact: AutoGaze actual generation and LLaVA/lmms paths may require Linux/CUDA unless SDPA/eager fallback is confirmed.
- Proposed fix: run isolated import probes in `envs/autogaze`, `envs/llava-ov2`, `envs/ov-encoder`, and `envs/lmms-eval` after lightweight dependency sync decisions. Do not patch around `flash_attn` until source/import probes identify whether it is mandatory.
- Requires user HF token: no
- Requires external repo clone: no, current source exists
- Requires weight download: no for import probes
- Requires CUDA machine: only if `flash_attn` proves mandatory
- Requires MPS optional test: optional
- Requires code change: maybe later, depending on fallback path

### B05: Heavy model envs are not synced or locked

- Classification: `dependency_resolution_failure`
- Severity: high: prevents Project A/LLaVA path and high: prevents Project B/OV path
- Evidence: `envs/autogaze`, `envs/ov-encoder`, `envs/llava-ov2`, `envs/lmms-eval`, and `envs/mps-probe` contain pyproject scaffolding but no lock files or synced envs.
- Impact: Real AutoGaze, OV-Encoder, LLaVA-OV2, and lmms-eval import/runtime status is unknown.
- Proposed fix: lock/sync each env separately, starting with no-download import probes. Keep `bridge-core` isolated.
- Requires user HF token: no for dependency resolution
- Requires external repo clone: no, except deferred standalone OV source if needed
- Requires weight download: no
- Requires CUDA machine: maybe for AutoGaze/flash_attn env
- Requires MPS optional test: only for `envs/mps-probe`
- Requires code change: no

### B06: Standalone OneVision-Encoder source snapshot is missing

- Classification: `source_repo_missing`
- Severity: high: prevents Project B/OV path if the bundled LLaVA source is insufficient
- Evidence: `external/OneVision-Encoder` is absent. `docs/public/external_snapshot.md` records this as deferred because `external/LLaVA-OneVision-2/transformers_impl/onevision_encoder/` exists.
- Impact: Project B direct integration may need a distinct authoritative OneVision-Encoder source or HF custom-code snapshot.
- Proposed fix: decide whether bundled `transformers_impl/onevision_encoder` is authoritative enough. If not, identify and snapshot the separate OneVision-Encoder source/custom code without weights.
- Requires user HF token: maybe
- Requires external repo clone: maybe
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: no

### B07: LLaVA-OV2 processor/custom-code import has not been proven

- Classification: `processor_import_blocker`
- Severity: high: prevents Project A/LLaVA path
- Evidence: HF custom-code source exists, but `transformers>=5.7.0`, `torch`, `codec-video-prep`, OpenCV, and codec processor imports have not been tested in `envs/llava-ov2`.
- Impact: Project A real backend path cannot proceed until processor/backend imports and attention fallback behavior are verified.
- Proposed fix: run `scripts/probe_llava_ov2_env.py` in an isolated, synced `envs/llava-ov2` environment without weights.
- Requires user HF token: no for local custom-code import
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: maybe, depending on `flash_attn`
- Requires MPS optional test: optional
- Requires code change: maybe later if import path needs adjustment

### B08: lmms-eval path is isolated but not runnable yet

- Classification: `lmms_eval_blocker`
- Severity: high: prevents Project A/LLaVA path for later benchmark
- Evidence: `envs/lmms-eval` exists but is not synced. Source audit shows broad dependencies and LLaVA-OV2 adapter defaulting to `flash_attention_2`.
- Impact: Later answer-level benchmark path cannot proceed until dependency resolution, adapter import, and profiling hook plan are verified.
- Proposed fix: keep isolated, run no-weight import probe first, then decide whether to override `attn_implementation` or patch adapter behavior in a separate public code change.
- Requires user HF token: not for import probe, yes later for model weights
- Requires external repo clone: no, source exists
- Requires weight download: no for import probe
- Requires CUDA machine: maybe if adapter remains flash-attention-only
- Requires MPS optional test: optional
- Requires code change: likely later for profiling hooks

### B09: Root `python` command is missing

- Classification: `script_failure`
- Severity: low: docs or cleanup
- Evidence: `python -m py_compile scripts/*.py` failed with `zsh:1: command not found: python`.
- Impact: Commands written with bare `python` fail on this macOS host, although project Python 3.11 exists under `envs/bridge-core/.venv/bin/python`.
- Proposed fix: prefer `uv run python` from a configured env or document `python3`/project-python fallback for local macOS diagnostics.
- Requires user HF token: no
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: docs/script cleanup only if desired

### B10: Apple `python3` py_compile writes to a blocked cache path

- Classification: `script_failure`
- Severity: low: docs or cleanup
- Evidence: `python3 -m py_compile scripts/*.py` failed with `PermissionError` under `/Users/mrc/Library/Caches/com.apple.python/...`.
- Impact: The failure is local cache/sandbox behavior, not a syntax failure. The same scripts compiled with project Python 3.11.
- Proposed fix: use project Python, set `PYTHONPYCACHEPREFIX` to a writable path, or run under `uv`.
- Requires user HF token: no
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: no

### B11: uv cache access can fail inside the managed sandbox

- Classification: `script_failure`
- Severity: low: docs or cleanup
- Evidence: sandboxed `uv run python ../../scripts/check_linux_env.py` failed opening `/Users/mrc/.cache/uv/sdists-v9/.git`; escalated rerun passed.
- Impact: Some `uv run` commands can fail in this managed environment even when the env itself is valid.
- Proposed fix: use an approved/escalated uv command, configure `UV_CACHE_DIR` to a writable path such as `/private/tmp/vtc-uv-cache`, or use the existing env interpreter for pure syntax checks.
- Requires user HF token: no
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: no
- Requires code change: maybe docs/script cleanup

### B12: MPS is optional and not validated for model paths

- Classification: `mps_optional_blocker`
- Severity: low: docs or cleanup
- Evidence: `check_linux_env.py` reports `torch` not importable in bridge-core, as intended. No MPS model env has been synced or probed.
- Impact: MPS cannot be claimed for AutoGaze, OV-Encoder, LLaVA-OV2, or lmms-eval. This does not block Linux.
- Proposed fix: run `envs/mps-probe` only after choosing a minimal torch install. Treat failures as non-official diagnostics.
- Requires user HF token: no
- Requires external repo clone: no
- Requires weight download: no
- Requires CUDA machine: no
- Requires MPS optional test: yes
- Requires code change: no

### Non-Blockers Confirmed

- Classification: `test_failure`
- Status: no active blocker. Bridge-core tests passed: 35/35.

- Classification: `profiling_schema_blocker`
- Status: no active blocker. Existing profiling tests passed, and smoke outputs exist under ignored `projects/gaze-ov-bridge/out/`.

## Recommended Execution Order

1. Source `scripts/env_weights.sh` and rerun `check_linux_env.py` so HF cache paths are proven before any download-capable command.
2. Verify HF auth/access without downloading weights.
3. Install or confirm system `ffmpeg` on the Linux target before codec/video backend tests.
4. Run isolated no-weight dependency lock/import probes, one env at a time: `llava-ov2`, `ov-encoder`, `autogaze`, `lmms-eval`, then optional `mps-probe`.
5. Resolve `flash_attn`/attention fallback decisions from probe evidence.
6. Decide whether the bundled OneVision-Encoder source is sufficient or whether `external/OneVision-Encoder` must be snapshot separately.
7. Only after the above, plan HF weight downloads under `weights/`.
