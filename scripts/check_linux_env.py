"""Print bridge-core environment diagnostics."""

from __future__ import annotations

import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


VTC_ROOT = Path(__file__).resolve().parents[1]


def run_version(command: list[str]) -> str:
    executable = shutil.which(command[0])
    if executable is None:
        return "not found"

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return f"error: {exc}"

    output = (result.stdout or result.stderr).strip().splitlines()
    if not output:
        return f"found at {executable}"
    return output[0]


def import_status(module_name: str, distribution_name: str | None = None) -> tuple[bool, str]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 - diagnostics should report import failures.
        return False, f"not importable: {exc.__class__.__name__}: {exc}"

    version = getattr(module, "__version__", None)
    if version is None and distribution_name:
        try:
            from importlib.metadata import version as dist_version

            version = dist_version(distribution_name)
        except Exception:
            version = None

    if version is None:
        return True, "importable"
    return True, f"importable ({version})"


def print_status(label: str, value: str) -> None:
    print(f"{label}: {value}")


def main() -> int:
    missing_required: list[str] = []

    print_status("Python version", sys.version.replace("\n", " "))
    print_status("platform", platform.platform())
    print_status("machine", platform.machine())
    print_status("current working directory", str(Path.cwd()))
    print_status("inferred VTC root", str(VTC_ROOT))
    print_status("HF_HOME", os.environ.get("HF_HOME", "not set"))
    print_status("HF_HUB_CACHE", os.environ.get("HF_HUB_CACHE", "not set"))
    print_status("uv", run_version(["uv", "--version"]))
    print_status("git", run_version(["git", "--version"]))
    print_status("ffmpeg", run_version(["ffmpeg", "-version"]))

    required = [
        ("numpy", "numpy", "numpy"),
        ("PIL", "PIL", "pillow"),
        ("pytest", "pytest", "pytest"),
    ]
    optional = [
        ("torch", "torch", "torch"),
        ("transformers", "transformers", "transformers"),
        ("flash_attn", "flash_attn", "flash-attn"),
        ("decord", "decord", "decord"),
        ("opencv", "cv2", "opencv-python"),
    ]

    torch_available = False

    for label, module_name, dist_name in required:
        ok, status = import_status(module_name, dist_name)
        print_status(f"{label} import status", status)
        if not ok:
            missing_required.append(label)

    for label, module_name, dist_name in optional:
        ok, status = import_status(module_name, dist_name)
        print_status(f"{label} import status", status)
        if label == "torch":
            torch_available = ok

    if torch_available:
        import torch

        print_status("torch CUDA availability", str(torch.cuda.is_available()))
        mps_backend = getattr(torch.backends, "mps", None)
        mps_available = bool(mps_backend and torch.backends.mps.is_available())
        print_status("torch MPS availability", str(mps_available))

    if missing_required:
        print_status("Level 1 status", f"missing required dependencies: {', '.join(missing_required)}")
        return 1

    print_status("Level 1 status", "ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
