from __future__ import annotations

from vtc_projector_eval.matrix import DEFAULT_PRESETS, build_matrix


def test_build_matrix_expands_all_models_for_smoke_preset():
    rows = build_matrix(preset="smoke", projector_model="all", limit=1)

    assert {row["model"] for row in rows} == {"vtc_fourier_llava15", "vtc_divt_llava15"}
    assert {row["limit"] for row in rows} == {1}
    assert {row["task"] for row in rows} == set(DEFAULT_PRESETS["smoke"])
    assert all("model_args" in row for row in rows)


def test_build_matrix_accepts_task_override_and_divt_threshold():
    rows = build_matrix(
        preset="smoke",
        projector_model="divt",
        tasks="mme,pope",
        limit=3,
        divt_threshold=0.75,
    )

    assert [row["task"] for row in rows] == ["mme", "pope"]
    assert {row["model"] for row in rows} == {"vtc_divt_llava15"}
    assert rows[0]["limit"] == 3
    assert "divt_threshold=0.75" in rows[0]["model_args"]


def test_build_matrix_rejects_unknown_projector_model():
    try:
        build_matrix(preset="smoke", projector_model="unknown")
    except ValueError as exc:
        assert "projector_model" in str(exc)
    else:
        raise AssertionError("expected ValueError")
