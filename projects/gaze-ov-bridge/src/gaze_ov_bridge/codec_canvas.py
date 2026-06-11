"""Codec-compatible canvas helpers for Project A."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

from .geometry import selected_blocks_to_src_positions


def build_src_positions(selected_blocks: Iterable[Sequence[int]]) -> np.ndarray:
    return selected_blocks_to_src_positions(selected_blocks)
