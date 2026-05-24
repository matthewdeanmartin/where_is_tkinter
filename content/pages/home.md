Title: Where is TkInter?
save_as: index.html
url:
Date: 2026-05-24
Slug: home
sortorder: 1
Summary: Which Python versions include tkinter on Windows, macOS, and Linux?

## Availability Matrix

Quick reference: which Python versions have tkinter on each platform.

| Version | **Windows** | **macOS** | **Linux** |
|---------|:-----------: | :-----------: | :-----------:|
| 3.8 | ✅ Tk 8.6.9 | — | ✅ Tk 8.6.12 |
| 3.9 | ✅ Tk 8.6.12 | — | ✅ Tk 8.6.14 |
| 3.10 | ✅ Tk 8.6.12 | — | ✅ Tk 9.0.3 |
| 3.11 | ✅ Tk 8.6.12 | — | ✅ Tk 9.0.3 |
| 3.12 | ❌ No | — | ❌ No |
| 3.13 | ✅ Tk 8.6.12 | — | ✅ Tk 9.0.3 |
| 3.14 | ✅ Tk 8.6.15 | — | ✅ Tk 9.0.3 |


Legend: ✅ = tkinter present &nbsp; ❌ = missing &nbsp; ⚠️ = probe error &nbsp; — = not yet tested

## Per-platform details

- [Windows]({filename}windows.md) — python.org installer, uv-managed Python
- [macOS]({filename}macos.md) — python.org, Homebrew, uv
- [Linux]({filename}linux.md) — system packages, uv, pyenv
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

## About

**TkInter** is Python's standard GUI toolkit — but many Python distributions ship without it,
and it silently breaks at import time with no obvious fix.

"Where is TkInter?" tracks which Python versions, distributions, and Docker images include
tkinter, and how to get it when it's missing.
