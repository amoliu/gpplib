import sys, os
import datetime
import time
import gpplib
from gpplib.Utils import *

# matlab -nodesktop -nosplash -nojvm -r "cd /Users/arvind/git/gpplib/RomsMatlab/;SaveRomsData;exit;"


PathToMatRomsScripts = '/Users/arvind/gpplib/RomsMatlab/'
Data_Dir = '/Users/arvind/data/roms3/'
GP_Data_Dir = '/Users/arvind/data/romsGP/'
Remote_Data_Dir = '/mnt/data/storage/datasets/roms3'
RemoteGp_Data_Dir = '/mnt/data/storage/datasets/romsGP'

done  = False
while (not done):
	now = datetime.datetime.now() + datetime.timedelta(hours=+8)
	matlabCmd = 'matlab -nodesktop -nosplash -nojvm -r \"cd %s;GetRomsDataForDay(%04d,%02d,%02d,\'%s\');exit\"'%(PathToMatRomsScripts,now.year,now.month,now.day,Data_Dir)
	print matlabCmd
	os.system(matlabCmd)

	# Now sync this data with Cinaps.
	# rsync -avz data/roms3 -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms3
	rsyncCmd = 'rsync -avz %s -e \"ssh -l resl\" resl@cinaps.usc.edu:%s'%(Data_Dir,Remote_Data_Dir)
	print rsyncCmd
	os.system(rsyncCmd)

	rsyncCmd = 'rsync -avz %s -e \"ssh -l resl\" resl@cinaps.usc.edu:%s'%(GP_Data_Dir, RemoteGp_Data_Dir)
	print rsyncCmd
	os.system(rsyncCmd)

	Monolith_Data_Dir = '/home/arvind/data/roms/'
	rsyncCmdMonolith = 'rsync -avz %s/sfcst*.mat -e \"ssh -l arvind\" arvind@monolith.robotlab:%s'%(Data_Dir,Monolith_Data_Dir)
	print rsyncCmdMonolith
	os.system(rsyncCmdMonolith)
	done = True
	#time.sleep(1800)
