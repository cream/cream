PWD=$(shell pwd)
VIRTUALENV=dev
SITE_PACKAGES=$(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")
PYTHON=$(shell python -c "import sys; p = 'python2' if sys.version_info.major == 3 else 'python'; sys.stdout.write(p)")

all:
	@echo "Please choose:"
	@echo "make setup - initialize virtualenv and modules"
	@echo "make update - pull and update git submodules"
	@echo "make develop - (re)build a development environment (do \`. ./dev/bin/activate\` first)"

pyjavascriptcore:
	bzr clone lp:~fredreichbier/+junk/pyjavascriptcore

update-pyjavascriptcore: pyjavascriptcore
	cd pyjavascriptcore && bzr pull && python setup.py install

setup:
	virtualenv $(VIRTUALENV) -p $(PYTHON)
	git submodule update --init
	rm -rf $(PWD)/data/melange-widgets/src $(PWD)/src/modules/melange/src/data/widgets
	ln -T -s $(PWD)/data/melange-widgets/src $(PWD)/src/modules/melange/src/data/widgets
	$(shell echo $$SHELL) -c "source $(VIRTUALENV)/bin/activate; make _setup2"
	@echo "export CREAM_EXECUTION_MODE=development" >> $(VIRTUALENV)/bin/activate
	@echo "export CREAM_VERBOSITY=5" >> $(VIRTUALENV)/bin/activate

_setup2:
	easy_install ooxcb
	easy_install bjoern
	make pyjavascriptcore update-pyjavascriptcore
	make develop

update:
	git pull
	git submodule update --init

develop:
	rm -rf $(SITE_PACKAGES)/cream
	python tools/build_tree.py
	python tools/build_tree.py

.phony: all setup update develop update-bjoern
