"""
Probe script: run inside ANY Python interpreter to test tkinter availability.
Outputs a single JSON object to stdout. Exit code is irrelevant to callers.

Usage:
    python probe_tkinter.py
    uv run --python 3.11 python probe_tkinter.py
"""

import json
import platform
import sys


def probe() -> dict:
    info = {
        "python_version": sys.version,
        "python_version_tuple": list(sys.version_info[:3]),
        "executable": sys.executable,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
        "has_tkinter": False,
        "tkinter_version": None,
        "tcl_version": None,
        "tk_version": None,
        "error": None,
    }

    try:
        import tkinter as tk

        info["has_tkinter"] = True
        info["tkinter_version"] = getattr(tk, "TkVersion", None)
        info["tcl_version"] = getattr(tk, "TclVersion", None)
        # Try to get Tk version string
        try:
            root = tk.Tk()
            root.withdraw()
            info["tk_version"] = root.tk.eval("info patchlevel")
            root.destroy()
        except Exception as e:
            info["tk_version"] = str(e)
    except ImportError as e:
        info["error"] = str(e)
    except Exception as e:
        info["has_tkinter"] = False
        info["error"] = str(e)

    return info


if __name__ == "__main__":
    result = probe()
    print(json.dumps(result, indent=2))
