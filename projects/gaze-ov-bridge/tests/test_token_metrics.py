from gaze_ov_bridge.token_metrics import (
    autogaze_candidate_tokens_per_frame,
    build_compression_metrics,
    build_token_counts,
    dense_native_merged_visual_tokens,
    dense_native_raw_patch_tokens,
    project_a_token_counts,
    project_b_token_count,
    safe_ratio,
)


def test_autogaze_candidate_tokens_default_scales():
    assert autogaze_candidate_tokens_per_frame() == 340


def test_dense_token_formulas():
    assert dense_native_raw_patch_tokens(num_frames=3) == 3 * 16 * 16
    assert dense_native_merged_visual_tokens(num_frames=3) == 3 * 8 * 8


def test_project_a_and_b_token_formulas():
    assert project_a_token_counts(selected_112_blocks=7) == {
        "project_a_raw_patch_tokens": 28,
        "project_a_llm_visual_tokens": 7,
    }
    assert project_b_token_count(valid_autogaze_entries=11) == 11


def test_safe_ratio_handles_zero_denominator():
    assert safe_ratio(5, 0) is None
    assert safe_ratio(5, None) is None
    assert safe_ratio(5, 10) == 0.5


def test_compression_metrics_use_safe_ratios_and_reductions():
    token_counts = build_token_counts(
        num_frames=2,
        selected_112_blocks=16,
        autogaze_valid_tokens_total=20,
    )

    compression = build_compression_metrics(token_counts)

    assert token_counts["autogaze_candidate_tokens_total"] == 680
    assert token_counts["dense_native_raw_patch_tokens"] == 512
    assert token_counts["dense_native_merged_visual_tokens"] == 128
    assert token_counts["project_a_raw_patch_tokens"] == 64
    assert token_counts["project_a_llm_visual_tokens"] == 16
    assert token_counts["project_b_ov_direct_tokens"] == 20
    assert compression["project_a_vs_dense_raw_ratio"] == 64 / 512
    assert compression["project_a_vs_dense_visual_ratio"] == 16 / 128
    assert compression["project_a_raw_reduction"] == 1 - (64 / 512)
    assert compression["project_b_vs_autogaze_candidates_ratio"] == 20 / 680


def test_compression_metrics_keep_zero_denominator_values_null():
    token_counts = build_token_counts(
        num_frames=0,
        selected_112_blocks=0,
        autogaze_valid_tokens_total=0,
    )

    compression = build_compression_metrics(token_counts)

    assert compression["project_a_vs_dense_raw_ratio"] is None
    assert compression["project_b_vs_dense_native_ratio"] is None
    assert compression["project_b_reduction_vs_dense_native"] is None
