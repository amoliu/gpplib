''' Class that can return parsed glider status from strings
'''
import re
import datetime
import time

class GliderTermParser(object):
    def __init__(self,**kwargs):
        self.gState = {}
        
    def getGpsDegree(self,webb_gps_str):
        p=webb_gps_str.find(".")
        d=float(webb_gps_str[0:p-2])
        return d+cmp(d,0)*float(webb_gps_str[p-2:len(webb_gps_str)])/60
    
    def ClearGliderState(self,**kwargs):
        self.gState = {}
        
    def ParseMessage(self,msg):
        g = {}
        j = msg
        try:
            if(len(j) > 0 and j[-1] == '='):
                leftovers = j[0:-1]
            else:
                #print j
                leftovers = ""
                m = re.match("[ ]*(GPS|DR)[ ]*(TooFar|Location|Invalid)[ :]+([0-9\\.\\-]*) N ([0-9\\.\\-]*) E.*",j)
                if(m and m.group(1) == "GPS" and m.group(2) == "Location"):
                    #print m.groups()
                    g['lat'] = self.getGpsDegree(m.group(3))
                    g['lon'] = self.getGpsDegree(m.group(4))
                m = re.match("[ ]*sensor:[ ]*([a-z_]+)(?:\\(([a-zA-Z]+)\\))*[ ]*=[ ]*([0-9\\.-]+)[ ]*(lat|lon|enum)*.*",j)
                if(m):
                    #print m.groups()
                    if(m.group(1) == "m_battery"):
                        g['battery'] = float(m.group(3))
                    elif(m.group(1) == "m_vacuum"):
                        g['vacuum'] = float(m.group(3))
                m = re.match("MissionName:([a-zA-Z0-9\\.\\-\\_]*) MissionNum:([a-zA-Z0-9\\.\\-\\_]*) \\(([0-9\\.]*)\\)",j)
                if(m):
                    #print m.groups()
                    g['missionfile'] = m.group(1)
                    g['mission'] = m.group(2)
                    g['missionnum'] = m.group(3)
                m = re.match("[ ]*Waypoint: \\(([0-9\\.\\-]*),([0-9\\.\\-]*)\\) Range: ([0-9\\.]*)([a-zA-Z]*), Bearing: ([0-9\\.\\-]*)deg, Age: (.*)",j)
                if(m):
                    #print m.groups()
                    g['wp_lat'] = self.getGpsDegree(m.group(1))
                    g['wp_lon'] = self.getGpsDegree(m.group(2))
                    g['wp_range'] = float(m.group(3))
                    g['wp_bearing'] = float(m.group(5))
                    #x = datetime(*time.strptime(m.group(6),"%H:%Mh:m")[:6])
                    g['wp_time'] = 0 #x.hour*60+x.minute
                m = re.match("[ ]*Because:([a-zA-Z0-9 ]*) \\[(.*)\\]",j)
                if(m):
                    #print m.groups()
                    g['because'] = m.group(1)
                m = re.match("Vehicle Name: ([a-zA-Z\\-\_0-9]*)",j)
                if(m):
                    #print m.groups()
                    g['name'] = m.group(1)
                m = re.match("[ ]*Curr Time: (.*) MT:[ ]*([0-9\\.]*)",j)
                if(m):
                    #print m.groups()
                    g['time'] = time.strptime(m.group(1),"%a %b %d %H:%M:%S %Y")
                m = re.match("GliderDos[ ]+([A-Z]+)[ ]([\-0-9])[ ]+>",j)
                if(m):
                    g['at_glider_dos_prompt'] = (True,m.group(1),m.group(2))
                    
                m= re.match("Mission completed ([A-Za-z]+), ret = ([0-9\-])+",j)
                if(m):
                    g['mission_completed'] = (True,m.group(1),m.group(2))
                m = re.match("deleting >/var/opt/gmc/gliders/([a-z\-]+)/([a-zA-Z0-9\_]+.MI)< Successful",j)
                if(m):
                    g['sendSuccessful'] = (True,m.group(1),m.group(2))
                
                # Some more random matches...
                if "disabling Iridium" in j:
                    g['iridiumDisabled'] = (True)
        except ValueError:
                print 'Ignoring ValueError Exception. TODO: FIXME later!'
                pass
        except:
                print 'Ignoring general Exception. TODO: FIXME later!'
                pass
                
        # Aggregate everything we've seen so far in our composite state...
        for key,val in g.items():
            self.gState[key]=val
            self.gState['lastUpdated'] = datetime.datetime.utcnow()
        
        return g


from dockserverTalk.dialogues import Buffer

class GliderLogger(Buffer):
    def __init__(self,dockserverComm):
        Buffer.__init__(self)
        self.gliderName=dockserverComm.gliderName
        self.gliderConfig=dockserverComm.gliderConfig
        self.MPQueue=dockserverComm.MPQueue
        self.gliderStatus=2 # undocked to start with
        self.lat=None
        self.lon=None
        self.time=None
        self.latlonFlag=False
        self.timeFlag=False
        self.dataFlag=False
        self.maxDataValidityInSecs = 60 # 1 minute
        self.gparse = GliderParser()
        
        print "Initialising ",self.gliderName
        self.MPQueue.put((self.gliderName,
                          self.lat,
                          self.lon,
                          self.time,
                          self.gliderStatus))

    # override the add method.
    def add(self,mesg):
        self+=mesg
        while True:
            mesg=self.getCompleteLine()
            #if len(mesg):
            #    sys.stderr.write(self.gliderName+": "+mesg)
            if mesg=='':
                break
            
            g = self.gparse.ParseMessage(mesg)
        
        if (datetime.datetime.utcnow()-self.gparse.gState['lastUpdated'])>datetime.timedelta(seconds=self.maxDataValidityInSecs):
            self.gState={}
            return
        else:
            print 'We got some updates'
            print self.gparse.gState
        
        self.pushOntoQueue(g)

    def pushOntoQueue(self,g):
        if self.dataFlag or self.gliderStatus_changed:
                self.dataFlag=False
                '''self.MPQueue.put((self.gliderName,
                                  self.lat,
                                  self.lon,
                                  self.time,
                                  self.gliderStatus))
                                  '''
                self.MPQueue.put((self.gliderName,mesg,g))
    @property
    def gliderStatus_changed(self):
        status=self.gliderConfig.status
        if status!=self.gliderStatus:
            self.gliderStatus=status
            return True
        else:
            return False



        
    
