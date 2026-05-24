Title: Where is TkInter?
save_as: index.html
url:
Date: 2026-05-24
Slug: home
sortorder: 1
Summary: Which Python versions include tkinter on Windows, macOS, and Linux?

## Availability Matrix

Quick reference for **uv / python-build-standalone** (the Python that uv, rye, and Hatch
download automatically). Results for python.org installers, pyenv, or system packages
will differ — per-platform pages show a separate table for each channel.

| Version | **Windows** | **macOS** | **Linux** |
|---------|:-----------: | :-----------: | :-----------:|
| 3.8 | ✅ Tk 8.6.9 | — | ✅ Tk 8.6.12 |
| 3.9 | ✅ Tk 8.6.12 | — | ✅ Tk 8.6.14 |
| 3.10 | ✅ Tk 8.6.12 | — | ✅ Tk 9.0.3 |
| 3.11 | ✅ Tk 8.6.12 | — | ✅ Tk 9.0.3 |
| 3.12 | ✅ Tk 8.6.15 | — | ❌ No |
| 3.13 | ✅ Tk 8.6.12 | — | ✅ Tk 9.0.3 |
| 3.14 | ✅ Tk 8.6.15 | — | ✅ Tk 9.0.3 |


Legend: ✅ = tkinter present &nbsp; ❌ = missing &nbsp; ⚠️ = probe error &nbsp; — = not yet tested

## Per-platform details

- [Windows]({filename}windows.md) — uv / python-build-standalone, pyenv
- [macOS]({filename}macos.md) — uv / python-build-standalone, pyenv
- [Linux]({filename}linux.md) — uv / python-build-standalone, pyenv
- [Docker images]({filename}docker.md) — bookworm, slim, alpine, windowsservercore

## Fix it

- [How to fix missing TkInter]({filename}fix.md) — step-by-step for every OS
- [Configure your project]({filename}configure.md) — pyproject.toml settings for uv, Poetry, pip, conda

## Quick diagnosis

```python
python -c "import tkinter; print(tkinter.TkVersion)"
```

If that raises `ModuleNotFoundError`, your Python was built or installed without Tcl/Tk support.
Pick your platform above to find out why and what to do.

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


## About

**TkInter** is Python's standard GUI toolkit — but many Python distributions ship without it,
and it silently breaks at import time with no obvious fix.

"Where is TkInter?" tracks which Python versions, distributions, and Docker images include
tkinter, and how to get it when it's missing.
