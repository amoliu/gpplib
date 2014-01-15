# Makefile for creating or cleaning up gpplib.
# @author: Arvind A de Menezes Pereira
# @date: May-15-2012
all:
	python setup.py build
	# Make C++ documentation
	if command -v doxygen; then cd gpp_in_cpp && doxygen Doxyfile && cd ..; \
        else echo "Doxygen not found. Not making documentation."; fi
	# Make Python documentation in Sphinx
	cd docs && make html && cd ..
	#python setup.py install
	# Not installing via this make. Please run "make install" or "sudo make install" instead.

clean:
	python setup.py clean
	rm -rf dist/
	rm -rf build/
	rm -rf gpplib.egg-info/
	cd docs && make clean && rm -rf html/ && cd ..
