# Where Is TkInter?

A reference site tracking which Python versions and distributions include
tkinter on Windows, macOS, and Linux — and how to fix it when it's missing.

## How it works

1. **`gather_data.py`** — run on each target OS to probe Python versions via uv.
   Results are saved to `data/<os>.json` and committed to the repo.
   Published Python versions don't change, so results only need to be collected once
   per version/OS combination.

2. **`generate_pages.py`** — reads the data files and writes Pelican `.md` pages
   into `content/pages/`. Run this before building the site.

3. **Pelican** — renders the site from `content/` to `output/`.

## Quick start

```bash
# Install dependencies
uv sync

# Probe all Python versions on the current OS (skip already-recorded ones)
make gather

# Generate content pages from all collected data
make generate-pages

# Build the site
make html

# Or do the last two in one shot
make build
```

## Gathering data on a new OS

```bash
# Clone the repo, then:
uv sync
make gather
git add data/
git commit -m "chore: gather data on <os>"
git push
```

The `gather` workflow in `.github/workflows/gather.yml` automates this on a
monthly schedule across Windows, macOS, and Linux runners.

## Project layout

```
data/
  windows.json   # tkinter probe results for Windows (committed)
  macos.json     # ... macOS
  linux.json     # ... Linux

probe_tkinter.py    # lightweight probe — run inside any Python interpreter
gather_data.py      # orchestrates uv to test many Python versions
generate_pages.py   # converts data/*.json → content/pages/*.md

content/
  pages/
    about.md          # hand-written
    fix.md            # hand-written
    # windows.md, macos.md, linux.md, matrix.md, configure.md  ← generated

themes/simple-pages/  # minimal Pelican theme
```

## Adding a new Python version

Edit `DEFAULT_VERSIONS` in `gather_data.py`, re-run `make gather` on each OS,
commit the updated data files, then `make build`.
