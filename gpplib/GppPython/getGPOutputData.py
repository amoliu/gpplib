#!/usr/bin/env python
import os,sys
import gpplib
from gpplib.Utils import *

def printUsage(pgmName):
    print 'Usage : %s [yy] [mm] [dd] '%(pgmName)
    
    
def GetDataFromDay(yy,mm,dd,storeDataDir):
    for i in range(0,3):
        wgetCmd = 'wget robotics.usc.edu/~geoff/nobackup/sfcst_%04d%02d%02d_%d.mat'%(yy,mm,dd,i)
        print wgetCmd
        os.system(wgetCmd)
	moveCmd = 'mv sfcst_%04d%02d%02d_%d.mat %s/'%(yy,mm,dd,i,storeDataDir)
	print moveCmd
	os.system(moveCmd)   

conf = gpplib.GppConfig()
storeDataDir = conf.myDataDir + 'romsGP'
try:
    os.mkdir(storeDataDir)
except:
    pass

if len(sys.argv)==1 or len(sys.argv)>4:
    printUsage(sys.argv[0])
else:
    GetDataFromDay(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),storeDataDir)

