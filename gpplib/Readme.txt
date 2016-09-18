============================
Glider Path Planning Library
============================

Contains a library of path planning routines. Currently the types of planners 
supported are:
1. Heuristic planners such as A*
2. Markov Decision Process based planner

The planners are available in C++ and Python. The C++ planner classes have also got Python equivalents.

This repository also has a small Matlab based ROMS data download code-base, as well as routines to utilize ROMS data in Python
which has been downloaded using the Matlab ROMS download code.

===================
Directory Structure
===================

The directory structure (when first downloaded) is as follows:
gpplib
    - RomsMatlab -> Matlab files mainly for Roms data download from JPL's Thredds server.
    - gpplib -> Installable Glider Path Planning Library
    	- docs -> Documentation files (needs compilation and Doxygen+Sphinx).
    	- gpp_in_cpp -> C++ modules for Glider path planning which use Boost.
    	- gpplib -> Glider Path Planning Library in Python.
    - GppPython -> Python files that use gpplib and/or gpp_in_cpp
    - DbdMatlab -> Files to process 'real' glider data in Matlab
    - gliderDataProcessing -> Source code for processing DBD/EBD files (from Teledyne Webbresearch)


============================================
ROMS data download, processing and placement
============================================

This planner is primarily for Ocean-going slow-moving underwater vehicles. We simulate these
vehicles in Regional Ocean Model current fields, which we need to have access to. There are a few steps
which are required to get from having this code to being able to run the more advanced planners:

    1. We need ROMS data! For this, we run code within RomsMatlab. This is fairly simple to do. 
    Just modify SaveRomsData.m to specify the appropriate date range, lat-lon range etc. and let it run. 
    If JPL is hosting this data, it will download it from their server.
    
    2. We need to convert to the format our planner uses internally called the "sfcst_" file. This
    file is basically a Matlab .mat file which contains only ocean current data within a specified
    region (N,S,E,W) and for some hours (usually in 24 hr increments). The RomsMatlab directory
    has a script for doing this automatically, if you point it to the directory where SaveRomsData.m 
    stored your data files.
    
	3. Once this data has been placed somewhere, update config.py to point to it. The Makefile
	automatically makes a "config.shelf" which is used by all the other programs. We recommend
	that you add other configuration parameters to config.py if you need them.
	You may then subclass gpplib.Utils.GppConfig to get your configuration variables.

2012 (c) Arvind A. de Menezes Pereira <arvind.pereira@gmail.com> .
