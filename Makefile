PWD=$(shell pwd)
TREE=$(PWD)/src
VIRTUALENV=dev
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
	@echo "export PYTHONPATH=$(TREE):\$$PYTHONPATH XDG_DATA_DIRS=$(TREE)/data:\$$XDG_DATA_DIRS" >> $(VIRTUALENV)/bin/activate

update:
	git pull
	git submodule update --init

develop:
	rm -rf $(TREE)
	$(PYTHON) repos/tools/build_tree.py $(PWD)/repos $(TREE)

.phony: all setup update develop
