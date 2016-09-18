'''
:Author: Arvind A de Menezes Pereira
:Date: $Date: 2012-05-16 15:00:00 PST (Wed, 16 May 2011) $
:Revision: $Revision: 1 $
:Summary: Here we define a class which can use pre-computed correlations from ROMS datasets,
to determine which of them can and should be included in the planning map. Based upon this,
we then construct the transition graph consisting only of the well-correlated nodes.

This creates RiskMap3.shelf's transition models.
'''
import gpplib
import numpy as np
import scipy.io as sio
import shelve
import os,sys,re
import time, math, datetime
import getopt
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.GenGliderModelUsingGPRoms import ProduceGPTransitionGraph
from gpplib.SfcstOpener import SfcstGPOpen
from gpplib.InterpRoms import * # This has our Trilinear interpolation
from gpplib.Utils import RomsTimeConversion

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv)<=5:
        print 'Usage %s s_yy,s_mm,s_dd,e_yy,e_mm,e_dd, [useCurrentTime=1/not-supplied, useCurrentTime=0]'%(argv[0])
        sys.exit(-1)
    s_yy,s_mm,s_dd,e_yy,e_mm,e_dd = int(argv[1]),int(argv[2]),int(argv[3]),int(argv[4]),int(argv[5]),int(argv[6])
    
    if len(argv)==7:
        useCurrentTime = int(argv[6])
    
    if datetime.date(s_yy,s_mm,s_dd)==datetime.datetime.today().date and useCurrentTime==True:
        useCurrentTime = True
    else:
        useCurrentTime = False
    
    dr = gpplib.Utils.DateRange( s_yy,s_mm,s_dd,e_yy,e_mm,e_dd )
    print 'Finding Transition models from %04d-%02d-%02d to %04d-%02d-%02d.'%(s_yy,s_mm,s_dd,e_yy,e_mm,e_dd)
    numDays = 1
    posNoise = 0.001
    stepHrs = 12
    numSteps = 8
    conf = gpplib.Utils.GppConfig()
    ptg = ProduceGPTransitionGraph(conf.riskMapDir+'RiskMap3.shelf',conf.romsDataDir)
    ptg.UseRomsNoise = True
    
    if useCurrentTime:
        rtc  = RomsTimeConversion()
        numHrsFromNow = 1
        s_indx = rtc.GetRomsIndexNhoursFromNow(s_yy,s_mm,s_dd,numHrsFromNow)
        e_indx = s_indx + stepHrs
        t_start = time.time()
        transModel = ptg.CreateTransitionModelFromProxemicGraphAndGPBetweenHours2(yy,mm,dd,s_indx,e_indx,1.5,posNoise)
        t_end = time.time()
        print 'Time taken to generate model=%f'%(t_end-t_start)
    else:
        s_indx = 0
        for (yy,mm,dd) in dr.DateList:
            for startStep in range(0,numSteps):
                s_indx = startStep * (48/numSteps)
                e_indx = s_indx + stepHrs
                t_start = time.time()
                #import pdb; pdb.set_trace()
                transModel = ptg.CreateTransitionModelFromProxemicGraphAndGPBetweenHours2(yy,mm,dd,s_indx,e_indx,1.5,posNoise)
                t_end = time.time()
                print 'Time taken to generate model=%f'%(t_end-t_start)
if __name__ == "__main__":
    sys.exit(main())
