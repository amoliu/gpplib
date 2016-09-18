''' Simple connection to the glider for the purpose of watching for certain things automatically.
'''
import socket
import xml.dom.minidom
import select
import time

class GTEnums():
    pass


class GliderTerminalPacket(object):
    ''' XML packet for glider
    '''
    def __init__(self,**kwargs):
        self.packData = {}
        if kwargs.has_key('senderID'):
            self.packData['senderID'] = kwargs['senderID']
        if kwargs.has_key('senderBuildVersion'):
            self.packData['senderBuildVersion'] = kwargs['senderBuildVersion']
        if kwargs.has_key('senderVersion'):
            self.packData['senderVersion'] = kwargs['senderVersion']
        if kwargs.has_key('type'):
            self.packData['type'] = kwargs['type']
        if kwargs.has_key('action'):
            self.packData['action'] = kwargs['action']


class GliderTerminal(object):
    ''' Connection to a glider
    ''' 
    def __init__(self,host='10.1.1.20',port=6564):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))
        self.dsHost, self.dsPort = host, port
        print self.sock.getsockname()
        print self.sock.getpeername()
        #self.sock.close()
        
    def GetPacket(self):
        response = self.sock.recv(8192)
        doc=xml.dom.minidom.parseString(response)
        packets = doc.getElementsByTagName('packet')
        dataInPacket={}
        for a in packets:
            dataInPacket['action']= a.getAttribute('action')
            dataInPacket['senderBuildVersion']=a.getAttribute('senderBuildVersion')
            dataInPacket['senderID']=a.getAttribute('senderID')
            dataInPacket['senderVersion']=a.getAttribute('senderVersion')
            dataInPacket['type'] = a.getAttribute('type')
            
        print dataInPacket
        print response
        
    def SendResponse(self):
        outPack = ''
        outPack+='<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>'
        outPack+='<packet action=\"keepalivePacket" senderBuildVersion=\"glider 7.6 Optode 4330F\" '
        outPack+='senderID=\"Administrator;172.16.145.132;Glider Terminal;%d\" '%(int(time.time()))
        outPack+='senderVersion=\"Glider Terminal;7.6\" type=\"packet\">'
        outPack+='</packet>'
        self.sock.send(outPack)
        
        
    def Close(self):
        self.sock.close()

gt= GliderTerminal()
gt.GetPacket()
gt.SendResponse()
gt.GetPacket()
gt.Close()
