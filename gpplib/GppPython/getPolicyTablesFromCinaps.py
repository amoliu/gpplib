#!/usr/bin/env python

from os import system
from gpplib.Utils import GppConfig

conf = GppConfig()
policyTableLocation = conf.myDataDir+'PolicyTables/'
rsyncCmd = 'rsync -avz -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/PolicyTables/ %s'%(policyTableLocation) 
print rsyncCmd
system( rsyncCmd )
