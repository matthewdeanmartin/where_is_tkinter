"""
Generate Pelican content pages from the tkinter probe data files in data/.

Run after gather_data.py (and optionally gather_pyenv.py) has been executed on
all target platforms and the resulting JSON files have been committed to the repo.

Usage:
    uv run python generate_pages.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
CONTENT_DIR = Path(__file__).parent / "content" / "pages"
TODAY = datetime.now().strftime("%Y-%m-%d")

OS_NAMES = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}
OS_ORDER = ["windows", "macos", "linux"]

# Ordered list of channels to look for, per OS.
# Each entry: (source_key, data filename suffix, display label, short label)
CHANNELS: list[tuple[str, str, str, str]] = [
    (
        "uv-managed",
        "",  # data/<os>.json
        "uv / python-build-standalone",
        "uv / python-build-standalone",
    ),
    (
        "pyenv",
        "_pyenv",  # data/<os>_pyenv.json
        "pyenv",
        "pyenv",
    ),
]

SOURCE_LINKS = {
    "uv-managed": "https://github.com/astral-sh/python-build-standalone",
    "pyenv": "https://github.com/pyenv/pyenv",
    "pyenv-win": "https://github.com/pyenv-win/pyenv-win",
    "python.org": "https://www.python.org/downloads/",
}

SOURCE_DISPLAY_NAMES = {
    "uv-managed": "uv / python-build-standalone",
    "pyenv": "pyenv",
    "pyenv-win": "pyenv-win",
    "python.org": "python.org installer",
}

SOURCE_NOTES = {
    "uv-managed": (
        "These results reflect what you get when uv (or rye / Hatch, which use "
        "the same builds) installs Python automatically via `uv python install`. "
        "Results may differ from python.org installers, pyenv, or system packages."
    ),
    "pyenv": (
        "These results reflect pyenv-managed Pythons. pyenv compiles CPython from "
        "source — tkinter is present only if the Tcl/Tk development headers "
        "(`tk-dev` / `tk-devel`) were installed *before* `pyenv install`."
    ),
    "pyenv-win": (
        "These results reflect [pyenv-win](https://github.com/pyenv-win/pyenv-win)-managed "
        "Pythons. pyenv does not officially support Windows; pyenv-win is a separate "
        "fork by @kirankotari that installs native Windows CPython binaries "
        "(the same pre-built packages as python.org, so tkinter behaviour matches "
        "a fresh python.org install with the default options)."
    ),
}

CHANNELS_EXPLAINER = """\
## Python Distribution Channels

The same version number (e.g. 3.12) can have or lack tkinter depending on
*where* the Python came from:

| Channel | How it installs Python | tkinter included? |
|---------|------------------------|:-----------------:|
| **python.org installer** | Download from python.org; Windows/macOS bundle Tcl/Tk | ✅ Windows & macOS / ❌ Linux |
| **uv / python-build-standalone** | `uv python install` downloads Astral's pre-built CPython | Varies by version — see tables below |
| **pyenv** (Linux/macOS) | Compiles CPython from source | ❌ unless `tk-dev` present at build time |
| **pyenv-win** (Windows only) | Installs native Windows CPython binaries; separate fork of pyenv by @kirankotari | Matches python.org defaults |
| **rye** | Uses the same python-build-standalone as uv | Same as uv |
| **Hatch** | Uses python-build-standalone | Same as uv |
| **conda / mamba** | Downloads conda-forge or defaults channel builds | ✅ (tk package included) |
| **Microsoft Store** | Windows Store Python | ❌ No tkinter |
| **Linux system package** | `apt install python3`, `dnf install python3` | ❌ unless `python3-tk` also installed |
| **Docker official image** | See [Docker page]({filename}docker.md) | Varies by image variant |

**The data on this site covers uv / python-build-standalone and pyenv / pyenv-win.**
Per-platform pages show a separate table for each channel so you can compare directly.
"""

# Version-specific fix recommendations
MISSING_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "windows": {
        "default": (
            "Re-run the official Python installer from **python.org** and, "
            "under *Optional Features*, tick **tcl/tk and IDLE**."
        ),
        "uv": (
            "When uv downloads Python it uses the python-build-standalone "
            "distribution, which currently ships *without* Tcl/Tk on some "
            "versions. Install Python from **python.org** instead and point "
            "uv at it with `uv python pin <path>`, or add "
            "`[tool.uv] python-preference = \"only-system\"` to your "
            "`pyproject.toml`."
        ),
    },
    "macos": {
        "default": (
            "Use the official Python installer from **python.org**, or "
            "install via Homebrew: `brew install python-tk@3.x`."
        ),
        "uv": (
            "uv's python-build-standalone may lack Tcl/Tk. "
            "Install `python-tk` via Homebrew and use "
            "`uv python pin system` or install from python.org."
        ),
    },
    "linux": {
        "default": (
            "Install the OS package: "
            "`sudo apt install python3-tk` (Debian/Ubuntu) or "
            "`sudo dnf install python3-tkinter` (Fedora/RHEL)."
        ),
        "uv": (
            "python-build-standalone does not bundle Tcl/Tk on Linux. "
            "Install via your distro's package manager and set "
            "`python-preference = \"only-system\"` in your `pyproject.toml`."
        ),
    },
}

PYPROJECT_GUIDANCE = """\
## Configuring pyproject.toml to Prefer a Python with Tkinter

