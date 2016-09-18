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


'''
   Several classes for connecting to the WebbResearch dockserver.

   A typical invocation is
   
   dc=ThreadedDockserverComm('localhost','sim_061',6564,debug=True)
   dc.start() # start the thread.
   
   That is it!
   
   9 Dec 2009 Lucas Merckelbach. (lucas.merckelbach@noc.soton.ac.uk)
   16 Jan 2011
   Comes with no Warranty.

   Released under GPL v3 licence
'''
import threading
import socket, time
import os
import time
import dockserverXML
import dockserverConfig
import dialogues
from Queue import Queue, Empty
import sys
import fsm

class DockserverTalkError(Exception):
    def __init__(self,*args):
        Exception.__init__(self,*args)


class Debug:
    ''' Class to display, if wanted, some info on the screen or stderr
        Can be disabled. Different colours are used to distinguish between
        various sources. Defined are msgin (mesg from dockserver), msout
        (mesg to dockserver) info (for info, obviously) announce (used to tell
        we got a connect or so) and fail (if something goes wrong.)
    '''
    def __init__(self,fd=None):
        if fd==None:
            self.__fd=os.sys.stderr
        else:
            self.__fd=fd
        self.__printDebugInfo=False
        
    def enable(self):
        self.__printDebugInfo=True
    def disable(self):
        self.__printDebugInfo=False
    def msgin(self,mesg):
        if self.__printDebugInfo:
            self.__fd.writelines('\033[93m'+mesg+'\033[0m\n')
            self.__fd.flush()
    def msgout(self,mesg):
        if self.__printDebugInfo:
            self.__fd.writelines('\033[92m'+mesg+'\033[0m\n')
            self.__fd.flush()
    def info(self,mesg):
        if self.__printDebugInfo:
            self.__fd.writelines('\033[94m'+mesg+'\033[0m\n')
            self.__fd.flush()
    def announce(self,mesg):
        if self.__printDebugInfo:
            self.__fd.writelines('\033[95m'+mesg+'\033[0m\n')
            self.__fd.flush()
    def fail(self,mesg):
        if self.__printDebugInfo:
            self.__fd.writelines('\033[91m'+mesg+'\033[0m\n')
            self.__fd.flush()

class Timer(object):
    def __init__(self,interval, wait=False):
        self.interval=interval
        if wait:
            self.reset()
        else:
            self.set_timed_out()

    def reset(self):
        self.timeStamp=time.time()

    def set_timed_out(self):
        self.timeStamp=time.time()-self.interval 
        
    def get_timed_out(self):
        if self.interval<0:
            return False
        R=time.time()-self.timeStamp>self.interval
        return R

    def isTimedOut(self):
        R=self.get_timed_out()
        if R:
            self.reset()
        return R

    def cancel(self):
        self.interval=-1.

        
