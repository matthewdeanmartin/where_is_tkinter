"""
Gather tkinter availability data for Docker official Python images by reading
their Dockerfiles from the docker-library/python GitHub repo.

This avoids pulling multi-GB images — we inspect the Dockerfiles instead.
Results are written to data/docker.json and committed to the repo.

Usage:
    uv run python gather_docker.py
    uv run python gather_docker.py --force   # re-fetch all, ignore cache
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "docker.json"

_RAW = "https://raw.githubusercontent.com/docker-library/python/master"
_API = "https://api.github.com/repos/docker-library/python/contents"

DEFAULT_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]


def fetch(url: str, accept: str = "text/plain") -> str | None:
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "where-is-tkinter/1.0", "Accept": accept}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"    fetch error {url}: {e}")
        return None


def list_variants(version: str) -> list[tuple[str, str]]:
    """
    Return (variant_name, dockerfile_path) pairs for a given Python minor version,
    discovered via the GitHub API.  variant_name is the docker tag suffix
    (e.g. "bookworm", "slim-bookworm", "alpine3.22").
    """
    variants = []

    def scan_dir(api_path: str, tag_prefix: str = "") -> None:
        url = f"{_API}/{api_path}"
        raw = fetch(url, accept="application/vnd.github+json")
        if raw is None:
            return
        try:
            entries = json.loads(raw)
        except json.JSONDecodeError:
            return
        for entry in entries:
            name = entry["name"]
            kind = entry["type"]
            if kind == "dir":
                # Could be a variant dir (has Dockerfile) or a grouping dir
                # like "windows/" — recurse one level
                sub_api = f"{api_path}/{name}"
                sub_raw = fetch(f"{_API}/{sub_api}", accept="application/vnd.github+json")
                if sub_raw is None:
                    continue
                try:
                    sub_entries = json.loads(sub_raw)
                except json.JSONDecodeError:
                    continue
                sub_names = {e["name"] for e in sub_entries}
                if "Dockerfile" in sub_names:
                    tag = f"{tag_prefix}{name}" if tag_prefix else name
                    dockerfile_path = f"{api_path}/{name}/Dockerfile".replace(
                        f"{version}/", "", 1
                    )
                    variants.append((tag, f"{version}/{api_path.split('/', 1)[-1]}/{name}/Dockerfile"))
                else:
                    # One more level (e.g. windows/windowsservercore-ltsc2022)
                    for sub_entry in sub_entries:
                        if sub_entry["type"] == "dir":
                            deep_api = f"{sub_api}/{sub_entry['name']}"
                            deep_raw = fetch(
                                f"{_API}/{deep_api}",
                                accept="application/vnd.github+json",
                            )
                            if deep_raw is None:
                                continue
                            try:
                                deep_entries = json.loads(deep_raw)
                            except json.JSONDecodeError:
                                continue
                            if any(e["name"] == "Dockerfile" for e in deep_entries):
                                tag = f"{name}-{sub_entry['name']}"
                                variants.append(
                                    (
                                        tag,
                                        f"{version}/{name}/{sub_entry['name']}/Dockerfile",
                                    )
                                )

    scan_dir(version)
    return variants


def list_variants_simple(version: str) -> list[tuple[str, str]]:
    """
    Simpler approach: fetch the top-level directory listing for a version
    and probe each subdirectory for a Dockerfile.
    """
    url = f"{_API}/{version}"
    raw = fetch(url, accept="application/vnd.github+json")
    if raw is None:
        return []
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError:
        return []

    variants = []
    for entry in entries:
        if entry["type"] != "dir":
            continue
        name = entry["name"]
        # Check for Dockerfile directly in this dir
        df_url = f"{_RAW}/{version}/{name}/Dockerfile"
        content = fetch(df_url)
        if content is not None:
            variants.append((name, df_url, content))
            continue
        # One level deeper (e.g. windows/windowsservercore-ltsc2022)
        sub_url = f"{_API}/{version}/{name}"
        sub_raw = fetch(sub_url, accept="application/vnd.github+json")
        if sub_raw is None:
            continue
        try:
            sub_entries = json.loads(sub_raw)
        except json.JSONDecodeError:
            continue
        for sub in sub_entries:
            if sub["type"] != "dir":
                continue
            sub_name = sub["name"]
            sub_df_url = f"{_RAW}/{version}/{name}/{sub_name}/Dockerfile"
            sub_content = fetch(sub_df_url)
            if sub_content is not None:
                variants.append((f"{name}-{sub_name}", sub_df_url, sub_content))

    return variants


def analyze_dockerfile(content: str, variant: str) -> dict:
    """Determine tkinter status by inspecting Dockerfile content."""
    lines = content.lower()

    if "alpine" in variant:
        has_tk = "py3-tk" in lines or "python3-tkinter" in lines
        return {
            "has_tkinter": has_tk,
            "confidence": "high",
            "reasoning": (
                "Alpine image includes py3-tk"
                if has_tk
                else "Alpine images do not install py3-tk; tkinter unavailable"
            ),
        }

    if "windows" in variant or "windowsservercore" in variant:
        # Windows images build Python from source; look for tcl/tk flags
        has_tcl = "tcltk" in lines or "tcl_library" in lines or "tk_library" in lines
        return {
            "has_tkinter": has_tcl,
            "confidence": "medium",
            "reasoning": (
                "Windows image references Tcl/Tk in build flags"
                if has_tcl
                else "No Tcl/Tk flags found in Windows Dockerfile; tkinter likely absent"
            ),
        }

    # Debian full and slim: tkinter compiled in if tk-dev present during build
    has_tk_dev = "tk-dev" in lines
    is_slim = "slim" in variant
    if has_tk_dev:
        note = (
            "tk-dev present at compile time; _tkinter.so retained in slim image"
            if is_slim
            else "tk-dev installed at compile time; tkinter built in"
        )
        return {"has_tkinter": True, "confidence": "high", "reasoning": note}

    return {
        "has_tkinter": False,
        "confidence": "medium",
        "reasoning": "tk-dev not found in Dockerfile",
    }


def os_family(variant: str) -> str:
    if "windows" in variant or "windowsservercore" in variant:
        return "windows"
    return "linux"


def load_existing() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"source": "docker", "generated_at": None, "results": {}}


def save(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved {DATA_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions", nargs="+", default=DEFAULT_VERSIONS)
    parser.add_argument(
        "--force", action="store_true", help="Re-fetch even already-recorded entries"
    )
    args = parser.parse_args()

    data = load_existing()
    results = data.setdefault("results", {})

    for version in args.versions:
        print(f"\nPython {version}: discovering variants...")
        version_results = results.setdefault(version, {})

        found = list_variants_simple(version)
        if not found:
            print(f"  No variants found (version may not be in repo yet)")
            continue

        for variant, dockerfile_url, content in found:
            if not args.force and variant in version_results:
                existing = version_results[variant]
                status = "YES" if existing.get("has_tkinter") else "NO"
                print(f"  {variant}: already recorded ({status}), skipping")
                continue

            analysis = analyze_dockerfile(content, variant)
            status = "YES" if analysis["has_tkinter"] else "NO"
            print(f"  {variant}: {status} ({analysis['confidence']} confidence)")
            version_results[variant] = {
                "version": version,
                "variant": variant,
                "image_tag": f"python:{version}-{variant}",
                "dockerfile_url": dockerfile_url,
                "os_family": os_family(variant),
                **analysis,
            }

    save(data)


if __name__ == "__main__":
    main()