### uv

Tell uv to prefer system-installed Pythons (which have tkinter from the OS
package manager or the official python.org installer) over its own
python-build-standalone downloads:

```toml
[tool.uv]
# Prefer system Python; fall back to managed only if no match found.
python-preference = "system"
```

Or pin to a specific interpreter path:

```toml
[tool.uv]
python = "/usr/bin/python3.11"
```

### Poetry

Poetry respects the `python` field in `[tool.poetry.dependencies]` but cannot
directly select a build variant.  Point it at a system Python that has tkinter:

```toml
[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.env]
# (poetry 2.x+) or use 'poetry env use /path/to/python'
```

Then before running `poetry install`:

```bash
poetry env use /usr/bin/python3.11   # Linux/macOS
poetry env use C:/Python311/python.exe  # Windows
```

### pip / venv

Always create your venv from an interpreter that has tkinter:

```bash
# Linux: install the OS package first
sudo apt install python3-tk

# Then create your venv from that interpreter
python3 -m venv .venv
```

### conda / Mamba

Conda ships tkinter in the `tk` package.  Add it to your environment:

```yaml
dependencies:
  - python=3.11
  - tk
```

Or on the command line:

```bash
conda install tk
```
"""


def load_channel_data(os_key: str, suffix: str) -> dict:
    path = DATA_DIR / f"{os_key}{suffix}.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fmt_generated_at(raw: str | None) -> str:
    if not raw:
        return "unknown"
    try:
        dt = datetime.fromisoformat(raw)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return raw


def version_sort_key(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    except ValueError:
        return (999,)


def format_version_table(results: dict) -> str:
    if not results:
        return "_No data collected yet._\n"

    rows = []
    for version, info in sorted(results.items(), key=lambda kv: version_sort_key(kv[0])):
        has = info.get("has_tkinter")
        if has is True:
            status = "✅ Yes"
            tk_ver = info.get("tk_version") or "?"
            detail = f"Tk {tk_ver}"
        elif has is False:
            status = "❌ No"
            detail = info.get("error") or ""
            if len(detail) > 80:
                detail = detail[:77] + "..."
        else:
            status = "⚠️ Error"
            err = info.get("error") or "unknown error"
            detail = err[:77] + "..." if len(err) > 80 else err

        py_ver = info.get("python_version", "")
        patch = py_ver.split()[0] if py_ver else version
        rows.append(f"| {version} | {patch} | {status} | {detail} |")

    header = (
        "| Minor | Exact version | Has tkinter? | Notes |\n"
        "|-------|---------------|:------------:|-------|\n"
    )
    return header + "\n".join(rows) + "\n"


def render_channel_section(
    source_key: str,
    display_label: str,
    data: dict,
) -> str:
    """Render a h3 section for one channel on an OS page."""
    # Use the actual source recorded in the file (e.g. pyenv-win) rather than
    # the generic channel key, so the label and note are always accurate.
    actual_source = data.get("source", source_key)
    results = data.get("results", {})
    generated_at = fmt_generated_at(data.get("generated_at"))
    link = SOURCE_LINKS.get(actual_source, SOURCE_LINKS.get(source_key, ""))
    note = SOURCE_NOTES.get(actual_source, SOURCE_NOTES.get(source_key, ""))
    name = SOURCE_DISPLAY_NAMES.get(actual_source, display_label)
    linked_label = f"[{name}]({link})" if link else name

    table = format_version_table(results)

    no_data = ""
    if not results:
        no_data = "\n> No data collected yet for this channel.\n"

    return f"""\
### {linked_label}

> {note}

