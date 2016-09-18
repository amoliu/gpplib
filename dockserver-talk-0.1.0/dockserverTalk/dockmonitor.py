#
# Copyright 2010-2012, Lucas Merckelbach (lucas.merckelbach@hzg.de)
#
#This file is part of dockserver-talk.
#
#dockserver-talk is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#dockserver-talk is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with dockserver-talk.  If not, see <http://www.gnu.org/licenses/>.


import dockserverTalk as DT
import time
from dialogues import GPSLogger
import sys

class DockMonitor(DT.ThreadedDockserverComm):
    def __init__(self,dockserver,port,Q,senderID='DockMonitor;0',debug=True):
        DT.ThreadedDockserverComm.__init__(self,dockserver,None,port,senderID,debug)
        self.threads=[]
        self.monitored=[]
        self.dockserver=dockserver
        self.port=port
        self.debugging=debug
        self.gliderInfo={'ID':'dockserver','Status':0}
        self.Q=Q
        self.senderID=senderID

    def launchGliderThread(self,glider):
        t=DT.ThreadedDockserverComm(self.dockserver,glider,self.port,
                                    senderID=self.senderID,debug=self.debugging)
        t.connect_bufferHandler(GPSLogger)
        self.threads.append(t)
        self.monitored.append(glider)
        self.gliderInfo[glider]=None
        sys.stderr.write("Starting thread for %s (%s)\n"%(glider,t._Thread__name))
        t.start()

    def checkForNewGliders(self):
        newGliders=[i for i in self.dockserverConfig.gliders.keys() 
                    if i not in self.monitored]
        try:
            newGliders.remove('unknown')
        except:
            pass
        for g in newGliders:
            self.launchGliderThread(g)

    def processMPQueue(self):
        if not DT.ThreadedDockserverComm.MPQueue.empty():
            while not DT.ThreadedDockserverComm.MPQueue.empty():
                x=DT.ThreadedDockserverComm.MPQueue.get_nowait()
                #DT.ThreadedDockserverComm.MPQueue.task_done()
                glider=x[0]
                try:
                    lat=float(x[1])
                    lon=float(x[2])
                    tm=float(x[3])
                except TypeError:
                    lat=lon=tm=9e9
                status=int(x[4])
                self.gliderInfo[glider]=(lat,lon,tm,status)
            self.Q.put(self.gliderInfo)

    def cleanup(self):
        self.s.close()
        sys.stderr.write("Terminating glider %d threads...\n"%(len(self.threads)))
        for t in self.threads:
            if t.isAlive():
                t.terminate()
        for t in self.threads: # wait for all threads to close before continuing.
            t.join()
        sys.stderr.write("Thread DockMonitor (%s) terminated.\n"%(self._Thread__name))
        
    def reconnect(self,max_tries):
        reconnected=False
        self.gliderInfo['Status']=2 # reconnecting
        self.Q.put(self.gliderInfo)
        for n in range(max_tries):
            sys.stderr.write("Trying to reconnect in 60 seconds.\n")
            try:
                self.handle_connect()
                reconnected=True
                self.monitored=[] # ensures new threads are created for each glider
                sys.stderr.write("Reconnected to dockserver.\n")
                self.gliderInfo['Status']=1 # reconnecting
                break
            except:
                pass
            time.sleep(60)
        if not reconnected:
            self.gliderInfo['Status']=3 # broken
        self.Q.put(self.gliderInfo)
        return reconnected

        
    def run(self,max_tries=10):
        self.gliderInfo['Status']=1
        while not self._terminate:
            self.addSignal("keepalive",self.fsm) # always send a keepalive (if timed out)
            try:
                self.handle_write()
            except DT.socket.error,e:
                sys.stderr.write("dockmonitor (thread %s) failed to handle write operation.\n"%(self._Thread__name))
                if not self.reconnect(max_tries): # reconnect failed.
                    break
            try:
                self.handle_read()
            except:
                self.debug.announce('%s timed out'%(self._Thread__name))
            self.checkForNewGliders()
            self.processMPQueue()
        self.cleanup()

