#!/usr/bin/env python
import os,sys
import gpplib
from gpplib.Utils import *

conf = GppConfig()
rsyncCmd = 'rsync -avz ./gliderModelNS*.shelf -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/gliderModelNS/'
print rsyncCmd
os.system(rsyncCmd)

rsyncCmd = 'rsync -avz ./gliderModelGP2*.shelf -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/NoisyGliderModels/'
print rsyncCmd
os.system(rsyncCmd)

rsyncCmd = 'rsync -avz ./gliderModel3*.shelf -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/NoisyGliderModels/'
print rsyncCmd
os.system(rsyncCmd)
