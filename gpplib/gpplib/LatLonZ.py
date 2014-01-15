import bisect
import numpy as np

class LatLonZ(object):

    def __init__(self,lat,lon,Z):
        self.lat, self.lon, self.Z = lat,lon,Z
        
    def FilterLatLonZ_ValuesBetweenLatLonValues(self,latN=34.15,latS=33.0,lonW=-119.0,lonE=-117.5):
        ''' Filter out the data that does not fall in the range
         (latS,latN) and (lonW,lonE) 
             Args:
                 lat,lon,Z (nparrays): Y,X,Z data
                 latN, latS, lonW, lonE (floats): the ranges.
                 
            Returns:
                filtered lat,lon,Z vectors
         '''
        idxN = np.where(self.lat<=latN)
        lat = self.lat[idxN]; lon=self.lon[idxN]; Z=self.Z[idxN]
        idxS = np.where(lat>=latS)
        lat = lat[idxS]; lon=lon[idxS]; Z=Z[idxS]
        idxE = np.where(lon<=lonE)
        lat = lat[idxE]; lon=lon[idxE]; Z=Z[idxE]
        idxW = np.where(lon>=lonW)
        self.lat = lat[idxW]; self.lon=lon[idxW]; self.Z=Z[idxW]
        self.argSortLat, self.argSortLon = np.argsort(self.lat), np.argsort(self.lon)
        self.lowIndLat, self.lowIndLon = 0, 0
        self.highIndLat, self.highIndLon = self.lat.shape[0],self.lon.shape[0]
        self.latRev = self.lat[::-1]
        self.lonRev = self.lon[::-1]
        self.ZRev = self.Z[::-1]
        
        self.latStep = self.latRev.shape[0]/np.unique(self.latRev).shape[0]
    
        return self.lat, self.lon, self.Z
    
    ''' This is too slow!!! O(n^4) in the worst-case!
    def getNearestZforLatLon(self,lat,lon):
        lat_indx = np.where(self.lat== self.lat[np.fabs(self.lat-lat).argmin()])
        tLat,tLon,tZ = self.lat[lat_indx], self.lon[lat_indx], self.Z[lat_indx]
        #lon_indx = np.where(tLon==lon)
        closest_indx = np.fabs(tLon-lon).argmin()
        return tZ[closest_indx]
    '''

    def findNearestIndexToLatLon(self,lat,lon):
        lat_indx = bisect.bisect_left(self.latRev, lat) # This is the location where we are looking for
        closest_indx = np.fabs(self.lonRev[lat_indx:lat_indx+self.latStep]-lon).argmin()
        return closest_indx+lat_indx

    
    def getNearestZforLatLon(self,lat,lon):
        ''' We were not able to find lat,lon quickly enough using the more powerful
            numpy versions. (too many operations).
            
            Super fast k*log(n) lookups.
        '''
        return self.ZRev[self.findNearestIndexToLatLon(lat, lon)]
    
    def getLinInterpZforLatLon(self,lat,lon):
        ''' While the nearest Z value from the previous step might work to some extent, we need 
            a better way to get the true Z value around this lat-lon location.
        '''
        Delta = 0.0005
        i = self.findNearestIndexToLatLon(lat, lon)
        #import pdb;pdb.set_trace()
        if lat>=self.latRev[i]:
            lat1 = self.latRev[i]; lat2 = lat+Delta
        else:
            lat1 = lat-Delta; lat2 = self.latRev[i]
        
        if lon>=self.lonRev[i]:
            lon1 = self.lonRev[i]; lon2=lon+Delta
        else:
            lon1 = lon-Delta; lon2=self.lonRev[i]
        
        # could be optimized further, but let us go with this for now.
        i11 = self.findNearestIndexToLatLon(lat1,lon1)
        i12 = self.findNearestIndexToLatLon(lat2,lon1)
        i21 = self.findNearestIndexToLatLon(lat1,lon2)
        i22 = self.findNearestIndexToLatLon(lat2,lon2)
        
        xDif = self.lonRev[i22] - self.lonRev[i11]
        yDif = self.latRev[i22] - self.latRev[i11]
        fQ11,fQ12,fQ21,fQ22 = self.ZRev[i11],self.ZRev[i12],self.ZRev[i21],self.ZRev[i22]
        if xDif !=0 and yDif !=0:
            return (fQ11*(self.lonRev[i22]-lon)*(self.latRev[i22]-lat) + \
                    fQ12*(self.lonRev[i22]-lon)*(lat-self.latRev[i11])+ \
                    fQ21*(lon-self.lonRev[i11])*(self.latRev[i22]-lat)+ \
                    fQ22*(lon-self.lonRev[i11])*(lat-self.latRev[i11]))/(xDif*yDif)
        else:
            return (fQ11+fQ22+fQ21+fQ22)/4.0
        
        