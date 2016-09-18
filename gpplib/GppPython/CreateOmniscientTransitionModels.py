''' Take the individual models created by ParallelizeTransModels.py and 
create the original transition model by consolidating their contents. '''

import re, sys, os
import shelve
import gpplib
from gpplib.Utils import *
from gpplib.Utils import DateRange

def readStates( fileName ):
    states = {}
    stF = open( fileName, 'r' )
    if stF:
        stLines = stF.readlines()
        for line in stLines:
            m = re.match( '([0-9]+)=([0-9]+),([0-9]+),([0-9]+)', line )
            if m:
                state = int( m.group(1) )
                t,x,y = int( m.group(2) ), int( m.group(3) ), int( m.group(4) )
                print '%d,%d,%d,%d'%( state, t, x, y )
                states[ state ] = (t,x,y)
        stF.close()
    return states

conf = GppConfig()

yy_s,mm_s,dd_s = 2013, 8, 12
yy_e,mm_e,dd_e = 2013, 8, 20

dr = DateRange( yy_s, mm_s, dd_s, yy_e, mm_e, dd_e )
numHours = len(dr.DateList)*24
outputModel = '%s/gliderModelNS_GP_%04d%02d%02d_0_%d_0.001.shelf'%(conf.myDataDir+'gliderModelNS',yy_s,mm_s,dd_s,numHours)

dirList = os.listdir(conf.myDataDir+'gliderModelNS')

mainShelf = shelve.open( outputModel )
for indx, theDate in enumerate(dr.DateList):
    yy,mm,dd = theDate
    expectedFile = 'gliderModelNS_GP_%04d%02d%02d_0_48_0.001.shelf'%(yy,mm,dd)
    if  expectedFile in dirList:
        reStr = 'gliderModelNS_GP_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]+)_([0-9]+)_([0-9\.]+).shelf$'
        print 'Consolidating %s: '%expectedFile
        partShelfFile = '%s/%s'%(conf.myDataDir+'gliderModelNS',expectedFile)
        partShelf = shelve.open( partShelfFile, writeback=False )
        
        baseTime = indx * 24
        
        for key in partShelf.keys():
                #import pdb; pdb.set_trace()
                if type(partShelf[key])==dict:
                    tempDict = {}
                    if mainShelf.has_key(key): # For FinalLocs and TransProb
                        tempDict = mainShelf[key]
                    for k,v in partShelf[key].items():
                        m = re.match('([0-9]+),([0-9]+),([0-9]+),([0-9]+),([0-9]+)',k)
                        if m:
                            t1,x1,y1,x2,y2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
                            lookupStr = '%d,%d,%d,%d,%d'%(t1+baseTime,x1,y1,x2,y2)
			    print lookupStr
                            tempDict[ lookupStr ] = v
                    mainShelf[key]= tempDict
                elif type(partShelf[key])==float: # For the GenTime key
                    if not mainShelf.has_key(key):
                        mainShelf[key] = 0.
                    val = mainShelf[key]
                    val += partShelf[key]
                    mainShelf[key] = val
        print 'Done...'
        partShelf.close()
        print yy,mm,dd
    else:
        print 'Error! Did not find data file : %s'%(expectedFile)
        sys.exit( -1 )
        
mainShelf.close()

rsyncCmd = 'rsync -avz %s -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/gliderModelNS/'%(outputModel)
print rsyncCmd
os.system( rsyncCmd )
