#!/usr/bin/env python
'''
:Author: Arvind A de Menezes Pereira
:Date: 2013-04-27 16:40:00 PST (Sat, 27 Apr 2013) $
:Revision: $Revision: 1 $
:Summary: Here we define a class which can use pre-computed correlations from ROMS datasets,
to determine which of them can and should be included in the planning map. Based upon this,
we then construct the transition graph consisting only of the well-correlated nodes.

This creates RiskMap7.shelf's transition models. RiskMap7 is created by running createRiskObsMapsApr2013.py
'''
import gpplib
import numpy as np
import scipy.io as sio
import shelve
import os,sys,re
import time, math, datetime
import getopt
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.GenTransitionModelsUsingRoms import ProduceTransitionGraph
from gpplib.Utils import RomsTimeConversion

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv)<=5:
        print 'Usage %s s_yy,s_mm,s_dd,e_yy,e_mm,e_dd,  [useCurrentTime=1/not-supplied, useCurrentTime=0]'%(argv[0])
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
    posNoise = 0.01
    stepHrs = 6
    numSteps = 8
    conf = gpplib.Utils.GppConfig()
    ptg = ProduceTransitionGraph(conf.riskMapDir+'RiskMap7.shelf',conf.romsDataDir)
    ptg.UseRomsNoise = True
    curNoiseVals = [0.01, 0.03, 0.1, 0.3]
    
    if useCurrentTime:
        for curNoiseSigma in curNoiseVals:
            rtc  = RomsTimeConversion()
            numHrsFromNow = 1
            s_indx = rtc.GetRomsIndexNhoursFromNow(s_yy,s_mm,s_dd,numHrsFromNow)
            e_indx = s_indx + stepHrs
            t_start = time.time()
            transModel = ptg.CreateTransitionModelFromProxemicGraphBetweenHours2(yy,mm,dd,s_indx,e_indx,1.5,curNoiseSigma,posNoise)
            t_end = time.time()
            print 'Time taken to generate model=%f'%(t_end-t_start)
    else:
        s_indx = 0
    
    for (yy,mm,dd) in dr.DateList:
        for curNoiseSigma in curNoiseVals:
            for startStep in range(0,numSteps):
                s_indx = startStep * (48/numSteps)
                e_indx = s_indx + stepHrs
                t_start = time.time()
                #transModel = ptg.CreateTransitionModelFromProxemicGraph(yy,mm,dd,numDays,1.5,curNoiseSigma,posNoise)
                transModel = ptg.CreateTransitionModelFromProxemicGraphBetweenHours2(yy,mm,dd,s_indx,e_indx,1.5,curNoiseSigma,posNoise)
                t_end = time.time()
                print 'Time taken to generate model=%f'%(t_end-t_start)

if __name__ == "__main__":
    sys.exit(main())
