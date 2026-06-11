# Model Environment Lockfile Status

Status date: `2026-06-11T14:11:43Z`

Branch: `feature/gaze-ov-bridge-local`

Base commit inspected: `5a8c24a`

This check resolves the dirty working tree caused by untracked model-environment `uv.lock` files. No weights were downloaded, no external repositories were cloned, no model inference was run, and no files under `external/`, `weights/`, `artifacts/`, or `projects/gaze-ov-bridge/out/` were staged.

## Decision

Commit the five model environment lockfiles as public reproducibility artifacts:

- `envs/autogaze/uv.lock`
- `envs/llava-ov2/uv.lock`
- `envs/lmms-eval/uv.lock`
- `envs/mps-probe/uv.lock`
- `envs/ov-encoder/uv.lock`

Reason:

- Each lockfile has a matching `pyproject.toml`.
- Each lockfile has a matching `.python-version`.
- Each lockfile is valid TOML.
- `uv lock --check` exits successfully for each environment.
- No secrets or tokens were found.
- No absolute local paths such as `/Users/...` or `/home/...` were found.

The `lmms-eval` lockfile contains the expected relative editable source path `../../external/lmms-eval`, matching `envs/lmms-eval/pyproject.toml`. This is not an absolute local path, but it means the lock is only usable after the source-only external repo is present.

## Lockfile Table

| Lockfile | Size | Matching `pyproject.toml` | Matching `.python-version` | Valid TOML | Secret scan | Local absolute path scan | Project path scan | `uv lock --check` | Decision | Reason |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `envs/autogaze/uv.lock` | 351K | yes | yes | yes | clean | clean | clean | pass, resolved 78 packages | committed | Reproducible AutoGaze env lock; generated metadata only. |
| `envs/llava-ov2/uv.lock` | 211K | yes | yes | yes | clean | clean | clean | pass, resolved 65 packages | committed | Reproducible LLaVA-OV2 env lock; generated metadata only. |
| `envs/lmms-eval/uv.lock` | 755K | yes | yes | yes | clean | clean | expected relative `../../external/lmms-eval` | pass, resolved 159 packages | committed | Reproducible lmms-eval env lock; depends on source-only external checkout. |
| `envs/mps-probe/uv.lock` | 104K | yes | yes | yes | clean | clean | clean | pass, resolved 32 packages | committed | Optional Mac/MPS probe lock; not official support. |
| `envs/ov-encoder/uv.lock` | 212K | yes | yes | yes | clean | clean | clean | pass, resolved 49 packages | committed | Reproducible OV-Encoder env lock; generated metadata only. |

## Commands Run

Status:

```bash
git status --short
ls -lh envs/*/uv.lock
```

Metadata presence:

```bash
for d in envs/autogaze envs/llava-ov2 envs/lmms-eval envs/mps-probe envs/ov-encoder; do
  test -f "$d/pyproject.toml"
  test -f "$d/.python-version"
done
```

Secret and path scan:

```bash
grep -R "HF_TOKEN\|token\|/Users/\|/home/\|weights/\|external/" envs/*/uv.lock || true
```

The broad grep reports package names such as `tokenizers` and the expected relative `../../external/lmms-eval` source path. A tighter scan found:

- secret terms: 0
- absolute local paths: 0
- project storage paths: only `../../external/lmms-eval` in `envs/lmms-eval/uv.lock`

TOML validation:

```bash
cd envs/bridge-core
UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv run python - <<'PY'
from pathlib import Path
import tomllib

for p in sorted(Path("../..").glob("envs/*/uv.lock")):
    tomllib.loads(p.read_text())
    print(f"OK TOML: {p}")
PY
cd ../..
```

Lock check:

```bash
for d in envs/autogaze envs/llava-ov2 envs/lmms-eval envs/mps-probe envs/ov-encoder; do
  (cd "$d" && UV_CACHE_DIR=/private/tmp/vtc-uv-cache uv lock --check) || true
done
```

## Portability Notes

Linux remains the official target. These lockfiles are useful public reproducibility artifacts, but model-specific runtime readiness is still not proven:

- Heavy model environments still need isolated `uv sync` and import probes.
- `ffmpeg` must be installed and verified on Linux before codec/backend tests.
- `flash_attn`, CUDA, and SDPA/eager fallback behavior remain runtime blockers until probed.
- `envs/mps-probe` is best-effort only and does not establish official support.
- If Linux runtime probes require different pins, regenerate the relevant lockfile on the Linux target and update this document.
