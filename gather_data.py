"""
Gather tkinter availability data across Python versions using uv.

Run this script on each target OS (Windows, macOS, Linux). Results are written
to data/<os>.json and are meant to be committed to the repo so the site can
render them without re-running the expensive downloads.

Usage:
    uv run python gather_data.py
    uv run python gather_data.py --dry-run
    uv run python gather_data.py --versions 3.9 3.10 3.11 3.12 3.13

The script skips versions that already have a result in the data file so it is
safe to re-run as new Python versions are released.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# CPython versions to probe.  Add new ones here as they're released.
# Format: "major.minor" – uv will pick the latest patch for each.
DEFAULT_VERSIONS = [
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    "3.14",
]

DATA_DIR = Path(__file__).parent / "data"
PROBE_SCRIPT = Path(__file__).parent / "probe_tkinter.py"


def os_key() -> str:
    """Return a short OS identifier used as the data filename."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system  # "windows" or "linux"


def data_file() -> Path:
    return DATA_DIR / f"{os_key()}.json"


def load_existing(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"os": os_key(), "source": "uv-managed", "generated_at": None, "results": {}}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    data.setdefault("source", "uv-managed")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {path}")


def probe_version(version: str, dry_run: bool = False) -> dict | None:
    """Run probe_tkinter.py under a specific Python version via uv."""
    # Use forward slashes so the path works on all platforms and avoids
    # Windows backslash escaping issues when uv passes the path to the subprocess.
    probe_path = PROBE_SCRIPT.as_posix()
    cmd = [
        "uv",
        "run",
        f"--python={version}",
        "--python-preference", "managed",
        "--no-project",
        "python",
        probe_path,
    ]

    print(f"  Probing Python {version} ... ", end="", flush=True)

    if dry_run:
        print("(dry-run skipped)")
        return None

    # Strip variables that uv / the current venv inject and that bleed into
    # child uv invocations, causing them to use the wrong Python stdlib.
    _drop = {
        "PYTHONPATH",
        "PYTHONHOME",
        "VIRTUAL_ENV",
        "VIRTUAL_ENV_PROMPT",
        "UV_INTERNAL__PYTHONHOME",
    }
    env = {k: v for k, v in os.environ.items() if k not in _drop}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if result.returncode != 0 and not result.stdout.strip():
            print(f"FAILED\n    stderr: {result.stderr.strip()[:200]}")
            return {
                "version_requested": version,
                "error": result.stderr.strip()[:500],
                "has_tkinter": None,
            }
        data = json.loads(result.stdout)
        status = "YES" if data.get("has_tkinter") else "NO"
        print(f"{status}  (Python {data.get('python_version', '?')[:6]})")
        return data
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return {"version_requested": version, "error": "timeout", "has_tkinter": None}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"version_requested": version, "error": str(e), "has_tkinter": None}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--versions",
        nargs="+",
        default=DEFAULT_VERSIONS,
        metavar="VERSION",
        help="Python versions to probe (default: all in DEFAULT_VERSIONS list)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-probe versions that already have results",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without actually running uv",
    )
    args = parser.parse_args()

    path = data_file()
    data = load_existing(path)

    print(f"OS: {os_key()}")
    print(f"Data file: {path}")
    print(f"Versions to probe: {args.versions}")
    print()

    for version in args.versions:
        if not args.force and version in data["results"]:
            existing = data["results"][version]
            status = "YES" if existing.get("has_tkinter") else "NO"
            print(f"  Python {version}: already have result ({status}), skipping")
            continue

        result = probe_version(version, dry_run=args.dry_run)
        if result is not None:
            data["results"][version] = result

    if not args.dry_run:
        save(path, data)


if __name__ == "__main__":
    main()