Data collected: {generated_at}
{no_data}
{table}"""


def generate_os_page(os_key: str) -> None:
    os_name = OS_NAMES[os_key]
    sortorder = {"windows": 2, "macos": 3, "linux": 4}[os_key]

    channel_sections = []
    any_missing = False

    for source_key, suffix, display_label, _ in CHANNELS:
        data = load_channel_data(os_key, suffix)
        if not data:
            continue
        results = data.get("results", {})
        if any(info.get("has_tkinter") is False for info in results.values()):
            any_missing = True
        channel_sections.append(
            render_channel_section(source_key, display_label, data)
        )

    channels_body = "\n\n".join(channel_sections) if channel_sections else (
        "_No data collected yet for this platform._\n"
    )

    recs = MISSING_RECOMMENDATIONS.get(os_key, {})
    default_rec = recs.get("default", "See the fix page for instructions.")
    uv_rec = recs.get("uv", "")

    fix_section = ""
    if any_missing:
        fix_section = f"""
## When tkinter Is Missing

**Official installer / system Python:** {default_rec}

**uv-managed Python:** {uv_rec}

See the [Fix Missing TkInter]({{filename}}fix.md) page for full instructions.
"""

    content = f"""\
Title: TkInter on {os_name}
save_as: {os_key}/index.html
url: {os_key}/
Date: {TODAY}
Slug: {os_key}
sortorder: {sortorder}
Summary: Which Python versions include tkinter on {os_name}?

# TkInter Availability on {os_name}

