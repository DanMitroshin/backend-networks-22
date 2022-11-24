PIP = ./venv/bin/pip
PIP_COMPILE = ./venv/bin/pip-compile
PYTHON = ./venv/bin/python


venv:
	python -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install pip-tools

compile_requirements:
	$(PIP_COMPILE) requirements.in

install_requirements:
	$(PIP) install -r requirements.txt

migrate:
	$(PYTHON) manage.py migrate

run:
	$(PYTHON) manage.py runserver --settings APIBackendService.settings.development 0.0.0.0:7002

run_production:
	$(PYTHON) manage.py runserver --settings APIBackendService.settings.production