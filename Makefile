all:
	@echo "Please choose:"
	@echo "make develop - build a development environment (to be used in a virtualenv)"
develop:
	rm -rf $(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_python_lib()")/cream
	python tools/build_tree.py
	python tools/build_tree.py
