''' Take the individual models created by ParallelizeTransModels.py and 
create the original transition model by consolidating their contents. '''

import re, sys, os
import shelve
import gpplib
from gpplib.Utils import *

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

yy,mm,dd = 2013, 8, 13
outputModel = '%s/gliderModelNS_GP_%04d%02d%02d_0_48_0.001.shelf'%(conf.myDataDir+'gliderModelNS',yy,mm,dd)

dirList = os.listdir(conf.myDataDir+'gliderModelNS')

mainShelf = shelve.open( outputModel )
for file in dirList:
    reStr = 'gliderModelNS_GP_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]+)_([0-9]+)_([0-9]+)_([0-9]+)_([0-9\.]+).shelf$'
    m= re.match( reStr, file )
    if m:
        yr,mo,dy,sIndx,eIndx,sState,eState,pNoise = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), \
                int(m.group(6)), int(m.group(7)), float(m.group(8))
        if yr==yy and mm == mo and dd == dy:
            print 'Consolidating %s: '%file
            partShelfFile = '%s/%s'%(conf.myDataDir+'gliderModelNS',file)
            partShelf = shelve.open( partShelfFile, writeback=False )
            for key in partShelf.keys():
                #import pdb; pdb.set_trace()
                if type(partShelf[key])==dict:
                    tempDict = {}
                    if mainShelf.has_key(key): # For FinalLocs and TransProb
                        tempDict = mainShelf[key]
                    for k,v in partShelf[key].items():
                        tempDict[k] = v
                    mainShelf[key]= tempDict
                elif type(partShelf[key])==float: # For the GenTime key
                    if not mainShelf.has_key(key):
                        mainShelf[key] = 0.
                    val = mainShelf[key]
                    val += partShelf[key]
                    mainShelf[key] = val
            #for key, val in partShelf.items():
            #    mainShelf[key] = val
            print 'Done. Moving...'
            partShelf.close()
            moveCmd = 'mv %s partFiles/'%(partShelfFile)
            print moveCmd
            os.system( moveCmd )
            
        print yr,mo,dy,sIndx,eIndx,sState,eState,pNoise
        
mainShelf.close()

rsyncCmd = 'rsync -avz %s -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/gliderModelNS/'%(outputModel)
print rsyncCmd
os.system( rsyncCmd )
