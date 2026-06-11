#!/usr/bin/env python3
"""Print VTC Hugging Face download plan without downloading files."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = repo_root()
    print("VTC Hugging Face download plan")
    print()
    print("No files are downloaded by this script.")
    print()
    print("Cache policy:")
    print(f"  HF_HOME={root / 'weights' / 'hf_home'}")
    print(f"  HF_HUB_CACHE={root / 'weights' / 'hf_home' / 'hub'}")
    print()
    print("Candidate repos:")
    print("  AutoGaze candidates, verify from external/AutoGaze docs before use:")
    print("    1. nvidia/AutoGaze")
    print("    2. bfshi/AutoGaze")
    print("  OneVision-Encoder:")
    print("    lmms-lab-encoder/onevision-encoder-large")
    print("  LLaVA-OV2:")
    print("    lmms-lab-encoder/LLaVA-OneVision-2-8B-Instruct")
    print()
    print("Expected local directories:")
    print(f"  AutoGaze weights: {root / 'weights' / 'checkpoints' / 'AutoGaze'}")
    print(f"  OV-Encoder weights: {root / 'weights' / 'checkpoints' / 'onevision-encoder-large'}")
    print(
        "  LLaVA-OV2 weights: "
        f"{root / 'weights' / 'checkpoints' / 'LLaVA-OneVision-2-8B-Instruct'}"
    )
    print(
        "  LLaVA-OV2 code-only snapshot: "
        f"{root / 'external' / 'LLaVA-OneVision-2-8B-Instruct-code'}"
    )
    print()
    print("Weight downloads require VTC_ALLOW_WEIGHT_DOWNLOAD=1 plus a target flag.")
    print("Example:")
    print("  VTC_ALLOW_WEIGHT_DOWNLOAD=1 VTC_DOWNLOAD_OV_ENCODER=1 bash scripts/hf_download_weights.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

