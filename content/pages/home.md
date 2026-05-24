Title: Where is TkInter?
save_as: index.html
url:
Date: 2026-05-24
Slug: home

**TkInter** is Python's standard GUI toolkit — but many Python distributions ship without it, and it silently breaks at import time with no obvious fix.

This site tracks which Python versions, distributions, and Docker images include tkinter, and how to get it when it's missing.

## Browse by source

- [Windows]({filename}windows.md) — python.org installer, uv-managed Python
- [macOS]({filename}macos.md) — python.org, Homebrew, uv
- [Linux]({filename}linux.md) — system packages, uv, pyenv
- [Docker images]({filename}docker.md) — bookworm, slim, alpine, windowsservercore
- [Cross-platform matrix]({filename}matrix.md) — all versions and platforms at a glance

## Fix it

- [How to fix missing TkInter]({filename}fix.md) — step-by-step for every OS
- [Configure your project]({filename}configure.md) — pyproject.toml settings for uv, Poetry, pip, conda

## Quick diagnosis

```python
python -c "import tkinter; print(tkinter.TkVersion)"
```

If that raises `ModuleNotFoundError`, your Python was built or installed without Tcl/Tk support. Pick your platform above to find out why and what to do.
