PWD=$(shell pwd)
VIRTUALENV=dev
SITE_PACKAGES=$(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")
PYTHON=$(shell python -c "import sys; p = 'python2' if sys.version_info.major == 3 else 'python'; sys.stdout.write(p)")

all:
	@echo "Please choose:"
	@echo "make setup - initialize virtualenv and modules"
	@echo "make update - pull and update git submodules"
	@echo "make develop - (re)build a development environment (do \`. ./dev/bin/activate\` first)"

setup:
	virtualenv $(VIRTUALENV) -p $(PYTHON) --system-site-packages
	git submodule update --init
	$(shell echo $$SHELL) -c "source $(VIRTUALENV)/bin/activate; make develop"
	@echo "export CREAM_VERBOSITY=5" >> $(VIRTUALENV)/bin/activate

update:
	git pull
	git submodule update --init

develop:
	rm -rf $(SITE_PACKAGES)/cream
	python repos/tools/build_tree.py
	$(shell echo $$SHELL) -c "cd repos/melange-widgets; python setup.py install"

.phony: all setup update develop
