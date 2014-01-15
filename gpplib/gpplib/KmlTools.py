'''
@author: Arvind Antonio de Menezes Pereira
@summary: Mini python kml creator for creating tracks.

'''

import os
import re
import time
import math
import gpplib
from gpplib.LatLonConversions import *
import simplekml


class GpplibKml(object):
    def __init__(self,**kwargs):
        self.kml = ''

    def GetUnixTimeFromString(self,str):
        #int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone
        return int(time.mktime(time.strptime( str, '%Y-%m-%d %H:%M:%S'))) - time.timezone
    
    def GetTimeString(self,epoch):
        str = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(epoch))
        return str
    
    def GetKMLTimeString(self,epoch):
        str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch))
        return str

    def AddKmlHeader(self,documentName=''):
        self.kml += '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2"'
        self.kml += ' xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2"'
        self.kml += ' xmlns:atom="http://www.w3.org/2005/Atom">\n'
        self.kml += '<Document>\n'
        self.kml += '<name>%s</name>'%(documentName)
        self.AddAirportStyleMap()
        
    def AddAirportStyleMap(self):
        self.kml += '<StyleMap id="msn_airports">\n<Pair><key>normal</key><styleUrl>#sn_airports</styleUrl></Pair>\n'
        self.kml += '<Pair><key>highlight</key><styleUrl>#sh_airports</styleUrl></Pair>\n</StyleMap>\n'
        self.kml += '<Style id="sh_airports"><IconStyle><color>ff10ffe8</color><scale>1.4</scale>\n'
        self.kml += '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>\n'
        self.kml += '<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>\n'
        self.kml += '</IconStyle></Style>\n'
        self.kml += '<Style id="sn_airports"><IconStyle><color>ff10ffe8</color><scale>1.2</scale>\n'
        self.kml += '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>\n'
        self.kml += '<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>\n'
        self.kml += '</IconStyle></Style>\n'

    def AddCustomStyleMap(self,**kwargs):
        if kwargs.has_key('BalloonStyle'):
            pass
        if kwargs.has_key('IconStyle'):
            pass
        if kwargs.has_key('LabelStyle'):
            pass
        if kwargs.has_key('LineStyle'):
            pass
        if kwargs.has_key('ListStyle'):
            pass
        if kwargs.has_key('PolyStyle'):
            pass

    def CloseKmlHeader(self):
        self.kml = self.kml+ '</Document>\n</kml>\n'
        
    def AddFolder(self,folderName,**kwargs):
        self.kml = self.kml+ '<Folder>\n<name>' + folderName +'</name>\n'
    
    def AddPlaceMark(self,placeMarkName,**kwargs):
        if kwargs.has_key('styleUrl'):
            style_url = kwargs['styleUrl']
        else:
            style_url = '#msn_airports'
        self.kml += '<Placemark>\n<name>%s</name>\n'%(placeMarkName) + '<styleUrl>%s</styleUrl>\n'%(style_url)
    
    def ClosePlaceMark(self):
        self.kml = self.kml+ '</Placemark>\n'

    def CloseFolder(self):
        self.kml = self.kml +'</Folder>\n'
        
    def WriteKml(self,fileName):
        m_kml = re.match('([\w]+).[kK][mM][lL]$',fileName)
        if not m_kml:
            fileName = fileName+'.kml'
        self.f = open(fileName,'w')
        self.f.write(self.kml)
        self.f.close()






