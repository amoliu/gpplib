import sys, os
import datetime
import time
import gpplib
from gpplib.Utils import *
from RomsFTP import RomsFTP

# matlab -nodesktop -nosplash -nojvm -r "cd /Users/arvind/git/gpplib/RomsMatlab/;SaveRomsData;exit;"

conf = gpplib.Utils.GppConfig()

PathToMatRomsScripts = '/Users/arvind/gpplib/RomsMatlab/'
Data_Dir = '*.nc'
Remote_Data_Dir = '/mnt/data/storage/datasets/roms4/'

dr = DateRange(2013,4,26,2013,4,26)

# Now sync this data with Cinaps.
# rsync -avz data/roms3 -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms3
rsyncCmd = 'rsync -avz %s -e \"ssh -l resl\" resl@cinaps.usc.edu:%s'%(Data_Dir,Remote_Data_Dir)
print rsyncCmd
os.system(rsyncCmd)
Monolith_Data_Dir = '/home/arvind/data/roms/'
rsyncCmdMonolith = 'rsync -avz sfcst*.mat -e \"ssh -l arvind\" arvind@monolith.robotlab:%s'%(Monolith_Data_Dir)
print rsyncCmdMonolith
os.system(rsyncCmdMonolith)

rsyncCmd = 'rsync -avz sfcst*.mat -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms7/'
print rsyncCmd
os.system( rsyncCmd )

rsyncCmd = 'rsync -avz -e \"ssh -l resl\" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms7/sfcst*.mat %s'%(conf.romsDataDir)
print rsyncCmd
os.system(rsyncCmd)

#time.sleep(1800)
