#!/usr/bin/env python
import os,sys
import gpplib
from gpplib.Utils import *

conf = GppConfig()
# Get Roms-based transition models
# and put them onto Cinaps...
rsyncCmd = 'rsync -avz -e \"ssh -l arvind\" 192.168.0.188:~/code/gpplib/GppPython/gliderModel*.shelf %s/NoisyGliderModels4/'%(conf.myDataDir)
rsyncCmd = 'rsync -avz -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/NoisyGliderModels/gliderModel*.shelf %s/NoisyGliderModels4/'%(conf.myDataDir)
print rsyncCmd
os.system(rsyncCmd)


# ---- Get Roms data from Cinaps -----
romsRsyncCmd = 'rsync -avz -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms3/sfcst_201207*.mat %s/roms/'%(conf.myDataDir)
print romsRsyncCmd
os.system(romsRsyncCmd)
romsRsyncCmd = 'rsync -avz -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms3/sfcst_201209*.mat %s/roms/'%(conf.myDataDir)
print romsRsyncCmd
os.system(romsRsyncCmd)