class DockserverComm(object):
    '''\
        Main class for a communication line with the dockserver.
        Note that gliderName may be None. In that case only the dockserver
        configuration is asked.
        
        Normally you would use ThreadedDockserverComm, which inherits from 
        this class.
    '''
    KeepAliveTimeOut=60.
    KeepAliveRecvTimeOut=90.
    DockconnectTimeOut=10.
    DockconfigurationTimeOut=10.
    GliderStatusTimeOut=10.
    GliderConnectTimeOut=10.

    def __init__(self, host, gliderName, port=6564,senderID="dockserverComm;0",debug=True):
        self.hostName=host
        self.gliderName=gliderName
        self.port=port
        self.debug=Debug()
        if debug:
            self.debug.enable()
        #
        self.bufferHandler=dialogues.Buffer()
        self.dockserverConfig=dockserverConfig.DockserverConfig(host)
        self.gliderConfig=dockserverConfig.GliderConfig(gliderName)
        self.bufferLength=4 # chunk size of reading froms socket.
        self.buffer=""
        self.recvdMessages=[]
        self.pendingMessages=[]
        self.initialiseXML(senderID)
        self.initialiseTimers()
        if gliderName:
            self.setupGliderFSM()
        else:
            self.setupDockFSM()
                        # State Machine. Set up here.

    def initialiseXML(self,senderID):
        ''' Initialises all xml objects. These objects write and parse the messages sent.
        '''
        gliderCfg=self.gliderConfig
        cfg=self.dockserverConfig
        configurationOnly=not bool(gliderCfg.name)
        self.xml={}
        self.xml['keepalive']=dockserverXML.KeepAlive(senderID=senderID)
        self.xml['dockconnect']=dockserverXML.DockConnect(senderID=senderID)
        self.xml['dockconfiguration']=dockserverXML.DockConfiguration(cfg,configurationOnly,senderID=senderID)
        self.xml['gliderstatus']=dockserverXML.GliderStatus(gliderCfg,senderID=senderID)
        self.xml['gliderconnect']=dockserverXML.GliderConnect(gliderCfg,senderID=senderID)
        self.xml['glidercommand']=dockserverXML.GliderCommand(gliderCfg,senderID=senderID)

    def initialiseTimers(self):
        ''' Initialise timers related to the various messages. '''
        self.timers={}
        self.timers['keepalive']=Timer(DockserverComm.KeepAliveTimeOut)
        self.timers['dockconnect']=Timer(DockserverComm.DockconnectTimeOut)
        self.timers['dockconfiguration']=Timer(DockserverComm.DockconfigurationTimeOut)
        self.timers['gliderstatus']=Timer(DockserverComm.GliderStatusTimeOut)
        self.timers['gliderconnect']=Timer(DockserverComm.GliderConnectTimeOut)
        self.timers['keepaliverecv']=Timer(DockserverComm.KeepAliveRecvTimeOut,wait=True)


    def addSignal(self,signal,fsm):
        ''' adds a signal to the FSM's memory. Signals are 'dockconnect' and the like.
        '''
        if signal not in fsm.memory:
            fsm.memory.append(signal)
            self.debug.info("signal %s send to fsm memory."%(signal))
        #self.debug.info("fsm memory:"+fsm.memory.__str__())

    #### FSM state definitions
    def send_dockconfiguration(self,fsm):
        self.debug.info("Glider %s: sending dockconfiguration"%(self.gliderName))
        self.addSignal("dockconfiguration",fsm)
        self.timers['dockconfiguration'].interval=30.

    def initialGlider(self,fsm):
        self.debug.info("%s: state: initialGlider"%(self.gliderName))
        self.addSignal("gliderstatus",fsm)

    # def gliderstatus(self,fsm):
    #     self.debug.info("%s: state: gliderstatus"%(self.gliderName))
    #     self.addSignal("gliderconnect",fsm)
    #     self.timers['gliderstatus'].cancel()
    #     self.bufferHandler.pushOntoQueue()

    # def gliderconnect(self,fsm):
    #     self.debug.info("%s: state: gliderconnect"%(self.gliderName))
    #     self.addSignal("gliderconnect",fsm)
    #     self.timers['gliderconnect'].interval=1e9
    #     #self.timers['gliderconnect'].cancel()
    #     text = self.xml['gliderconnect'].cfg.text
    #     self.bufferHandler.add(text)

    def setupDockFSM(self):
        ''' Sets up the Finite State Machine for main thread'''
        self.debug.info("Setting up DockFSM")
        f=fsm.FSM('initial',[])
        # In initial, send request for dockconfiguration, and do nothing otherwise
        f.add_transition     ('recv_keepalive','initial', self.send_dockconfiguration,'verify_send_dockconfiguration')
        f.add_transition     ('reset',         'initial', None, None)
        # exception handling:
        f.add_transition_any (                 'initial', self.send_dockconfiguration,'verify_send_dockconfiguration')

        # in verify_dockconfiguration, ignore recv_keepalive, go to initial on reset, and to dockserverconfiguration when recvd the 
        # recv_dockconfiguration.
        f.add_transition     ('recv_keepalive',        'verify_send_dockconfiguration', None,  None)
        f.add_transition     ('reset',                 'verify_send_dockconfiguration', None, 'initial')
        f.add_transition     ('recv_dockconfiguration','verify_send_dockconfiguration', None,'dockconfiguration')
        
        # in dockconfiguration, stick here, unless receiving reset.
        f.add_transition     ('recv_keepalive','dockconfiguration',None,                   None)
        f.add_transition     ('reset',         'dockconfiguration',None, 'initial')
        # exception handling:
        f.add_transition_any (                 'dockconfiguration',None,None)
        #
        self.fsm=f


    def send_gliderstatus(self,fsm):
        self.debug.info("%s: state: %s"%(self.gliderName,fsm.current_state))
        self.addSignal("gliderstatus",fsm)

    def send_gliderconnect(self,fsm):
        self.debug.info("%s: state: %s"%(self.gliderName,fsm.current_state))
        self.addSignal("gliderconnect",fsm)

    def gliderconnect(self,fsm):
        self.debug.info("%s: state: %s"%(self.gliderName,fsm.current_state))
        text = self.xml['gliderconnect'].cfg.text
        self.bufferHandler.add(text)
        self.debug.info("text:  %s"%(text))
        self.bufferHandler.pushOntoQueue() # to push data on a the message bus (if implemented)

    def setupGliderFSM(self):
        ''' Sets up the Finite State Machine for a specific glider'''
        self.debug.info("Setting up GliderFSM")
        f=fsm.FSM('initialGlider',[])

        # first send gliderstatus request
        f.add_transition     ('recv_keepalive','initialGlider',    self.send_gliderstatus,'verify_send_gliderstatus')
        f.add_transition     ('reset',         'initialGlider',    self.send_gliderstatus,'verify_send_gliderstatus')
        
        # check it and send glider connect request
        f.add_transition_list(['recv_gliderstatusUndocked',
                               'recv_gliderstatusDocked',
                               'recv_gliderstatusUnserviced'],'verify_send_gliderstatus',self.send_gliderconnect,'verify_send_gliderconnect')
        f.add_transition     ('recv_keepalive',               'verify_send_gliderstatus',None,                    None)
        f.add_transition     ('reset',                        'verify_send_gliderstatus',None,                    'initialGlider')
        
        # verify send glider connect request.
        f.add_transition     ('recv_keepalive',               'verify_send_gliderconnect',None,                    None)
        f.add_transition     ('reset',                        'verify_send_gliderconnect',None,                    'initialGlider')
        f.add_transition     ('recv_gliderstatusDocked',      'verify_send_gliderconnect',self.gliderconnect,      'docked')
        f.add_transition     ('recv_gliderstatusUndocked',    'verify_send_gliderconnect',self.gliderconnect,      'undocked')
        f.add_transition     ('recv_gliderstatusUnserveced',  'verify_send_gliderconnect',self.gliderconnect,      'unserviced')
        
        # docked
        f.add_transition     ('recv_gliderstatusDocked',      'docked',self.gliderconnect,      'docked')
        f.add_transition     ('recv_gliderstatusUndocked',    'docked',self.gliderconnect,      'undocked')
        f.add_transition     ('recv_gliderstatusUnserviced',  'docked',None,                    'unserviced')
        f.add_transition     ('recv_keepalive',               'docked',None,                     None)
        f.add_transition     ('reset',                        'docked',None,                    'initialGlider')

        # undocked
        f.add_transition     ('recv_gliderstatusDocked',      'undocked',self.gliderconnect,      'docked')
        f.add_transition     ('recv_gliderstatusUndocked',    'undocked',self.gliderconnect,      'undocked')
        f.add_transition     ('recv_gliderstatusUnserviced',  'undocked',None,                    'unserviced')
        f.add_transition     ('recv_keepalive',               'undocked',None,                     None)
        f.add_transition     ('reset',                        'undocked',None,                    'initialGlider')

        # unserviced
        f.add_transition     ('recv_gliderstatusDocked',      'unserviced',self.gliderconnect,      'docked')
        f.add_transition     ('recv_gliderstatusUndocked',    'unserviced',self.gliderconnect,      'undocked')
        f.add_transition     ('recv_gliderstatusUnserviced',  'unserviced',None,                    'unserviced')
        f.add_transition     ('recv_keepalive',               'unserviced',None,                     None)
        f.add_transition     ('reset',                        'unserviced',None,                    'initialGlider')
        self.fsm=f                                  

    def parseMessage(self,mesg):
        ''' parses message with the right xml object
            if a keep alive packet is received, the timer for this is reset.
            the output from xml.parse() is given to the FSM to change state 
            if necessary.
        '''
        self.debug.msgin(mesg)
        for key,xml in self.xml.iteritems():
            if xml.messageCheck(mesg):
                self.debug.info("parsing message for %s"%(key))
                break
        input_symbol=xml.parse()
        if input_symbol=='recv_keepalive':
            self.timers['keepaliverecv'].reset()
        self.debug.fail(key+" "+input_symbol)
        self.fsm.process(input_symbol)

    def processFSMMemory(self):
        ''' processes the signals (message types) that are flagged
            to be sent at some time. (if timed out).
        '''
        if len(self.fsm.memory)==0:
            return [] # nothing to do
        expiredSignals=[]
        for i,signal in enumerate(self.fsm.memory):
            if self.timers[signal].isTimedOut():
                expiredSignals.append(i)
        if not expiredSignals:
            return [] # nothing to do YET
        expiredSignals.reverse()
        mesg=[]
        for i in expiredSignals:
            s=self.fsm.memory.pop(i)
            mesg.insert(0,self.xml[s].write())
        return mesg

    def connect_bufferHandler(self,BufferClass):
        ''' Connects a bufferHandler class to buffer handler.
            This can be any class that is is subclassed from the Buffer class
            and implements getCompleteLine and add methods.
        '''
        self.bufferHandler=BufferClass(self)

    def removePacketsFromBuffer(self):
        ''' removes a complete <packet></packet> message from the
            self.buffer, if exists. The message gets appended to
            self.recvdMessages.
        '''
        idx=self.buffer.find("</packet>")
        if idx!=-1:
            self.recvdMessages.append(self.buffer[:idx+9])
            self.buffer=self.buffer[idx+9:]
    
    def sendCommand(self,command):
        xml=self.xml['glidercommand']
        xml.set_command(command)
        mesg=xml.write()
        self.pendingMessages.append(mesg)

