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


'''Some classes that help to store the configuration of the
   dockserver: which gliders are known and connected to it.

   9 Dec 2009 Lucas Merckelbach. (lucas.merckelbach@noc.soton.ac.uk)

   Comes with no Warranty.

   Released under GPL v3 licence
'''


STATUS={'0':'0','1':'Docked','2':'Undocked','3':'Unknown'}

class GliderLink:
    def __init__(self):
        self.port=None
        self.device=None
        self.status=None
        
    def set(self,port,device,status=None):
        self.port=port
        self.device=device
        self.status=status
        
class GliderConfig(GliderLink):
    def __init__(self,name):
        GliderLink.__init__(self)
        self.name=name
        self.status='0'
        self.text=''

class DockserverConfig:
    def __init__(self,hostName):
        self.hostName=hostName
        self.gliders={}
    def add(self,gliderconfig):
        name=gliderconfig.name
        self.gliders[name]=gliderconfig
    def show(self):
        fmt="%10s%10s%15s%10s%10s"
        gliders=self.gliders.keys()
        gliders.sort()
        print fmt%("Name","Status","Port","Device","Status")
        for g in gliders:
            cfg=self.gliders[g]
            if cfg.port==None:
                print fmt%(g,STATUS[cfg.status],'-','-','-')
            else:
                print fmt%(g,STATUS[cfg.status],cfg.port,cfg.device,cfg.status)



