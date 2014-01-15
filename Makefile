# @author : Arvind A de Menezes Pereira
# @summary: Makefile for the entire Glider Path Planning Library 
#     Before running this ensure that you have all the dependencies such as Python, Boost etc.
#     Also, you need to configure the data directories in gppConf.py in this directory

all:
	# First run gppConf.py
	python config.py

	# Now, go to the gpplib directory and make it
	cd gpplib && make && cd ..


install:
	# Attempt to install the python libraries
	cd gpplib && python setup.py install && cd ..

home_install:
	# Install locally instead. Please ensure that you have your local site-packages
	# directory in your PYTHON_PATH
	cd gpplib && python setup.py install --prefix=~ && cd ..


clean:
	cd gpplib && make clean && cd ..
	rm config.shelf
