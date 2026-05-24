Title: How to Fix Missing TkInter
save_as: fix-missing-tkinter/index.html
url: fix-missing-tkinter/
Date: 2026-05-24
Slug: fix-missing-tkinter
sortorder: 6
Summary: How to fix missing tkinter on Windows, Linux, and macOS without skipping Python versions.

# How to Fix Missing TkInter

`ModuleNotFoundError: No module named 'tkinter'` means your Python was built or installed
without Tcl/Tk support. You don't need to switch Python versions — tkinter can be added to
an existing installation.

## Windows

Tkinter ships with the python.org installer but is an optional component that may not have
been selected. Fix it without reinstalling from scratch:

1. Open **Add or Remove Programs** → find **Python 3.x**
2. Click **Modify**
3. On the *Optional Features* screen, tick **tcl/tk and IDLE**
4. Click **Next** → **Install**

Verify:
```
python -c "import tkinter; print(tkinter.TkVersion)"
```

**If you installed Python via uv:** uv uses python-build-standalone, which does not include
Tcl/Tk. Install Python from [python.org](https://www.python.org/downloads/) instead and
point uv at it:

```toml
# pyproject.toml
[tool.uv]
python-preference = "only-system"
```

Or pin explicitly: `uv python pin C:/Python312/python.exe`

## Linux (Debian / Ubuntu)

Tkinter is a separate package. Install it for your Python version:

```bash
# Python 3.12
sudo apt install python3.12-tk

# Or for the default python3
sudo apt install python3-tk
```

No reinstall needed — this patches the existing interpreter in place.

## Linux (Fedora / RHEL / CentOS)

```bash
# Python 3.12 specifically
sudo dnf install python3.12-tkinter

# Or for the default python3
sudo dnf install python3-tkinter
```

On older RHEL/CentOS you may need to enable the `powertools` or `crb` repo first:
```bash
sudo dnf config-manager --enable crb
sudo dnf install python3.12-tkinter
```

**If you installed Python via uv or pyenv:** the interpreter was compiled without Tcl/Tk
headers. Install the system tkinter package and use the system Python, or install the
Tcl/Tk dev headers and recompile:

```bash
# Debian/Ubuntu — install headers then recompile via pyenv
sudo apt install tk-dev
pyenv install 3.12.10

# Fedora/RHEL
sudo dnf install tk-devel
pyenv install 3.12.10
```

## macOS

**Homebrew Python:**
```bash
brew install python-tk@3.12
```

**python.org installer:** Download the latest 3.12.x pkg from
[python.org](https://www.python.org/downloads/macos/) — it bundles Tcl/Tk.

**uv-managed Python:** Same issue as Linux — python-build-standalone lacks Tcl/Tk.
Install from python.org or Homebrew and set `python-preference = "only-system"`.

## Verifying the fix

```python
python -c "import tkinter; print(tkinter.TkVersion)"
```

Should print a version number like `8.6` or `9.0`. If it still raises `ModuleNotFoundError`,
double-check that the `python` on your PATH is the same interpreter you installed tkinter for:

```bash
which python   # or: where python  (Windows)
python -c "import sys; print(sys.executable)"
```
