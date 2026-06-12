from __future__ import annotations

from pathlib import Path

from vtc_projector_eval.sources import SOURCE_SPECS, audit_sources


def test_audit_sources_reports_present_expected_files(tmp_path: Path):
    fourier = tmp_path / "external" / "Fourier-Compressor"
    divt = tmp_path / "external" / "DiVT"
    (fourier / "fourier_compressor" / "integrations" / "llava").mkdir(parents=True)
    (divt / "llava" / "model" / "multimodal_projector").mkdir(parents=True)
    (divt / "llava" / "model" / "language_model").mkdir(parents=True)
    (fourier / "pyproject.toml").write_text("[project]\nname='Fourier-Compressor'\n", encoding="utf-8")
    (fourier / "fourier_compressor" / "integrations" / "llava" / "monkey_patch.py").write_text(
        "def apply_to_llava(reserve=12): pass\n",
        encoding="utf-8",
    )
    (fourier / "fourier_compressor" / "compress.py").write_text(
        "def compress_square(features, reserve=12): pass\n",
        encoding="utf-8",
    )
    (divt / "pyproject.toml").write_text("[project]\nname='llava'\n", encoding="utf-8")
    (divt / "llava" / "model" / "multimodal_projector" / "builder.py").write_text(
        "class DiVT: pass\nthreshold = 0.65\n",
        encoding="utf-8",
    )
    (divt / "llava" / "model" / "language_model" / "llava_llama.py").write_text(
        "def generate(threshold=0.65): pass\n",
        encoding="utf-8",
    )

    records = audit_sources(tmp_path)

    assert set(records) == set(SOURCE_SPECS)
    assert records["fourier"]["status"] == "present"
    assert records["fourier"]["required_files_present"] is True
    assert records["fourier"]["terms"]["apply_to_llava"] is True
    assert records["divt"]["status"] == "present"
    assert records["divt"]["terms"]["threshold"] is True


def test_audit_sources_reports_missing_files(tmp_path: Path):
    records = audit_sources(tmp_path)

    assert records["fourier"]["status"] == "missing"
    assert records["fourier"]["required_files_present"] is False
    assert "external/Fourier-Compressor" in records["fourier"]["path"]
