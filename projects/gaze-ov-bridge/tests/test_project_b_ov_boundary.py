from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from gaze_ov_bridge.autogaze_decode import decode_flat_ids
from gaze_ov_bridge.io_artifacts import (
    write_decoded_entries,
    write_pack_plan,
    write_patch_positions,
    write_patches,
    write_stats,
)
from gaze_ov_bridge.ov_pack import build_ov_pack_plan
from gaze_ov_bridge.project_b_ov_boundary import (
    build_ov_boundary_payload,
    inspect_ov_encoder_source,
    load_project_b_boundary_artifacts,
    validate_no_native_union,
    validate_pack_plan,
    validate_patch_positions,
    validate_patches,
)


def _decoded_entries() -> list[dict[str, int]]:
    return decode_flat_ids([0, 4, 20, 84])


def _patch_positions() -> np.ndarray:
    return np.asarray(
        [
            [0.0, 3.5, 3.5],
            [0.0, 1.5, 1.5],
            [0.0, 0.5, 0.5],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )


def _patches() -> np.ndarray:
    return np.zeros((4, 14, 14, 3), dtype=np.uint8)


def test_valid_ov_boundary_payload_preserves_one_token_per_entry():
    payload = build_ov_boundary_payload(
        decoded_entries=_decoded_entries(),
        patches=_patches(),
        patch_positions=_patch_positions(),
        pack_plan=build_ov_pack_plan(num_tokens=4),
    )

    assert payload["patches"].shape == (4, 14, 14, 3)
    assert payload["patch_positions"].shape == (4, 3)
    assert payload["meta"]["total_tokens"] == 4
    assert payload["meta"]["confirms_no_native_union"] is True


def test_invalid_patch_positions_shape_is_rejected():
    with pytest.raises(ValueError, match="shape"):
        validate_patch_positions(np.asarray([0.0, 1.0, 2.0]))

    with pytest.raises(ValueError, match="shape"):
        validate_patch_positions(np.zeros((4, 2), dtype=np.float32))


def test_invalid_patch_shape_is_rejected():
    with pytest.raises(ValueError, match="patches"):
        validate_patches(np.zeros((4, 14, 3), dtype=np.uint8))

    with pytest.raises(ValueError, match="14x14"):
        validate_patches(np.zeros((4, 16, 16, 3), dtype=np.uint8))


def test_decoded_entry_count_mismatch_is_rejected():
    entries = _decoded_entries()
    positions = _patch_positions()[:3]

    with pytest.raises(ValueError, match="one OV token"):
        validate_no_native_union(entries, positions)


def test_fractional_positions_are_validated_from_decoded_entries():
    validate_patch_positions(_patch_positions(), decoded_entries=_decoded_entries())

    bad = _patch_positions()
    bad[0, 1] = 4.5
    with pytest.raises(ValueError, match="fractional"):
        validate_patch_positions(bad, decoded_entries=_decoded_entries())


def test_pack_plan_validation_rejects_padding_token_metadata():
    plan = build_ov_pack_plan(num_tokens=4)
    validate_pack_plan(plan, num_tokens=4)

    bad = dict(plan)
    bad["tokens"] = [dict(token) for token in plan["tokens"]]
    bad["tokens"][0]["padding"] = True
    with pytest.raises(ValueError, match="padding"):
        validate_pack_plan(bad, num_tokens=4)


def test_load_project_b_boundary_artifacts_and_profile_schema(tmp_path):
    entries = _decoded_entries()
    positions = _patch_positions()
    patches = _patches()
    pack_plan = build_ov_pack_plan(num_tokens=4)
    stats = {
        "total_tokens": 4,
        "tokens_by_scale": {"28": 1, "56": 1, "112": 1, "224": 1},
        "token_counts": {
            "autogaze_candidate_tokens_total": 340,
            "autogaze_valid_tokens_total": 4,
            "dense_native_raw_patch_tokens": 256,
            "project_b_ov_direct_tokens": 4,
        },
        "compression": {
            "project_b_vs_autogaze_candidates_ratio": 4 / 340,
            "project_b_vs_dense_native_ratio": 4 / 256,
        },
    }
    write_decoded_entries(entries, tmp_path / "decoded_entries.json")
    write_patch_positions(positions, tmp_path / "patch_positions.npy")
    write_patches(patches, tmp_path / "patches.npy")
    write_pack_plan(pack_plan, tmp_path / "pack_plan.json")
    write_stats(stats, tmp_path / "stats.json")

    loaded = load_project_b_boundary_artifacts(tmp_path)

    assert loaded["payload"]["meta"]["total_tokens"] == 4
    assert loaded["stats"]["confirms_no_native_union"] is True
    assert loaded["profile_fields"]["token_counts"]["project_b_ov_direct_tokens"] == 4


def test_ov_encoder_source_inspection_reports_missing_paths(tmp_path):
    result = inspect_ov_encoder_source(tmp_path)

    assert result["source_root"] == str(tmp_path)
    assert result["modeling_file"] is None
    assert result["config_file"] is None
    assert result["has_patch_positions"] is False
    assert result["status"] == "missing"


def test_project_b_boundary_smoke_writes_profile(tmp_path):
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "smoke_project_b_ov_boundary.py"
    )
    spec = importlib.util.spec_from_file_location("smoke_project_b_ov_boundary", script_path)
    assert spec is not None and spec.loader is not None
    smoke_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke_module)

    source_dir = tmp_path / "source"
    out_dir = tmp_path / "out"
    entries = _decoded_entries()
    write_decoded_entries(entries, source_dir / "decoded_entries.json")
    write_patch_positions(_patch_positions(), source_dir / "patch_positions.npy")
    write_patches(_patches(), source_dir / "patches.npy")
    write_pack_plan(build_ov_pack_plan(num_tokens=4), source_dir / "pack_plan.json")
    write_stats(
        {
            "total_tokens": 4,
            "token_counts": {
                "autogaze_candidate_tokens_total": 340,
                "autogaze_valid_tokens_total": 4,
                "dense_native_raw_patch_tokens": 256,
                "project_b_ov_direct_tokens": 4,
            },
            "compression": {
                "project_b_vs_autogaze_candidates_ratio": 4 / 340,
                "project_b_vs_dense_native_ratio": 4 / 256,
            },
        },
        source_dir / "stats.json",
    )

    result = smoke_module.run_smoke(source_dir=source_dir, out_dir=out_dir, source_root=tmp_path)
    profile = json.loads((out_dir / "profile.json").read_text(encoding="utf-8"))

    assert result["stats"]["total_tokens"] == 4
    assert profile["project"]["track"] == "project_b_ov_direct"
    assert profile["project"]["policy_name"] == "ov_boundary_no_union"
    assert profile["timings_s"]["validate_positions"] is not None
    assert profile["token_counts"]["project_b_ov_direct_tokens"] == 4
