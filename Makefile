VIRTUALENV=dev

all:
	@echo "Please choose:"
	@echo "make setup - initialize a virtualenv"
	@echo "make init - initialize git submodules"
	@echo "make update - update git submodules"
	@echo "make develop - build a development environment (do \`make env\` first)"

setup:
	virtualenv $(VIRTUALENV)

init:
	git submodule update --init

update:
	git submodule update

develop:
	rm -rf $(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")/cream
	python tools/build_tree.py
	python tools/build_tree.py

