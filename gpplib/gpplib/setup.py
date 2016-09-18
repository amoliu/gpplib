import os
from setuptools import setup, Extension
#from distutils.core import setup

setup(
    name='gpplib',
    version='1.0.1a',
    author='Arvind A. de Menezes Pereira',
    author_email='arvind.pereira@gmail.com',
    packages=['gpplib','gpp_in_cpp'],
    url='http://git.robotics.usc.edu/resl-aquatic/gpplib',
    license='LICENSE.txt',
    description='Glider path planning library.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.5.0",
        "matplotlib >= 1.0",
        "scipy >= 0.8.0",
        "networkx >= 1.6",
        "Sphinx >= 1.0.0"
    ],
    classifiers=[
	"Development Status :: 3 - Alpha",
	"Topic :: Path Planning",
	"License :: MIT License",
    ],
    ext_modules=[
	Extension('gpp_in_cpp.ImgMap',
	   	['gpp_in_cpp/MyImageMap.cpp'],
	   	include_dirs=['gpp_in_cpp'],
	   	library_dirs=['/',],
      		libraries=['boost_python'],
		extra_compile_args=['-g']
	      ),
	   ],
)
