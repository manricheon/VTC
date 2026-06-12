from __future__ import annotations

from pathlib import Path

from vtc_projector_eval.assets import PROJECTOR_ASSETS, asset_by_key


def test_projector_assets_capture_hf_repo_and_local_checkpoint_paths():
    fourier = asset_by_key("fourier")
    divt = asset_by_key("divt")

    assert fourier["hf_repo"] == "whyisverysmart/Fourier-LLaVA-v1.5-7B-144"
    assert fourier["local_path"] == Path("weights/checkpoints/Fourier-LLaVA-v1.5-7B-144")
    assert fourier["visual_tokens"] == 144
    assert fourier["runtime_knob"] == "FOURIER_RESERVE=12"

    assert divt["hf_repo"] == "hyunlee86/llava-v1.5-7b-divt-0.65"
    assert divt["local_path"] == Path("weights/checkpoints/llava-v1.5-7b-divt-0.65")
    assert divt["visual_tokens"] == 74.1
    assert divt["runtime_knob"] == "DIVT_THRESHOLD=0.65"


def test_projector_assets_keep_stable_keys():
    assert [asset["key"] for asset in PROJECTOR_ASSETS] == ["fourier", "divt"]
