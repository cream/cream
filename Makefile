PWD=$(shell pwd)
VIRTUALENV=dev
SITE_PACKAGES=$(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")

all:
	@echo "Please choose:"
	@echo "make setup - initialize virtualenv and modules"
	@echo "make update - pull and update git submodules"
	@echo "make develop - (re)build a development environment (do \`. ./dev/bin/activate\` first)"

pyjavascriptcore:
	bzr clone lp:pyjavascriptcore
	cd pyjavascriptcore && python setup.py install

bjoern:
	git clone git://github.com/jonashaag/bjoern.git

update-bjoern: bjoern
	cd bjoern/ && git pull && python setup.py install

setup:
	virtualenv $(VIRTUALENV)
	git submodule update --init
	ln -s $(PWD)/data/melange-widgets $(PWD)/src/modules/melange/widgets
	$(shell echo $$SHELL) -c "source $(VIRTUALENV)/bin/activate; make _setup2"

_setup2:
	easy_install ooxcb
	make pyjavascriptcore
	make bjoern update-bjoern
	make develop

update:
	git pull
	git submodule update

develop:
	rm -rf $(SITE_PACKAGES)/cream
	python tools/build_tree.py
	python tools/build_tree.py

.phony: all setup update develop update-bjoern
