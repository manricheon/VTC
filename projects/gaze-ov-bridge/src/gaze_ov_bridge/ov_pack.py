"""Metadata-only canvas slot planning for Project B OV-direct tokens."""

from __future__ import annotations


def build_ov_pack_plan(
    *,
    num_tokens: int,
    canvas_size: int = 224,
    patch_size: int = 14,
) -> dict[str, object]:
    """Assign OV-direct tokens to stable 224x224 canvas slots.

    Padding slots are reported as a count only. They are intentionally excluded
    from token metadata so one input token remains one metadata row.
    """

    if num_tokens < 0:
        raise ValueError("num_tokens must be non-negative")
    if canvas_size <= 0:
        raise ValueError("canvas_size must be positive")
    if patch_size <= 0:
        raise ValueError("patch_size must be positive")
    if canvas_size % patch_size != 0:
        raise ValueError("canvas_size must be divisible by patch_size")

    canvas_grid = canvas_size // patch_size
    slots_per_canvas = canvas_grid * canvas_grid
    num_canvases = 0 if num_tokens == 0 else (num_tokens + slots_per_canvas - 1) // slots_per_canvas
    total_slots = num_canvases * slots_per_canvas

    tokens: list[dict[str, int]] = []
    for token_idx in range(num_tokens):
        canvas_idx = token_idx // slots_per_canvas
        slot_idx = token_idx % slots_per_canvas
        tokens.append(
            {
                "token_idx": token_idx,
                "canvas_idx": canvas_idx,
                "slot_idx": slot_idx,
                "row": slot_idx // canvas_grid,
                "col": slot_idx % canvas_grid,
            }
        )

    return {
        "canvas_size": canvas_size,
        "patch_size": patch_size,
        "canvas_grid": canvas_grid,
        "slots_per_canvas": slots_per_canvas,
        "num_canvases": num_canvases,
        "total_slots": total_slots,
        "total_padding_slots": total_slots - num_tokens,
        "tokens": tokens,
    }
