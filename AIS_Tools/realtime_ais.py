''' Get real-time AIS data... This is done by listening to the telnet port :
telnet sandbar.ucsd.edu 8060
'''
import time
from telnetlib import Telnet
from process_ais_data import AISGpp
    
aisgpp = AISGpp()
aisMsgList = []
t = Telnet('sandbar.ucsd.edu',8060)
end_time = time.time() + 60.

while time.time()<end_time:
    ais_msg = t.read_until('\n',1)
    ais_dec_msg = aisgpp.ParseAIS_String(ais_msg)
    if ais_dec_msg!=None:
        print ais_dec_msg
        aisMsgList.append(ais_dec_msg)
t.close()

aisgpp.msgList = aisMsgList
aisgpp.CreateIndexByVessels()
aisgpp.PlotCoursesOnMap()


#t.interact()