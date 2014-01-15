'''
:Author: Arvind A de Menezes Pereira
:Date: $Date: 2012-05-16 15:00:00 PST (Wed, 16 May 2011) $
:Revision: $Revision: 1 $
:Summary: Here we define a class which can use pre-computed correlations from ROMS datasets,
to determine which of them can and should be included in the planning map. Based upon this,
we then construct the transition graph consisting only of the well-correlated nodes.

This creates RiskMap2.shelf's transition models.
'''
import gpplib
import numpy as np
import scipy.io as sio
import shelve
import os,sys,re
import time, math
import getopt
from gpplib.GenGliderModelUsingRoms import GliderModel
from gpplib.GenTransitionModelsUsingRoms import ProduceTransitionGraph
from gpplib.Utils import RomsTimeConversion

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv)<=5:
        print 'Usage %s s_yy,s_mm,s_dd,e_yy,e_mm,e_dd, cur_noise'%(argv[0])
        sys.exit(-1)
    s_yy,s_mm,s_dd,e_yy,e_mm,e_dd = int(argv[1]),int(argv[2]),int(argv[3]),int(argv[4]),int(argv[5]),int(argv[6])
    dr = gpplib.Utils.DateRange( s_yy,s_mm,s_dd,e_yy,e_mm,e_dd )
    print 'Finding Transition models from %04d-%02d-%02d to %04d-%02d-%02d.'%(s_yy,s_mm,s_dd,e_yy,e_mm,e_dd)
    numDays = 1
    posNoise = 0.01
    #curNoiseVals = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.32, 0.5]
    rtc  = RomsTimeConversion()
    s_indx = rtc.GetRomsIndexNhoursFromNow(s_yy,s_mm,s_dd,1)
    e_indx = s_indx + 12
    
    curNoiseVals = [0.003, 0.01, 0.03, 0.1, 0.3]
    conf = gpplib.Utils.GppConfig()
    ptg = ProduceTransitionGraph(conf.riskMapDir+'RiskMap3.shelf',conf.romsDataDir)
    ptg.UseRomsNoise = True
    
    for (yy,mm,dd) in dr.DateList:
        for curNoiseSigma in curNoiseVals:
            t_start = time.time()
            #transModel = ptg.CreateTransitionModelFromProxemicGraph(yy,mm,dd,numDays,1.5,curNoiseSigma,posNoise)
            transModel = ptg.CreateTransitionModelFromProxemicGraphBetweenHours(yy,mm,dd,s_indx,e_indx,1.5,curNoiseSigma,posNoise)
            t_end = time.time()
            print 'Time taken to generate model=%f'%(t_end-t_start)
if __name__ == "__main__":
    sys.exit(main())
