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
	$(shell echo $$SHELL) -c "source $(VIRTUALENV)/bin/activate; make _setup2"
	@echo "export CREAM_EXECUTION_MODE=development" >> $(VIRTUALENV)/bin/activate
	@echo "export CREAM_VERBOSITY=5" >> $(VIRTUALENV)/bin/activate

_setup2:
	easy_install ooxcb
	make develop

update:
	git pull
	git submodule update --init

develop:
	rm -rf $(SITE_PACKAGES)/cream
	python tools/build_tree.py
	$(shell echo $$SHELL) -c "cd data/melange-widgets; python setup.py install"

.phony: all setup update develop
