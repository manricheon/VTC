#!/usr/bin/env python3
"""Import-only compatibility probe for the isolated LLaVA-OV2 environment."""

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


ENV_NAME = "llava_ov2"


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


def command_check(command: str) -> dict:
    path = shutil.which(command)
    if path is None:
        return {"available": False, "path": None, "version": None}
    try:
        proc = subprocess.run([command, "-version"], check=False, capture_output=True, text=True, timeout=5)
        first_line = (proc.stdout or proc.stderr).splitlines()[0] if (proc.stdout or proc.stderr) else None
    except Exception as exc:
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
    _sample = tuple(range(128))
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
    hf_code = root / "external" / "LLaVA-OneVision-2-8B-Instruct-code"
    github_code = root / "external" / "LLaVA-OneVision-2" / "transformers_impl" / "llavaonevision2"
    files = {
        "hf_modeling": hf_code / "modeling_llava_onevision2.py",
        "hf_codec_processing": hf_code / "codec_video_processing_llava_onevision2.py",
        "hf_video_processing": hf_code / "video_processing_llava_onevision2.py",
        "github_modeling": github_code / "modeling_llavaonevision2.py",
        "github_processing": github_code / "processing_llavaonevision2.py",
    }
    terms = [
        "flash_attn",
        "flash_attention",
        "flash_attention_2",
        "attn_implementation",
        "_supports_flash_attn",
        "_supports_sdpa",
        "sdpa",
        "eager",
        "ALL_ATTENTION_FUNCTIONS",
        "patch_positions",
        "image_grid_thw",
        "codec",
        "codec-video-prep",
        "src_patch_position",
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
        "hf_code_root": str(hf_code),
        "github_code_root": str(github_code),
        "files": findings,
        "classification": {
            "patch_positions_path_found": any(item["terms"].get("patch_positions", False) for item in findings.values()),
            "codec_processing_found": any(item["terms"].get("codec", False) for item in findings.values()),
            "supports_sdpa_declared": any(item["terms"].get("_supports_sdpa", False) for item in findings.values()),
            "supports_flash_attn_declared": any(item["terms"].get("_supports_flash_attn", False) for item in findings.values()),
            "eager_fallback_found": any(item["terms"].get("eager", False) for item in findings.values()),
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
            "track": "compat_probe",
            "policy_name": ENV_NAME,
        },
        "environment": result["environment"],
        "memory_mb": result["profiling_capability"]["memory_mb"],
        "probe": result,
        "notes": ["Import-only probe.", "No weights downloaded and no model inference run."],
    }
    compat_path.write_text(json.dumps(json_ready(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    profile_path.write_text(json.dumps(json_ready(profile), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"compat": str(compat_path), "profile": str(profile_path)}


def main() -> int:
    root = repo_root()
    hf_code = root / "external" / "LLaVA-OneVision-2-8B-Instruct-code"
    github_source = root / "external" / "LLaVA-OneVision-2"
    for path in (hf_code, github_source):
        if path.exists():
            sys.path.insert(0, str(path))
    imports = {
        "torch": import_check("torch"),
        "transformers": import_check("transformers"),
        "decord": import_check("decord"),
        "cv2": import_check("cv2"),
        "qwen_vl_utils": import_check("qwen_vl_utils"),
        "codec_video_prep": import_check("codec_video_prep"),
        "hf_configuration": import_check("configuration_llava_onevision2"),
        "hf_processing": import_check("processing_llava_onevision2"),
        "hf_modeling": import_check("modeling_llava_onevision2"),
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
        "versions": {
            "torch": dist_version("torch"),
            "transformers": dist_version("transformers"),
            "decord": dist_version("decord"),
            "codec-video-prep": dist_version("codec-video-prep"),
            "opencv-python": dist_version("opencv-python"),
            "opencv-python-headless": dist_version("opencv-python-headless"),
            "qwen-vl-utils": dist_version("qwen-vl-utils"),
            "numpy": dist_version("numpy"),
            "pillow": dist_version("Pillow"),
        },
        "imports": imports,
        "commands": {"ffmpeg": command_check("ffmpeg")},
        "source_audit": source_findings(root),
        "attention_fallback": {
            "supports_sdpa_declared": None,
            "eager_fallback_found": None,
            "status": "source_suggests_fallback_but_import_probe_must_confirm",
        },
        "profiling_capability": profiling_capability(),
        "weights_downloaded": False,
        "model_inference_run": False,
    }
    result["attention_fallback"]["supports_sdpa_declared"] = result["source_audit"]["classification"][
        "supports_sdpa_declared"
    ]
    result["attention_fallback"]["eager_fallback_found"] = result["source_audit"]["classification"][
        "eager_fallback_found"
    ]
    paths = write_outputs(root, result)
    print(
        "LLaVA-OV2 probe complete: "
        f"codec_processing={result['source_audit']['classification']['codec_processing_found']}"
    )
    print(f"compat_json={paths['compat']}")
    print(f"profile_json={paths['profile']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

