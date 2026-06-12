from __future__ import annotations


def test_lmms_eval_plugin_metadata_is_lightweight():
    from vtc_projector_eval.models import AVAILABLE_MODELS

    assert AVAILABLE_MODELS == {
        "vtc_fourier_llava15": "FourierLlava15",
        "vtc_divt_llava15": "DiVTLlava15",
    }
