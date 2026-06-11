"""Stdlib-first process and optional accelerator memory probes."""

from __future__ import annotations

import importlib.util
import sys
import tracemalloc


MB = 1024 * 1024


MEMORY_KEYS = (
    "process_peak_rss",
    "tracemalloc_peak",
    "cuda_peak_allocated",
    "cuda_peak_reserved",
    "mps_current_allocated",
)


def _bytes_to_mb(value: int | float | None) -> float | None:
    if value is None:
        return None
    return float(value) / MB


def process_peak_rss_mb() -> float | None:
    try:
        import resource
    except ImportError:
        return None

    try:
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None

    if sys.platform == "darwin":
        return _bytes_to_mb(peak)
    return float(peak) / 1024.0


def tracemalloc_peak_mb(start_if_needed: bool = True) -> float | None:
    if not tracemalloc.is_tracing():
        if not start_if_needed:
            return None
        tracemalloc.start()

    try:
        _current, peak = tracemalloc.get_traced_memory()
    except RuntimeError:
        return None
    return _bytes_to_mb(peak)


def _optional_torch_memory_mb() -> dict[str, float | None]:
    result = {
        "cuda_peak_allocated": None,
        "cuda_peak_reserved": None,
        "mps_current_allocated": None,
    }

    if importlib.util.find_spec("torch") is None:
        return result

    try:
        import torch
    except Exception:  # noqa: BLE001 - optional diagnostic path.
        return result

    try:
        if torch.cuda.is_available():
            result["cuda_peak_allocated"] = _bytes_to_mb(torch.cuda.max_memory_allocated())
            result["cuda_peak_reserved"] = _bytes_to_mb(torch.cuda.max_memory_reserved())
    except Exception:  # noqa: BLE001 - optional diagnostic path.
        pass

    try:
        mps = getattr(torch, "mps", None)
        backends = getattr(torch, "backends", None)
        backend_mps = getattr(backends, "mps", None) if backends is not None else None
        if mps is not None and backend_mps is not None and backend_mps.is_available():
            current_allocated = getattr(mps, "current_allocated_memory", None)
            if callable(current_allocated):
                result["mps_current_allocated"] = _bytes_to_mb(current_allocated())
    except Exception:  # noqa: BLE001 - optional diagnostic path.
        pass

    return result


def collect_memory_mb(include_torch: bool = True) -> dict[str, float | None]:
    memory = {
        "process_peak_rss": process_peak_rss_mb(),
        "tracemalloc_peak": tracemalloc_peak_mb(),
        "cuda_peak_allocated": None,
        "cuda_peak_reserved": None,
        "mps_current_allocated": None,
    }

    if include_torch:
        memory.update(_optional_torch_memory_mb())

    return memory
