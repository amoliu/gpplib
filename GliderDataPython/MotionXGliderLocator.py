''' This program will allow us to automatically get updates from the gliders when they are at the surface.
The update will come via email as soon as a new location has been parsed, and will contain the latest
location of the glider as well as the tentative location for surfacing.
'''
import gpplib
from gpplib.GliderParse import *
from gpplib.Utils import *
import dockserverTalk.dockserverTalk as DT
from dockserverTalk.dialogues import Buffer
import time
import gpxpy
import gpxpy.gpx




# Modify these three variables to suit your situation:
dockserver="10.1.1.20"
gliders= ["sim_039","rusalka","he-ha-pe" ]
glider = "sim_039"
port=6564
# A sender ID must consist of "name;number" otherwise the dockserver 
# doesn't answer apparently.
senderID="arvind-pereira;0xabcde0123"
senderID="test-dt;0xb1gb00b5"
# If debugging is True, then raw packets sent to and received from the 
# dockserver can be inspected.
debugging=False

def CreateTrack(gliderName,lat,lon,**kwargs):
    gpx = gpxpy.gpx.GPX()
    # Create first track in our GPX:
    #gpx_track = gpxpy.gpx.GPXTrack()
    #gpx.tracks.append(gpx_track)
    # Create first segment in our GPX track:
    gpx_last_waypoint = gpxpy.gpx.GPXWaypoint(lat,lon,0,datetime.datetime.today(),gliderName,'GliderLocation from Dockserver')
    gpx.waypoints.append(gpx_last_waypoint)
    
    if kwargs.has_key('wpt_lat') and kwargs.has_key('wpt_lon'):
        wpt_lat, wpt_lon =  kwargs['wpt_lat'], kwargs['wpt_lon']
        gpx_aim_waypoint = gpxpy.gpx.GPXWaypoint(wpt_lat,wpt_lon)
        gpx.waypoints.append(gpx_aim_waypoint)
    
    #gpx_segment = gpxpy.gpx.GPXTrackSegment()
    #gpx_track.segments.append(gpx_segment)
    # Create points:
    #gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1234, 5.1234, elevation=0))
    #gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1235, 5.1235, elevation=0))
    #gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(2.1236, 5.1236, elevation=0))
    
    # You can add routes and waypoints, too...
    return gpx.to_xml()

import tempfile, os

def EmailTrack(gliderName,gpxTrack,gState):
    gpxFileName = '%s.gpx'%(gliderName)
    f = open(gpxFileName,'w')
    f.write(gpxTrack)
    f.close()
    
    ggmail = GliderGMail('usc.glider','cinaps123')
    ggmail.mail('arvind.pereira@gmail.com','Position Update for Glider %s using GPPLIB. (c) Arvind Pereira.'%(gliderName),gpxTrack+str(gState),gpxFileName)
    os.unlink(gpxFileName)
    


class MyBuffer(Buffer):
    def __init__(self,dockserverComm):
        Buffer.__init__(self,dockserverComm)
        # when we put data on the queue, and someone
        # is reading out the queue, we use the name
        # of the glider as identifier.
        self.glider=dockserverComm.gliderName
        self.MPQueue=dockserverComm.MPQueue
        self.gparse = GliderTermParser()

    # override the add method.
    def add(self,mesg):
        self+=mesg # note that self is a list.
        while True:
            # getCompleteLine is a method of Buffer and subclassed.
            # this method returns a complete line (incl. CR) or an
            # empty string
            mesg=self.getCompleteLine()
            if mesg=='':
                break
            self.gparse.ParseMessage(mesg)
            # We have something to write. Let's put it into the dockserver's
            # Message Passing Queue
            self.MPQueue.put((self.glider,mesg,self.gparse.gState))


gliderThreads = []

# Create a threaded dockserver Comm instance
t=DT.ThreadedDockserverComm(dockserver,glider,port,
                                senderID=senderID,debug=debugging)
# connect our MyBuffer class to the buffer handler:
t.connect_bufferHandler(MyBuffer)
# start the thread
t.start()
    
    
# Of course, if you have two gliders, or more, you can fire up as many threads.
# Each thread will communicate through the same Queue.

if not t.isAlive():
    raise IOError,"DockserverComm instance didn't start up."
else:
    print "Ok so far. Going to listen to 20 lines of dialogue."
    print "Make sure that the glider produces a dialogue, otherwise"
    print "we'll get stuck..."
ln=0
lastGpxTrack, lastParsed = None, time.time()
while 1:
    if not DT.ThreadedDockserverComm.MPQueue.empty():
        while not DT.ThreadedDockserverComm.MPQueue.empty():
            x=DT.ThreadedDockserverComm.MPQueue.get_nowait()
            gliderName,mesg,gState=x
            print gliderName,"says:",mesg.rstrip(),gState
            #if not (gState == lastGstate) and time.time()-lastParsed>10.0:
            if gState.has_key('lat') and gState.has_key('lon'):
                    if gState.has_key('wpt_lat') and gState.has_key('wpt_lon'):
                        gpxTrack = CreateTrack(gliderName,gState['lat'],gState['lon'], \
                            wpt_lat=gState['wpt_lat'], wpt_lon=gState['wpt_lon'])
                    else:
                        gpxTrack = CreateTrack(gliderName,gState['lat'],gState['lon'])
                    if gpxTrack != lastGpxTrack and time.time()-lastParsed>30.0:
                        print 'GpxTrack is: %s'%(gpxTrack)
                        EmailTrack(gliderName,gpxTrack,gState)
                        lastGpxTrack = gpxTrack
                        lastParsed = time.time()
            ln+=1
    else:
        # if there is nothing in the queue, then
        # sleep briefly not to keep the CPU busy all the time...
        time.sleep(0.1)
    #if ln>=200:
    #    break
