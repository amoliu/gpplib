'''
:Author: Arvind A de Menezes Pereira
:Date: $Date: 2012-06-13 16:41:00 PST (Wed, 16 May 2011) $
:Revision: $Revision: 1 $
:Summary: Here we define a class which can use pre-computed correlations from ROMS datasets,
to determine which of them can and should be included in the planning map. Based upon this,
we then construct the transition graph consisting only of the well-correlated nodes.
'''
#!/usr/bin/python
import gpplib
import numpy as np
import scipy.io as sio
import shelve
from gpplib.GenGliderModelUsingRoms import GliderModel
import os,sys,re
import time, math, random
import getopt

class ProduceTimeIndexedTransitionGraph(GliderModel):
    ''' Class to produce time-indexed transition graphs. If this works well, we are going to move it to
    gpplib. We load up the risk map (which is created by GetRiskObsMaps.py)
    '''
    def __init__(self,riskMapShelfFN='RiskMap.shelf',sfcst_directory='./'):
        super(ProduceTimeIndexedTransitionGraph,self).__init__(riskMapShelfFN,sfcst_directory)
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
        
        
    def GenerateModelForAction(self,i,j,x,y,d_max,numDays,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3, simStartTime=0 ):
        ''' Generates the model for taking a certain action (on the discrete planning graph).
        
        Args: i,j,x,y,d_max,numDays,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 
        
        '''
        self.numParticles = 30
        x_sims,y_sims = np.zeros((self.numParticles,1)),np.zeros((self.numParticles,1))
        t_sims = np.zeros((self.numParticles,1))
        xTrack,yTrack = [],[]
        if self.ObsDetLatLon(self.lat_pts[j],self.lon_pts[i],self.lat_pts[y],self.lon_pts[x])==False:
            if math.sqrt((i-x)*(i-x)+(j-y)*(j-y)) <= d_max and (i,j)!=(x,y):
                startT = time.time()
                print 'Generating model from %d,%d to %d,%d. Starting at time: %f to do %d trials.'%(i,j,x,y,startT,self.numParticles)
                
                for k in range(0,self.numParticles):
                        if not usingNoisyStarts:
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(self.lat_pts[j], self.lon_pts[i], \
                                                          self.lat_pts[y], self.lon_pts[x], self.maxDepth,\
                                                          self.u, self.v, self.lat, self.lon, self.depth, simStartTime, False)
                        else: # Using Noisy starts
                            sLat,sLon = self.GetLatLonfromXY(i+random.gauss(0,noiseSigmaX), j+random.gauss(0,noiseSigmaY)); 
                            gLat,gLon = self.GetLatLonfromXY(x+random.gauss(0,noiseSigmaX), y+random.gauss(0,noiseSigmaY));
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(sLat, sLon, gLat, gLon, self.maxDepth, \
                                                          self.u, self.v, self.lat, self.lon, self.depth, k , False)
                        tempX,tempY = self.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
                        xTrack.append(tempX); yTrack.append(tempY)
                        if possibleCollision == False:
                            x_sims[k],y_sims[k] = (tempX[-1:]-i),(tempY[-1:]-j)
                            t_sims[k] = tArray[-1:]/3600.
                        else:
                            if len(tempX)>=2 and len(tempY)>=2:
                                x_sims[k],y_sims[k] = (tempX[-1:]-i),(tempY[-1:]-j)
                                t_sims[k] = tArray[-1:]/3600.
                            else:
                                x_sims[k],y_sims[k] = 0,0
                endT = time.time()
                print ' Took: %f secs.'%(endT-startT)
                return x_sims,y_sims,xTrack,yTrack,t_sims
        return None,None,None,None,None
        
        
    def CreateTransitionModelFromProxemicGraph(self,yy,mm,dd,numDays=3,dmax = 1.5,romsNoise=None,posNoise=None,debugMe=False):
        ''' Create the transition models '''
        
        gm_str,rn_str,pn_str = 'gliderModel_TI_%04d%02d%02d_%d'%(yy,mm,dd,numDays),'',''
        useNoisyStarts = False
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays+2)
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
        for t in range(0,24*numDays):
            for a in self.g.nodes():
                for b in self.g.nodes():
                    if a!=b:
                        x1,y1 = self.GetXYfromNodeStr(a); 
                        x2,y2 = self.GetXYfromNodeStr(b)
                        #if x1 == 7 or x2 == 7 and math.sqrt((x1-x2)**2+(y1-y2)**2)<=dmax:
                        #    import pdb; pdb.set_trace()
                        x_sims,y_sims,xTrack,yTrack,t_sims = self.GenerateModelForAction(x1, y1, x2, y2, dmax, numDays, useNoisyStarts, self.sigmaX, self.sigmaY, t )
                        if x_sims!=None and y_sims!=None:
                            tf = t_sims.mean(axis=0)
                            lookupStr = '%d,%d,%d,%d,%d'%(x1,y1,x2,y2,t)
                            #if debugMe:
                            #    import pdb; pdb.set_trace()
                            self.FinalLocs[lookupStr] = (x_sims,y_sims,t_sims)
                            self.TracksInModel[lookupStr] = (xTrack,yTrack)
                            zero_loc,max_dims,transProbs = self.CalculateTransProbabilities(x_sims, y_sims,self.numParticles)                             
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


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv)<=5:
        print 'Usage %s s_yy,s_mm,s_dd,e_yy,e_mm,e_dd'%(argv[0])
        sys.exit(-1)
    s_yy,s_mm,s_dd,e_yy,e_mm,e_dd = int(argv[1]),int(argv[2]),int(argv[3]),int(argv[4]),int(argv[5]),int(argv[6])
    dr = gpplib.Utils.DateRange( s_yy,s_mm,s_dd,e_yy,e_mm,e_dd )
    print 'Finding Transition models from %04d-%02d-%02d to %04d-%02d-%02d.'%(s_yy,s_mm,s_dd,e_yy,e_mm,e_dd)
    numDays = 2
    posNoise = 0.01                    
    curNoiseVals = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.32, 0.5]
    conf = gpplib.Utils.GppConfig()
    ptg = ProduceTimeIndexedTransitionGraph(conf.riskMapDir+'RiskMap.shelf',conf.romsDataDir)
    ptg.UseRomsNoise = True
    for (yy,mm,dd) in dr.DateList:
        for curNoiseSigma in curNoiseVals:
            transModel = ptg.CreateTransitionModelFromProxemicGraph(yy,mm,dd,numDays,1.5,curNoiseSigma,posNoise)

if __name__ == "__main__":
    sys.exit(main())
