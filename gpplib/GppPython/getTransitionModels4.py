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
from gpplib.GenGliderModelUsingRoms import GliderModel
import os,sys,re
import time, math
import getopt

class ProduceTransitionGraph(GliderModel):
    ''' Class to produce transition graphs. If this works well, we are going to move it to
    gpplib. We load up the risk map (which is created by GetRiskObsMaps.py)
    '''
    def __init__(self,riskMapShelfFN='RiskMap.shelf',sfcst_directory='./'):
        super(ProduceTransitionGraph,self).__init__(riskMapShelfFN,sfcst_directory)
        riskMapShelf = shelve.open(riskMapShelfFN,writeback=False)
        self.g = riskMapShelf['NodesInGraph']
        self.allNearests = riskMapShelf['LandProxemics']
        self.LatLonLocs = riskMapShelf['LatLonLocs']
        self.convVals = riskMapShelf['convVals']
        #self.riskMap  = riskMapShelf['riskMap']
        #self.riskMapArray = riskMapShelf['riskMapArray']
        self.conf = gpplib.Utils.GppConfig()
        riskMapShelf.close()
        #self.gm = GliderModel(riskMapShelfFN,self.conf.romsDataDir)
        
    def GetXYfromNodeStr(self,nodeStr):
        ''' Convert from the name of the node string to the locations.
        '''
        m = re.match('\(([0-9\.]+),([0-9\.]+)\)',nodeStr)
        if m:
            return int(m.group(1)),int(m.group(2))
        else:
            return None, None
        
    def CreateTransitionModelFromProxemicGraph(self,yy,mm,dd,numDays=3,dmax = 1.5,romsNoise=None,posNoise=None,debugMe=False):
        ''' Create the transition models '''
        
        gm_str,rn_str,pn_str = 'gliderModel_%04d%02d%02d_%d'%(yy,mm,dd,numDays),'',''
        useNoisyStarts = False
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays,True,True)
        # Correct for the glider's velocity
        self.gVel = 0.22 # Estimated glider speed based upon the last few runs.
        print 'Generating the transisition model for %04d-%02d-%02d over %d days using '%(yy,mm,dd,numDays)
        startTime = time.time()
        if romsNoise!=None:
            self.sigmaCurU = romsNoise
            self.sigmaCurV = romsNoise
            self.UseRomsNoise = True
            rn_str = '_RN_%.3f'%(romsNoise)
        else:
            self.UseRomsNoise = False
            
        if posNoise!=None:
            self.sigmaX = posNoise
            self.sigmaY = posNoise
            pn_str = '_%.3f'%(posNoise)
            useNoisyStarts = True
        else:
            self.sigmaX = None
            self.sigmaY = None
        
        self.gModel = {}
        for a in self.g.nodes():
            for b in self.g.nodes():
                if a!=b:
                    x1,y1 = self.GetXYfromNodeStr(a); 
                    x2,y2 = self.GetXYfromNodeStr(b)
                    #if x1 == 7 or x2 == 7 and math.sqrt((x1-x2)**2+(y1-y2)**2)<=dmax:
                    #    import pdb; pdb.set_trace()
                    x_sims,y_sims,xTrack,yTrack = self.GenerateModelForAction(x1, y1, x2, y2, dmax, numDays, useNoisyStarts, self.sigmaX, self.sigmaY )
                    if x_sims!=None and y_sims!=None:
                        lookupStr = '%d,%d,%d,%d'%(x1,y1,x2,y2)
                        #if debugMe:
                        #    import pdb; pdb.set_trace()
                        self.FinalLocs[lookupStr] = (x_sims,y_sims)
                        self.TracksInModel[lookupStr] = (xTrack,yTrack)
                        zero_loc,max_dims,transProbs = self.CalculateTransProbabilities(x_sims, y_sims, numDays-1)                             
                        if transProbs != None:
                            self.TransModel[lookupStr] = (zero_loc,max_dims,transProbs)
                            #import pdb; pdb.set_trace()
        endTime = time.time()
        gmShelf = shelve.open( gm_str+pn_str+rn_str+'.shelf' )
        gmShelf['TransModel'] = self.TransModel
        gmShelf['FinalLocs'] = self.FinalLocs
        gmShelf['TracksInModel'] = self.TracksInModel
        gmShelf['GenTime'] = endTime - startTime
        gmShelf.close()
                            
        return self.TransModel
    
    def CreateTransitionModelFromProxemicGraphBetweenHours(self,yy,mm,dd,s_indx=0,e_indx=48,dmax = 1.5,romsNoise=None,posNoise=None,debugMe=False):
        ''' Create the transition models '''
        numDays = int((e_indx-s_indx)/24+0.5)
        gm_str,rn_str,pn_str = 'gliderModel3_%04d%02d%02d_%d'%(yy,mm,dd,numDays),'',''
        useNoisyStarts = False
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays,True,True)
        print 'Generating the transisition model for %04d-%02d-%02d over %d hours using '%(yy,mm,dd,numDays)
        startTime = time.time()
        if romsNoise!=None:
            self.sigmaCurU = romsNoise
            self.sigmaCurV = romsNoise
            self.UseRomsNoise = True
            rn_str = '_RN_%.3f'%(romsNoise)
        else:
            self.UseRomsNoise = False
            
        if posNoise!=None:
            self.sigmaX = posNoise
            self.sigmaY = posNoise
            pn_str = '_%.3f'%(posNoise)
            useNoisyStarts = True
        else:
            self.sigmaX = None
            self.sigmaY = None
        
        self.gModel = {}
        for a in self.g.nodes():
            for b in self.g.nodes():
                if a!=b:
                    x1,y1 = self.GetXYfromNodeStr(a); 
                    x2,y2 = self.GetXYfromNodeStr(b)
                    #if x1 == 7 or x2 == 7 and math.sqrt((x1-x2)**2+(y1-y2)**2)<=dmax:
                    #    import pdb; pdb.set_trace()
                    x_sims,y_sims,xTrack,yTrack = self.GenerateModelForActionInHourRange(x1, y1, x2, y2, dmax, s_indx, e_indx, useNoisyStarts, self.sigmaX, self.sigmaY )
                    if x_sims!=None and y_sims!=None:
                        lookupStr = '%d,%d,%d,%d'%(x1,y1,x2,y2)
                        #if debugMe:
                        #    import pdb; pdb.set_trace()
                        self.FinalLocs[lookupStr] = (x_sims,y_sims)
                        self.TracksInModel[lookupStr] = (xTrack,yTrack)
                        zero_loc,max_dims,transProbs = self.CalculateTransProbabilities(x_sims, y_sims, numDays-1)                             
                        if transProbs != None:
                            self.TransModel[lookupStr] = (zero_loc,max_dims,transProbs)
                            #import pdb; pdb.set_trace()
        endTime = time.time()
        gmShelf = shelve.open( gm_str+pn_str+rn_str+'.shelf' )
        gmShelf['TransModel'] = self.TransModel
        gmShelf['FinalLocs'] = self.FinalLocs
        gmShelf['TracksInModel'] = self.TracksInModel
        gmShelf['GenTime'] = endTime - startTime
        gmShelf.close()
                            
        return self.TransModel
    

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


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
    s_indx = 0 # rtc.GetRomsIndexNhoursFromNow(s_yy,s_mm,s_dd,2)
    e_indx = s_indx + 24
    
    curNoiseVals = [0.01, 0.03, 0.1, 0.3]
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
