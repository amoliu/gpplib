''' **GenGliderModelUsingRoms** - This is a swiss-army knife module with a class called GliderModel,
which does a ton of stuff.
'''
import numpy as np
import scipy.io as sio
import math
import shelve
from InterpRoms import * # This has our Trilinear interpolation
import os, re
from SfcstOpener import SfcstOpen
import time
import random

class GliderModel(object):
    ''' **GliderModel class**. This is one of the most important classes in 'gpplib' since it contains
    most of the tools necessary for
        
        1. Loading ROMS current data
        2. Running Simulations (with full 3-d simulation or 2-d simulation)
        3. Running Re-entrant Simulations (again with full 3-d or 2-d simulations)
        4. Collision Detection routines
        5. Risk-map plotting routines
        6. Plotting current maps
        7. Create Transition models
        
    '''
    def __init__(self,shelfName='RiskMap.shelf',sfcst_directory='./'):
        self.scale = 1    # 1 unit = 1 km
        self.latDegInM,self.lonDegInM,self.gVel = 110913.73, 92901.14,0.278 # 0.278 m/sec
        self.gVelNom = self.gVel # gVelNom is used to compute how long a dive will take, gVel is the real vel.
        self.gVelVar  = 0.1
        self.gDirVar  = 0.1
        self.numTrials = 24
        self.maxTimeSteps = 5.
        self.Tp = 250.   # A glider yo has a period of approximately 250 secs. to about 400 secs.
        self.maxDepth = 60.
        self.ObsThresh = 0.99
        self.MaxObsSteps = 10
        self.MinDepth = 0.0
        self.MaxDepth = 80.0;
        self.UseRomsNoise = False
        self.sigmaCurU = 0.1
        self.sigmaCurV = 0.1
        self.TransModel={}
        self.FinalLocs = {}
        self.TracksInModel={}
        self.Initialized = False
        self.doneSimulating = False
        self.InitFromRiskMapShelf(shelfName)
        self.sfcst_directory = sfcst_directory
        self.sfOpen = SfcstOpen()
        self.sigmaX = 0.3
        self.sigmaY = 0.3
        self.LastRomsDataLoaded = None
        self.LastDepthAvgCur = None
        pass
    
    
    def SimulateDive(self,sLat,sLon,tLat,tLon,maxDepth,u,v,lat,lon,depth,t,FullSimulation=True,HoldValsOffMap=True):
        ''' **SimulateDive** : Perform a full kinematic simulation for a dive.
        
        Args: sLat,sLon,tLat,tLon,maxDepth,u,v,lat,lon,depth,t,FullSimulation=True,HoldValsOffMap=True
        
            sLat, sLon : start latitude and longitude
            tLat, tLon : target latitude and longitude
            maxDepth : maximum depth for the dive.
            u,v : An np.array containing the Roms currents for that particular day.
            these are in the form: u[time,depth,lon,lat], v[time,depth,lon,lat]
            lat,lon : An array with the lat, lon values for which ROMS currents are available.
            depth : Depth array with the depths for which ROMS currents are available.
            t : time index which should be used
            FullSimulation : True for 3d simulation. False for 2d simulation.
            HoldValsOffMap : Flag indicating whether going off the map should be treated as a collision or not
        
        Returns: latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision
            
            latFin, lonFin : final latitude and longitude after the simulation
            latArray, lonArray, depthArray, tArray : lat, lon, depth and time arrays
            possibleCollision : true if a collision is detected.
            CollisionReason : string indicating the reason for collision.
        '''
        self.sLat, self.sLon, self.tLat,self.tLon = sLat,sLon,tLat,tLon
        CollisionReason = None
        possibleCollision = False
        latDiff,lonDiff = (tLat-sLat)*self.latDegInM, (tLon-sLon)*self.lonDegInM
        dist = math.sqrt(latDiff**2 + lonDiff**2)
        angle = math.atan2(latDiff, lonDiff)
        timeReqd = dist/self.gVelNom
        numYos = math.floor(timeReqd/self.Tp+0.5)
        yoTime = numYos * self.Tp
        if FullSimulation==True:
            dT = self.Tp/self.maxTimeSteps
        else:
            dT = self.Tp/self.maxTimeSteps
        tArray = np.arange(0,timeReqd,dT)
        d1,d2 = FindLowAndHighIndices(maxDepth,depth)
        d0,d1 = FindLowAndHighIndices(self.MinDepth,depth)
        #import pdb; pdb.set_trace()
        depthAvgCurStr = '%04d%02d%02d_%d'%(self.yy,self.mm,self.dd,self.numDays)
        if self.LastDepthAvgCur != depthAvgCurStr:
            d1,d2 = FindLowAndHighIndices(maxDepth,self.depth)
            d0,d1 = FindLowAndHighIndices(self.MinDepth,self.depth)
            u2,v2 = self.u[:,d0:d2,:,:],self.v[:,d0:d2,:,:]
            print 'Averaging depths between indices %d and %d.'%(d0,d2)
            u2ma,v2ma = np.ma.masked_array(u2,np.isnan(u2)),np.ma.masked_array(v2,np.isnan(v2))
            self.dAvgU,self.dAvgV = u2ma.mean(axis=1).filled(np.nan),v2ma.mean(axis=1).filled(np.nan)
            self.depthArray = maxDepth/2. *(2-np.cos(2*math.pi/self.Tp * tArray)) - maxDepth/2.
            #u2,v2 = self.u[:,0:d2,:,:],self.v[:,0:d2,:,:]
            #self.dAvgU,self.dAvgV = u2.mean(axis=1),v2.mean(axis=1)
            self.LastDepthAvgCur = depthAvgCurStr
        (tMax,dMax,l1Max,l2Max) = u.shape
        #import pdb; pdb.set_trace()
        myLat,myLon = sLat,sLon
        x,y = 0,0
        prevU,prevV = None,None
        xArray,yArray = [],[]
        latArray,lonArray = [],[]
        
        #import pdb; pdb.set_trace()
        t_prime = float(t)
        totalDist = 0.
        
        curNoiseU = random.gauss(0,self.sigmaCurU)
        curNoiseV = random.gauss(0,self.sigmaCurV)
        
        for i in range(0,len(tArray)):
                    tVal = int(t_prime)
                    if(tVal>=tMax-1.):
                        tVal = tMax-1.
                    
                    if FullSimulation==True:
                        '''
                         Slower, (plausibly more accurate) kinematic simulation which relies upon 
                         trilinear interpolation to handle simulations.
                        '''
                        curU,curV = TriLinearInterpolate(self.depthArray[i],myLat,myLon,int(tVal),depth,lat,lon,u),\
                                    TriLinearInterpolate(self.depthArray[i],myLat,myLon,int(tVal),depth,lat,lon,v)
                    else:
                        '''
                         Faster, simulation using depth-averaged bilinear interpolation.
                        '''
                        curU,curV = BilinearInterpolate(myLat,myLon,lat,lon,self.dAvgU[int(tVal)]), \
                                BilinearInterpolate(myLat,myLon,lat,lon,self.dAvgV[int(tVal)])
                    if math.isnan(curU) or math.isnan(curV):
                        if prevU==None and prevV==None:
                                CollisionReason = 'RomsNanAtStart'
                                possibleCollision = True
                                break
                        if not HoldValsOffMap:
                                CollisionReason = 'RomsNanLater'
                                possibleCollision = True
                                break
                        else:
                            curU,curV = prevU,prevV
                    
                    if  self.GetObs(myLat,myLon,HoldValsOffMap):
                        CollisionReason = 'Obstacle'
                        possibleCollision = True
                        break
                        
                    if (self.UseRomsNoise == True):
                        curU = curU + curNoiseU
                        curV = curV + curNoiseV    

                    effU,effV = self.gVel*math.cos(angle) + curU, self.gVel*math.sin(angle) + curV
                    deltaX,deltaY = effU*dT,effV*dT
                    deltaR = math.sqrt(deltaX**2+deltaY**2)
                    totalDist += deltaR
                    x,y = x+deltaX, y+deltaY #(x+(effU*dT)),(y+(effV*dT))
                    t_prime+=dT/3600.
                    myLat,myLon = sLat+y/self.latDegInM, sLon+x/self.lonDegInM
                    latArray.append(myLat) 
                    lonArray.append(myLon)
                    prevU,prevV = curU, curV
                    #xArray.append(x)
                    #yArray.append(y)
                #import pdb; pdb.set_trace()
        # Truncate the depth and time arrays if they are longer than the position arrays.
        lonArrayLen = len(lonArray)
        tArray = tArray[0:lonArrayLen]; self.depthArray= self.depthArray[0:lonArrayLen] # Truncate the array here...         
        
        xFin,yFin = x,y
        latFin,lonFin = myLat,myLon
        return xFin,yFin,latFin,lonFin,latArray,lonArray,self.depthArray,tArray,possibleCollision,CollisionReason,totalDist
    
    def OpenSfcstFile(self,sfcst_directory,yy,mm,dd):
        ''' Open a Small-Forecast ROMS data file. These are data files stored in Matlab structures,
        which have been provided to us 'JPL<http://ourocean.jpl.nasa.gov>'.
        
        Args:

            * sfcst_directory(str) : Indicates the ROMS data directory where the small-forecast files are stored.
            * yy (int) : Year
            * mm (int) : Month
            * dd (int) : Day


        Returns:

            * u (numpy array) : easting currents
            * v (numpy array) : westing currents
            * time (numpy array) : time array
            * depth (numpy array) : depth array
            * lat (numpy array) : lat array
            * lon (numpy array) : lon array
        '''
        temp_sfcst = sio.loadmat('%s/sfcst_%04d%02d%02d.mat'%(sfcst_directory,yy,mm,dd))
        if temp_sfcst.has_key('forecast'):
            forecast = temp_sfcst['forecast'][0]
            u = forecast['u'][0]['u'][0][0]
            v = forecast['v'][0]['v'][0][0]
            time = forecast['time']
            depth = forecast['depth']
            lat = forecast['lat']
            lon = forecast['lon']
        return u,v,time,depth,lat,lon
    
    def TruncateOffMapIndices(self,i,j):
        tHeight,tWidth = self.riskMapArray.shape
        if i<1:
            i=1
        if j<0:
            j=0
        if i>tWidth-1:
            i=tWidth-1
        if j>tHeight-1:
            j=tHeight-1
        return i,j        
    
    def GetObs(self,lat,lon,OffMapNotObs=False):
        ''' Get whether a location is an obstacle or not.
        This is being checked on the original obstacle map.
        
        Args:
            * lat (float) : latitude
            * lon (float) : longitude
            * OffMapNotObs=False (bool): When true going off the map is a collision. When false, the off-map location is an extrapolation of the nearest on-map pixel.
        
        Returns:
            * 1 if Obstacle
            * 0 otherwise
        
        '''
        i,j = self.GetPxPyFromLatLon(lat, lon)
        tHeight,tWidth = self.obsMap.shape
        if i>=1 and j>=1 and i<=(tWidth-1) and j<=(tHeight-1):
            return self.obsMap[int(j),int(i)]
        else:
            if OffMapNotObs==False: # We are going to treat being off map as an obstacle
                return 1
            else:
                i,j = self.TruncateOffMapIndices(i, j)
                return self.obsMap[int(j),int(i)]
            
    def GetRiskFromRiskMapArray(self,j,i):
        ''' Get Risk Values from the risk map array with indices from the risk map itself.
        The locations are rounded up to the nearest integer before a direct lookup in the 
        map is done. (No bilinear interpolation for now).
        
        Args: j,i
            * j (float) : y-axis location
            * i (float) : x-axis location
            
        Returns:
            * value of riskMapArray[j,i]
        '''
        i,j = self.TruncateOffMapIndices(i, j)
        return self.riskMapArray[int(j),int(i)]
    
    def GetRisk(self,lat,lon,OffMapNotObs=False):
        ''' Get Risk Values for Lat-Lon location
        
        Args: lat,lon,OffMapNotObs=True
            * lat (float) : Latitude
            * lon (float) : Longitude
            * OffMapNotObs (bool) : Whether going off the map should be treated as a collision.
        
        Returns:
            * value of risk from RiskMapArray
        '''
        i,j = self.GetPxPyFromLatLon(lat, lon)
        tHeight,tWidth = self.riskMapArray.shape
        if i>=0 and j>=0 and i<tWidth and j<tHeight:
            return self.riskMapArray[int(j),int(i)]
        else:
            if not OffMapNotObs: # We are going to treat being off map as an obstacle
                return 1.0
            else:
                i,j = self.TruncateOffMapIndices(i, j)
                return self.riskMapArray[int(j),int(i)]
    
    def ObsDetLatLon(self,lat1,lon1,lat2,lon2):
        ''' Detect if the straight line path between (and including) the given lat/lon locations 
        has a collision or not.
        
        Args: lat1,lon1,lat2,lon2
            * lat1, lon1 : lat/lon locations for the first point
            * lat2, lon2 : lat/lon locations for the second point
        
        Returns:
            True if collision detected (i.e. will run into an obstacle)
            False if this is a free straight line path
        '''
        if self.GetRisk(lat1,lon1)>=self.ObsThresh or self.GetRisk(lat2,lon2)>=self.ObsThresh:
            return True
        #import pdb; pdb.set_trace()
        if lon1<lon2:
            sLon,eLon = lon1,lon2
        else:
            sLon,eLon = lon2,lon1
        if lat1<lat2:
            sLat,eLat = lat1,lat2
        else:
            sLat,eLat = lat2,lat1
        if lon1!=lon2:
            m1=(lat2-lat1)/float(lon2-lon1)
            LON = np.linspace(sLon,eLon,self.MaxObsSteps)
            for lon0 in LON:
                lat0=m1*(lon0-lon1)+lat1
                if self.GetRisk(lat0,lon0)>=self.ObsThresh:
                    return True
        if lat1!=lat2:
            m2=(lon2-lon1)/float(lat2-lat1)
            LAT = np.linspace(sLat,eLat,self.MaxObsSteps)
            for lat0 in LAT:
                lon0 = m2*(lat0-lat1)+lon1
                if self.GetRisk(lat0,lon0)>=self.ObsThresh:
                    return True
        return False
        
    def GetPxPyFromLatLon(self,my_lat,my_lon):
        '''
        Sometimes we might want to get the x,y location in px from the original risk/bathymap.
        '''
        py = (my_lat - self.lat0deg)/self.py2deg
        px = (my_lon - self.lon0deg)/self.px2deg
        return px,py
    
    def GetLatLonFromPxPy(self,my_px,my_py):
        '''
        If we want to get the lat,lon from the original risk/bathymap.
        '''
        lat = self.lat0deg+ my_py*self.py2deg
        lon = self.lon0deg+ my_px*self.px2deg
        return lat,lon
    
    ''' Initializes the map from the shelf. This function expects the data in the shelf to be of a certain type.
    The variables that it updates are:
        1. riskMap  : This has a sub-sampled version of the risk map.
        2. riskMapArray: 
        3. lat_pts, lon_pts 
    '''
    def InitFromRiskMapShelf(self,shelfName):
        riskMapShelf = shelve.open(shelfName,writeback=False)
        self.riskMap = riskMapShelf['riskMap'][::-1,:]
        self.riskMapArray = riskMapShelf['riskMapArray'][::-1,:]
        self.lat_pts, self.lon_pts = riskMapShelf['lat_pts'], riskMapShelf['lon_pts']
        self.x_pts, self.y_pts = riskMapShelf['x_pts'], riskMapShelf['y_pts']
        self.obsMap = riskMapShelf['obsMap'][::-1,:]
        self.px2deg,self.py2deg = riskMapShelf['px2deg'],riskMapShelf['py2deg']
        self.px2m,self.py2m = riskMapShelf['px2m'], riskMapShelf['py2m']
        self.latDeg2m,self.lonDeg2m = riskMapShelf['latDeg2m'],riskMapShelf['lonDeg2m']
        self.lat0deg,self.lon0deg = riskMapShelf['lat0deg'],riskMapShelf['lon0deg']
        #self.LatLonLocs = riskMapShelf['LatLonLocs']
        
        self.lpGraph = riskMapShelf['NodesInGraph']
        self.lpProxemics = riskMapShelf['LandProxemics']
        self.convVals = riskMapShelf['convVals']
        self.ReverseY = False
        riskMapShelf.close()
        self.Width,self.Height = self.riskMap.shape
        self.Initialized = True
    
    def GetXYfromLatLon(self,my_lat, my_lon):
        lat2y,lon2x = (self.Height-1)/(self.lat_pts[self.Height-1]-self.lat_pts[0]), (self.Width-1)/(self.lon_pts[self.Width-1]-self.lon_pts[0])
        x,y = (my_lon-self.lon_pts[0])* lon2x , (my_lat-self.lat_pts[0])*lat2y
        if self.ReverseY:
            y=self.Height-y-1
        return x,y
    
    def GetLatLonfromXY(self,x,y):
        if self.ReverseY:
            y = self.Height-y-1
        y2lat,x2lon = (self.lat_pts[self.Height-1]-self.lat_pts[0])/float(self.Height-1), (self.lon_pts[self.Width-1]-self.lon_pts[0])/float(self.Width-1)
        lon,lat = x*x2lon + self.lon_pts[0], y*y2lat + self.lat_pts[0]
        return lat,lon
    
    
    def GetLatLonFromPotMapXY(self,x,y):
        '''
        This converts from PotentialMapXY coordinates to Lat-Lon. Look at GetRiskObsMaps.py for more details.
        '''
        x0,y0 = self.xL/self.deltaX,self.yD/self.deltaY
        #self.x2lon,self.y2lat = self.#rMap.GetLonDiff()/self.w, rMap.GetLatDiff()/self.h
        self.pX2lon,self.pY2lat = self.x2lon * self.deltaX, self.y2lat * self.deltaY
        return rMap.GetOyDeg()+(y0+y)*self.pY2lat,rMap.GetOxDeg()+(x0+x)*self.pX2lon
   
    def GetRmapXYfromLatLon(self,lat,lon):
       x0,y0 = 0,0
       lon0,lat0 = rMap.GetOxDeg(),rMap.GetOyDeg()
       self.lon2x,self.lat2y = self.w/rMap.GetLonDiff(), self.h/rMap.GetLatDiff()
       return x0+((lon-lon0)*self.lon2x),y0+((lat-lat0)*self.lat2y)
    
    def GetXYfromNodeStr(self,nodeStr):
        ''' Convert from the name of the node string to the locations.
        Args:
            nodeStr (string): A string in the form of '(x,y)'.
        
        Returns:
            x,y if the string is in the form expected.
            None,None if a mal-formed string.
        '''
        m = re.match('\(([0-9\.]+),([0-9\.]+)\)',nodeStr)
        if m:
            return int(m.group(1)),int(m.group(2))
        else:
            return None, None
    
    '''
    def FindNearestNodeOnGraph(self,curNode, goal):
        nearest_dist = float('inf')
        nearest_node = (None,None)
        
        if curNode != goal: # Unless we're aiming for the goal
            minDist = 0.4   # we probably do NOT want to keep aiming
        else:               # for a node which we're already close to.
            return goal
        
        for a in self.lpGraph.nodes():
            i,j = curNode
            x,y = self.GetXYfromNodeStr(a)
            dist = math.sqrt((i-x)**2+(j-y)**2)
            if not self.ObsDetLatLon(self.lat_pts[j],self.lon_pts[i], \
                                                            self.lat_pts[y],self.lon_pts[x]):
                    if dist<nearest_dist and dist>=minDist:
                        nearest_node =  (x,y)
                        nearest_dist = dist
        return nearest_node
    '''
    
    
    
    
    def CalculateTransProbabilities(self,x_sims,y_sims,numDays=3):
        '''
        Given the simulation vectors, compute the transition probabilities.
        Here x_sim[i],y_sim[i] should be the final surfacing locations after each dive.
        '''
        x_sims,y_sims = np.where(np.isnan(x_sims),0,x_sims), np.where(np.isnan(y_sims),0,y_sims)
        x_sims,y_sims  = x_sims[x_sims.nonzero()],y_sims[y_sims.nonzero()]
        numNonZeros = len(x_sims)
        if numNonZeros > 0:
            x_min,x_max,y_min,y_max = np.min(x_sims) , np.max(x_sims), np.min(y_sims), np.max(y_sims)
            zero_loc = math.ceil(np.max(np.abs([x_min,x_max,y_min,y_max])))
            max_dims = 2 * zero_loc +1
            transProbs = np.zeros((max_dims,max_dims))
            # Round off to the nearest location.
            #import pdb; pdb.set_trace()
            numTrials = numNonZeros# 24*numDays
            for i in range(0,numTrials):
                transProbs[math.floor(y_sims[i]+0.5)+zero_loc][math.floor(x_sims[i]+0.5)+zero_loc]=\
                    transProbs[math.floor(y_sims[i]+0.5)+zero_loc][math.floor(x_sims[i]+0.5)+zero_loc]+1
            transProbs = transProbs/float(numTrials)
            return zero_loc,max_dims,transProbs
        return None,None,None
    
    def GenerateTransitionModelString(self,lookupStr,TransModel):
        '''
        Generate Transition model string - useful for saving the model to file.
        '''
        midVal,arrSize,modelArray = TransModel[0],TransModel[1],TransModel[2]
        outputStr = '%s, %f %f '%(lookupStr,midVal,arrSize)
        for i in range(0,int(arrSize)):
            for j in range(0,int(arrSize)):
               outputStr+='%f '%(modelArray[i][j])
        return outputStr
    
    def LatLonToRomsXY(self,lat0,lon0,lat,lon):
        '''
        Convert from Lat-Lon to ROMS XY.
        
        Args: lat0,lon0,lat,lon
            * lat0 (float) : Latitude to be converted
            * lon0 (float) : Longitude to be converted
            * lat (np-array) : Numpy array containing lat array from ROMS
            * lon (np-array) : Numpy array containing lon array from ROMS
        
        Returns:
            * x (float) : Roms X-index
            * y (float) : Roms Y-index
        '''
        y,y1 = FindLowAndHighIndices(lat0,lat)
        x,x1 = FindLowAndHighIndices(lon0,lon)
        return x,y
    
    def GetRomsData(self,yy,mm,dd,numDays,useNewFormat = True,useForeCastOnly = False ):
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
        if self.LastRomsDataLoaded != dataToBeLoaded:
            self.numDays = numDays
            daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]
            if yy%4 == 0:
                daysInMonths[1] = 29
            if useNewFormat:
                u,v,time,depth,lat,lon = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d_0.mat'%(self.sfcst_directory,yy,mm,dd))
            else:
                u,v,time,depth,lat,lon = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d.mat'%(self.sfcst_directory,yy,mm,dd))
            myDay, myMonth, myYear = dd,mm,yy
            
        if useForeCastOnly:
            for i in range(1,3):
                u1,v1,time1,depth1,lat1,lon1 = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d_%d.mat'%(self.sfcst_directory,yy,mm,dd,i))
                u,v=np.concatenate((u,u1),axis=0),np.concatenate((v,v1),axis=0)
                time1=time1+np.ones((24,1))*24*i
                time=np.concatenate((time,time1),axis=0)
                self.numDays = numDays
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time,depth,lat,lon
            self.yy,self.mm,self.dd,self.numDays = yy,mm,dd,i
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
                if useNewFormat:
                    u1,v1,time1,depth1,lat1,lon1 = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d_0.mat'%(self.sfcst_directory,myYear,myMonth,myDay))
                else:
                    u1,v1,time1,depth1,lat1,lon1 = self.sfOpen.LoadFile('%s/sfcst_%04d%02d%02d.mat'%(self.sfcst_directory,myYear,myMonth,myDay))
                #import pdb;pdb.set_trace()
                u,v=np.concatenate((u,u1),axis=0),np.concatenate((v,v1),axis=0)
                time1=time1+np.ones((24,1))*24*day
                time=np.concatenate((time,time1),axis=0)
                self.numDays = numDays
            self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time,depth,lat,lon
            self.yy,self.mm,self.dd,self.numDays = yy,mm,dd,numDays
        return self.u,self.v,self.time1,self.depth,self.lat,self.lon
    
    def PlotNewRiskMapFig(self,DispLandWhite=True):
        ''' PlotNewRiskmapFig - Produces a pretty picture from the RiskMapArray which is 
        useful for providing a context within which to plot simulation results. Requires
        'matplotlib<http://matplotlib.sourceforge.net>' pyplot functionality
        ''' 
        import matplotlib.pyplot as plt
        rMap,width,height = self.riskMap,self.Width,self.Height
        mapResX, mapResY = 200, 200
        X,Y = np.linspace(-0.5,width-0.5,mapResX),np.linspace(-0.5,height+0.5,mapResY)
        aX,aY = np.meshgrid(X,Y)
        Z = np.zeros((mapResX,mapResY))
        for j in range(0,mapResY):
            for i in range(0,mapResX):
                lat,lon = self.GetLatLonfromXY(X[i],Y[j])
                Z[j,i] = self.GetRisk(lat,lon)
        plt.pcolor(aX,aY,Z)
        plt.xlim((-0.5,width-0.5))
        plt.ylim((-0.5,height+0.5))
        
    def PlotCurrentField(self,t,**kwargs):
        ''' PlotNewRiskmapFig - Produces a pretty picture from the RiskMapArray which is 
        useful for providing a context within which to plot simulation results. Requires
        'matplotlib<http://matplotlib.sourceforge.net>' pyplot functionality
        
        Args: t
            * t (int) : time index for the current data file that was loaded last.
        ''' 
        if kwargs.has_key('max_depth'):
            max_depth = kwargs['max_depth']
        else:
            max_depth = self.MaxDepth
        if kwargs.has_key('min_depth'):
            min_depth = kwargs['min_depth']
        else:
            min_depth = self.MinDepth
        if kwargs.has_key('arrow_color'):
            arrow_color = kwargs['arrow_color']
        else:
            arrow_color = 'k'
            
        d0,d1 = FindLowAndHighIndices(min_depth,self.depth)
        d1,d2 = FindLowAndHighIndices(max_depth,self.depth)
        print 'Averaging depths between indices %d and %d.'%(d0,d2)
        
        import matplotlib.pyplot as plt
        mapResX, mapResY = 20, 20
        width,height = self.Width, self.Height
        #import pdb; pdb.set_trace()
        u2,v2 = self.u[:,d0:d2,:,:],self.v[:,d0:d2,:,:]
        u2ma,v2ma = np.ma.masked_array(u2,np.isnan(u2)),np.ma.masked_array(v2,np.isnan(v2))
        u_mean, v_mean = u2ma.mean(axis=1).filled(np.nan),v2ma.mean(axis=1).filled(np.nan)
        
        #u_mean, v_mean = self.u.mean(axis=1),self.v.mean(axis=1)
        X,Y = np.linspace(0, width-0.5, mapResX), np.linspace(0, height-0.5, mapResY)
        aX,aY = np.meshgrid(X,Y)
        U,V = np.zeros((mapResX,mapResY)),np.zeros((mapResX,mapResY))
        for j in range(0,mapResY):
            for i in range(0,mapResX):
                myLat,myLon = self.GetLatLonfromXY(X[i],Y[j])
                if self.GetRisk(myLat, myLon, False )<0.9:
                    U[j,i], V[j,i] = BilinearInterpolate(myLat,myLon,self.lat,self.lon,u_mean[int(t)]), \
                                    BilinearInterpolate(myLat,myLon,self.lat,self.lon,v_mean[int(t)])
        q = plt.quiver(aX,aY,U,V,scale=self.gVel*10,color=arrow_color)
        p = plt.quiverkey(q,1,height-0.5,self.gVel,"%.3f m/s"%(self.gVel),coordinates='data',color='k')
                
    def GenerateModelForAction(self,i,j,x,y,d_max,numDays,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 ):
        ''' Generates the model for taking a certain action (on the discrete planning graph).
        
        Args: i,j,x,y,d_max,numDays,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 
        
        '''
        x_sims,y_sims = np.zeros((24*numDays-1,1)),np.zeros((24*numDays-1,1))
        xTrack,yTrack = [],[] 
        if self.ObsDetLatLon(self.lat_pts[j],self.lon_pts[i],self.lat_pts[y],self.lon_pts[x])==False:
            if math.sqrt((i-x)*(i-x)+(j-y)*(j-y)) <= d_max and (i,j)!=(x,y):
                startT = time.time()
                print 'Generating model from %d,%d to %d,%d. Starting at time: %f to do %d trials.'%(i,j,x,y,startT,24*(numDays-1))
                
                for k in range(0,24*(numDays-1)):
                        if not usingNoisyStarts:
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(self.lat_pts[j], self.lon_pts[i], \
                                                          self.lat_pts[y], self.lon_pts[x], self.maxDepth,\
                                                          self.u, self.v, self.lat, self.lon, self.depth, k, False)
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
                        else:
                            if len(tempX)>=2 and len(tempY)>=2:
                                x_sims[k],y_sims[k] = (tempX[-1:]-i),(tempY[-1:]-j)
                            else:
                                x_sims[k],y_sims[k] = 0,0
                endT = time.time()
                print ' Took: %f secs.'%(endT-startT)
                return x_sims,y_sims,xTrack,yTrack
        return None,None,None,None
    
    
    def GenerateModelForActionInHourRange(self,i,j,x,y,d_max,s_indx=0,e_indx=48,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 ):
        ''' Generates the model for taking a certain action (on the discrete planning graph).
        
        Args: i,j,x,y,d_max,numDays,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 
        
        '''
        numDays = int((e_indx-s_indx)/24+0.5)
        
        x_sims,y_sims = np.zeros((e_indx-s_indx,1)),np.zeros((e_indx-s_indx,1))
        xTrack,yTrack = [],[] 
        if self.ObsDetLatLon(self.lat_pts[j],self.lon_pts[i],self.lat_pts[y],self.lon_pts[x])==False:
            if math.sqrt((i-x)*(i-x)+(j-y)*(j-y)) <= d_max and (i,j)!=(x,y):
                startT = time.time()
                print 'Generating model from %d,%d to %d,%d. Starting at time: %f to do %d trials.'%(i,j,x,y,startT,e_indx-s_indx)
                
                for k in range(s_indx,e_indx):
                        if not usingNoisyStarts:
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(self.lat_pts[j], self.lon_pts[i], \
                                                          self.lat_pts[y], self.lon_pts[x], self.maxDepth,\
                                                          self.u, self.v, self.lat, self.lon, self.depth, k, False)
                        else: # Using Noisy starts
                            sLat,sLon = self.GetLatLonfromXY(i+random.gauss(0,noiseSigmaX), j+random.gauss(0,noiseSigmaY)); 
                            gLat,gLon = self.GetLatLonfromXY(x+random.gauss(0,noiseSigmaX), y+random.gauss(0,noiseSigmaY));
                            #import pdb; pdb.set_trace()
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(sLat, sLon, gLat, gLon, self.maxDepth, \
                                                          self.u, self.v, self.lat, self.lon, self.depth, k , False)
                        tempX,tempY = self.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
                        xTrack.append(tempX); yTrack.append(tempY)
                        if possibleCollision == False:
                            if len(tempX) > 0:
                                x_sims[k-s_indx],y_sims[k-s_indx] = (tempX[-1:]-i),(tempY[-1:]-j)
                        else:
                            if len(tempX)>=2 and len(tempY)>=2:
                                x_sims[k-s_indx],y_sims[k-s_indx] = (tempX[-1:]-i),(tempY[-1:]-j)
                            else:
                                x_sims[k-s_indx],y_sims[k-s_indx] = 0,0
                endT = time.time()
                print ' Took: %f secs.'%(endT-startT)
                return x_sims,y_sims,xTrack,yTrack
        return None,None,None,None
    
    
    def GenerateModelForActionStartingAtTime(self,i,j,x,y,d_max,s_indx=0,numRuns=30,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 ):
        ''' Generates the model for taking a certain action (on the discrete planning graph).
        
        Args: i,j,x,y,d_max,s_indx=0,numRuns=30,usingNoisyStarts=False, noiseSigmaX=0.3, noiseSigmaY=0.3 
        
        '''
        x_sims,y_sims, t_sims = np.zeros((numRuns,1)),np.zeros((numRuns,1)),np.zeros((numRuns,1))
        xTrack,yTrack,tTrack = [],[],[] 
        if self.ObsDetLatLon(self.lat_pts[j],self.lon_pts[i],self.lat_pts[y],self.lon_pts[x])==False:
            if math.sqrt((i-x)*(i-x)+(j-y)*(j-y)) <= d_max and (i,j)!=(x,y):
                startT = time.time()
                print 'Generating model from %d,%d to %d,%d (starting at %d). Starting at time: %f to do %d trials.'%(i,j,x,y,s_indx,startT,numRuns)
                for k in range(0,numRuns):
                        if not usingNoisyStarts:
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(self.lat_pts[j], self.lon_pts[i], \
                                                          self.lat_pts[y], self.lon_pts[x], self.maxDepth,\
                                                          self.u, self.v, self.lat, self.lon, self.depth, k, False)
                        else: # Using Noisy starts
                            sLat,sLon = self.GetLatLonfromXY(i+random.gauss(0,noiseSigmaX), j+random.gauss(0,noiseSigmaY)); 
                            gLat,gLon = self.GetLatLonfromXY(x+random.gauss(0,noiseSigmaX), y+random.gauss(0,noiseSigmaY));
                            xFin,yFin,latFin,lonFin,latArray,lonArray,depthArray,tArray,possibleCollision,CollisionReason,totalDist = \
                                        self.SimulateDive(sLat, sLon, gLat, gLon, self.maxDepth, \
                                                          self.u, self.v, self.lat, self.lon, self.depth, s_indx , False)
                        tempX,tempY = self.GetXYfromLatLon(np.array(latArray), np.array(lonArray))
                        xTrack.append(tempX); yTrack.append(tempY), tTrack.append(np.array(tArray))
                        if possibleCollision == False:
                            if len(tempX) > 0:
                                x_sims[k],y_sims[k],t_sims[k] = (tempX[-1:]-i),(tempY[-1:]-j),(tArray[-1:]-tArray[0])
                        else:
                            if len(tempX)>=2 and len(tempY)>=2:
                                x_sims[k],y_sims[k],t_sims[k] = (tempX[-1:]-i),(tempY[-1:]-j),(tArray[-1:]-tArray[0])
                            else:
                                x_sims[k],y_sims[k],t_sims[k] = 0,0,0
                endT = time.time()
                print ' Took: %f secs.'%(endT-startT)
                return x_sims,y_sims,t_sims,xTrack,yTrack,tTrack
        return None,None,None,None,None,None
    
    def CalculateTransProbabilitiesWithTime(self,x_sims,y_sims,t_sims, t_start,tMax):
        ''' Given the simulation vectors, compute the transition probabilities.
            Here x_sim[i],y_sim[i] should be the final surfacing locations after each dive.
        '''
        
        x_sims,y_sims = np.where(np.isnan(x_sims),0,x_sims), np.where(np.isnan(y_sims),0,y_sims)
        t_sims = np.where(t_sims/3600.>tMax,0,t_sims/3600.)
        x_sims,y_sims,t_sims  = x_sims[x_sims.nonzero()],y_sims[x_sims.nonzero()],t_sims[x_sims.nonzero()]
        x_sims,y_sims,t_sims  = x_sims[y_sims.nonzero()],y_sims[y_sims.nonzero()],t_sims[y_sims.nonzero()]
        x_sims,y_sims,t_sims  = x_sims[t_sims.nonzero()],y_sims[t_sims.nonzero()],t_sims[t_sims.nonzero()]

        #x_sims,y_sims,t_sims = t_sims[t_sims.nonzero()]
        numNonZeros = len(x_sims)
        if numNonZeros > 0:
            x_min,x_max,y_min,y_max = np.min(x_sims) , np.max(x_sims), np.min(y_sims), np.max(y_sims)
            zero_loc = math.ceil(np.max(np.abs([x_min,x_max,y_min,y_max])))
            max_dims = 2 * zero_loc +1
            transProbs = np.zeros((max_dims,max_dims,tMax))
            numTrials = numNonZeros
            #import pdb; pdb.set_trace()
            for i in range(0,numTrials):
                transProbs[math.floor(y_sims[i]+0.5)+zero_loc][math.floor(x_sims[i]+0.5)+zero_loc][math.floor(t_sims[i]+0.5)]=\
                    transProbs[math.floor(y_sims[i]+0.5)+zero_loc][math.floor(x_sims[i]+0.5)+zero_loc][math.floor(t_sims[i]+0.5)]+1
            transProbs = transProbs/float(numTrials)
            return zero_loc, max_dims, transProbs
        return None, None, None
    
    def GenerateTransitionModelsUsingRomsData(self,yy,mm,dd,numDays=3,d_max=1.5,useNoisyStarts=False,saveTextFile=False,modelNum=0):
        ''' Perform lots of simulations to get the transition models.
        
        Args: yy,mm,dd,numDays=3,d_max=1.5,useNoisyStarts=False,saveTextFile=False,modelNum=0
            * yy (int) : Year
            * mm (int) : Month
            * dd (int) : Day
            * numDays (int) : Number of days to simulate for
            * useNoisyStarts (bool) : Whether to use random locations for starts. If so, set the position noise by doing  
        
        '''
        if saveTextFile == True:
            saveFileName = 'GliderModel_%d_dmax_%d'%(modelNum,d_max)
            f1 = open(saveFileName,'w')
        

        u,v,time1,depth,lat,lon = self.GetRomsData(yy,mm,dd,numDays)
        #self.u,self.v,self.time1,self.depth,self.lat,self.lon = u,v,time1,depth,lat,lon
        # Go create a larger set of arrays with u,v,lat,lon
        for j in range(0,self.Height):
            for i in range(0,self.Width):
                for y in range(0,self.Height):
                    for x in range(0,self.Width):
                        x_sims,y_sims,xTrack,yTrack = self.GenerateModelForAction(i, j, x, y, d_max, numDays, useNoisyStarts, self.sigmaX, self.sigmaY )
                        if x_sims!=None and y_sims!=None:
                            lookupStr = '%d,%d,%d,%d'%(i,j,x,y)
                            self.FinalLocs[lookupStr] = (x_sims,y_sims)
                            self.TracksInModel[lookupStr] = (xTrack,yTrack)
                            zero_loc,max_dims,transProbs = self.CalculateTransProbabilities(x_sims, y_sims, numDays-1)                             
                            if transProbs != None:
                                self.TransModel[lookupStr] = (zero_loc,max_dims,transProbs)
                            #import pdb; pdb.set_trace()
                            if saveTextFile == True:
                                str2bWritten = self.GenerateTransitionModelString(lookupStr, self.TransModel[lookupStr])
                                f1.write(str2bWritten+"\n")
        if saveTextFile == True:
            f1.close()
        return self.TransModel

    def RepairTransitionModel(self):
        self.DeletedModelEntries = []
        TransModelKeys = self.TransModel.keys()
        # Recalculate the Transition Probabilities based upon the final Locations
        for t_key in TransModelKeys:
            x_sims,y_sims = self.FinalLocs['%s'%(t_key)]
            zero_loc,max_dims,transProbs = self.CalculateTransProbabilities(x_sims, y_sims)
            if transProbs == None:
                deletedEntry = self.TransModel.pop('%s'%(t_key))
                self.FinalLocs.pop('%s'%(t_key))
                print 'Removing Transition Model %s: '%(t_key),deletedEntry
                self.DeletedModelEntries.append(deletedEntry)
        return self.TransModel
    
    def InitSim(self,sLat,sLon,tLat,tLon,maxDepth,startT,FullSimulation=True,HoldValsOffMap=True):
        ''' Re-entrant Simulation Initialization function.
    
        '''
        self.sLat,self.sLon,self.tLat,self.tLon,self.maxDepth,self.startT = sLat,sLon,tLat,tLon,maxDepth,startT
        depthAvgCurStr = '%04d%02d%02d_%d'%(self.yy,self.mm,self.dd,self.numDays)
        
        self.MaxDepth = maxDepth
        
        if self.LastDepthAvgCur != depthAvgCurStr:
            d1,d2 = FindLowAndHighIndices(maxDepth,self.depth)
            d0,d1 = FindLowAndHighIndices(self.MinDepth,self.depth)
            u2,v2 = self.u[:,d0:d2,:,:],self.v[:,d0:d2,:,:]
            print 'Averaging depths between indices %d and %d.'%(d0,d2)
            u2ma,v2ma = np.ma.masked_array(u2,np.isnan(u2)),np.ma.masked_array(v2,np.isnan(v2))
            self.dAvgU,self.dAvgV = u2ma.mean(axis=1).filled(np.nan),v2ma.mean(axis=1).filled(np.nan)
            #u2,v2 = self.u[:,0:d2,:,:],self.v[:,0:d2,:,:]
            #self.dAvgU,self.dAvgV = u2.mean(axis=1),v2.mean(axis=1)
            self.LastDepthAvgCur = depthAvgCurStr
        latDiff,lonDiff = (self.tLat-self.sLat)*self.latDegInM, (self.tLon-self.sLon)*self.lonDegInM
        self.dist = math.sqrt(latDiff**2 + lonDiff**2)
        self.angle = math.atan2(latDiff, lonDiff)
        self.timeReqd = self.dist/self.gVel
        self.numYos = math.floor(self.timeReqd/self.Tp+0.5)
        self.yoTime = self.numYos * self.Tp
        self.FullSimulation = FullSimulation
        if FullSimulation==True:
            self.dT = self.Tp/self.maxTimeSteps
        else:
            self.dT = self.Tp/self.maxTimeSteps
        self.tArray = np.arange(0,self.timeReqd,self.dT)
        self.CollisionReason = None
        self.possibleCollision = False
        
        #import pdb; pdb.set_trace()
        self.myLat,self.myLon = sLat,sLon
        self.x,self.y = 0,0
        self.prevU,self.prevV = None,None
        self.xArray,self.yArray = [],[]
        self.latArray,self.lonArray = [],[]
        self.depthArray = maxDepth/2. *(2-np.cos(2*math.pi/self.Tp * self.tArray)) - maxDepth/2. - self.MinDepth
        #import pdb; pdb.set_trace()
        self.t_prime = float(startT)
        self.totalDist = 0.
        self.lastIndx = 0
        curNoiseU = random.gauss(0,self.sigmaCurU)
        curNoiseV = random.gauss(0,self.sigmaCurV)
        self.doneSimulating = False
        
    
    
    def SimulateDive_R(self,MaxTimeToSimulate=-1,HoldValsOffMap=True):
        '''
        Re-entrant Simulator: This simulation call does a re-entrant simulation to allow to allow
        small dive-simulations to be done, which can be broken down by fractions of time.
        
        Method:
            1. InitSim(sLat,sLon,tLat,tLon,maxDepth,startT,FullSimulation=True,HoldValsOffMap=True)
            2. SimulateDive_R(ReEnter=False,MaxTimeToSimulate=-1,HoldValsOffMap=True)
    
        MaxTimeToSimulate should be >0 to actually cause the simulator to simulate for a certain
        amount of time.
    
        Args:
        '''
        (tMax,dMax,l1Max,l2Max) = self.u.shape
        i = self.lastIndx
        
        simulTime = 0.0
        dTinHrs = self.dT/3600.
        
        for i in range(self.lastIndx,len(self.tArray)):
                    tVal = int(self.t_prime)
                    if(tVal>=tMax-1.):
                        tVal = tMax-1.
                    
                    if self.FullSimulation==True:
                        '''
                         Slower, (plausibly more accurate) kinematic simulation which relies upon 
                         trilinear interpolation to handle simulations.
                        '''
                        curU,curV = TriLinearInterpolate(self.depthArray[i],self.myLat,self.myLon,int(tVal),self.depth,self.lat,self.lon,self.u),\
                                    TriLinearInterpolate(self.depthArray[i],self.myLat,self.myLon,int(tVal),self.depth,self.lat,self.lon,self.v)
                    else:
                        '''
                         Faster, simulation using depth-averaged bilinear interpolation.
                        '''
                        curU,curV = BilinearInterpolate(self.myLat,self.myLon,self.lat,self.lon,self.dAvgU[int(tVal)]), \
                                BilinearInterpolate(self.myLat,self.myLon,self.lat,self.lon,self.dAvgV[int(tVal)])
                    if math.isnan(curU) or math.isnan(curV):
                        if self.prevU==None and self.prevV==None:
                                self.CollisionReason = 'RomsNanAtStart'
                                self.possibleCollision = True
                                self.doneSimulating = True
                                break
                        if not HoldValsOffMap:
                                self.CollisionReason = 'RomsNanLater'
                                self.possibleCollision = True
                                self.doneSimulating = True
                                break
                        else:
                            curU,curV = self.prevU,self.prevV
                    
                    if  self.GetObs(self.myLat,self.myLon,HoldValsOffMap):
                        self.CollisionReason = 'Obstacle'
                        self.possibleCollision = True
                        self.doneSimulating = True
                        break
                        
                    if (self.UseRomsNoise == True):
                        curU = curU + curNoiseU
                        curV = curV + curNoiseV    

                    effU,effV = self.gVel*math.cos(self.angle) + curU, self.gVel*math.sin(self.angle) + curV
                    deltaX,deltaY = effU*self.dT,effV*self.dT
                    deltaR = math.sqrt(deltaX**2+deltaY**2)
                    self.totalDist += deltaR
                    self.x,self.y = self.x+deltaX, self.y+deltaY #(x+(effU*dT)),(y+(effV*dT))
                    self.t_prime+=dTinHrs
                    simulTime += dTinHrs
                    self.myLat,self.myLon = self.sLat+self.y/self.latDegInM, self.sLon+self.x/self.lonDegInM
                    self.latArray.append(self.myLat) 
                    self.lonArray.append(self.myLon)
                    self.prevU,self.prevV = curU, curV
                    if MaxTimeToSimulate>0:
                        if simulTime>=MaxTimeToSimulate:
                            self.doneSimulating = False
                            break
                    self.lastIndx = i
        if self.lastIndx >= (len(self.tArray)-1):
            self.doneSimulating = True # We actually got done!
        self.xFin,self.yFin = self.x, self.y
        self.latFin,self.lonFin = self.myLat,self.myLon
        
        # Truncate the depth and time arrays if they are longer than the position arrays.
        lonArrayLen = len(self.lonArray)
        self.tArray = self.tArray[0:lonArrayLen]; self.depthArray= self.depthArray[0:lonArrayLen] # Truncate the array here... 
        
        return self.xFin,self.yFin,self.latFin,self.lonFin,self.latArray,self.lonArray,self.depthArray,self.tArray,self.possibleCollision,self.CollisionReason,self.totalDist

                
