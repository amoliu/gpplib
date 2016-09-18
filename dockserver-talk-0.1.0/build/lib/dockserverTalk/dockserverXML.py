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


'''Several classes for reading and writing xml packets for
   WebbResearch Dockserver.

   This is a minimal implementation, just to serve the purpose
   that we can extract the glider dialogue from the dockserver

   9 Dec 2009 Lucas Merckelbach.  (lucas.merckelbach@noc.soton.ac.uk)

   Comes with no Warranty.

   Released under GPL v3 licence
'''

from xml.dom import minidom
from xml.parsers.expat import ExpatError
import dockserverConfig
import os
import socket

VERSION=0.1

class XMLElement(object):
    def __init__(self,name):
        self.name=name
        self.attributes={}
        self.children={}

    def addAttribute(self,name,value):
        self.attributes[name]=value

    def addChild(self,name,xmlelement):
        self.children[name]=xmlelement

    def addAttributes(self,lst):
        for n,v in lst:
            self.addAttribute(n,v)

class XMLWriter:
    ''' Base class for writing xml messages'''
    def __init__(self,senderID='dockserverComm;0'):
        try:
            loginName=os.getlogin()
        except:
            try:
                loginName=os.environ['LOGNAME']
            except:
                loginName=os.getuid()
        hostname=socket.gethostname()
        xmlelement=XMLElement('packet')
        xmlelement.addAttributes([("type","request"),
                                  ("senderID","%s;%s;%s"%(loginName,hostname,senderID)),
                                  ("senderVersion","dockserverComm;%s"%(VERSION))])
        self.xmlelement=xmlelement

    def write(self):
        doc=minidom.Document()
        emptytxt=doc.createTextNode('')# this forces the packets to look like <packet>...</packet>
        packet=doc.createElement(self.xmlelement.name)
        for n,v in self.xmlelement.attributes.iteritems():
            packet.setAttribute(n,v)
        if self.xmlelement.children:
            for i,c in self.xmlelement.children.iteritems():
                child=doc.createElement(c.name)
                for nn,vv in c.attributes.iteritems():
                    child.setAttribute(nn,vv)
                child.appendChild(emptytxt)
                packet.appendChild(child)
        else:
            packet.appendChild(emptytxt)
        doc.appendChild(packet)
        return doc.toxml(encoding="UTF-8")

    def __call__(self):
        return self.write()

class XMLReader:
    ''' base class to read XML packets sent from the dockserver
        the list is not complete, only the responses on dockConfig
        gliderstatus and gliderconnect are implemented.
    '''
    def __init__(self):
        self.mesg=None
        self.responseaction=None
        self.responsetype='response'

    def messageCheck(self,mesg):
        self.initialise(mesg)
        if self.packetAttributes['type']==self.responsetype and \
           self.packetAttributes['action']==self.responseaction:
            return True
        else:
            self.mesg=None
            return False
        
    def readPacket(self):
        ''' reads a packet. This should not go wrong. If it does, the
            serial line is closed and others will continue to be
            monitored. If it does go wrong, things have to be investigated
            on per case basis.
        '''
        try:
            doc=minidom.parseString(self.mesg)
        except ExpatError:
            # could not read message. What to do?
            print "failed to read mesg. This is what I got:"
            print "---------------------------"
            print self.mesg
            print "---------------------------"
        if not doc.hasChildNodes:
            raise ValueError," no children. Investigate."
        # So far so good, the xml message is properly constructed
        # each doc has the form of packet /packet
        packets=doc.getElementsByTagName('packet')
        if len(packets)!=1:
            raise ValueError, "some something else than 1 packet in xml doc"
        self.packet=packets[0]
        
    def readPacketAttributes(self):
        self.packetAttributes=dict((i,j) for i,j in self.packet.attributes.items())

    def initialise(self,mesg):
        self.mesg=mesg
        self.readPacket()
        self.readPacketAttributes()




class DockConnect(XMLWriter,XMLReader):
    ''' To request to connect to dockserver '''
    def __init__(self,senderID='dockserverTalk;0'):
        XMLReader.__init__(self) 
        XMLWriter.__init__(self,senderID=senderID)
        self.responsetype="request"# I think this is a bug in dockserver protocol.
        self.responseaction="dockConnect"
        self.xmlelement.addAttribute("action","dockConnect")
        self.xmlelement.addAttribute("type","request")
	self.xmlelement.addAttribute("senderOption","") # this too. Should be Options.

    def parse(self):
        # nothing to do here, return None
        return 'recv_dockconnect'
    

