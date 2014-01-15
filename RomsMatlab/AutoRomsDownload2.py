import sys, os
import datetime
import time
import gpplib
from gpplib.Utils import *

# matlab -nodesktop -nosplash -nojvm -r "cd /Users/arvind/git/gpplib/RomsMatlab/;SaveRomsData;exit;"


PathToMatRomsScripts = '/Users/arvind/gpplib/RomsMatlab/'
Data_Dir = '/Volumes/data/roms5/' #'/Users/arvind/data/roms5/'
Remote_Data_Dir = '/mnt/data/storage/datasets/roms7'
Local_Dir = Data_Dir

dr = DateRange(2013,8,28,2013,8,31)

done  = False
for yy,mm,dd  in dr.DateList:
	now = datetime.datetime.now() + datetime.timedelta(hours=+8)
	matlabCmd = 'matlab -nodesktop -nosplash -nojvm -r \"cd %s;GetRomsDataForDay(%04d,%02d,%02d,\'%s\');exit\"'%(\
				PathToMatRomsScripts,yy,mm,dd,Local_Dir)
	print matlabCmd
	os.system(matlabCmd)
	for seqNum in range(0,4):
		matlabCmd2 = 'matlab -nodesktop -nosplash -nojvm -r \"cd %s;SaveSmallRomsForecast(%2d,%2d,%04d,%d,\'%s\');exit\"'%(\
					PathToMatRomsScripts,dd,mm,yy,seqNum,Local_Dir)
		print matlabCmd2
		os.system(matlabCmd2)

# Now sync this data with Cinaps.
# rsync -avz data/roms3 -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms3
rsyncCmd = 'rsync -avz %s/fcst*.mat -e \"ssh -l resl\" resl@cinaps.usc.edu:%s'%(Local_Dir,Remote_Data_Dir)
print rsyncCmd
os.system(rsyncCmd)
Monolith_Data_Dir = '/home/arvind/data/roms/'
rsyncCmdMonolith = 'rsync -avz %s/sfcst*.mat -e \"ssh -l arvind\" arvind@monolith.robotlab:%s'%(Local_Dir,Monolith_Data_Dir)
print rsyncCmdMonolith
os.system(rsyncCmdMonolith)
#time.sleep(1800)

rsyncCmdSfcst = 'rsync -avz %s/sfcst*.mat -e \"ssh -l resl\" resl@cinaps.usc.edu:%s'%(Local_Dir,Remote_Data_Dir)
print rsyncCmdSfcst
os.system( rsyncCmdSfcst )
