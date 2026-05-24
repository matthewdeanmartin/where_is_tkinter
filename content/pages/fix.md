Title: How to Fix Missing TkInter
save_as: fix-missing-tkinter/index.html
url: fix-missing-tkinter/
Date: 2026-05-24
Slug: fix-missing-tkinter
sortorder: 6
Summary: Guides on how to install Tkinter on various operating systems.

# Fixing Missing TkInter

If you've encountered `ImportError: No module named '_tkinter'`, your Python installation is missing the necessary Tcl/Tk support.

## Linux (Ubuntu/Debian)

Run the following command:
```bash
sudo apt-get install python3-tk
```

## Linux (Fedora/CentOS/RHEL)

Run:
```bash
sudo dnf install python3-tkinter
```

## macOS

If you are using Homebrew:
```bash
brew install python-tk
```

## Windows

Tkinter is usually included with the official Python installer from python.org. If it's missing, you may need to re-run the installer and ensure "tcl/tk and IDLE" is selected in the optional features.
