import re, sys, os
import gpplib
from gpplib.Utils import *

dr = DateRange(2013,8,14,2013,8,15)


wayPtList = [(33.449855,-118.359328),(33.543039,-118.331636),(33.46926,-118.418188),(33.523829,-118.588117),(33.488213,-118.701459),(33.522344,-118.757254)]

numThreads = 24

if numThreads< len(dr.DateList)*len(wayPtList):
    raise ('Too few number of threads...')
else:
    for yy,mm,dd in dr.DateList:
        for lat,lon in wayPtList:
            #cmd = 'nohup python PreComputePolicyNS_MDP_GP.py %04d %02d %2d %f %f > /dev/null &'%(yy,mm,dd,lat,lon)
            cmd = 'nohup python PreComputePolicyGP_MDP.py %04d %02d %2d %f %f &'%(yy,mm,dd,lat,lon)
            print cmd
            os.system(cmd)
