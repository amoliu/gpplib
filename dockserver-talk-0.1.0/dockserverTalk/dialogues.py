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


import time
import sys

class Buffer(list):
    def __init__(self,dockserverComm=None):
        pass
    def add(self,mesg):
        self+=mesg

    def getCompleteLine(self):
        try:
            idx=self.index("\n")
            msg="".join([self.pop(0) for i in range(idx+1)])
            # mostlines are terminated by \r\n, but not
            # all. So msg can end on \r or not. Just replace
            # \r by "" if present.
            msg=msg.replace("\r","")
            #os.sys.stdout.write(">"+msg)
            #os.sys.stdout.flush()
        except ValueError:
            msg=''
        return msg

    def pushOntoQueue(self):
        pass

class Dialogue(Buffer):
    def __init__(self,dockserverComm):
        Buffer.__init__(self)
        self.log=[]
        self.maxLog=1000
    # override the add method.
    def add(self,mesg):
        self+=mesg
        while True:
            mesg=self.getCompleteLine()
            if mesg=='':
                break
            self.log.append(mesg)
            if len(self.log)>self.maxLog:
                self.log.pop(0)

class GPSLogger(Buffer):
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
            if 'GPS Location' in mesg:
                words=mesg.split()
                if len(words)>5: # line is long enough
                    self.lat=words[2]
                    self.lon=words[4]
                    self.latlonFlag=True
            if 'Curr Time' in mesg:
                words=mesg.split()
                if len(words)>7:
                    tmp=" ".join([words[4],
                                  words[3],
                                  words[6],
                                  words[5],
                                  "UTC"])
                    try:
                        q=time.strptime(tmp,"%d %b %Y %H:%M:%S %Z")
                        self.time=time.mktime(q)
                        self.timeFlag=True
                    except ValueError:
                        pass # the line seems garbled. ignore.
        if self.latlonFlag and self.timeFlag:
            self.dataFlag=True
            self.latlonFlag=False
            self.timeFlag=False
        self.pushOntoQueue()

    def pushOntoQueue(self):
        if self.dataFlag or self.gliderStatus_changed:
                self.dataFlag=False
                self.MPQueue.put((self.gliderName,
                                  self.lat,
                                  self.lon,
                                  self.time,
                                  self.gliderStatus))
    @property
    def gliderStatus_changed(self):
        status=self.gliderConfig.status
        if status!=self.gliderStatus:
            self.gliderStatus=status
            return True
        else:
            return False



            
