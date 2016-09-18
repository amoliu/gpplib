''' This class has been sub-classed from GliderModel to produce transition models which use confidence measures from a GP. '''
import gpplib
import numpy as np
import scipy.io as sio
import shelve
from gpplib.GenGliderModelUsingRoms import GliderModel
import os,sys,re
import time, math
import getopt
from gpplib.SfcstOpener import SfcstGPOpen
from gpplib.InterpRoms import * # This has our Trilinear interpolation

class ProduceNS_GPTransitionGraph(GliderModel):
    ''' Class to produce transition graphs. If this works well, we are going to move it to
    gpplib. We load up the risk map (which is created by GetRiskObsMaps.py)
    '''
    def __init__(self,riskMapShelfFN='RiskMap3.shelf',sfcst_directory='./',**kwargs ):
        super(ProduceNS_GPTransitionGraph,self).__init__(riskMapShelfFN,sfcst_directory)
        riskMapShelf = shelve.open(riskMapShelfFN,writeback=False)
        self.locG = riskMapShelf['NodesInGraph']
        self.g = self.LoadTimeGraph(riskMapShelf['NodesInGraph'],48)
        self.allNearests = riskMapShelf['LandProxemics']
        self.LatLonLocs = riskMapShelf['LatLonLocs']
        self.convVals = riskMapShelf['convVals']
        #self.riskMap  = riskMapShelf['riskMap']
        #self.riskMapArray = riskMapShelf['riskMapArray']
        self.conf = gpplib.Utils.GppConfig()
        riskMapShelf.close()
        self.sfGPOpen = SfcstGPOpen()
        self.LastRomsGpDataLoaded = ''
        self.sfcstGpDirectory = self.conf.romsGpDataDir
        
        self.tMax = 5 # Max of 5 hours to go between two nodes.
        
        #self.gm = GliderModel(riskMapShelfFN,self.conf.romsDataDir)
        
    def LoadTimeGraph(self,g,maxT):
        import networkx as nx
        g2 = nx.DiGraph()
        for n in g.nodes():
            x,y = self.GetXYfromNodeStr(n)
            for t in range(0,maxT):
                g2.add_node( (x,y,t) )
        return g2
                
    def GetGP_RomsData(self,yy,mm,dd,numDays,useForeCastOnly=False):
        ''' A Pre-caching version to get Roms-Data. Since the class
        can be made to hold the data that was last loaded, this intelligently
        ensures that the data being requested isn't already loaded up. If it is,
        it will return the data requested. If not, it opens the file (if it exists)
        and serves that up instead.
        
        Args: yy,mm,dd,numDays,useNewFormat = True
            * yy (int) : Year
            * mm (int) : Month
            * dd (int) : Day
            * numDays (int) : Number of days to simulate for
            * useNewFormat (bool) : Old data was stored in file-names like sfcst_yymmdd.mat. The new ones use filenames like sfcst_yymmdd_seqNum.mat. Uses new format by default.
            
        '''
        dataToBeLoaded = '%04d%02d%02d_%d'%(yy,mm,dd,numDays)
        # Update only if needed!
        if self.LastRomsGpDataLoaded != dataToBeLoaded:
            self.numDaysGP = numDays
            daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
            if yy%4 == 0:
                daysInMonths[1] = 29
            u,v,time,depth,lat,lon,u_iv,v_iv,u_gp,v_gp,u_kv,v_kv = \
                self.sfGPOpen.LoadFile('%s/sfcst_%04d%02d%02d_0.mat'%(self.sfcstGpDirectory,yy,mm,dd))
            myDay, myMonth, myYear = dd,mm,yy
            
        if useForeCastOnly:
            for i in range(1,3):
                u1,v1,time1,depth1,lat1,lon1,u_iv1,v_iv1,u_gp1,v_gp1,u_kv1,v_kv1 = \
                    self.sfGPOpen.LoadFile('%s/sfcst_%04d%02d%02d_%d.mat'%(self.sfcstGpDirectory,yy,mm,dd,i))
                u,v=np.concatenate((u,u1),axis=0),np.concatenate((v,v1),axis=0)
                u_iv,v_iv,u_kv,v_kv = np.concatenate((u_iv,u_iv1),axis=0),np.concatenate((v_iv,v_iv1),axis=0), \
                                    np.concatenate((u_kv,u_kv1),axis=0),np.concatenate((v_kv,v_kv1),axis=0)
                u_gp,v_gp = np.concatenate((u_gp,u_gp1),axis=0),np.concatenate((v_gp,v_gp1),axis=0)
                time1=time1+np.ones((24,1))*24*i
                time=np.concatenate((time,time1),axis=0)
                self.numDays = numDays
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time,depth,lat,lon
            self.yy,self.mm,self.dd,self.numDays = yy,mm,dd,i
            self.u_gp,self.v_gp,self.u_iv,self.v_iv,self.u_kv,self.v_kv = \
                u_gp,v_gp,u_iv,v_iv,u_kv,v_kv
        else:
            for day in range(1,numDays):
                myDay = myDay+1
                if myDay>daysInMonths[mm-1]:
                    myDay = 1
                    myMonth = myMonth+1
                    if myMonth>12:
                        myMonth = 1
                        myYear = myYear+1
                # TODO: Write a test for the file, so we can break if we cannot open the file.
                u1,v1,time1,depth1,lat1,lon1,u_iv1,v_iv1,u_gp1,v_gp1,u_kv1,v_kv1 = \
                  self.sfGPOpen.LoadFile('%s/sfcst_%04d%02d%02d_0.mat'%(self.sfcstGpDirectory,myYear,myMonth,myDay))
                #import pdb;pdb.set_trace()
                u,v=np.concatenate((u,u1),axis=0),np.concatenate((v,v1),axis=0)
                u_iv,v_iv,u_kv,v_kv = np.concatenate((u_iv,u_iv1),axis=0),np.concatenate((v_iv,v_iv1),axis=0), \
                                    np.concatenate((u_kv,u_kv1),axis=0),np.concatenate((v_kv,v_kv1),axis=0)
                u_gp,v_gp = np.concatenate((u_gp,u_gp1),axis=0),np.concatenate((v_gp,v_gp1),axis=0)
                time1=time1+np.ones((24,1))*24*day
                time=np.concatenate((time,time1),axis=0)
                self.numDays = numDays
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time,depth,lat,lon
            self.yy,self.mm,self.dd,self.numDays = yy,mm,dd,numDays
            self.u_gp,self.v_gp,self.u_iv,self.v_iv,self.u_kv,self.v_kv = \
                u_gp,v_gp,u_iv,v_iv,u_kv,v_kv
        return self.u,self.v,self.time1,self.depth,self.lat,self.lon
            
    
    
    def CreateTransitionModelFromProxemicGraphAndGPBetweenHours(self,yy,mm,dd,s_indx=0,e_indx=48,dmax = 1.5, posNoise = None):
        ''' Create the transition models '''
        numDays = int((e_indx-s_indx)/24+0.5)
        gm_str,rn_str,pn_str = 'gliderModelGP_%04d%02d%02d_%d'%(yy,mm,dd,numDays),'',''
        useNoisyStarts = False
        u,v,time1,depth,lat,lon = \
            self.GetGP_RomsData(yy,mm,dd,numDays,True)
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays,True,True)
        print 'Generating the transition model for %04d-%02d-%02d over %d hours using '%(yy,mm,dd,numDays)
        startTime = time.time()
        
        u_iv, v_iv = np.ma.masked_array(self.u_iv,np.isnan(self.u_iv)), np.ma.masked_array(self.v_iv,np.isnan(self.v_iv))
        
        u_ivmean,v_ivmean = np.sqrt(np.mean(u_iv[s_indx:e_indx,0],axis=0)).filled(np.nan), np.sqrt(np.mean(v_iv[s_indx:e_indx,0],axis=0)).filled(np.nan)
        
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
                    #import pdb; pdb.set_trace()
                    x1,y1 = self.GetXYfromNodeStr(a); lat1,lon1 = self.GetLatLonfromXY(x1,y1)
                    x2,y2 = self.GetXYfromNodeStr(b); lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                    u_iv1,v_iv1 = BilinearInterpolate(lat1,lon1,lat,lon,u_ivmean), \
                        BilinearInterpolate(lat1,lon1,lat,lon,v_ivmean)
                    u_iv2,v_iv2 = BilinearInterpolate(lat2,lon2,lat,lon,u_ivmean), \
                        BilinearInterpolate(lat1,lon1,lat,lon,v_ivmean)
                    
                    #if x1 == 7 or x2 == 7 and math.sqrt((x1-x2)**2+(y1-y2)**2)<=dmax:
                    #import pdb; pdb.set_trace()
                    sigmaX1, sigmaY1 = np.sqrt(np.max(u_iv[s_indx:e_indx,0,x1,y1],axis=0)),np.sqrt(np.max(v_iv[s_indx:e_indx,0,x1,y1]))
                    sigmaX2, sigmaY2 = np.sqrt(np.max(u_iv[s_indx:e_indx,0,x2,y2],axis=0)),np.sqrt(np.max(v_iv[s_indx:e_indx,0,x2,y2]))
                    sX,sY = np.array([sigmaX1,sigmaX2]),np.array([sigmaY2,sigmaY2])
                    sXma,sYma = np.ma.masked_array(sX,np.isnan(sX)),np.ma.masked_array(sY,np.isnan(sY))
                    sigmaX,sigmaY = np.max(sXma), np.max(sYma)
                    sigmaX = sigmaY if isnan(sigmaX) else sigmaX
                    sigmaY = sigmaY if isnan(sigmaY) else sigmaY
                    self.sigmaCurU, self.sigmaCurV = sigmaX, sigmaY
                    
                    print '%d,%d,%d,%d, sigmaU=%.4f, sigmaV=%.4f'%(x1,y1,x2,y2,sigmaX,sigmaY)
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
    
    
    def CreateNS_TransitionModelFromProxemicGraphAndGPBetweenHours(self,yy,mm,dd,s_indx=0,e_indx=48,dmax=1.5,posNoise = None ):
        ''' Create Non stationary transition models '''
        gm_str, rn_str, pn_str = 'gliderModelNS_GP_%04d%02d%02d_%d_%d'%(yy,mm,dd,s_indx,e_indx),'',''
        useNoisyStarts=False
        numDays = (e_indx - s_indx)/24 + 1
        u,v,time1,depth,lat,lon = \
            self.GetGP_RomsData(yy,mm,dd,numDays,True)
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays,True,True)
        print 'Generating the transition model for %04d-%02d-%02d over %d days using '%(yy,mm,dd,numDays)
        startTime = time.time()
        
        u_iv, v_iv = np.ma.masked_array(self.u_iv,np.isnan(self.u_iv)), np.ma.masked_array(self.v_iv,np.isnan(self.v_iv))
        
        u_ivmean,v_ivmean = np.sqrt(np.mean(u_iv[s_indx:e_indx,0],axis=0)).filled(np.nan), np.sqrt(np.mean(v_iv[s_indx:e_indx,0],axis=0)).filled(np.nan)
        
        if posNoise!=None:
            self.sigmaX = posNoise
            self.sigmaY = posNoise
            pn_str = '_%.3f'%(posNoise)
            useNoisyStarts = True
        else:
            self.sigmaX = None
            self.sigmaY = None
        
        defNoise = 0.05 # Default value of noise when we have NaNs
        self.gModel = {}
        self.NoiseUsed = {}
        for a in self.locG.nodes():
            x1,y1 = self.GetXYfromNodeStr(a); lat1,lon1 = self.GetLatLonfromXY(x1,y1)
            for b in self.locG.nodes():
                x2,y2 = self.GetXYfromNodeStr(b); lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                if a!=b:
                    if math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)) <= dmax:
                        for t1 in range(s_indx,e_indx):
                            
                            lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                            u_iv1,v_iv1 = BilinearInterpolate(lat1,lon1,lat,lon,u[t1]), \
                                          BilinearInterpolate(lat1,lon1,lat,lon,v[t1])
                            u_iv2,v_iv2 = BilinearInterpolate(lat2,lon2,lat,lon,u[t1+self.tMax]), \
                                          BilinearInterpolate(lat2,lon2,lat,lon,v[t1+self.tMax])
                            sigmaX1, sigmaY1 = np.sqrt(np.max(u_iv[t1:t1+self.tMax,0,x1,y1],axis=0)),np.sqrt(np.max(v_iv[t1:t1+self.tMax,0,x1,y1]))
                            sigmaX2, sigmaY2 = np.sqrt(np.max(u_iv[t1:t1+self.tMax,0,x2,y2],axis=0)),np.sqrt(np.max(v_iv[t1:t1+self.tMax,0,x2,y2]))
                            sX,sY = np.array([sigmaX1,sigmaX2]),np.array([sigmaY2,sigmaY2])
                            sXma,sYma = np.ma.masked_array(sX,np.isnan(sX)),np.ma.masked_array(sY,np.isnan(sY))
                            sigmaX,sigmaY = np.max(sXma), np.max(sYma)
                            sigmaX = sigmaY if (np.isnan(sigmaX) and not np.isnan(sigmaY) ) else sigmaX
                            sigmaY = sigmaX if (np.isnan(sigmaY) and not np.isnan(sigmaX) ) else sigmaY
                            if math.isnan(sigmaX): sigmaX = defNoise
                            if math.isnan(sigmaY): sigmaY = defNoise
                            print '%d,%d,%d,%d,%d, sigmaX=%.4f, sigmaY=%.4f'%(t1,x1,y1,x2,y2,sigmaX,sigmaY)
                            x_sims,y_sims,t_sims,xTrack,yTrack,tTrack = self.GenerateModelForActionStartingAtTime(x1, y1, x2, y2, dmax, t1, 30, useNoisyStarts, sigmaX, sigmaY )
                            if x_sims!=None and y_sims!=None:
                                lookupStr = '%d,%d,%d,%d,%d'%(t1,x1,y1,x2,y2)
                                #if debugMe:
                                #import pdb; pdb.set_trace()
                                self.FinalLocs[lookupStr] = (x_sims,y_sims,t_sims)
                                self.NoiseUsed[lookupStr] = (sigmaX,sigmaY)
                                #self.TracksInModel[lookupStr] = (xTrack,yTrack,tTrack)
                                zero_loc,max_dims,transProbs = self.CalculateTransProbabilitiesWithTime(x_sims, y_sims, t_sims, t1, 10)                             
                                if transProbs != None:
                                    self.TransModel[lookupStr] = (zero_loc,max_dims,transProbs)
                                #import pdb; pdb.set_trace()
        endTime = time.time()
        gmShelf = shelve.open( gm_str+pn_str+rn_str+'.shelf' )
        gmShelf['TransModel'] = self.TransModel
        gmShelf['FinalLocs'] = self.FinalLocs
        #gmShelf['TracksInModel'] = self.TracksInModel
        gmShelf['GenTime'] = endTime - startTime
        gmShelf.close()
        
        return self.TransModel
    
    def readStates( self, fileName ):
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
        
    def CreateNS_TransitionModelFromProxemicGraphAndGPBetweenHoursForStates(self,yy,mm,dd,s_indx=0,e_indx=48,dmax=1.5,posNoise = None, sState=0,eState=3983 ):
        ''' Create Non stationary transition models. Meant for a more parallelized version though.
        Here, we pass this function a file called "states.txt" which it will
        process, and then ask it to handle a partial range. '''
        gm_str, rn_str, pn_str = 'gliderModelNS_GP_%04d%02d%02d_%d_%d_%d_%d'%(yy,mm,dd,s_indx,e_indx,sState,eState),'',''
        useNoisyStarts=False
        numDays = (e_indx - s_indx)/24 + 1
        u,v,time1,depth,lat,lon = \
            self.GetGP_RomsData(yy,mm,dd,numDays,True)
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays,True,True)
        print 'Generating the transition model for %04d-%02d-%02d over %d days using '%(yy,mm,dd,numDays)
        startTime = time.time()
        
        u_iv, v_iv = np.ma.masked_array(self.u_iv,np.isnan(self.u_iv)), np.ma.masked_array(self.v_iv,np.isnan(self.v_iv))
        
        u_ivmean,v_ivmean = np.sqrt(np.mean(u_iv[s_indx:e_indx,0],axis=0)).filled(np.nan), np.sqrt(np.mean(v_iv[s_indx:e_indx,0],axis=0)).filled(np.nan)
        
        if posNoise!=None:
            self.sigmaX = posNoise
            self.sigmaY = posNoise
            pn_str = '_%.3f'%(posNoise)
            useNoisyStarts = True
        else:
            self.sigmaX = None
            self.sigmaY = None
            
        defNoise = 0.05 # Default value of noise when we have NaNs
        states = self.readStates( "states.txt" )
        self.NoiseUsed = {}
        self.gModel = {}
        for stateIdx in range(sState,eState):#self.locG.nodes():
            a = states[ stateIdx ]
            #x1,y1 = self.GetXYfromNodeStr(a); lat1,lon1 = self.GetLatLonfromXY(x1,y1)
            t1,x1,y1 = a; lat1,lon1 = self.GetLatLonfromXY(x1,y1)
            for b in states.values():#self.locG.nodes():
                t2,x2,y2 = b; lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                #x2,y2 = self.GetXYfromNodeStr(b); lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                if a!=b:
                    if math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)) <= dmax:
                        lookupStr = '%d,%d,%d,%d,%d'%(t1,x1,y1,x2,y2)
                        if not self.TransModel.has_key(lookupStr):
                            #for t1 in range(s_indx,e_indx):
                            lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                            u_iv1,v_iv1 = BilinearInterpolate(lat1,lon1,lat,lon,u[t1]), \
                                          BilinearInterpolate(lat1,lon1,lat,lon,v[t1])
                            u_iv2,v_iv2 = BilinearInterpolate(lat2,lon2,lat,lon,u[t1+self.tMax]), \
                                          BilinearInterpolate(lat2,lon2,lat,lon,v[t1+self.tMax])
                            sigmaX1, sigmaY1 = np.sqrt(np.max(u_iv[t1:t1+self.tMax,0,x1,y1],axis=0)),np.sqrt(np.max(v_iv[t1:t1+self.tMax,0,x1,y1]))
                            sigmaX2, sigmaY2 = np.sqrt(np.max(u_iv[t1:t1+self.tMax,0,x2,y2],axis=0)),np.sqrt(np.max(v_iv[t1:t1+self.tMax,0,x2,y2]))
                            sX,sY = np.array([sigmaX1,sigmaX2]),np.array([sigmaY2,sigmaY2])
                            sXma,sYma = np.ma.masked_array(sX,np.isnan(sX)),np.ma.masked_array(sY,np.isnan(sY))
                            sigmaX,sigmaY = np.max(sXma), np.max(sYma)
                            sigmaX = sigmaY if (np.isnan(sigmaX) and not np.isnan(sigmaY) ) else sigmaX
                            sigmaY = sigmaX if (np.isnan(sigmaY) and not np.isnan(sigmaX) ) else sigmaY
                            if math.isnan(sigmaX): 
                                sigmaX = defNoise
                            if math.isnan(sigmaY): 
                                sigmaY = defNoise
                            print '%d,%d,%d,%d,%d, sigmaX=%.4f, sigmaY=%.4f'%(t1,x1,y1,x2,y2,sigmaX,sigmaY)
                            x_sims,y_sims,t_sims,xTrack,yTrack,tTrack = self.GenerateModelForActionStartingAtTime(x1, y1, x2, y2, dmax, t1, 30, useNoisyStarts, sigmaX, sigmaY )
                            if x_sims!=None and y_sims!=None:
                                lookupStr = '%d,%d,%d,%d,%d'%(t1,x1,y1,x2,y2)
                                #if debugMe:
                                #import pdb; pdb.set_trace()
                                self.FinalLocs[lookupStr] = (x_sims,y_sims,t_sims)
                                self.NoiseUsed[lookupStr] = (sigmaX,sigmaY)
                                #self.TracksInModel[lookupStr] = (xTrack,yTrack,tTrack)
                                zero_loc,max_dims,transProbs = self.CalculateTransProbabilitiesWithTime(x_sims, y_sims, t_sims, t1, 10)                             
                                if transProbs != None:
                                    self.TransModel[lookupStr] = (zero_loc,max_dims,transProbs)
                                #import pdb; pdb.set_trace()
        endTime = time.time()
        gmShelf = shelve.open( gm_str+pn_str+rn_str+'.shelf' )
        gmShelf['TransModel'] = self.TransModel
        gmShelf['FinalLocs'] = self.FinalLocs
        gmShelf['NoiseUsed'] = self.NoiseUsed
        #gmShelf['TracksInModel'] = self.TracksInModel
        gmShelf['GenTime'] = endTime - startTime
        gmShelf.close()
        
        return self.TransModel
        
    
    def CreateTransitionModelFromProxemicGraphAndGPBetweenHours2(self,yy,mm,dd,s_indx=0,e_indx=48,dmax = 1.5, posNoise = None):
        ''' Create the transition models '''
        numDays = int((e_indx-s_indx)/24+0.5)
        gm_str,rn_str,pn_str = 'gliderModelGP2_%04d%02d%02d_%d_%d'%(yy,mm,dd,s_indx,e_indx),'',''
        useNoisyStarts = False
        u,v,time1,depth,lat,lon = \
            self.GetGP_RomsData(yy,mm,dd,numDays,True)
        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays,True,True)
        print 'Generating the transition model for %04d-%02d-%02d over %d hours using '%(yy,mm,dd,numDays)
        startTime = time.time()
        
        u_iv, v_iv = np.ma.masked_array(self.u_iv,np.isnan(self.u_iv)), np.ma.masked_array(self.v_iv,np.isnan(self.v_iv))
        
        u_ivmean,v_ivmean = np.sqrt(np.mean(u_iv[s_indx:e_indx,0],axis=0)).filled(np.nan), np.sqrt(np.mean(v_iv[s_indx:e_indx,0],axis=0)).filled(np.nan)
        
        if posNoise!=None:
            self.sigmaX = posNoise
            self.sigmaY = posNoise
            pn_str = '_%.3f'%(posNoise)
            useNoisyStarts = True
        else:
            self.sigmaX = None
            self.sigmaY = None
            
        defNoise = 0.05
        self.gModel = {}
        for a in self.g.nodes():
            for b in self.g.nodes():
                if a!=b:
                    #import pdb; pdb.set_trace()
                    x1,y1 = self.GetXYfromNodeStr(a); lat1,lon1 = self.GetLatLonfromXY(x1,y1)
                    x2,y2 = self.GetXYfromNodeStr(b); lat2,lon2 = self.GetLatLonfromXY(x2,y2)
                    if math.sqrt((i-x)*(i-x)+(j-y)*(j-y)) <= dmax:
                        u_iv1,v_iv1 = BilinearInterpolate(lat1,lon1,lat,lon,u_ivmean), \
                            BilinearInterpolate(lat1,lon1,lat,lon,v_ivmean)
                        u_iv2,v_iv2 = BilinearInterpolate(lat2,lon2,lat,lon,u_ivmean), \
                            BilinearInterpolate(lat1,lon1,lat,lon,v_ivmean)
                        
                        sigmaX1, sigmaY1 = np.sqrt(np.max(u_iv[s_indx:e_indx,0,x1,y1],axis=0)),np.sqrt(np.max(v_iv[s_indx:e_indx,0,x1,y1]))
                        sigmaX2, sigmaY2 = np.sqrt(np.max(u_iv[s_indx:e_indx,0,x2,y2],axis=0)),np.sqrt(np.max(v_iv[s_indx:e_indx,0,x2,y2]))
                        sX,sY = np.array([sigmaX1,sigmaX2]),np.array([sigmaY2,sigmaY2])
                        sXma,sYma = np.ma.masked_array(sX,np.isnan(sX)),np.ma.masked_array(sY,np.isnan(sY))
                        sigmaX,sigmaY = np.max(sXma), np.max(sYma)
                        if math.isnan(sigmaX): 
                            sigmaX = defNoise
                        if math.isnan(sigmaY): 
                            sigmaY = defNoise
                        print '%d,%d,%d,%d, sigmaX=%.4f, sigmaY=%.4f'%(x1,y1,x2,y2,sigmaX,sigmaY)
                        x_sims,y_sims,xTrack,yTrack = self.GenerateModelForActionInHourRange(x1, y1, x2, y2, dmax, s_indx, e_indx, useNoisyStarts, sigmaX, sigmaY )
                        if x_sims!=None and y_sims!=None:
                            lookupStr = '%d,%d,%d,%d'%(x1,y1,x2,y2)
                            #if debugMe:
                            #import pdb; pdb.set_trace()
                            self.FinalLocs[lookupStr] = (x_sims,y_sims)
                            #self.TracksInModel[lookupStr] = (xTrack,yTrack)
                            self.NoiseUsed[lookupStr] = (sigmaX,sigmaY)
                            zero_loc,max_dims,transProbs = self.CalculateTransProbabilities(x_sims, y_sims, numDays-1)                             
                            if transProbs != None:
                                self.TransModel[lookupStr] = (zero_loc,max_dims,transProbs)
                        #import pdb; pdb.set_trace()
        endTime = time.time()
        gmShelf = shelve.open( gm_str+pn_str+rn_str+'.shelf' )
        gmShelf['TransModel'] = self.TransModel
        gmShelf['FinalLocs'] = self.FinalLocs
        gmShelf['NoiseUsed'] = self.NoiseUsed
        #gmShelf['TracksInModel'] = self.TracksInModel
        gmShelf['GenTime'] = endTime - startTime
        gmShelf.close()
                            
        return self.TransModel
    
    

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
