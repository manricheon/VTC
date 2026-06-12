"""Expected checkpoint assets for projector eval runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


FOURIER_ASSET = {
    "key": "fourier",
    "label": "Fourier-LLaVA-v1.5-7B-144",
    "hf_repo": "whyisverysmart/Fourier-LLaVA-v1.5-7B-144",
    "local_path": Path("weights/checkpoints/Fourier-LLaVA-v1.5-7B-144"),
    "base_model": "LLaVA-v1.5-7B",
    "visual_tokens": 144,
    "runtime_knob": "FOURIER_RESERVE=12",
    "notes": "Paper checkpoint; wrapper still applies Fourier's LLaVA runtime patch.",
}

DIVT_ASSET = {
    "key": "divt",
    "label": "DiVT0.65",
    "hf_repo": "hyunlee86/llava-v1.5-7b-divt-0.65",
    "local_path": Path("weights/checkpoints/llava-v1.5-7b-divt-0.65"),
    "base_model": "LLaVA-v1.5-7B",
    "visual_tokens": 74.1,
    "runtime_knob": "DIVT_THRESHOLD=0.65",
    "notes": "Official DiVT 0.65 checkpoint.",
}

PROJECTOR_ASSETS = [FOURIER_ASSET, DIVT_ASSET]


def asset_by_key(key: str) -> dict[str, Any]:
    for asset in PROJECTOR_ASSETS:
        if asset["key"] == key:
            return dict(asset)
    raise KeyError(f"unknown projector asset key: {key}")
