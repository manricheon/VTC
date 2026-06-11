from __future__ import annotations

import json
import importlib.util

import numpy as np
import pytest

from gaze_ov_bridge.io_artifacts import (
    write_selected_blocks,
    write_src_positions,
    write_stats,
)
from gaze_ov_bridge.project_a_llava_boundary import (
    build_llava_codec_payload,
    inspect_llava_codec_source,
    load_project_a_boundary_artifacts,
    validate_src_positions,
)


def test_valid_src_positions_build_llava_payload():
    selected_blocks = [(0, 0, 0), (0, 1, 2)]
    src_positions = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
            [0, 2, 4],
            [0, 2, 5],
            [0, 3, 4],
            [0, 3, 5],
        ],
        dtype=np.int64,
    )

    payload = build_llava_codec_payload(
        selected_blocks=selected_blocks,
        src_positions=src_positions,
        meta={"video_id": "unit"},
    )

    assert payload["src_positions"].dtype == np.int64
    assert payload["src_positions"].tolist() == src_positions.tolist()
    assert payload["selected_blocks"] == selected_blocks
    assert payload["meta"]["selected_112_blocks"] == 2
    assert payload["meta"]["raw_patch_tokens"] == 8
    assert payload["meta"]["llm_visual_tokens"] == 2


def test_invalid_src_positions_shape_is_rejected():
    with pytest.raises(ValueError, match="shape"):
        validate_src_positions(np.array([0, 1, 2]))

    with pytest.raises(ValueError, match="shape"):
        validate_src_positions(np.array([[0, 1], [0, 2]]))


def test_invalid_native_patch_range_is_rejected():
    src_positions = np.array([[0, 16, 0]], dtype=np.int64)

    with pytest.raises(ValueError, match="native_h/native_w"):
        validate_src_positions(src_positions)


def test_selected_blocks_and_src_positions_count_mismatch_is_rejected():
    selected_blocks = [(0, 0, 0), (0, 1, 2)]
    src_positions = np.array(
        [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
        ],
        dtype=np.int64,
    )

    with pytest.raises(ValueError, match="selected_blocks"):
        validate_src_positions(src_positions, selected_blocks=selected_blocks)


def test_invalid_2x2_block_ordering_is_rejected():
    selected_blocks = [(0, 0, 0)]
    src_positions = np.array(
        [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [0, 1, 1],
        ],
        dtype=np.int64,
    )

    with pytest.raises(ValueError, match="2x2"):
        validate_src_positions(src_positions, selected_blocks=selected_blocks)


def test_load_project_a_boundary_artifacts_and_profile_schema(tmp_path):
    selected_blocks = [(0, 0, 0)]
    src_positions = np.array(
        [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
        dtype=np.int64,
    )
    stats = {
        "selected_112_blocks": 1,
        "raw_patch_tokens": 4,
        "llm_visual_tokens": 1,
        "token_counts": {
            "selected_112_blocks": 1,
            "project_a_raw_patch_tokens": 4,
            "project_a_llm_visual_tokens": 1,
            "dense_native_raw_patch_tokens": 256,
            "dense_native_merged_visual_tokens": 64,
        },
        "compression": {
            "project_a_vs_dense_raw_ratio": 4 / 256,
            "project_a_vs_dense_visual_ratio": 1 / 64,
        },
    }
    write_selected_blocks(selected_blocks, tmp_path / "selected_blocks.json")
    write_src_positions(src_positions, tmp_path / "src_positions.npy")
    write_stats(stats, tmp_path / "stats.json")

    loaded = load_project_a_boundary_artifacts(tmp_path)

    assert loaded["payload"]["meta"]["selected_112_blocks"] == 1
    assert loaded["stats"]["raw_patch_tokens"] == 4

    profile = loaded["profile_fields"]
    assert profile["token_counts"]["selected_112_blocks"] == 1
    assert profile["compression"]["project_a_vs_dense_raw_ratio"] == 4 / 256


def test_llava_codec_source_inspection_reports_missing_paths(tmp_path):
    result = inspect_llava_codec_source(tmp_path)

    assert result["source_root"] == str(tmp_path)
    assert result["codec_processing_file"] is None
    assert result["processor_file"] is None
    assert result["has_process_codec_video"] is False
    assert result["status"] == "missing"


def test_project_a_boundary_smoke_writes_profile(tmp_path):
    repo_root = tmp_path.parents[0]
    script_path = (
        repo_root
        / "projects"
        / "gaze-ov-bridge"
        / "scripts"
        / "smoke_project_a_llava_boundary.py"
    )
    if not script_path.exists():
        script_path = (
            __import__("pathlib").Path(__file__).resolve().parents[1]
            / "scripts"
            / "smoke_project_a_llava_boundary.py"
        )
    spec = importlib.util.spec_from_file_location("smoke_project_a_llava_boundary", script_path)
    assert spec is not None and spec.loader is not None
    smoke_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke_module)

    source_dir = tmp_path / "source"
    out_dir = tmp_path / "out"
    selected_blocks = [(0, 0, 0)]
    src_positions = np.array(
        [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1]],
        dtype=np.int64,
    )
    stats = {
        "selected_112_blocks": 1,
        "raw_patch_tokens": 4,
        "llm_visual_tokens": 1,
        "token_counts": {
            "selected_112_blocks": 1,
            "project_a_raw_patch_tokens": 4,
            "project_a_llm_visual_tokens": 1,
            "dense_native_raw_patch_tokens": 256,
            "dense_native_merged_visual_tokens": 64,
        },
        "compression": {
            "project_a_vs_dense_raw_ratio": 4 / 256,
            "project_a_vs_dense_visual_ratio": 1 / 64,
        },
    }
    write_selected_blocks(selected_blocks, source_dir / "selected_blocks.json")
    write_src_positions(src_positions, source_dir / "src_positions.npy")
    write_stats(stats, source_dir / "stats.json")

    result = smoke_module.run_smoke(source_dir=source_dir, out_dir=out_dir, source_root=tmp_path)
    profile = json.loads((out_dir / "profile.json").read_text(encoding="utf-8"))

    assert result["stats"]["selected_112_blocks"] == 1
    assert profile["project"]["track"] == "project_a_codec"
    assert profile["project"]["policy_name"] == "llava_boundary_contract"
    assert profile["timings_s"]["validate_src_positions"] is not None
    assert profile["token_counts"]["project_a_raw_patch_tokens"] == 4
