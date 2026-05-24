UV ?= uv
PELICANOPTS=
GHA_WORKFLOWS := .github/workflows

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
	@echo 'GitHub Actions maintenance:'
	@echo '   make gha-validate      parse workflows and run zizmor'
	@echo '   make gha-pin           pin GitHub Actions refs to commit SHAs'
	@echo '   make gha-upgrade       pin and validate GitHub Actions workflows'
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

# ── GitHub Actions maintenance ───────────────────────────────────────────────

gha-validate:
	@echo 'Validating GitHub Actions workflows'
	@$(UV) run --with pyyaml python -c "from pathlib import Path; import yaml; workflows=sorted(Path('$(GHA_WORKFLOWS)').glob('*.yml')); [yaml.safe_load(path.read_text(encoding='utf-8')) for path in workflows]; print(f'YAML parse OK: {len(workflows)} workflow(s)')"
	@$(UV) run --with pyyaml python -c "from pathlib import Path; import yaml; data=yaml.safe_load(Path('$(GHA_WORKFLOWS)/deploy.yml').read_text(encoding='utf-8')); build_steps=data['jobs']['build']['steps']; deploy_steps=data['jobs']['deploy']['steps']; upload=next(step for step in build_steps if step.get('uses', '').startswith('actions/upload-pages-artifact@')); deploy=next(step for step in deploy_steps if step.get('uses', '').startswith('actions/deploy-pages@')); assert upload['with']['path'] == './output'; assert deploy['id'] == 'deployment'; print('Pages deploy workflow OK:', upload['uses'], '->', deploy['uses'])"
	@$(UV) run --with pyyaml python -c "from pathlib import Path; import yaml; data=yaml.safe_load(Path('$(GHA_WORKFLOWS)/gather.yml').read_text(encoding='utf-8')); steps=data['jobs']['gather']['steps']; upload=next(step for step in steps if step.get('uses', '').startswith('actions/upload-artifact@')); assert upload['with']['name'] == 'data-$${{ matrix.os_key }}'; assert upload['with']['path'] == 'data/$${{ matrix.os_key }}.json'; print('Gather workflow OK:', upload['uses'])"
	@uvx zizmor --no-progress $(GHA_WORKFLOWS)

gha-pin:
	@echo 'Pinning GitHub Actions to current commit SHAs'
	@$(UV) run python -c "import os, subprocess; token=os.environ.get('GITHUB_TOKEN') or subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip(); assert token, 'Set GITHUB_TOKEN or run: gh auth login'; env=dict(os.environ, GITHUB_TOKEN=token); raise SystemExit(subprocess.run(['uvx', 'gha-update'], env=env).returncode)"

gha-upgrade: gha-pin gha-validate
	@echo 'GitHub Actions upgrade complete'


.PHONY: help gather gather-force gather-dry-run gather-docker generate-pages build \
        html clean regenerate serve devserver publish gha-validate gha-pin gha-upgrade
