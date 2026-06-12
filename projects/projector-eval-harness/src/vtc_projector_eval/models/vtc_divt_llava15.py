"""lmms-eval model wrapper for DiVT LLaVA-1.5 checkpoints."""

from __future__ import annotations

import os
from time import perf_counter

from lmms_eval.models.simple.llava import Llava

from vtc_projector_eval.runtime_profile import record_generation_profiles


def _set_divt_threshold(model: object, threshold: float) -> None:
    if hasattr(model, "threshold"):
        setattr(model, "threshold", threshold)
    config = getattr(model, "config", None)
    if config is not None:
        setattr(config, "threshold", threshold)
    get_model = getattr(model, "get_model", None)
    if callable(get_model):
        inner = get_model()
        projector = getattr(inner, "mm_projector", None)
        if projector is not None and hasattr(projector, "threshold"):
            setattr(projector, "threshold", threshold)


class DiVTLlava15(Llava):
    """Load a DiVT LLaVA fork/checkpoint and set inference threshold explicitly."""

    def __init__(self, divt_threshold: float = 0.65, **kwargs) -> None:
        self.divt_threshold = float(divt_threshold)
        super().__init__(**kwargs)
        _set_divt_threshold(self.model, self.divt_threshold)
        self.vtc_projector_profile = {
            "model": "vtc_divt_llava15",
            "divt_threshold": self.divt_threshold,
        }

    def generate_until(self, requests):
        start = perf_counter()
        outputs = super().generate_until(requests)
        elapsed = perf_counter() - start
        record_generation_profiles(
            path=os.environ.get("VTC_PROJECTOR_PROFILE_JSONL"),
            model="vtc_divt_llava15",
            policy_name=f"divt_threshold_{self.divt_threshold}",
            requests=list(requests),
            outputs=list(outputs),
            total_time_s=elapsed,
            token_counts={"llm_visual_tokens": None},
        )
        return outputs
