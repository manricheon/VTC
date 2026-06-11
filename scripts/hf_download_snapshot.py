#!/usr/bin/env python3
"""Token-safe wrapper around huggingface_hub.snapshot_download."""

from __future__ import annotations

import argparse
import errno
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def import_hf():
    try:
        from huggingface_hub import HfApi
        from huggingface_hub import snapshot_download
        from huggingface_hub.utils import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError
    except Exception as exc:
        print(f"ERROR: huggingface_hub is not importable: {type(exc).__name__}: {exc}", file=sys.stderr)
        print("Run: cd envs/hf-tools && uv sync", file=sys.stderr)
        raise SystemExit(1)
    return HfApi, snapshot_download, GatedRepoError, HfHubHTTPError, RepositoryNotFoundError


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def token_from_env(enabled: bool) -> str | None:
    if not enabled:
        return None
    return os.environ.get("HF_TOKEN")


def classify_error(exc: Exception, gated_type, http_type, not_found_type) -> tuple[int, str]:
    message = str(exc)
    lowered = message.lower()
    if isinstance(exc, gated_type) or "gated" in lowered:
        return (
            2,
            "Gated repo access required. Request/accept access on Hugging Face, authenticate, then rerun.",
        )
    if isinstance(exc, not_found_type) or "repo not found" in lowered or "404" in lowered:
        return (
            3,
            "Repository not found or not visible with current credentials. Check repo id, repo type, and access.",
        )
    if "401" in lowered or "403" in lowered or "unauthorized" in lowered or "forbidden" in lowered:
        return (
            2,
            "Authentication or permission required. Set HF_TOKEN or run 'hf auth login' under HF_HOME.",
        )
    if isinstance(exc, OSError) and getattr(exc, "errno", None) == errno.ENOSPC:
        return (5, "Insufficient disk space. Free space under weights/ or choose a larger volume.")
    if isinstance(exc, (TimeoutError, socket.timeout, ConnectionError)) or "connection" in lowered:
        return (4, "Network failure. Check connectivity and retry.")
    if isinstance(exc, http_type):
        return (4, "Hugging Face Hub HTTP error. Check network, repo access, and retry.")
    return (1, "Unexpected download failure. Inspect the error and retry after addressing it.")


def write_manifest(args: argparse.Namespace, local_dir: Path, cache_dir: Path | None, resolved_path: Path) -> Path:
    manifest = {
        "repo_id": args.repo_id,
        "repo_type": args.repo_type,
        "revision": args.revision,
        "local_dir": str(local_dir),
        "cache_dir": str(cache_dir) if cache_dir else None,
        "resolved_path": str(resolved_path),
        "files_count": count_files(local_dir),
        "timestamp": utc_now(),
        "allow_patterns": args.allow_pattern,
        "ignore_patterns": args.ignore_pattern,
    }
    local_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = local_dir / "snapshot_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--repo-type", choices=["model", "dataset", "space"], default="model")
    parser.add_argument("--local-dir", required=True)
    parser.add_argument("--cache-dir")
    parser.add_argument("--revision")
    parser.add_argument("--allow-pattern", action="append", dest="allow_pattern")
    parser.add_argument("--ignore-pattern", action="append", dest="ignore_pattern")
    parser.add_argument(
        "--dry-run-like-list",
        action="store_true",
        help="List matching repo files through the Hub API without downloading snapshots.",
    )
    parser.add_argument(
        "--token-from-env",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use HF_TOKEN from the environment if present. Token value is never printed.",
    )
    args = parser.parse_args(argv)

    HfApi, snapshot_download, GatedRepoError, HfHubHTTPError, RepositoryNotFoundError = import_hf()
    token = token_from_env(args.token_from_env)
    local_dir = Path(args.local_dir).expanduser().resolve()
    cache_dir = Path(args.cache_dir or os.environ.get("HF_HUB_CACHE", "")).expanduser().resolve() if (args.cache_dir or os.environ.get("HF_HUB_CACHE")) else None

    print(f"repo_id: {args.repo_id}")
    print(f"repo_type: {args.repo_type}")
    print(f"revision: {args.revision or 'default'}")
    print(f"local_dir: {local_dir}")
    print(f"cache_dir: {cache_dir or 'huggingface_hub default'}")
    print(f"HF_TOKEN: {'present (value hidden)' if token else 'not set; using HF_HOME login state or public access'}")

    try:
        if args.dry_run_like_list:
            files = HfApi().list_repo_files(
                repo_id=args.repo_id,
                repo_type=args.repo_type,
                revision=args.revision,
                token=token,
            )
            print(f"files_count: {len(files)}")
            for name in files[:50]:
                print(f"  {name}")
            if len(files) > 50:
                print(f"  ... {len(files) - 50} more")
            print("No files downloaded.")
            return 0

        resolved = snapshot_download(
            repo_id=args.repo_id,
            repo_type=args.repo_type,
            revision=args.revision,
            local_dir=str(local_dir),
            cache_dir=str(cache_dir) if cache_dir else None,
            allow_patterns=args.allow_pattern,
            ignore_patterns=args.ignore_pattern,
            token=token,
        )
        manifest_path = write_manifest(args, local_dir, cache_dir, Path(resolved))
    except Exception as exc:
        code, action = classify_error(exc, GatedRepoError, HfHubHTTPError, RepositoryNotFoundError)
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"Action: {action}", file=sys.stderr)
        return code

    print(f"snapshot_path: {resolved}")
    print(f"manifest: {manifest_path}")
    print("Download complete. Token value was not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

