Matlab code to download ROMS data.
----------------------------------

This code requires MATLAB as well as the DAP software for Matlab which can be downloaded from:
http://www.opendap.org/download
Specifically, you want to install loaddap, and the library it depends upon -> libdap.

The files in this directory are primarily designed to download ROMS data from the JPL server hosting
the ROMS data files.

To download the actual ROMS data in it's entirety for a day, modify the script "SaveRomsData.m" 
to indicate the date range you need the data for, and then run it.

It will download all the data from the ROMS forecast in files called "fcst_yyyymmdd_seqNum.mat".

seqNum will be 0, 1, ... since ROMS has 72 hours of data and we store 0-23, 24-47, 48-71, 72 hour data in each fcst file.

After the data has been downloaded, it is possible to pick a subset of this data and store it in a 
smaller sfcst_yyyymmdd_seqNum.dat file for actual use in planners and so on. To do this modify and run "SaveAllRomsData.m"

