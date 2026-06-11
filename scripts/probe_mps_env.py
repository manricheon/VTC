#!/usr/bin/env python3
"""Optional Mac/MPS import and profiling capability probe."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

from probe_common import hf_cache_status, source_path_status, weight_path_status


ENV_NAME = "mps_probe"


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
    except Exception as exc:
        return {"installed": False, "version": None, "error": repr(exc)}


def import_check(module: str) -> dict:
    try:
        importlib.import_module(module)
        return {"importable": True, "error": None}
    except Exception as exc:
        return {"importable": False, "error": f"{type(exc).__name__}: {exc}"}


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
    _sample = [idx * 2 for idx in range(128)]
    _, peak = tracemalloc.get_traced_memory()
    del _sample
    tracemalloc.stop()
    torch_info = {
        "torch_importable": False,
        "torch_version": None,
        "cuda_available": None,
        "cuda_peak_allocated_mb": None,
        "cuda_peak_reserved_mb": None,
        "mps_available": None,
        "mps_built": None,
        "mps_current_allocated_mb": None,
        "error": None,
    }
    if importlib.util.find_spec("torch") is not None:
        try:
            import torch

            torch_info["torch_importable"] = True
            torch_info["torch_version"] = getattr(torch, "__version__", None)
            torch_info["cuda_available"] = bool(torch.cuda.is_available()) if hasattr(torch, "cuda") else False
            if torch_info["cuda_available"]:
                torch_info["cuda_peak_allocated_mb"] = torch.cuda.max_memory_allocated() / (1024.0 * 1024.0)
                torch_info["cuda_peak_reserved_mb"] = torch.cuda.max_memory_reserved() / (1024.0 * 1024.0)
            mps_backend = getattr(getattr(torch, "backends", None), "mps", None)
            if mps_backend is not None:
                torch_info["mps_built"] = bool(mps_backend.is_built()) if hasattr(mps_backend, "is_built") else None
                torch_info["mps_available"] = bool(mps_backend.is_available())
            else:
                torch_info["mps_available"] = False
            mps_module = getattr(torch, "mps", None)
            if torch_info["mps_available"] and mps_module is not None and hasattr(mps_module, "current_allocated_memory"):
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


def write_outputs(root: Path, result: dict) -> dict:
    compat_dir = root / "artifacts" / "compat"
    profile_dir = root / "artifacts" / "profiles"
    compat_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)
    compat_path = compat_dir / f"{ENV_NAME}_probe.json"
    profile_path = profile_dir / f"compat_{ENV_NAME}.json"
    profile = {
        "schema_version": "compat-probe-1.0",
        "run_id": f"compat_{ENV_NAME}_{int(time.time())}",
        "created_at_utc": result["created_at_utc"],
        "project": {
            "project_name": "gaze-ov-bridge",
            "track": "compat_probe",
            "policy_name": ENV_NAME,
        },
        "environment": result["environment"],
        "memory_mb": result["profiling_capability"]["memory_mb"],
        "probe": result,
        "notes": [
            "Optional best-effort Mac/MPS probe.",
            "Linux remains the official target.",
            "No weights downloaded and no model inference run.",
        ],
    }
    compat_path.write_text(json.dumps(json_ready(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    profile_path.write_text(json.dumps(json_ready(profile), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"compat": str(compat_path), "profile": str(profile_path)}


def main() -> int:
    root = repo_root()
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
            "official_target": False,
        },
        "versions": {
            "torch": dist_version("torch"),
            "numpy": dist_version("numpy"),
            "pillow": dist_version("Pillow"),
        },
        "imports": {
            "torch": import_check("torch"),
            "numpy": import_check("numpy"),
            "PIL": import_check("PIL"),
        },
        "paths": {
            "hf_cache": hf_cache_status(root),
            "sources": source_path_status(root),
            "weights": weight_path_status(root),
        },
        "profiling_capability": profiling_capability(),
        "interpretation": {
            "mps_is_official_target": False,
            "failure_blocks_linux_target": False,
            "status": "best_effort_optional_probe",
        },
        "weights_downloaded": False,
        "model_inference_run": False,
    }
    paths = write_outputs(root, result)
    mps_available = result["profiling_capability"]["torch"]["mps_available"]
    print(f"MPS probe complete: platform={platform.system()} mps_available={mps_available}")
    print(f"compat_json={paths['compat']}")
    print(f"profile_json={paths['profile']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
