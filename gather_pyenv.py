"""
Gather tkinter availability data for pyenv-managed Python versions.

Run this script on a machine with pyenv (Linux/macOS) or pyenv-win (Windows)
installed and one or more Python versions already installed via
`pyenv install <version>`.  Results are written to data/<os>_pyenv.json.

Platform notes
--------------
Linux / macOS — uses the official pyenv (https://github.com/pyenv/pyenv).
  Compiles CPython from source.  Tkinter is present only if the Tcl/Tk
  development headers (tk-dev / tk-devel) were installed *before* running
  `pyenv install`.

Windows — pyenv does not officially support Windows outside WSL, and WSL
  Pythons are Linux builds, not native Windows.  Use pyenv-win instead
  (https://github.com/pyenv-win/pyenv-win), which installs native Windows
  CPython binaries.  This script detects pyenv-win automatically and records
  the variant in the data file so the site can label it correctly.

Usage:
    uv run python gather_pyenv.py
    uv run python gather_pyenv.py --dry-run
    uv run python gather_pyenv.py --force
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

DATA_DIR = Path(__file__).parent / "data"
PROBE_SCRIPT = Path(__file__).parent / "probe_tkinter.py"


def os_key() -> str:
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def data_file() -> Path:
    return DATA_DIR / f"{os_key()}_pyenv.json"


def load_existing(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"os": os_key(), "source": "pyenv", "generated_at": None, "results": {}}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {path}")


def find_pyenv_root() -> tuple[Path, str] | tuple[None, None]:
    """
    Locate the pyenv root directory.

    Returns (root_path, variant) where variant is 'pyenv-win' or 'pyenv',
    or (None, None) if not found.
    """
    # Honour explicit PYENV_ROOT
    env_root = os.environ.get("PYENV_ROOT")
    if env_root:
        p = Path(env_root)
        if p.is_dir():
            variant = "pyenv-win" if is_windows() else "pyenv"
            return p, variant

    if is_windows():
        # pyenv-win default locations (versions/ lives directly under root)
        username = os.environ.get("USERNAME", "")
        candidates = [
            (Path.home() / ".pyenv" / "pyenv-win", "pyenv-win"),
            (Path(f"C:/Users/{username}/.pyenv/pyenv-win"), "pyenv-win"),
            (Path("C:/.pyenv/pyenv-win"), "pyenv-win"),
        ]
    else:
        candidates = [
            (Path.home() / ".pyenv", "pyenv"),
            (Path("/usr/local/opt/pyenv"), "pyenv"),  # some Homebrew setups
        ]

    for path, variant in candidates:
        if path.is_dir():
            return path, variant

    return None, None


def list_pyenv_versions(pyenv_root: Path) -> list[str]:
    """Return installed CPython version strings (major.minor.patch)."""
    versions_dir = pyenv_root / "versions"
    if not versions_dir.is_dir():
        return []

    versions = []
    for entry in sorted(versions_dir.iterdir()):
        name = entry.name
        # Skip non-CPython installs (anaconda, pypy, miniconda, etc.)
        if not name[0].isdigit():
            continue
        for exe_rel in ("bin/python", "bin/python3", "Scripts/python.exe"):
            exe = entry / exe_rel
            if exe.is_file():
                versions.append(name)
                break
    return versions


def python_exe_for_version(pyenv_root: Path, version: str) -> Path | None:
    base = pyenv_root / "versions" / version
    for rel in ("bin/python", "bin/python3", "Scripts/python.exe"):
        p = base / rel
        if p.is_file():
            return p
    return None


def minor_key(version: str) -> str:
    """Return 'major.minor' from a full version string like '3.12.4'."""
    parts = version.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return version


def probe_version(version: str, python_exe: Path, dry_run: bool = False) -> dict | None:
    probe_path = PROBE_SCRIPT.as_posix()
    cmd = [str(python_exe), probe_path]

    print(f"  Probing {version} ({python_exe}) ... ", end="", flush=True)

    if dry_run:
        print("(dry-run skipped)")
        return None

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
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
        "--force",
        action="store_true",
        help="Re-probe versions that already have results",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without running probes",
    )
    args = parser.parse_args()

    pyenv_root, variant = find_pyenv_root()
    if pyenv_root is None:
        if is_windows():
            print(
                "ERROR: pyenv-win not found.\n"
                "Install from https://github.com/pyenv-win/pyenv-win then run:\n"
                "  pyenv install 3.12.9\n"
                "Or set PYENV_ROOT to your pyenv-win root directory.",
                file=sys.stderr,
            )
        else:
            print(
                "ERROR: pyenv not found.\n"
                "Install from https://github.com/pyenv/pyenv then run:\n"
                "  pyenv install 3.12.9\n"
                "Or set PYENV_ROOT to your pyenv root directory.",
                file=sys.stderr,
            )
        sys.exit(1)

    print(f"OS:           {os_key()}")
    print(f"Variant:      {variant}")
    print(f"pyenv root:   {pyenv_root}")

    versions = list_pyenv_versions(pyenv_root)
    if not versions:
        print("\nNo pyenv-managed Python versions found.")
        print("Install some with: pyenv install 3.12.9")
        sys.exit(0)

    print(f"Found versions: {versions}")
    print()

    path = data_file()
    data = load_existing(path)
    # Record/update the variant so the site can label it correctly
    data["source"] = variant

    for version in versions:
        minor = minor_key(version)
        if not args.force and minor in data["results"]:
            existing = data["results"][minor]
            status = "YES" if existing.get("has_tkinter") else "NO"
            print(f"  {version} (minor {minor}): already have result ({status}), skipping")
            continue

        exe = python_exe_for_version(pyenv_root, version)
        if exe is None:
            print(f"  {version}: python executable not found, skipping")
            continue

        result = probe_version(version, exe, dry_run=args.dry_run)
        if result is not None:
            result["version_requested"] = minor
            data["results"][minor] = result

    if not args.dry_run:
        save(path, data)


if __name__ == "__main__":
    main()
