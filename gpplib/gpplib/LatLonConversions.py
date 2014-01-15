'''
Created on Sep 2, 2011
@summary: This Class is used to convert between Webb and Decimal degree formats for Lat, Lon
@author: Arvind Antonio de Menezes Pereira
'''

#!/usr/bin/python
import math
import numpy as np

class LLConvert():
    ''' Lat Lon Conversion routines from Webb to Decimal formats
    '''
    def __init__( self ):
        '''
         Socal Bight = -117 W to -121 W, 32 N to 34.5 N
         Len of Lat degrees in m = 110913.73 
         Len of Lon degrees in m = 92901.14
        '''
        
    def NpWebbToDecimalDeg(self,w_lat, w_lon):
        ''' Convert from Webb lat/lon degrees to decimal degrees
        Args:
            w_lat (np.array): latitude in Webb format
            w_lon (np.array): longitude in Webb format
        Returns:
            lat,lon: (np.array) latitude and longitude in degrees
        '''
        wLatMa,wLonMa = np.ma.masked_array(w_lat,np.isnan(w_lat)),np.ma.masked_array(w_lon,np.isnan(w_lon))
        w_lat_deg,w_lon_deg = np.floor(np.abs(wLatMa)/100.),np.floor(np.abs(wLonMa)/100.)
        latSign,lonSign = np.sign(wLatMa),np.sign(wLonMa)
        w_lat_min, w_lon_min = np.abs(wLatMa) - (np.abs(w_lat_deg)*100.), \
                                np.abs(wLonMa) - (np.abs(w_lon_deg)*100.)
        lat, lon = (latSign * (np.abs(w_lat_deg)+np.abs(w_lat_min/60.))).filled(np.nan), \
                    (lonSign * (np.abs(w_lon_deg)+np.abs(w_lon_min/60.))).filled(np.nan)
                    
        return lat, lon
    
    def WebbToDecimalDeg(self, w_lat, w_lon ):
        ''' Convert from Webb Lat/Lon to Decimal degrees 
        Args:
            w_lat (float): latitude in Webb format
            w_lon (float): longitude in Webb format
            
        Returns:
            lat,lon: (float) latitude and longitude in degrees
        '''
        if  not math.isnan(w_lat) and not math.isnan(w_lon):
            lat_sign, lon_sign = 1,1
            w_lat_deg = math.floor(abs(w_lat)/100.0)
            w_lon_deg = math.floor(abs(w_lon)/100.0)
            if w_lat < 0:
                lat_sign = -1
            if w_lon < 0:
                lon_sign = -1
            w_lat_min = abs(w_lat) - (abs(w_lat_deg)*100.0)
            w_lon_min = abs(w_lon) - (abs(w_lon_deg)*100.0)
            lat = lat_sign * (abs(w_lat_deg)+ abs(w_lat_min/60.))
            lon = lon_sign * (abs(w_lon_deg)+ abs(w_lon_min/60.))
            return lat,lon
        return float('nan'),float('nan')
    
    def NpDecimalDegToWebb(self, lat, lon ):
        ''' Convert from Decimal degrees to Webb Lat/Lon (Vectorized implementation)
        Args:
            lat_dec_deg (float): latitude in degrees
            lon_dec_deg (float): longitude in degrees
            
        Returns:
            lat,lon: (float) latitude and longitude in Webb format
        '''
        latMa, lonMa = np.ma.masked_array(lat,np.isnan(lat)),np.ma.masked_array(lon,np.isnan(lon))
        latSign,lonSign = np.sign(latMa),np.sign(lonMa)
        w_lat_deg, w_lon_deg = np.floor(np.abs(latMa)), np.floor(np.abs(lonMa))
        w_lat_min, w_lon_min = (np.abs(latMa)-w_lat_deg)*60., \
                            (np.abs(lonMa)-w_lon_deg)*60.
        w_lat, w_lon = (latSign * (w_lat_deg*100.+w_lon_min)).filled(np.nan), \
                lonSign*(w_lon_deg*100.+w_lon_min).filled(np.nan)
        
        return w_lat, w_lon
    
    def DecimalDegToWebb(self, lat_dec_deg, lon_dec_deg ):
        ''' Convert from Decimal to Webb Lat/Lon 
        Args:
            lat_dec_deg (float): latitude in degrees
            lon_dec_deg (float): longitude in degrees
            
        Returns:
            lat,lon: (float) latitude and longitude in Webb format
        '''
        if not math.isnan(lat_dec_deg) and not math.isnan(lon_dec_deg):
            lat_sign, lon_sign = 1,1
            if lat_dec_deg < 0:
                lat_sign = -1
            if lon_dec_deg < 0:
                lon_sign = -1
            w_lat_deg =  math.floor(abs(lat_dec_deg))
            w_lon_deg =  math.floor(abs(lon_dec_deg))
            w_lat_min = (abs(lat_dec_deg) - w_lat_deg) * 60.
            w_lon_min = (abs(lon_dec_deg) - w_lon_deg) * 60.
            w_lat = lat_sign * (w_lat_deg * 100. + w_lat_min)
            w_lon = lon_sign * (w_lon_deg * 100. + w_lon_min)
            return w_lat, w_lon
        return float('nan'), float('nan')

    def DegMinToDecimalDeg(self, w_lat_deg, w_lat_min , w_lon_deg, w_lon_min ):
        lat_sign, lon_sign = 1, 1
        if w_lat_deg < 0:
            lat_sign = -1
        if w_lon_deg < 0:
            lon_sign = -1
        lat = lat_sign * (abs(w_lat_deg) + abs(w_lat_min/60.0))
        lon = lon_sign * (abs(w_lon_deg) + abs(w_lon_min/60.0))
        return lat, lon
    
    
    def DecimalDegToDegMin(self, lat_dec_deg, lon_dec_deg ):
        lat_sign, lon_sign = 1, 1
        if lat_dec_deg < 0:
            lat_sign = -1
        if lon_dec_deg < 0:
            lon_sign = -1
        w_lat_deg = int(abs(lat_dec_deg))
        w_lon_deg = int(abs(lon_dec_deg))
        w_lat_min = (abs(lat_dec_deg) - abs(w_lat_deg)) * 60.0
        w_lon_min = (abs(lon_dec_deg) - abs(w_lon_deg)) * 60.0
        return w_lat_deg * lat_sign , w_lat_min  , w_lon_deg * lon_sign, w_lon_min