''' Relies on LibAIS, written by  Kurt Schwehr: 
Web: http://vislab-ccom.unh.edu/~schwehr/software/libais/
GITHUB: https://github.com/schwehr/libais.git

Here we assume you have this installed, as well as scipy, numpy and matplotlib
'''
import ais
import os, sys, re
import numpy as np
import scipy.io as sio
import gpplib
from gpplib import *
from gpplib.Utils import *
import time, datetime
from sets import Set
from gpplib.GenGliderModelUsingRoms import GliderModel
from matplotlib import pyplot as plt

conf = gpplib.Utils.GppConfig()

ais_data_dir = '/Users/arvind/Documents/data/AIS/data/'+'2010-01/'

class AISGpp(object):
    '''
            Here is a typical AIVDM data packet:
        
        --------------------------------------------------------------------
        !AIVDM,1,1,,B,177KQJ5000G?tO`K>RA1wUbN0TKH,0*5C
        --------------------------------------------------------------------
        
        And here is what the fields mean:
        
        Field 1, !AIVDM, identifies this as an AIVDM packet.
        
        Field 2 (1 in this example) is the count of fragments in the currently
        accumulating message.  The payload size of each sentence is limited by
        NMEA 0183's 82-character maximum, so it is sometimes required to split
        a payload over several fragment sentences.
        
        Field 3 (1 in this example) is the fragment number of this
        sentence. It will be one-based.  A sentence with a fragment count of
        1 and a fragment number of 1 is complete in itself.
        
        Field 4 (empty in this example) is a sequential message ID for
        multi-sentence messages.
        
        Field 5 (B in this example) is a radio channel code. AIS uses the high
        side of the duplex from two VHF radio channels: AIS Channel A is
        161.975Mhz (87B); AIS Channel B is 162.025Mhz (88B).
        
        Field 6 (177KQJ5000G?tO`K>RA1wUbN0TKH in this example) is the data
        payload. We'll describe how to decode this in later sections.
        
        Field 7 (0) is the number of fill bits requires to pad the data
        payload to a 6 bit boundary, ranging from 0 to 5.  Equivalently,
        subtracting 5 from this tells how many least significant bits of the
        last 6-bit nibble in the data payload should be ignored. Note that
        this pad byte has a tricky interaction with the <<<ITU-1371>>>
        requirement for byte alignment in over-the-air AIS messages; see the
        detailed discussion of message lengths and alignment in a later
        section.
        
        The \*-separated suffix (\*5C) is the NMEA 0183 data-integrity checksum
        for the sentence, preceded by "*".  It is computed on the entire
        sentence including the AIVDM tag but excluding the leading "!".
    '''
    def __init__(self,**kwargs):
        self.msgList = []
        
        
    def ParseAIS_String(self,ais_str):
        aivdm_m = re.match('!AIVDM,([0-9]*),([0-9]*),([0-9]*),([AB]+),([\w]+),([0-9]*)([*A-Z0-9]+)',ais_str)
        if(aivdm_m):
            self.frag_count =aivdm_m.group(1)
            self.frag_num   =aivdm_m.group(2)
            self.seq_msgid  =aivdm_m.group(3)
            self.radio_chan =aivdm_m.group(4)
            self.payload    =aivdm_m.group(5)
            self.fill_bits  =aivdm_m.group(6)
            self.nmea_chksum=aivdm_m.group(7)
            try:
                self.decodedMsg = ais.decode(self.payload)
                #print self.decodedMsg
                return self.decodedMsg
            except:
                self.decodedMsg = None
        return None

    def DecodeAIS(self,fileName):
        f = open(fileName,'r')
        lines = f.readlines()
        
        #aism = AIS_Message()
        
        msgList = []
        for line in lines:
            msg = self.ParseAIS_String(line)
            if msg!=None:
                msgList.append(msg)
        f.close()
        
        return msgList

    def FindUniqueVessels(self,msgList):
        vessels = Set()
        for msg in msgList:
            vessels.add(msg['mmsi'])
        return vessels

    def CreateMsgIndexByVessel(self,msgList,vessels):
        msgIndxByVessel = {}
        for vessel in vessels:
            msgIndxByVessel['%d'%(vessel)]=[]
            for idx,msg in enumerate(msgList):
                if msg['mmsi']==vessel:
                    msgIndxByVessel['%d'%(vessel)].append(msg)
        return msgIndxByVessel


    def GetDateTimeFromDateStr(self,myDate,myTime):
        yy = int(myDate)/10000
        mm_dd = myDate%10000
        mm = mm_dd/100
        dd = mm_dd%100
        
        hr = myTime/100
        mi = myTime%100
        
        print yy,mm,dd,hr,mi
        dt = datetime.datetime(yy,mm,dd,hr,mi)
        return dt
    
    def AddMessagesFromFileNamed(self,fileName):
        msgList = self.DecodeAIS(fileName)
        for msg in msgList:
            self.msgList.append(msg)
            
    def CreateIndexByVessels(self):
        self.vessels = self.FindUniqueVessels(self.msgList)
        self.vesselList = list(self.vessels)
        self.msgIndxByVessel = self.CreateMsgIndexByVessel(self.msgList, self.vessels)



    def PlotCoursesOnMap(self):
        gm = GliderModel(conf.myDataDir+'RiskMap.shelf',conf.myDataDir+'roms')
        plt.figure();
        gm.PlotNewRiskMapFig()
        #gm.GetXYfromLatLon()
        for vessel in self.vesselList:
            msgList = self.msgIndxByVessel['%d'%(vessel)]
            trackX,trackY = [],[]
            for msg in msgList:
                if msg.has_key('y'):
                    lat,lon = msg['y'],msg['x']
                    x,y = gm.GetXYfromLatLon(lat,lon)
                    trackX.append(x); trackY.append(y)
            plt.plot(trackX,trackY,'.-')


'''
aisgpp = AISGpp()
ais_data={}
ais_data['date'] = []
ais_data['filename'] = []
fileList = os.listdir(ais_data_dir)
for file in fileList:
    ais_m = re.match('ais_([0-9]+)-([0-9]+).dat',file)
    if ais_m:
        myDate = int(ais_m.group(1)); myTime=int(ais_m.group(2))
        myDt = aisgpp.GetDateTimeFromDateStr(myDate,myTime)
        ais_data['date'].append(myDt)
        ais_data['filename'].append(file)
        aisgpp.AddMessagesFromFileNamed(ais_data_dir+file)
aisgpp.CreateIndexByVessels()

#test_file=ais_data['filename'][0]
#aisgpp.AddMessagesFromFileNamed(ais_data_dir+test_file)
aisgpp.PlotCoursesOnMap(aisgpp)
'''




