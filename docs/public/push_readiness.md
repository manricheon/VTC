# Push Readiness Report

Date: 2026-06-12

## Target

- Repository: `git@github.com:manricheon/VTC.git`
- Branch to push: `feature/gaze-ov-bridge-local`
- Main handling: `main` was not pushed, not created, and not checked out.

## Current State

- Current branch: `feature/gaze-ov-bridge-local`
- Latest commit checked: `874362c`
- Remote URL: `git@github.com:manricheon/VTC.git`
- Dirty state: clean after removing storage-root placeholders from Git tracking.

## Remote Check

Command:

```bash
git ls-remote --heads origin main
```

Result:

```text
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

Status before escalated push attempt: blocked by SSH authentication or repository access in the sandboxed check. The user requested retrying the push outside the sandbox.

## Dangerous Tracked File Check

Equivalent corrected tracked-file scan was used because the originally requested grep pattern contains an empty alternation that this host's `grep` rejects.

Result: passed after cleanup commit `874362c`.

The tracked placeholder files formerly under `artifacts/`, `external/`, and `weights/` were removed from Git tracking before push. The corrected tracked-file scan now returns no matches for:

- storage roots
- `out/`
- virtualenvs
- model files
- array dumps
- JSONL outputs
- `.env`
- cache paths

## Large File Check

Command scanned files larger than 50 MB outside `.git`, `weights`, `external`, `artifacts`, project `out`, and root `.venv`.

Result: local ignored files present, but not tracked or staged:

```text
./envs/llava-ov2/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
./envs/ov-encoder/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
./envs/lmms-eval/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
./envs/lmms-eval/.venv/lib/python3.11/site-packages/pycocoevalcap/meteor/data/paraphrase-en.gz
./envs/autogaze/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
```

These files are ignored by `.gitignore` via `.venv/`, are not tracked by Git, and will not be pushed. They should still be treated as local generated environment payloads.

## Secret-like String Check

Result: actual-secret scan passed.

The broad scan matched documentation and script references to token environment variable names, not observed token values. No token value was printed or recorded.

Broad-match areas reviewed:

- `docs/local/pre_worktree_blockers.md`
- `docs/local/simplicity_review.md`
- `docs/public/autogaze_repo_verification.md`
- `docs/public/blocker_resolution_status.md`
- `docs/public/external_snapshot.md`
- `docs/public/hf_access_status.md`
- `docs/public/hf_downloads.md`
- `docs/public/model_env_lock_status.md`
- `docs/public/troubleshooting.md`
- `docs/public/weights_snapshot.md`
- `scripts/check_hf_assets.sh`
- `scripts/hf_auth_check.py`
- `scripts/hf_download_snapshot.py`
- `scripts/setup_hf_assets.sh`
- `scripts/vtc_doctor.sh`

An additional narrower tracked-file scan for literal token-looking values and assigned secret values returned no matches.

## .gitignore Status

Updated in commit `b8921cd` to include the requested missing patterns:

- `.cache/`
- `*.bin`
- `*.gguf`
- `*.onnx`
- `*.jsonl`
- `.env`

Already covered:

- `weights/`
- `external/`
- `artifacts/`
- `projects/*/out/`
- `.venv/`
- `__pycache__/`
- `*.safetensors`
- `*.pt`
- `*.pth`
- `*.npy`
- `*.npz`

## Agent and Guidance Files

Status: included intentionally on `feature/gaze-ov-bridge-local`.

Tracked guidance files include:

```text
.agents/skills/karpathy-engineering/SKILL.md
.agents/skills/karpathy-engineering/references/refactor_checklist.md
.agents/skills/karpathy-engineering/references/review_checklist.md
.agents/skills/karpathy-engineering/references/simple_code_checklist.md
AGENTS.md
PROJECT_PLAN.md
projects/gaze-ov-bridge/AGENTS.md
projects/gaze-ov-bridge/PROJECT_PLAN.md
projects/gaze-ov-bridge/docs/local/.gitkeep
projects/gaze-ov-bridge/prompts/.gitkeep
```

`CLAUDE.md` is not currently tracked.

## Recommendation

- `safe_to_push`: yes, pending successful GitHub SSH authentication outside the sandbox.
- Push scope:
  - push only `feature/gaze-ov-bridge-local`
  - do not push `main`
  - do not push tags
  - do not push `weights/`, `external/`, `artifacts/`, or project `out/`

Exact push command:

```bash
git push -u origin feature/gaze-ov-bridge-local
```

Do not push `main`.
