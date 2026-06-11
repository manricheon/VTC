import json
import subprocess
import sys
import time
from pathlib import Path

from gaze_ov_bridge.memory_probe import collect_memory_mb
from gaze_ov_bridge.profile_schema import (
    append_profile_jsonl,
    create_profile_record,
    write_profile_json,
)
from gaze_ov_bridge.profiling import StageTimer
from gaze_ov_bridge.token_metrics import build_token_counts


def test_timer_records_positive_elapsed_time():
    timer = StageTimer()

    with timer.stage("selector"):
        time.sleep(0.001)

    assert timer.timings_s["selector"] > 0


def test_memory_probe_returns_schema_without_requiring_torch():
    memory = collect_memory_mb()

    assert set(memory) == {
        "process_peak_rss",
        "tracemalloc_peak",
        "cuda_peak_allocated",
        "cuda_peak_reserved",
        "mps_current_allocated",
    }
    assert memory["process_peak_rss"] is None or memory["process_peak_rss"] >= 0
    assert memory["tracemalloc_peak"] is None or memory["tracemalloc_peak"] >= 0


def test_profile_record_is_json_serializable(tmp_path):
    token_counts = build_token_counts(
        num_frames=2,
        selected_112_blocks=8,
        autogaze_valid_tokens_total=13,
    )
    record = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_a_codec",
        env_name="bridge-core",
        policy_name="unit-test",
        input_metadata={
            "video_id": "synthetic",
            "num_frames": 2,
            "target_scales": [28, 56, 112, 224],
            "patch_size": 14,
        },
        token_counts=token_counts,
        timings_s={"total": 1.25, "selector": 0.25},
        memory_mb={
            "process_peak_rss": 100.0,
            "tracemalloc_peak": 3.0,
            "cuda_peak_allocated": None,
            "cuda_peak_reserved": None,
            "mps_current_allocated": None,
        },
        task_metrics={"score": 0.75},
        notes=["synthetic profile"],
        git_commit="abc123",
        run_id="run-test",
        created_at_utc="2026-01-01T00:00:00Z",
    )

    path = tmp_path / "profile.json"
    write_profile_json(record, path)
    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert loaded["schema_version"]
    assert loaded["run_id"] == "run-test"
    assert loaded["project"]["track"] == "project_a_codec"
    assert loaded["token_counts"]["selected_112_blocks"] == 8
    assert loaded["compression"]["project_a_vs_dense_visual_ratio"] == 8 / 128


def test_append_profile_jsonl_writes_one_record_per_line(tmp_path):
    record = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_b_ov_direct",
        env_name="bridge-core",
        run_id="jsonl-run",
    )
    path = tmp_path / "profiles.jsonl"

    append_profile_jsonl(record, path)
    append_profile_jsonl(record, path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["run_id"] == "jsonl-run"


def test_profile_summary_parses_synthetic_json(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    profile_path = tmp_path / "profile.json"
    record = create_profile_record(
        project_name="gaze-ov-bridge",
        track="project_a_codec",
        env_name="bridge-core",
        policy_name="summary-test",
        token_counts=build_token_counts(
            num_frames=1,
            selected_112_blocks=4,
            autogaze_valid_tokens_total=9,
        ),
        timings_s={"total": 0.5},
        memory_mb={
            "process_peak_rss": 42.0,
            "tracemalloc_peak": 1.0,
            "cuda_peak_allocated": None,
            "cuda_peak_reserved": None,
            "mps_current_allocated": None,
        },
        task_metrics={"score": 0.9},
        run_id="summary-run",
        created_at_utc="2026-01-01T00:00:00Z",
    )
    write_profile_json(record, profile_path)

    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts/profile_summary.py"), str(profile_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "summary-run" in result.stdout
    assert "project_a_codec" in result.stdout
    assert "summary-test" in result.stdout
    assert "0.9" in result.stdout
