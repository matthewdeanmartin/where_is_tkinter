Title: Where is TkInter?
save_as: index.html
url:
Date: 2026-05-24
Slug: home

**TkInter** is Python's standard GUI toolkit — but many Python distributions ship without it, and it silently breaks at import time with no obvious fix.

This site tracks which Python versions, distributions, and Docker images include tkinter, and how to get it when it's missing.

## Browse by source

- [Windows](/windows/) — python.org installer, uv-managed Python
- [macOS](/macos/) — python.org, Homebrew, uv
- [Linux](/linux/) — system packages, uv, pyenv
- [Docker images](/docker/) — bookworm, slim, alpine, windowsservercore
- [Cross-platform matrix](/matrix/) — all versions and platforms at a glance

## Fix it

- [How to fix missing TkInter](/fix-missing-tkinter/) — step-by-step for every OS
- [Configure your project](/configure/) — pyproject.toml settings for uv, Poetry, pip, conda

## Quick diagnosis

```python
python -c "import tkinter; print(tkinter.TkVersion)"
```

If that raises `ModuleNotFoundError`, your Python was built or installed without Tcl/Tk support. Pick your platform above to find out why and what to do.
