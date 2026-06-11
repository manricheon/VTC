"""Select LLaVA-OV2-compatible 112-anchor blocks from decoded AutoGaze entries."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .geometry import Block112, normalize_selected_blocks, scale_token_to_112_blocks
from .stats import build_project_a_stats


def _entry_int(entry: Mapping[str, Any], key: str) -> int:
    return int(entry[key])


def _evidence_record(
    entry: Mapping[str, Any],
    *,
    r112: int | None = None,
    c112: int | None = None,
    covered_112_blocks: list[tuple[int, int]] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "frame_idx": _entry_int(entry, "frame_idx"),
        "scale": _entry_int(entry, "scale"),
        "row": _entry_int(entry, "row"),
        "col": _entry_int(entry, "col"),
    }
    if r112 is not None and c112 is not None:
        record.update({"r112": int(r112), "c112": int(c112)})
    if covered_112_blocks is not None:
        record["covered_112_blocks"] = [(int(r), int(c)) for r, c in covered_112_blocks]
    return record


def select_112_anchor_blocks(
    decoded_entries: list[Mapping[str, Any]],
    *,
    hard_union: bool = False,
    num_frames: int | None = None,
) -> dict[str, Any]:
    selected_candidates: list[Block112] = []
    fine_votes: list[dict[str, Any]] = []
    region_priors_56: list[dict[str, Any]] = []
    frame_priors_28: list[dict[str, Any]] = []

    for entry in decoded_entries:
        frame_idx = _entry_int(entry, "frame_idx")
        scale = _entry_int(entry, "scale")
        row = _entry_int(entry, "row")
        col = _entry_int(entry, "col")

        covered = scale_token_to_112_blocks(scale, row, col)
        if scale == 112:
            r112, c112 = covered[0]
            selected_candidates.append((frame_idx, r112, c112))
        elif scale == 224:
            r112, c112 = covered[0]
            fine_votes.append(_evidence_record(entry, r112=r112, c112=c112))
            selected_candidates.append((frame_idx, r112, c112))
        elif scale == 56:
            region_priors_56.append(_evidence_record(entry, covered_112_blocks=covered))
            if hard_union:
                selected_candidates.extend((frame_idx, r112, c112) for r112, c112 in covered)
        elif scale == 28:
            frame_priors_28.append(_evidence_record(entry, covered_112_blocks=covered))
            if hard_union:
                selected_candidates.extend((frame_idx, r112, c112) for r112, c112 in covered)
        else:
            raise ValueError(f"unsupported decoded AutoGaze scale: {scale}")

    selected_blocks = normalize_selected_blocks(selected_candidates)
    duplicate_count = sum(count - 1 for count in Counter(selected_candidates).values() if count > 1)
    inferred_num_frames = num_frames
    if inferred_num_frames is None:
        max_frame = max((int(entry["frame_idx"]) for entry in decoded_entries), default=-1)
        inferred_num_frames = max_frame + 1

    stats = build_project_a_stats(
        decoded_entries=decoded_entries,
        selected_blocks=selected_blocks,
        num_frames=inferred_num_frames,
        hard_union=hard_union,
    )
    stats["duplicate_selected_blocks"] = duplicate_count

    return {
        "selected_blocks": selected_blocks,
        "fine_votes": fine_votes,
        "region_priors_56": region_priors_56,
        "frame_priors_28": frame_priors_28,
        "stats": stats,
    }
