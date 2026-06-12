"""lmms-eval plugin metadata.

`lmms_eval.models` imports this module when `LMMS_EVAL_PLUGINS=vtc_projector_eval`
is set. Keep it free of torch, transformers, and upstream model imports.
"""

AVAILABLE_MODELS = {
    "vtc_fourier_llava15": "FourierLlava15",
    "vtc_divt_llava15": "DiVTLlava15",
}
