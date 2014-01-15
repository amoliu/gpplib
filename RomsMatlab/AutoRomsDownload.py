import sys, os
import datetime
import time
import gpplib
from gpplib.Utils import *
from RomsFTP import RomsFTP

# matlab -nodesktop -nosplash -nojvm -r "cd /Users/arvind/git/gpplib/RomsMatlab/;SaveRomsData;exit;"
downloadFile = False
if len(sys.argv)>1:
   downloadFile = True

PathToMatRomsScripts = '/Users/arvind/gpplib/RomsMatlab/'
Data_Dir = './*.nc'
Remote_Data_Dir = '/mnt/data/storage/datasets/roms4/'

#dr = DateRange(2013,7,30,2013,7,30)
dt = datetime.date.today()
dr = DateRange( dt.year, dt.month, dt.day, dt.year, dt.month, dt.day )


done  = False
for yy,mm,dd  in dr.DateList:
  if downloadFile:
    rftp = RomsFTP('myocean/CA3km-forecast/CA')
    dirList = rftp.GetSimpleDirList('.')
    #print dirList
    if rftp.DoesFileExist('ca_subCA_fcst_%04d%02d%02d03.nc'%(yy,mm,dd)):
        rftp.ReadFile('ca_subCA_fcst_%04d%02d%02d03.nc'%(yy,mm,dd), 'ca_subCA_fcst_%04d%02d%02d03.nc'%(yy,mm,dd))
        rftp.Close()
    else:
        print 'File does not exist: ca_subCA_fcst_%04d%02d%02d03.nc'%(yy,mm,dd)
  now = datetime.datetime.now() + datetime.timedelta(hours=+8)
  matlabCmd = 'matlab -nodesktop -nosplash -nojvm -r \"cd %s;GetNCToSfcts(%02d,%02d,%04d);exit\"'%(PathToMatRomsScripts,dd,mm,yy) 
  print matlabCmd
  os.system(matlabCmd)
'''
# Now sync this data with Cinaps.
# rsync -avz data/roms3 -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/roms3
rsyncCmd = 'rsync -avz %s -e \"ssh -l resl\" resl@cinaps.usc.edu:%s'%(Data_Dir,Remote_Data_Dir)
print rsyncCmd
os.system(rsyncCmd)
Monolith_Data_Dir = '/home/arvind/data/roms/'
rsyncCmdMonolith = 'rsync -avz %s/sfcst*.mat -e \"ssh -l arvind\" arvind@monolith.robotlab:%s'%(Data_Dir,Monolith_Data_Dir)
print rsyncCmdMonolith
os.system(rsyncCmdMonolith)
#time.sleep(1800)
'''