class DockConfiguration(XMLWriter,XMLReader):
    ''' To ask dockConfiguration '''
    def __init__(self,cfg,configurationOnly=True,senderID='dockserverTalk;0'):
        XMLWriter.__init__(self,senderID=senderID)
        XMLReader.__init__(self) 
        self.responseaction="dockConfiguration"
	self.xmlelement.addAttribute("action","dockConfiguration")
	self.xmlelement.addAttribute("type","request")
	self.xmlelement.addAttribute("senderOption","") 
        self.dockserverConfig=cfg
        self.configurationOnly=configurationOnly

    def parse(self):
        cfgs={}
        # first figure uout which gliders this dockserver knows about:
        glidersNode=self.packet.getElementsByTagName('gliders')[0]
        gliders=glidersNode.getElementsByTagName('glider')
        for i in gliders:
            name=i.getAttribute('name')
            if name not in self.dockserverConfig.gliders.keys():
                cfg=dockserverConfig.GliderConfig(name)
            else:
                cfg=self.dockserverConfig.gliders[name]
            # set to undocked by default. If a link is found, it will be set to docked.
            cfg.set(None,None,'2')
            cfgs[name]=cfg
        # good, now which glider is connected to which serial device:
        linksNode=self.packet.getElementsByTagName('gliderLinks')[0]
        links=linksNode.getElementsByTagName('gliderLink')
        for i in links:
            name=i.getAttribute('gliderName')
            port=i.getAttribute('port')
            device=i.getAttribute('device')
            status=i.getAttribute('status')
            cfgs[name].set(port,device,status)
        # update the configs to dockserverConfig:
        for v in cfgs.itervalues():
            self.dockserverConfig.add(v)
        # generate the response string for the FSM:
        if self.configurationOnly:
            return 'recv_dockconfiguration'
        else:
            return 'req_gliderstatus'

        
class GliderStatus(XMLWriter,XMLReader):
    ''' Asks the gliderStatus'''
    GLIDERSTATUS={'1':'Docked','2':'Undocked','3':'Unserviced','0':'Unknown'}
    def __init__(self,cfg=None,senderID='dockserverTalk;0'):
        XMLWriter.__init__(self,senderID=senderID)
        XMLReader.__init__(self)
        if not cfg:
            raise ValueError," cfg required!"
        self.responseaction="gliderStatus"
	self.xmlelement.addAttribute("type","request")
	self.xmlelement.addAttribute("action","gliderStatus") 
	self.xmlelement.addAttribute("senderOption","") 
	self.xmlelement.addAttribute("gliderName",cfg.name) 
        self.config=cfg

    def parse(self):
        name=self.packetAttributes['name']
        status=self.packetAttributes['status']
        if status=='3': # glider seems not to be serviced and there is
                        # no configuration information here.
            pass
        else:
            self.config.status=status
            gliderLinksNode=self.packet.getElementsByTagName('gliderLinks')[0]
            gliderLinks=gliderLinksNode.getElementsByTagName('gliderLink')
            for j in gliderLinks:
                port=j.getAttribute('port')
                device=j.getAttribute('device')
                status=j.getAttribute('status')
                self.config.set(port,device,status)
        return 'recv_gliderstatus'+GliderStatus.GLIDERSTATUS[status]

            # there is much more to get from here, but we dont bother...

class GliderConnect(XMLWriter,XMLReader):
    ''' To ask gliderConnect. Can be done for gliderName or port.
        The latter has not been tested.
    '''
    def __init__(self,cfg,senderID='dockserverTalk;0'):
        XMLWriter.__init__(self,senderID=senderID)
        XMLReader.__init__(self) 
        self.responseaction="gliderConnect"
	self.xmlelement.addAttribute("type","request") 
	self.xmlelement.addAttribute("action","gliderConnect") 
	self.xmlelement.addAttribute("senderOption","") 
        self.xmlelement.addAttribute("gliderName",cfg.name) 
        self.cfg=cfg

    def parse(self):
        name=self.packetAttributes['gliderName']
        #port=self.packetAttributes['port']
        textNodes=self.packet.getElementsByTagName('text')
        text=''
        for textNode in textNodes:
            for i in textNode.childNodes:
                try:
                    text+=i.nodeValue.encode()
                except UnicodeEncodeError:
                    text='???'
        self.cfg.text=text
        #not necessary
        #gliderLinkNodes=self.packet.getElementsByTagName('gliderLink')[0]
        #status=gliderLinkNodes.getAttribute('status')
        status=self.cfg.status
        status_str=GliderStatus.GLIDERSTATUS[status]
        r="recv_gliderstatus%s"%(status_str)
        return r


class KeepAlive(XMLWriter,XMLReader):
    ''' constructs a keepAlive packet'''
    def __init__(self,senderID='dockserverTalk;0'):
        XMLWriter.__init__(self,senderID=senderID)
        XMLReader.__init__(self)
        self.responseaction="keepalivePacket"
	self.xmlelement.addAttribute("action","keepalivePacket") 
	self.xmlelement.addAttribute("senderOption","") 
        self.xmlelement.attributes.pop("type") # only this message does not have this.

    def parse(self):
        return 'recv_keepalive'
        

class GliderCommand(XMLWriter,XMLReader):
    ''' To ask glider command to be executed.
    '''
    def __init__(self,cfg,senderID='dockserverTalk;0'):
        XMLWriter.__init__(self,senderID=senderID)
        XMLReader.__init__(self) 
        self.action="gliderCommand"
        self.type="request"
	self.xmlelement.addAttribute("type","request") 
	self.xmlelement.addAttribute("action","gliderCommand") 
	self.xmlelement.addAttribute("senderOptions",";") 
	xmlGliderLink=XMLElement("gliderLink")
	xmlGliderLink.addAttribute("gliderName",cfg.name)
        self.xmlelement.addChild("gliderLink",xmlGliderLink)
        self.cfg=cfg

    def set_command(self,command):
        self.xmlelement.addAttribute("command",command)
        self.xmlelement.children["gliderLink"].addAttributes([
                ("gliderName",self.cfg.name),
                ("port",self.cfg.port),
                ("device",self.cfg.device)])

    def parse(self):
        return 'not_used?'
