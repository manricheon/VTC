"""lmms-eval model wrapper for Fourier-Compressor on LLaVA-1.5."""

from __future__ import annotations

import os
from time import perf_counter

from lmms_eval.models.simple.llava import Llava

from vtc_projector_eval.runtime_profile import record_generation_profiles


class FourierLlava15(Llava):
    """Apply Fourier-Compressor's LLaVA monkey patch before loading LLaVA."""

    def __init__(
        self,
        fourier_reserve: int = 12,
        fourier_norm: str | None = "ortho",
        **kwargs,
    ) -> None:
        from fourier_compressor.integrations.llava import apply_to_llava

        norm = None if fourier_norm in (None, "none", "None") else fourier_norm
        apply_to_llava(reserve=int(fourier_reserve), norm=norm)
        self.vtc_projector_profile = {
            "model": "vtc_fourier_llava15",
            "fourier_reserve": int(fourier_reserve),
            "fourier_norm": norm,
        }
        self.fourier_reserve = int(fourier_reserve)
        super().__init__(**kwargs)

    def generate_until(self, requests):
        start = perf_counter()
        outputs = super().generate_until(requests)
        elapsed = perf_counter() - start
        record_generation_profiles(
            path=os.environ.get("VTC_PROJECTOR_PROFILE_JSONL"),
            model="vtc_fourier_llava15",
            policy_name=f"fourier_reserve_{self.fourier_reserve}",
            requests=list(requests),
            outputs=list(outputs),
            total_time_s=elapsed,
            token_counts={"llm_visual_tokens": self.fourier_reserve * self.fourier_reserve},
        )
        return outputs
