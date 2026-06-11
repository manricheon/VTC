"""Shared helpers for VTC compatibility probe scripts."""

from __future__ import annotations

import os
from pathlib import Path


PAYLOAD_PATTERNS = (
    "*.safetensors",
    "*.bin",
    "*.pt",
    "*.pth",
    "*.gguf",
    "*.onnx",
)


def directory_size_bytes(path: Path) -> int | None:
    if not path.exists():
        return None
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def weight_path_status(root: Path) -> dict:
    checkpoints = root / "weights" / "checkpoints"
    targets = {
        "autogaze": checkpoints / "AutoGaze",
        "ov_encoder": checkpoints / "onevision-encoder-large",
        "llava_ov2": checkpoints / "LLaVA-OneVision-2-8B-Instruct",
    }
    result = {}
    for name, path in targets.items():
        payload_files: list[str] = []
        if path.exists():
            for pattern in PAYLOAD_PATTERNS:
                payload_files.extend(str(item) for item in path.rglob(pattern))
        result[name] = {
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": directory_size_bytes(path),
            "payload_file_count": len(payload_files),
            "payload_files_sample": sorted(payload_files)[:10],
            "manifest_exists": (path / "VTC_DOWNLOAD_MANIFEST.json").exists(),
        }
    return result


def hf_cache_status(root: Path) -> dict:
    expected_hf_home = root / "weights" / "hf_home"
    expected_hf_hub_cache = expected_hf_home / "hub"
    hf_home = os.environ.get("HF_HOME")
    hf_hub_cache = os.environ.get("HF_HUB_CACHE")
    return {
        "HF_HOME": hf_home,
        "HF_HUB_CACHE": hf_hub_cache,
        "expected_HF_HOME": str(expected_hf_home),
        "expected_HF_HUB_CACHE": str(expected_hf_hub_cache),
        "HF_HOME_under_weights": hf_home is not None and Path(hf_home).resolve() == expected_hf_home.resolve(),
        "HF_HUB_CACHE_under_weights": hf_hub_cache is not None
        and Path(hf_hub_cache).resolve() == expected_hf_hub_cache.resolve(),
        "HF_HOME_exists": expected_hf_home.exists(),
        "HF_HUB_CACHE_exists": expected_hf_hub_cache.exists(),
    }


def source_path_status(root: Path) -> dict:
    paths = {
        "autogaze": root / "external" / "AutoGaze",
        "llava_ov2_github": root / "external" / "LLaVA-OneVision-2",
        "llava_ov2_hf_code": root / "external" / "LLaVA-OneVision-2-8B-Instruct-code",
        "onevision_encoder_hf_code": root / "external" / "OneVision-Encoder",
        "lmms_eval": root / "external" / "lmms-eval",
    }
    return {name: {"path": str(path), "exists": path.exists()} for name, path in paths.items()}