class KmlTrackCreator( GpplibKml ):
    def __init__(self,**kwargs):
        super(KmlTrackCreator,self).__init__(**kwargs)
        
    def AddWebbLatLonTrack(self,myTime,lat,lon,depth,altMode):
        llConv = LLConvert()
        self.kml = self.kml + '<gx:Track>'
        self.when_str,self.cood_str,self.altMode_str = '','',''
        self.cood_lat,self.cood_lon,self.cood_alt,self.cood_when = [],[],[],[]
        for i in range(0,len(lat)):
            if not math.isnan(lat[i]) and not math.isnan(lon[i]) and not math.isnan(depth[i]) and not math.isnan(myTime[i]):
                d_lat,d_lon = llConv.WebbToDecimalDeg(lat[i], lon[i] )
                d_time =  GetKMLTimeString(myTime[i])
                d_depth = -depth[i]
                self.cood_lat.append(d_lat)
                self.cood_lon.append(d_lon)
                self.cood_alt.append(d_depth)
                self.cood_when.append(d_time)
        for when in self.cood_when:
            self.when_str = self.when_str+'<when>'+when+'</when>\n'  
        for i in range(len(self.cood_lat)):
            self.cood_str = self.cood_str+'<gx:coord>%f %f %f </gx:coord>\n'%(self.cood_lon[i],self.cood_lat[i],self.cood_alt[i])
        for i in range(len(self.cood_lat)):
            self.altMode_str = self.altMode_str+'<altitudeMode>%s</altitudeMode>\n'%(altMode)
        self.kml = self.kml + self.when_str
        self.kml = self.kml + self.cood_str
        self.kml = self.kml + self.altMode_str
        self.CloseTrack()
        
    def AddLatLonTrack(self,myTime,lat,lon,depth,altMode):
        llConv = LLConvert()
        self.kml = self.kml + '<gx:Track>'
        self.when_str,self.cood_str,self.altMode_str = '','',''
        self.cood_lat,self.cood_lon,self.cood_alt,self.cood_when = [],[],[],[]
        for i in range(0,len(lat)):
            if not math.isnan(lat[i]) and not math.isnan(lon[i]) and not math.isnan(depth[i]) and not math.isnan(myTime[i]):
                d_lat,d_lon = lat[i],lon[i] #%llConv.WebbToDecimalDeg(lat[i], lon[i] )
                d_time =  self.GetKMLTimeString(myTime[i])
                d_depth = depth[i]
                self.cood_lat.append(d_lat)
                self.cood_lon.append(d_lon)
                self.cood_alt.append(d_depth)
                self.cood_when.append(d_time)
        for when in self.cood_when:
            self.when_str = self.when_str+'<when>'+when+'</when>\n'  
        for i in range(len(self.cood_lat)):
            self.cood_str = self.cood_str+'<gx:coord>%f %f %f </gx:coord>\n'%(self.cood_lon[i],self.cood_lat[i],self.cood_alt[i])
        for i in range(len(self.cood_lat)):
            self.altMode_str = self.altMode_str+'<altitudeMode>%s</altitudeMode>\n'%(altMode)
        self.kml = self.kml + self.when_str
        self.kml = self.kml + self.cood_str
        self.kml = self.kml + self.altMode_str
        self.CloseTrack()
        
    def CloseTrack(self):
        self.kml = self.kml + '</gx:Track>\n'
    
    def CreateWebbKmlTrack(self,myTime,lat,lon,depth,altMode,folderName,placeMarkName):
        self.AddKmlHeader()
        self.AddFolder(folderName)
        self.AddPlaceMark(placeMarkName)
        self.AddWebbLatLonTrack(myTime, lat, lon, depth,altMode)
        self.ClosePlaceMark()
        self.CloseFolder()
        self.CloseKmlHeader()
    
    def CreateLatLonKmlTrack(self,myTime,lat,lon,depth,altMode,folderName,placeMarkName):
        self.AddKmlHeader()
        self.AddFolder(folderName)
        self.AddPlaceMark(placeMarkName)
        self.AddLatLonTrack(myTime, lat, lon, depth,altMode)
        self.ClosePlaceMark()
        self.CloseFolder()
        self.CloseKmlHeader()
    
import simplekml
from simplekml import Kml, Color
import os


class GpplibSimpleKML(object):
    def __init__(self,**kwargs):
        self.kml = simplekml.Kml(open=1)
        
    def GetUnixTimeFromString(self,str):
        #int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone
        return int(time.mktime(time.strptime( str, '%Y-%m-%d %H:%M:%S'))) - time.timezone
    
    def GetTimeString(self,epoch):
        str = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(epoch))
        return str
    
    def GetKMLTimeString(self,epoch):
        str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch))
        return str

    def SaveKmlFile(self,fileName):
        self.kml.save(fileName)
        
    def SaveKmzFile(self,fileName,**kwargs):
        self.kml.savekmz(fileName)
        
        



