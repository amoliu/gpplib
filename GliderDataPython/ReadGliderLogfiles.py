import gpplib
from gpplib.Utils import *
import re

class GliderConsoleLogFileReader(object):
    def __init__(self,**kwargs):
        self.LocPattern = re.compile("[ ]*(GPS|DR)[ ]*(TooFar|Location|Invalid)[ :]+([0-9\\.\\-]*) N ([0-9\\.\\-]*) E.*")
        self.SensorPattern = re.compile("[ ]*sensor:[ ]*([a-z_]+)(?:\\(([a-zA-Z]+)\\))*[ ]*=[ ]*([0-9\\.-]+)[ ]*(lat|lon|enum)*.*")
        self.MissionPattern = re.compile("MissionName:([a-zA-Z0-9\\.\\-\\_]*) MissionNum:([a-zA-Z0-9\\.\\-\\_]*) \\(([0-9\\.]*)\\)")
        self.WaypointPattern = re.compile("[ ]*Waypoint: \\(([0-9\\.\\-]*),([0-9\\.\\-]*)\\) Range: ([0-9\\.]*)([a-zA-Z]*), Bearing: ([0-9\\.\\-]*)deg, Age: (.*)")
        self.BecausePattern = re.compile("[ ]*Because:([a-zA-Z0-9 ]*) \\[(.*)\\]")
        self.VehiclePattern = re.compile("[ ]*Curr Time: (.*) MT:[ ]*([0-9\\.]*)")
        self.TimePattern = re.compile("[ ]*Curr Time: (.*) MT:[ ]*([0-9\\.]*)")
    
    def getGpsDegree(self,webb_gps_str):
        p=webb_gps_str.find(".")
        d=float(webb_gps_str[0:p-2])
        return d+cmp(d,0)*float(webb_gps_str[p-2:len(webb_gps_str)])/60
    
    def GetGpsLocation(self,m,locType="Location"):
        if(m and m.group(1) == "GPS" and m.group(2) == locType ):
                #print m.groups()
                lat = self.getGpsDegree(m.group(3))
                lon = self.getGpsDegree(m.group(4))
                return (lat,lon)
        else:
            return None
        
    def GetSensorValue(self,m,sensorType="m_battery"):
        if(m.group(1) == sensorType ):
            return float(m.group(3))
        else:
            return None
    
    def ParseData(self,msg):
        ''' ParseData = find useful information in the given data file '''
        g = {}
        if len(msg)>0:
            for line in msg:
                mL, mS, mM, mW, mB, mV, mT = \
                    self.LocPattern.match(line), self.SensorPattern.match(line), self.MissionPattern.match(line), \
                    self.WaypointPattern.match(line),self.BecausePattern.match(line),self.VehiclePattern.match(line), \
                    self.TimePattern.match(line)
                if mL:
                    gliderLoc = self.GetGpsLocation(mL)
                    if gliderLoc != None:
                        g['lat'],g['lon']=gliderLoc
                elif mS:
                    battery = self.GetSensorValue( mS,'m_battery' )
                    vacuum = self.GetSensorValue( mS, 'm_vacuum' )
                    if battery: g['battery']=battery
                    if vacuum: g['vacuum'] =vacuum
                elif mW:
                    g['wp_lat'], g['wp_lon'], g['wp_range'], g['wp_bearing'], g['wp_time'] = \
                        self.getGpsDegree(mW.group(1)),self.getGpsDegree(mW.group(2)), \
                        float(mW.group(3)),float(mW.group(5)),0
                elif mB:
                    g['because'] = mB.group(1)
                elif mV:
                    g['name'] = mV.group(1)
                elif mT:
                    g['time'] = time.strptime(m.group(1),'%a %b %d %H:%M:%S %Y')
        else:
            print 'Empty Message/File.'    
        
        return g
        
    def GetLogFileListForGliderBetweenDates(self,glider_name,dt1,dt2):
        ''' Get a list of all log files after a particular date.
        '''
        self.gftp = GliderFTP('/var/opt/gmc/gliders/'+glider_name+'/logs/')
        dir_list = self.gftp.GetSimpleDirList('')
        filtered_list = []
        for file in dir_list[0]:
            m = re.match('%s_modem_([0-9]{4})([0-9]{2})([0-9]{2})T([0-9]{2})([0-9]{2})([0-9]{2}).log'%(glider_name),file)
            if m:
                fyy,fmm,fdd,fhr,fmi,fse = \
                   int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6))
                
                file_dt = datetime.datetime(fyy,fmm,fdd,fhr,fmi,fse)
                if file_dt>=dt1 and file_dt<=dt2:
                    filtered_list.append(file)
        #print self.gftp.f.dir()
        self.gftp.Close()
        return filtered_list
    
    def ReadLogFileContents(self,glider_name,remoteFileName,tmp_log_file_dir = 'logs/'):
        self.gftp = GliderFTP('/var/opt/gmc/gliders/'+glider_name+'/logs/')
        import os, sys
        try:
            os.mkdir(tmp_log_file_dir)
        except OSError as (errno,strerror):
            pass
        lines_in_file = None
        localFileName = tmp_log_file_dir+'%s'%(remoteFileName)
        print 'Local file: %s'%(localFileName)
        if self.gftp.DoesFileExist(remoteFileName)==True:
            self.gftp.ReadFile(localFileName,remoteFileName)
            f = open(localFileName,'r')
            lines_in_file = f.readlines()
            f.close()
            
        self.gftp.Close()
        
        return lines_in_file
        

gclfr = GliderConsoleLogFileReader()
f = open('rusalka_modem_20120719T154158.log','r')
msg = f.readlines()
f.close()
g = gclfr.ParseData(msg)
print g
download_dir = 'logs/'
dt1 = datetime.datetime(2012,7,18,0,0)
dt2 = datetime.datetime.utcnow()
fileList =  gclfr.GetLogFileListForGliderBetweenDates('rusalka', dt1, dt2)
for file in fileList:
    lines =  gclfr.ReadLogFileContents('rusalka', file )
