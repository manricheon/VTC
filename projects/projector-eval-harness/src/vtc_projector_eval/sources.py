"""Source snapshot audit helpers for projector eval external repositories."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


SOURCE_SPECS: dict[str, dict[str, Any]] = {
    "fourier": {
        "name": "Fourier-Compressor",
        "path": "external/Fourier-Compressor",
        "remote": "https://github.com/whyisverysmart/Fourier-Compressor.git",
        "branch": "master",
        "expected_commit": "b846f44c5c189370a94e1ec71a7dcef5ccb36d55",
        "required_files": [
            "pyproject.toml",
            "fourier_compressor/integrations/llava/monkey_patch.py",
            "fourier_compressor/compress.py",
        ],
        "terms": ["apply_to_llava", "compress_square", "reserve"],
    },
    "divt": {
        "name": "DiVT",
        "path": "external/DiVT",
        "remote": "https://github.com/LeeHyun98/DiVT.git",
        "branch": "main",
        "expected_commit": "5ebbb162d5808d8ad3efc2514cc990487ac9296a",
        "required_files": [
            "pyproject.toml",
            "llava/model/multimodal_projector/builder.py",
            "llava/model/language_model/llava_llama.py",
        ],
        "terms": ["DiVT", "threshold", "clusterer"],
    },
}


def _git_value(path: Path, args: list[str]) -> str | None:
    if not (path / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _read_required_text(root: Path, required_files: list[str]) -> str:
    chunks: list[str] = []
    for relative in required_files:
        path = root / relative
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def audit_sources(repo_root: str | Path) -> dict[str, dict[str, Any]]:
    """Return source presence, git metadata, file checks, and key term matches."""

    root = Path(repo_root)
    records: dict[str, dict[str, Any]] = {}
    for key, spec in SOURCE_SPECS.items():
        source_path = root / spec["path"]
        required_files = list(spec["required_files"])
        missing_files = [
            relative for relative in required_files if not (source_path / relative).exists()
        ]
        text = _read_required_text(source_path, required_files) if source_path.exists() else ""
        commit = _git_value(source_path, ["rev-parse", "HEAD"])
        expected_commit = str(spec["expected_commit"])
        records[key] = {
            "name": spec["name"],
            "path": str(source_path),
            "remote_expected": spec["remote"],
            "remote_actual": _git_value(source_path, ["remote", "get-url", "origin"]),
            "branch_expected": spec["branch"],
            "branch_actual": _git_value(source_path, ["branch", "--show-current"]),
            "commit_expected": expected_commit,
            "commit_actual": commit,
            "commit_matches_expected": commit == expected_commit,
            "status": "present" if source_path.exists() else "missing",
            "required_files_present": source_path.exists() and not missing_files,
            "missing_required_files": missing_files,
            "terms": {term: term in text for term in spec["terms"]},
        }
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit projector eval source snapshots.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="VTC repository root. Defaults to current working directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(json.dumps(audit_sources(args.repo_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
