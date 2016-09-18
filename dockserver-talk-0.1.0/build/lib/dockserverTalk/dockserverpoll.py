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



''' A module with class DockserverPoll for easy polling of dockserver
    for now to see if a glider has docked and undocked again.
'''

import dockserverTalk
import time

class GliderStatus(object):
    def __init__(self,name,status=0):
        self.name = name
        self.has_connected = False
        self.has_disconnected = False
        self.ready_to_run = False
        self.timer = dockserverTalk.Timer(30) # after 5 minutes of
        self.set_status(status)               # disconnect assume
                                              # that it will be final

    def set_status(self,status):
        self.status = status
        if status == '1':
            self.has_connected = True
        elif status == '2' and self.has_connected:
            self.has_disconnected = True
        elif status == '1' and self.has_disconnected:
            self.has_disconnected = False
        if self.has_connected and self.has_disconnected:
            if self.timer.isTimedOut():
                self.ready_to_run=True
        else:
            self.timer.reset()

class DockserverPoll(object):
    def __init__(self,host,port):
        self.dc = dockserverTalk.ThreadedDockserverComm(host,None,port,debug=False)
        self.dc.DockserverconfigurationTimeOut=5. # override default of 10.
        self.dc.start() # launch the thread
        self.hosted_gliders={}
        time.sleep(10) # give dc the time to get the information from the dockserver

    def poll(self):
        for k,v in self.dc.dockserverConfig.gliders.iteritems():
            if k not in self.hosted_gliders.keys():
                self.hosted_gliders[k]=GliderStatus(k)
            self.hosted_gliders[k].set_status(v.status)
            if self.hosted_gliders[k].ready_to_run:
                if self.run_task(k):
                    self.hosted_gliders[k].ready_to_run=False
                    self.hosted_gliders[k].has_connected=False
                    self.hosted_gliders[k].has_disconnected=False

    def run_task(self,name):
        ''' dummy method, should be overwritten when subclassed.
            The method returns 1 on sucess and resets the connection flags,
            or 0 on failure, so that it will be executed again (and again...)'''
        print "running task for %s"%(name)
        return 1
        
    def loop(self,delay=10.):
        print "Polling dockserver every %f seconds."%(delay)
        while 1:
            self.poll()
            time.sleep(delay)


if __name__=='__main__':
    dp = DockserverPoll('141.4.0.159',6564)
    dp.loop()