class WaypointListKML(GpplibSimpleKML):
    ''' Create a waypoint list KML - Ideal for mission GOTO_L files '''
    def __init__(self,**kwargs):
        super(WaypointListKML,self).__init__(**kwargs)
        
    def CreateWaypointList(self,WaypointLat,WaypointLon,**kwargs):
        if kwargs.has_key('name'):
            line_name = kwargs['name']
        else: line_name = 'waypoint-list'
        if kwargs.has_key('line-width'):
            linewidth = kwargs['line-width']
        else: linewidth = 3
        if kwargs.has_key('line-color'):
            linecolor = kwargs['line-color']
        else: linecolor = Color.black
        if kwargs.has_key('line-alpha'):
            linealpha = kwargs['line-alpha']
        else: linealpha = 100
        if kwargs.has_key('Altitude'):
            Altitude = kwargs['Altitude']
        else:
            Altitude = []
        if len(WaypointLat) != len(WaypointLon):
            raise
        if Altitude==[]:
            Altitude = [1.0]*len(WaypointLat)
        
        linestring = self.kml.newlinestring(name='%s'%(line_name))
        linestring.coords = zip(WaypointLon,WaypointLat,Altitude)
        linestring.altitudemode = simplekml.AltitudeMode.relativetoground
        #linestring.extrude = 1
        linestring.style.linestyle.width = linewidth
        linestring.style.linestyle.color = Color.changealpha("%s"%(linealpha),linecolor)
        
                # Draw the waypoints.
        start_wpt = self.kml.newpoint()
        start_wpt.coords = [(WaypointLon[0],WaypointLat[0])]
        start_wpt.name = 'Start'
        start_wpt.description = 'Start Waypoint.\nCoords (%.6f,%.6f)'%(WaypointLat[0],WaypointLon[0])
        start_wpt.style.iconstyle.icon.href="http://maps.google.com/mapfiles/kml/paddle/grn-stars.png"
        
        goal_wpt = self.kml.newpoint()
        goal_wpt.coords = [(WaypointLon[-1],WaypointLat[-1])]
        goal_wpt.name = 'Goal'
        goal_wpt.description = 'Goal Waypoint.\nCoords (%.6f,%.6f)'%(WaypointLat[-1],WaypointLon[-1])
        goal_wpt.style.iconstyle.icon.href="http://maps.google.com/mapfiles/kml/paddle/G.png"
        
        if len(WaypointLon)>2:
            for idx,(wptLon,wptLat) in enumerate( zip(WaypointLon[1:-1],WaypointLat[1:-1]) ):
                int_wpt = self.kml.newpoint()
                int_wpt.coords = [(wptLon,wptLat,1.0)]
                int_wpt.description = 'Wpt %d,\nCoords (%.6f,%.6f)'%(idx+1,wptLat,wptLon)
                int_wpt.style.iconstyle.icon.href='http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png'
            

        


class GppKmlTrack( GpplibSimpleKML ):
    def __init__(self,**kwargs):
        super(GppKmlTrack,self).__init__(**kwargs)
        
    def CreateGxTrack(self,myTime,lat,lon,depth,**kwargs):
        ''' Create a GxTrack using SimpleKml
        
        Args:
            myTime : a list of time-epochs for the track
            lat    : a list of the latitude
            lon    : a list of the longitude
            depth  : a list of the depths (increasing depth +ve below water surface)
        
        Kwargs:
            roll   : roll in degrees
            pitch  : pitch in degrees
            yaw    : yaw in degrees
        '''
        roll,pitch,yaw = None, None, None
        if kwargs.has_key('yaw'):
            yaw = kwargs['yaw']
        if kwargs.has_key('pitch'):
            pitch=kwargs['pitch']
        if kwargs.has_key('roll'):
            roll =kwargs['roll']
                    
        coords = zip(lon,lat,depth)
        whens = []
        for when in myTime:
            whens.append(self.GetKMLTimeString(when))
        
        ourTrack = self.kml.newgxtrack( extrude=None,altitudemode=simplekml.AltitudeMode.relativetoground )
        trackData = ourTrack.newdata(coords,whens,yaw)
        ourTrack.style.iconstyle.icon.href='http://maps.google.com/mapfiles/kml/shapes/airports.png'
        


import scipy.io as sio
from scipy import ndimage

class GppKmlGroundOverlay( GpplibSimpleKML ):
    
    def __init__(self,**kwargs):
        super(GppKmlGroundOverlay,self).__init__(**kwargs)
        
    def CreateGroundOverlay(self,img,n,s,e,w,**kwargs):
        if kwargs.has_key('transparency'):
            transparency = kwargs['transparency']
        else:
            transparency = 0xb5
        
        picOverlay = self.kml.newgroundoverlay(name='MapOverlay')
        picOverlay.icon.href=img
        picOverlay.color= Color.changealpha("%x"%(0xb5),Color.white)
        llbox = simplekml.LatLonBox()
        llbox.north,llbox.south,llbox.east,llbox.west = n,s,e,w
        picOverlay.latlonbox = llbox
        
        
        
    
        
'''
#time,lat,lon,depth = [1],[2],[3],[4]
# lat,lon were in webb format
a = KmlTrackCreator()  
a.CreateKmlTrack(time,lat,lon,depth,altMode,folderName,placeMarkName)
print a.kml
a.WriteKml('arv2ryan.kml')
'''