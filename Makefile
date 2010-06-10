PWD=$(shell pwd)
VIRTUALENV=dev
SITE_PACKAGES=$(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")

all:
	@echo "Please choose:"
	@echo "make setup1 - initialize virtualenv and modules"
	@echo "make setup2 - initialize modules, call this after \`. ./dev/bin/activate\`)"
	@echo "make update - update git submodules"
	@echo "make develop - build a development environment (do \`. ./dev/bin/activate\` first)"

bjoern:
	git clone git://github.com/jonashaag/bjoern.git

update-bjoern: bjoern
	cd bjoern/ && git pull && python setup.py install

setup1:
	virtualenv $(VIRTUALENV)
	git submodule update --init
	ln -s $(PWD)/data/melange-widgets $(PWD)/src/modules/melange/widgets

setup2:
	easy_install ooxcb
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
