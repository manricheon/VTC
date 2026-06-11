#!/usr/bin/env python3
"""Import-only compatibility probe for the isolated AutoGaze environment."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path


ENV_NAME = "autogaze"
TRACK = "compat_probe"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_ready(value):
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


def dist_version(name: str) -> dict:
    try:
        return {"installed": True, "version": importlib.metadata.version(name)}
    except importlib.metadata.PackageNotFoundError:
        return {"installed": False, "version": None}
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"installed": False, "version": None, "error": repr(exc)}


def import_check(module: str) -> dict:
    try:
        importlib.import_module(module)
        return {"importable": True, "error": None}
    except Exception as exc:
        return {"importable": False, "error": f"{type(exc).__name__}: {exc}"}


def command_check(command: str) -> dict:
    path = shutil.which(command)
    if path is None:
        return {"available": False, "path": None, "version": None}
    try:
        proc = subprocess.run(
            [command, "-version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = (proc.stdout or proc.stderr).splitlines()[0] if (proc.stdout or proc.stderr) else None
    except Exception as exc:  # pragma: no cover - diagnostic path
        first_line = f"{type(exc).__name__}: {exc}"
    return {"available": True, "path": path, "version": first_line}


def process_peak_rss_mb() -> float | None:
    try:
        import resource

        raw = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except Exception:
        return None
    if platform.system() == "Darwin":
        return raw / (1024.0 * 1024.0)
    return raw / 1024.0


def profiling_capability() -> dict:
    tracemalloc.start()
    _sample = [idx for idx in range(128)]
    current, peak = tracemalloc.get_traced_memory()
    del _sample
    tracemalloc.stop()

    torch_info = {
        "torch_importable": False,
        "torch_version": None,
        "cuda_available": None,
        "cuda_peak_allocated_mb": None,
        "cuda_peak_reserved_mb": None,
        "mps_available": None,
        "mps_current_allocated_mb": None,
        "error": None,
    }
    if importlib.util.find_spec("torch") is not None:
        try:
            import torch

            torch_info["torch_importable"] = True
            torch_info["torch_version"] = getattr(torch, "__version__", None)
            cuda_available = bool(torch.cuda.is_available()) if hasattr(torch, "cuda") else False
            torch_info["cuda_available"] = cuda_available
            if cuda_available:
                torch_info["cuda_peak_allocated_mb"] = torch.cuda.max_memory_allocated() / (1024.0 * 1024.0)
                torch_info["cuda_peak_reserved_mb"] = torch.cuda.max_memory_reserved() / (1024.0 * 1024.0)
            mps_backend = getattr(getattr(torch, "backends", None), "mps", None)
            mps_available = bool(mps_backend.is_available()) if mps_backend is not None else False
            torch_info["mps_available"] = mps_available
            mps_module = getattr(torch, "mps", None)
            if mps_available and mps_module is not None and hasattr(mps_module, "current_allocated_memory"):
                torch_info["mps_current_allocated_mb"] = mps_module.current_allocated_memory() / (1024.0 * 1024.0)
        except Exception as exc:
            torch_info["error"] = f"{type(exc).__name__}: {exc}"

    return {
        "process_rss_available": process_peak_rss_mb() is not None,
        "tracemalloc_available": True,
        "torch_memory_available": torch_info["torch_importable"],
        "memory_mb": {
            "process_peak_rss": process_peak_rss_mb(),
            "tracemalloc_peak": peak / (1024.0 * 1024.0),
            "cuda_peak_allocated": torch_info["cuda_peak_allocated_mb"],
            "cuda_peak_reserved": torch_info["cuda_peak_reserved_mb"],
            "mps_current_allocated": torch_info["mps_current_allocated_mb"],
        },
        "torch": torch_info,
    }


def source_findings(root: Path) -> dict:
    source_root = root / "external" / "AutoGaze"
    files = {
        "pyproject": source_root / "pyproject.toml",
        "quick_start": source_root / "QUICK_START.md",
        "readme": source_root / "README.md",
    }
    terms = [
        "flash_attn",
        "flash-attn",
        "flash_attention",
        "flash_attention_2",
        "attn_implementation",
        "sdpa",
        "eager",
        "transformers~=4.51",
        "gazing_pos",
        "if_padded_gazing",
    ]
    findings = {}
    for label, path in files.items():
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        findings[label] = {
            "path": str(path),
            "exists": path.exists(),
            "terms": {term: term in text for term in terms},
        }
    return {
        "source_root": str(source_root),
        "source_root_exists": source_root.exists(),
        "files": findings,
        "classification": {
            "upstream_metadata_declares_flash_attn": findings["pyproject"]["terms"].get("flash_attn", False),
            "sdpa_mentioned": any(item["terms"].get("sdpa", False) for item in findings.values()),
            "eager_mentioned": any(item["terms"].get("eager", False) for item in findings.values()),
            "fallback_status": "probe_required",
        },
    }


def write_outputs(root: Path, result: dict) -> dict:
    compat_dir = root / "artifacts" / "compat"
    profile_dir = root / "artifacts" / "profiles"
    compat_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)
    compat_path = compat_dir / f"{ENV_NAME}_env.json"
    profile_path = profile_dir / f"compat_{ENV_NAME}.json"
    profile = {
        "schema_version": "compat-probe-1.0",
        "run_id": f"compat_{ENV_NAME}_{int(time.time())}",
        "created_at_utc": result["created_at_utc"],
        "project": {
            "project_name": "gaze-ov-bridge",
            "track": TRACK,
            "policy_name": ENV_NAME,
        },
        "environment": result["environment"],
        "memory_mb": result["profiling_capability"]["memory_mb"],
        "probe": result,
        "notes": [
            "Import-only probe.",
            "No weights downloaded and no model inference run.",
            "Missing flash_attn is documented unless a later source audit proves it is mandatory.",
        ],
    }
    compat_path.write_text(json.dumps(json_ready(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    profile_path.write_text(json.dumps(json_ready(profile), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"compat": str(compat_path), "profile": str(profile_path)}


def main() -> int:
    root = repo_root()
    source_root = root / "external" / "AutoGaze"
    if source_root.exists():
        sys.path.insert(0, str(source_root))

    imports = {
        "autogaze": import_check("autogaze"),
        "torch": import_check("torch"),
        "torchvision": import_check("torchvision"),
        "transformers": import_check("transformers"),
        "flash_attn": import_check("flash_attn"),
        "timm": import_check("timm"),
        "hydra": import_check("hydra"),
        "av": import_check("av"),
        "imageio": import_check("imageio"),
        "numpy": import_check("numpy"),
        "PIL": import_check("PIL"),
    }
    versions = {
        "torch": dist_version("torch"),
        "torchvision": dist_version("torchvision"),
        "transformers": dist_version("transformers"),
        "flash-attn": dist_version("flash-attn"),
        "timm": dist_version("timm"),
        "hydra-core": dist_version("hydra-core"),
        "av": dist_version("av"),
        "imageio": dist_version("imageio"),
        "numpy": dist_version("numpy"),
        "pillow": dist_version("Pillow"),
    }
    result = {
        "env_name": ENV_NAME,
        "created_at_utc": utc_now(),
        "environment": {
            "env_name": ENV_NAME,
            "platform": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "cwd": os.getcwd(),
            "vtc_root": str(root),
        },
        "versions": versions,
        "imports": imports,
        "commands": {"ffmpeg": command_check("ffmpeg")},
        "source_audit": source_findings(root),
        "attention_fallback": {
            "flash_attn_importable": imports["flash_attn"]["importable"],
            "sdpa_or_eager_source_mentions_found": None,
            "status": "linux_cuda_only_if_flash_attn_is_confirmed_mandatory",
        },
        "profiling_capability": profiling_capability(),
        "weights_downloaded": False,
        "model_inference_run": False,
    }
    result["attention_fallback"]["sdpa_or_eager_source_mentions_found"] = (
        result["source_audit"]["classification"]["sdpa_mentioned"]
        or result["source_audit"]["classification"]["eager_mentioned"]
    )
    paths = write_outputs(root, result)
    print(f"AutoGaze probe complete: flash_attn importable={imports['flash_attn']['importable']}")
    print(f"compat_json={paths['compat']}")
    print(f"profile_json={paths['profile']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