class ThreadedDockserverComm(threading.Thread, DockserverComm):
    ''' Class for dockserver communications based on a separate thread
        for each communication line.
    '''
    MPQueue = Queue()
    def __init__(self,host,glidername,port=6546,senderID='dockserverComm;0',debug=True):
        DockserverComm.__init__(self,host,glidername,port,senderID,debug)
        threading.Thread.__init__(self)
        self._terminate=False
        self.host=host
        self.port=port
        self.glidername=glidername
        self.__max_buffer_length=0
        self.initialiseSocket()
        self.daemon = True # make thread daemonic so it will be killed when python exits.

    def initialiseSocket(self):
        self.s = socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET,
                          socket.SO_REUSEADDR,1)
        self.s.settimeout(15)

    def terminate(self):
        self._terminate=True

    def handle_connect(self):
        self.s.connect((self.host,self.port))
        self.debug.info("Connected to dockserver.")

    def handle_read(self):
        s = self.s.recv(self.bufferLength)
        if len(s)==0: # if socket is setup via ssh, then if the dockserver dies, this is not seen as an error.
            raise socket.error    # we must raise an error ourselves.
        self.buffer+=s
        self.removePacketsFromBuffer()
        if len(self.recvdMessages)>0:
            R=self.parseMessage(self.recvdMessages.pop(0))
        # the buffer length is normally about 1000 elements. 
        # let's say that a problem arises if the buffer gets 100 times as big?
        if len(self.buffer)>100000: # apparently packages dont get
            sys.stderr.write(self.buffer)
            sys.stderr.write("Buffer overflow. Terminating thread.\n")
            self.terminate()      # removed. Should not happen...
        
    def handle_writeOrg(self):
        while (len(self.pendingMessages))>0:
            mesg=self.pendingMessages.pop(0)
            self.s.send(mesg)
            self.debug.msgout(mesg)
    def handle_write(self):
        self.pendingMessages+=self.processFSMMemory()
        while self.pendingMessages:
            mesg=self.pendingMessages.pop(0)
            self.s.send(mesg)
            self.debug.msgout(mesg)

    def handle_close(self):
        self.s.close()

    def cleanup(self):
        self.s.close()
        print "Thread %s (%s) terminated."%(self.glidername,self._Thread__name)
        
    def run(self):
        self.handle_connect()
        while not self._terminate:
            try:
                self.handle_write()
            except socket.error,e:
                # failed to write to dockserver.
                self.debug.announce(str(e))
                self.debug.announce('Error occurred in %s.'%(self._Thread__name))
                break
            try:
                self.handle_read()
            except socket.timeout,e:
                self.debug.announce(str(e))
                self.debug.announce('%s timed out'%(self._Thread__name))
            except socket.error,e:
                self.debug.announce(str(e))
                self.debug.announce('%s returned a netork error, assuming link went down. Retrying in 10 seconds.'%(self._Thread__name))
                self.handle_close()
                self.fsm.process('reset') # reset the FSM
                time.sleep(10)
                self.initialiseSocket()
                self.handle_connect()
            self.addSignal("keepalive",self.fsm) # always send a keepalive (if timed out)
            if self.timers['keepaliverecv'].isTimedOut():
                self.debug.fail('No keepalive messages received!')
        self.cleanup()




if __name__=='__main__':
    # typical use: Ideally you want these or similar lines in another) script.
    #dc=ThreadedDockserverComm('localhost','sim_061',6564,debug=True)
    #dc.connect_bufferHandler(dialogues.GPSLogger) # instead of the default Dialogue Class
    #dc.run() # start the thread. use start to run as a thread.

    # testing new state engine
    dc=ThreadedDockserverComm('141.4.0.159','sim_062',6564,debug=True)
    dc.connect_bufferHandler(dialogues.GPSLogger) # instead of the default Dialogue Class
    dc.run()
