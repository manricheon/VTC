#!/usr/bin/env python3
"""Token-safe Hugging Face authentication check.

This script never prints token values. It checks whether authentication is
available through HF_TOKEN or the Hugging Face token store under HF_HOME.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def masked_presence(name: str) -> str:
    return "present (value hidden)" if os.environ.get(name) else "not set"


def print_safe_instructions() -> None:
    print()
    print("Safe authentication options:")
    print("  source scripts/env_weights.sh")
    print("  cd envs/hf-tools")
    print("  uv sync")
    print("  uv run python ../../scripts/hf_auth_check.py")
    print("  export HF_TOKEN=<token from https://huggingface.co/settings/tokens>")
    print("  # or, if the hf CLI is installed:")
    print("  hf auth login")
    print()
    print("Do not paste tokens into project files. Do not commit tokens.")


def hf_cli_whoami() -> dict:
    hf_path = shutil.which("hf")
    if hf_path is None:
        return {"cli_available": False, "authenticated": False, "detail": "hf CLI not found"}
    try:
        proc = subprocess.run(
            ["hf", "auth", "whoami"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as exc:
        return {"cli_available": True, "authenticated": False, "detail": f"{type(exc).__name__}: {exc}"}

    output = (proc.stdout or proc.stderr).strip()
    if proc.returncode == 0:
        first_line = output.splitlines()[0] if output else "authenticated"
        return {"cli_available": True, "authenticated": True, "detail": first_line}
    return {"cli_available": True, "authenticated": False, "detail": output or "not authenticated"}


def hub_whoami() -> dict:
    try:
        from huggingface_hub import HfApi
        from huggingface_hub import get_token
    except Exception as exc:
        return {
            "hub_available": False,
            "token_available": bool(os.environ.get("HF_TOKEN")),
            "authenticated": False,
            "detail": f"huggingface_hub import failed: {type(exc).__name__}: {exc}",
        }

    env_token_present = bool(os.environ.get("HF_TOKEN"))
    token = os.environ.get("HF_TOKEN") or get_token()
    token_source = "HF_TOKEN" if env_token_present else ("HF_HOME token store" if token else None)
    if not token:
        return {
            "hub_available": True,
            "token_available": False,
            "token_source": None,
            "authenticated": False,
            "detail": "no token found",
        }

    try:
        who = HfApi().whoami(token=token)
    except Exception as exc:
        return {
            "hub_available": True,
            "token_available": True,
            "token_source": token_source,
            "authenticated": False,
            "detail": f"{type(exc).__name__}: {exc}",
        }

    name = who.get("name") or who.get("fullname") or who.get("email") or "authenticated user"
    return {
        "hub_available": True,
        "token_available": True,
        "token_source": token_source,
        "authenticated": True,
        "detail": name,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--public-only-ok",
        action="store_true",
        help="Return 0 even when no token is available because only public repos will be accessed.",
    )
    args = parser.parse_args(argv)

    root = repo_root()
    hf_home = os.environ.get("HF_HOME")
    hf_hub_cache = os.environ.get("HF_HUB_CACHE")
    print(f"VTC root: {root}")
    print(f"HF_HOME: {hf_home or 'not set'}")
    print(f"HF_HUB_CACHE: {hf_hub_cache or 'not set'}")
    print(f"HF_TOKEN: {masked_presence('HF_TOKEN')}")

    expected_hf_home = root / "weights" / "hf_home"
    expected_hub = expected_hf_home / "hub"
    if hf_home and Path(hf_home).resolve() == expected_hf_home.resolve():
        print("HF_HOME policy: ok")
    else:
        print(f"HF_HOME policy: expected {expected_hf_home}")
    if hf_hub_cache and Path(hf_hub_cache).resolve() == expected_hub.resolve():
        print("HF_HUB_CACHE policy: ok")
    else:
        print(f"HF_HUB_CACHE policy: expected {expected_hub}")

    hub_status = hub_whoami()
    cli_status = hf_cli_whoami()
    print(f"huggingface_hub available: {hub_status.get('hub_available')}")
    print(f"hub token available: {hub_status.get('token_available')}")
    if hub_status.get("authenticated"):
        print(f"hub whoami: authenticated as {hub_status['detail']}")
    else:
        print(f"hub whoami: not authenticated ({hub_status.get('detail')})")

    print(f"hf CLI available: {cli_status['cli_available']}")
    if cli_status["authenticated"]:
        print(f"hf CLI whoami: authenticated as {cli_status['detail']}")
    else:
        print(f"hf CLI whoami: not authenticated ({cli_status['detail']})")

    if hub_status.get("authenticated") or cli_status.get("authenticated"):
        print("Authentication status: authenticated")
        return 0

    if args.public_only_ok:
        print("Authentication status: unauthenticated, public-only mode accepted")
        return 0

    print("Authentication status: token missing or not valid for private/gated repos")
    print_safe_instructions()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

