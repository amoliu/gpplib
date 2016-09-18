#!/usr/bin/python
import os
import sys
import subprocess
import math

class LatLonMap():
    
    def __init__( self, res ):
        '''
         Socal Bight = -117 W to -121 W, 32 N to 34.5 N
         Len of Lat degrees in m = 110913.73 
         Len of Lon degrees in m = 92901.14
        '''
        self.lat_deg = 110913.73
        self.lon_deg = 92901.14
        
        ''' But we are going to concentrate only on the LA-Longbeach Areas for now '''
        self.ox_deg = -118.8
        self.oy_deg = 33.25
        
        self.res_x = res
        self.res_y = res
        
        self.res_lat = self.res_y / self.lat_deg
        self.res_lon = self.res_x / self.lon_deg
        
        # These are values for the region we are interested in.
        self.lat_diff = 0.8833333
        self.lon_diff = 1.1
        
        self.max_lat_diff = self.lat_diff / self.res_lat
        self.max_lon_diff = self.lon_diff / self.res_lon
        
        self.max_y_diff = math.ceil(self.lat_diff * self.lat_deg / self.res_y)
        
    def GetXY(self, lat, lon ):
        x = ( lon - self.ox_deg ) / self.res_lon
        y = self.max_y_diff - ( lat - self.oy_deg ) / self.res_lat
        
        return x,y
    
    def GetLatLon(self, x, y):
        lat = ( (self.max_y_diff - y) * self.res_lat ) + self.oy_deg
        lon = ( x * self.res_lon ) + self.ox_deg
        
        return lat,lon
    
    def WebbToDecimalDeg(self, w_lat_deg, w_lat_min , w_lon_deg, w_lon_min ):
        lat_sign, lon_sign = 1, 1
        if w_lat_deg < 0:
            lat_sign = -1
        if w_lon_deg < 0:
            lon_sign = -1
        lat = lat_sign * (abs(w_lat_deg) + abs(w_lat_min/60.0))
        lon = lon_sign * (abs(w_lon_deg) + abs(w_lon_min/60.0))
        
        return lat, lon
    
    def GetSign(self,deg):
        if deg < 0:
            return -1
        else : return 1
    
    def DecimalDegToWebb(self, lat_dec_deg, lon_dec_deg ):
        lat_sign, lon_sign = 1, 1
        if lat_dec_deg < 0:
            lat_sign = -1
        if lon_dec_deg < 0:
            lon_sign = -1
            
        w_lat_deg = int(lat_dec_deg)
        w_lon_deg = int(lon_dec_deg)
        
        w_lat_min = (abs(lat_dec_deg) - abs(w_lat_deg)) * 60.0
        w_lon_min = (abs(lon_dec_deg) - abs(w_lon_deg)) * 60.0
        
        return w_lat_deg * lat_sign , w_lat_min  , w_lon_deg * lon_sign, w_lon_min
        
    def DegDegToFullWebb(self, lat_dec_deg, lon_dec_deg ):
         wLatDeg, wLatMin, wLonDeg, wLonMin = self.DecimalDegToWebb(lat_dec_deg, lon_dec_deg )
         webbLat = abs(wLatDeg)*100. +wLatMin
         webbLon = abs(wLonDeg)*100. +wLonMin
         return webbLat*self.GetSign(lat_dec_deg), webbLon*self.GetSign(lon_dec_deg)
'''
def main():
    #Test it 
    lat_deg = [ 33, 33, 33, 33, 33 ]
    lat_min = [ 31.3089, 31.3455, 31.345, 31.3089, 29.8704 ]
    lon_deg = [ -118, -118, -118, -118, -118  ]
    lon_min = [ 13.8057, 05.4241, 05.4241, 13.8057, 31.545 ]
    
    m = LatLonMap( 100 )
    
    dec_lat = []
    dec_lon = []
    for i in range(0,5):
        temp_lat, temp_lon = m.WebbToDecimalDeg(lat_deg[i], lat_min[i], lon_deg[i], lon_min[i])
        print( "Webb to Lat-Lon ", temp_lat, temp_lon )
        dec_lat.append(temp_lat)
        dec_lon.append(temp_lon)
    
    w_lat_deg = []
    w_lat_min = []
    w_lon_deg = []
    w_lon_min = []
    for i in range(0,5):
        temp_lat_deg, temp_lat_min, temp_lon_deg, temp_lon_min = m.DecimalDegToWebb(dec_lat[i], dec_lon[i] )
        print("Lat-Lon to Webb", temp_lat_deg, temp_lat_min, temp_lon_deg, temp_lon_min, )
        
    
    x = []
    y = []    
    # Now we get the locations for the lat-lon pairs on the map
    for i in range(0,5):
        temp_x,temp_y = m.GetXY(dec_lat[i], dec_lon[i])
        print("Lat-Lon to XY", temp_x, temp_y )
        x.append(temp_x)
        y.append(temp_y)
        
        
main()
'''    