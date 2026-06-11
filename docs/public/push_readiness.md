# Push Readiness Report

Date: 2026-06-12

## Target

- Repository: `git@github.com:manricheon/VTC.git`
- Branch to push: `feature/gaze-ov-bridge-local`
- Main handling: `main` was not pushed, not created, and not checked out.

## Current State

- Current branch: `feature/gaze-ov-bridge-local`
- Latest commit checked: `b8921cd`
- Remote URL: `git@github.com:manricheon/VTC.git`
- Dirty state: clean after the `.gitignore` hygiene commit.

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

Status: blocked by SSH authentication or repository access. The current session cannot verify whether `main` exists or push the feature branch through the configured SSH remote.

## Dangerous Tracked File Check

Equivalent corrected tracked-file scan was used because the originally requested grep pattern contains an empty alternation that this host's `grep` rejects.

Result: blocked. These tracked placeholder files are under storage roots that the public push policy says must not be pushed:

```text
artifacts/.gitkeep
artifacts/profiles/.gitkeep
external/.gitkeep
weights/.gitkeep
```

Recommended fix: remove these placeholders from Git tracking in a separate cleanup commit, or explicitly approve keeping zero-byte placeholders despite the strict storage-root rule.

## Large File Check

Command scanned files larger than 50 MB outside `.git`, `weights`, `external`, `artifacts`, project `out`, and root `.venv`.

Result: blocked by untracked virtualenv payloads present in the working directory:

```text
./envs/llava-ov2/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
./envs/ov-encoder/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
./envs/lmms-eval/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
./envs/lmms-eval/.venv/lib/python3.11/site-packages/pycocoevalcap/meteor/data/paraphrase-en.gz
./envs/autogaze/.venv/lib/python3.11/site-packages/torch/lib/libtorch_cpu.dylib
```

These files are not staged or tracked, but the requested large-file gate lists them. Recommended fix: delete local model-env `.venv` directories after confirming they can be regenerated, or rerun the large-file gate with an explicit `envs/*/.venv` exclusion if that is the intended policy.

## Secret-like String Check

Result: manual review required. Matches are documentation and script references to token environment variable names, not observed token values. No token value was printed or recorded.

Matched areas:

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

Recommended fix: manually review these references before pushing a public repository. They appear to be safe instructions/status strings, but the requested push policy requires manual review for any match.

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

- `safe_to_push`: no
- Push blocked by:
  - SSH remote access failure.
  - Tracked `.gitkeep` placeholders under `artifacts/`, `external/`, and `weights/`.
  - Large untracked virtualenv payloads found by the requested large-file command.
  - Secret-like string matches that require manual review.

Exact push command once blockers are resolved:

```bash
git push -u origin feature/gaze-ov-bridge-local
```

Do not push `main`.
