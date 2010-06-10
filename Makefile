VIRTUALENV=dev
SITE_PACKAGES=$(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")

all:
	@echo "Please choose:"
	@echo "make setup - initialize virtualenv, download bjoern."
	@echo "make update - update git submodules"
	@echo "make develop - build a development environment (do \`. ./dev/bin/activate\` first)"

bjoern:
	git clone git://github.com/jonashaag/bjoern.git
	echo $(SITE_PACKAGES)

update-bjoern: bjoern
	cd bjoern/ && git pull && python setup.py install

setup1:
	virtualenv $(VIRTUALENV)
	git submodule update --init

setup2:
	easy_install ooxcb
	make bjoern
	make develop

update:
	git pull
	git submodule update

develop:
	rm -rf $(SITE_PACKAGES)/cream
	python tools/build_tree.py
	python tools/build_tree.py

.phony: all setup update develop update-bjoern
