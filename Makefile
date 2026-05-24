PELICANOPTS=

BASEDIR=$(CURDIR)
INPUTDIR=$(BASEDIR)/content
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py
PUBLISHCONF=$(BASEDIR)/publishconf.py

DEBUG ?= 0
ifeq ($(DEBUG), 1)
	PELICANOPTS += -D
endif

RELATIVE ?= 0
ifeq ($(RELATIVE), 1)
	PELICANOPTS += --relative-urls
endif

help:
	@echo 'Makefile for the "Where is TkInter?" site'
	@echo ''
	@echo 'Data collection (run on each target OS, then commit data/ to git):'
	@echo '   make gather            probe all Python versions on this OS'
	@echo '   make gather-force      re-probe even versions already in data/'
	@echo '   make gather-dry-run    show what would be probed without running'
	@echo '   make gather-docker     fetch Docker image data from Dockerfiles on GitHub'
	@echo ''
	@echo 'Page generation (run after data/ is up-to-date):'
	@echo '   make generate-pages    generate Pelican .md pages from data/ JSON'
	@echo ''
	@echo 'Site build:'
	@echo '   make html              (re)generate the web site'
	@echo '   make build             generate-pages + html (full pipeline)'
	@echo '   make clean             remove the generated files'
	@echo '   make regenerate        regenerate files upon modification'
	@echo '   make serve [PORT=8000] serve site at http://localhost:8000'
	@echo '   make devserver         serve and auto-regenerate on change'
	@echo '   make publish           generate using production settings'
	@echo ''
	@echo 'Set DEBUG=1 to enable Pelican debug output.'
	@echo ''

# ── Data collection ────────────────────────────────────────────────────────────

gather:
	uv run python gather_data.py

gather-force:
	uv run python gather_data.py --force

gather-dry-run:
	uv run python gather_data.py --dry-run

gather-docker:
	uv run python gather_docker.py

# ── Page generation ────────────────────────────────────────────────────────────

generate-pages:
	uv run python generate_pages.py

# ── Full pipeline ──────────────────────────────────────────────────────────────

build: generate-pages html

# ── Pelican site build ─────────────────────────────────────────────────────────

html:
	uv run pelican "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

clean:
	[ ! -d "$(OUTPUTDIR)" ] || rm -rf "$(OUTPUTDIR)"

regenerate:
	uv run pelican -r "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

serve:
	uv run pelican -l "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

devserver:
	uv run pelican -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS)

publish:
	uv run pelican "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(PUBLISHCONF)" $(PELICANOPTS)


.PHONY: help gather gather-force gather-dry-run gather-docker generate-pages build \
        html clean regenerate serve devserver publish