Results are shown separately for each Python distribution channel —
the same version number can behave differently depending on where Python came from.
See the [channels overview]({{filename}}home.md#python-distribution-channels) for background.

## By Channel

{channels_body}
{fix_section}"""

    out = CONTENT_DIR / f"{os_key}.md"
    out.write_text(content, encoding="utf-8")
    print(f"  Wrote {out}")


def build_matrix_table() -> str:
    """Matrix table using only the primary (uv-managed) channel."""
    all_versions: set[str] = set()
    per_os: dict[str, dict] = {}

    for os_key in OS_ORDER:
        data = load_channel_data(os_key, "")
        results = data.get("results", {})
        per_os[os_key] = results
        all_versions.update(results.keys())

    versions_sorted = sorted(all_versions, key=version_sort_key)

    header_cells = " | ".join(f"**{OS_NAMES[k]}**" for k in OS_ORDER)
    header = f"| Version | {header_cells} |\n"
    sep_cells = " | ".join(":-----------:" for _ in OS_ORDER)
    sep = f"|---------|{sep_cells}|\n"

    rows = []
    for v in versions_sorted:
        cells = []
        for os_key in OS_ORDER:
            info = per_os[os_key].get(v)
            if info is None:
                cells.append("—")
            elif info.get("has_tkinter") is True:
                tk_ver = info.get("tk_version") or "?"
                cells.append(f"✅ Tk {tk_ver}")
            elif info.get("has_tkinter") is False:
                cells.append("❌ No")
            else:
                cells.append("⚠️ Err")
        rows.append("| " + v + " | " + " | ".join(cells) + " |")

    return header + sep + "\n".join(rows) + "\n"


def generate_home_page() -> None:
    matrix_table = build_matrix_table()

    content = f"""\
Title: Where is TkInter?
save_as: index.html
url:
Date: {TODAY}
Slug: home
sortorder: 1
Summary: Which Python versions include tkinter on Windows, macOS, and Linux?

## Availability Matrix

Quick reference for **uv / python-build-standalone** (the Python that uv, rye, and Hatch
download automatically). Results for python.org installers, pyenv, or system packages
will differ — per-platform pages show a separate table for each channel.

{matrix_table}

Legend: ✅ = tkinter present &nbsp; ❌ = missing &nbsp; ⚠️ = probe error &nbsp; — = not yet tested

## Per-platform details

- [Windows]({{filename}}windows.md) — uv / python-build-standalone, pyenv
- [macOS]({{filename}}macos.md) — uv / python-build-standalone, pyenv
- [Linux]({{filename}}linux.md) — uv / python-build-standalone, pyenv
- [Docker images]({{filename}}docker.md) — bookworm, slim, alpine, windowsservercore

## Fix it

- [How to fix missing TkInter]({{filename}}fix.md) — step-by-step for every OS
- [Configure your project]({{filename}}configure.md) — pyproject.toml settings for uv, Poetry, pip, conda

## Quick diagnosis

```python
python -c "import tkinter; print(tkinter.TkVersion)"
```

If that raises `ModuleNotFoundError`, your Python was built or installed without Tcl/Tk support.
Pick your platform above to find out why and what to do.

{CHANNELS_EXPLAINER}

## About

**TkInter** is Python's standard GUI toolkit — but many Python distributions ship without it,
and it silently breaks at import time with no obvious fix.

"Where is TkInter?" tracks which Python versions, distributions, and Docker images include
tkinter, and how to get it when it's missing.
"""
    out = CONTENT_DIR / "home.md"
    out.write_text(content, encoding="utf-8")
    print(f"  Wrote {out}")


def generate_docker_page() -> None:
    path = DATA_DIR / "docker.json"
    if not path.exists():
        data = {}
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

    results = data.get("results", {})
    generated_at = fmt_generated_at(data.get("generated_at"))

    if not results:
        table = "_No data collected yet._\n"
    else:
        header = (
            "| Image tag | Variant | Has tkinter? | Confidence | Notes |\n"
            "|-----------|---------|:------------:|:----------:|-------|\n"
        )
        rows = []
        for version, variants in sorted(results.items()):
            for variant, info in sorted(variants.items()):
                tag = info.get("image_tag") or f"python:{version}-{variant}"
                has = info.get("has_tkinter")
                if has is True:
                    status = "✅ Yes"
                elif has is False:
                    status = "❌ No"
                else:
                    status = "⚠️ Unknown"
                conf = info.get("confidence") or "—"
                reasoning = info.get("reasoning") or ""
                if len(reasoning) > 70:
                    reasoning = reasoning[:67] + "..."
                rows.append(f"| `{tag}` | {variant} | {status} | {conf} | {reasoning} |")
        table = header + "\n".join(rows) + "\n"

    content = f"""\
Title: TkInter in Docker Python Images
save_as: docker/index.html
url: docker/
Date: {TODAY}
Slug: docker
sortorder: 5
Summary: Which official Docker Python images include tkinter, and how to add it when missing.

# TkInter in Docker Python Images

Data source: Dockerfiles in [docker-library/python](https://github.com/docker-library/python)
Data collected: {generated_at}

## Quick answer

| Variant family | Has tkinter? | Why |
|----------------|:------------:|-----|
| `bookworm` (full Debian 12) | ✅ Yes | `tk-dev` compiled in |
| `trixie` (full Debian 13) | ✅ Yes | `tk-dev` compiled in |
| `slim-bookworm` | ✅ Yes | `_tkinter.so` retained after slim cleanup |
| `slim-trixie` | ✅ Yes | `_tkinter.so` retained after slim cleanup |
| `alpine3.x` | ❌ No | `py3-tk` not installed |
| `windowsservercore` | ❌ No | No Tcl/Tk in Windows image build |

**Surprise:** slim images _do_ have tkinter. The `tk-dev` build dependency is removed
after compilation, but the compiled `_tkinter.so` stays in the image.

**Alpine** and **Windows Server Core** images do not have tkinter. This is the
most common reason tkinter-dependent tests fail in CI.

## Full table

{table}

## Adding tkinter to an Alpine image

```dockerfile
FROM python:3.13-alpine3.23

RUN apk add --no-cache py3-tk tcl-dev tk-dev
```

## Adding tkinter to a Windows Server Core image

There is no pre-built package. You need to build Python from source with Tcl/Tk,
or use the `bookworm`/`slim-bookworm` Linux image instead (which works fine in
Linux containers on Windows Docker Desktop).

## Headless tkinter for CI testing

Even when tkinter is present, a display is required to create windows.
In headless CI environments (GitHub Actions, Docker), use a virtual display:

```dockerfile
# Debian/Ubuntu-based images
RUN apt-get update && apt-get install -y --no-install-recommends xvfb
```

```bash
# In your test runner / entrypoint
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
pytest
```

Or use the `pytest-xvfb` plugin which handles this automatically.

## Recommended images for tkinter-dependent projects

If you need tkinter in Docker, use:

```
python:3.13-slim-bookworm   # small footprint, has tkinter
python:3.13-bookworm        # full image, has tkinter
```

Avoid `alpine` and `windowsservercore` for tkinter-dependent code.
"""
    out = CONTENT_DIR / "docker.md"
    out.write_text(content, encoding="utf-8")
    print(f"  Wrote {out}")


def generate_pyproject_page() -> None:
    content = f"""\
Title: Configuring Your Project for TkInter
save_as: configure/index.html
url: configure/
Date: {TODAY}
Slug: configure
sortorder: 7
Summary: How to configure pyproject.toml and package managers to pick a Python with tkinter.

# Configuring Your Project for TkInter

{PYPROJECT_GUIDANCE}
"""
    out = CONTENT_DIR / "configure.md"
    out.write_text(content, encoding="utf-8")
    print(f"  Wrote {out}")


def main() -> None:
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating pages...")
    generate_home_page()
    for os_key in OS_ORDER:
        generate_os_page(os_key)
    generate_docker_page()
    generate_pyproject_page()
    print("Done.")


if __name__ == "__main__":
    main()
