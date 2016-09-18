'''
@author: Arvind Pereira
@contact: arvind.pereira@gmail.com
@summary: Create KML file
'''
import GliderFileTools
import LatLonConversions

# Required for pylibkml
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages/')
from pylibkml import Kml,Utilities


# Global variables for the overall Kml document
class KmlCreator():
    def __init__(self):
        self.style= []
        self.folder = []
        self.icon_style = []
        self.line_color = 'ff0000ff' # red if line-color isn't set
        self.line_width = 3
    
    def SetLineColor(self,color='ffff0000'): # blue by default
        self.line_color = color
    
    def SetLineWidth(self,width = 3):
        self.line_width = width
    
    def WriteWptListToKml(self,WptLatList,WptLonList,WptTimeList=[],WptRiskList=[],options={}):
        wpt_list_placemark = []
        wpt_list_folder = []
        
        wpt_line_placemark = []
        wpt_line_str = []
        wpt_line_folder = []
        wpt_line_coods = []
        
        if len(WptTimeList)>0:
            WptTimePresent = 1
        else: WptTimePresent = 0
        
        if len(WptRiskList)>0:
            WptRiskPresent=1
        else: WptRiskPresent = 0
        
        self.SetIconHrefStyle('rusalka-glider-list-style','http://cinaps.usc.edu/gliders/img/glider1.png')
        self.SetIconHrefStyle('hehape-glider-list-style','http://cinaps.usc.edu/gliders/img/glider2.png')
        self.SetIconHrefStyle('start-wpt-list-style','http://maps.google.com/mapfiles/kml/paddle/grn-stars.png')
        self.SetIconHrefStyle('wpt-list-style','http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png')
        self.SetIconHrefStyle('stop-wpt-list-style','http://maps.google.com/mapfiles/kml/paddle/G.png')
    
        llConv = LatLonConversions.LLConvert()
        # Here the lat,lon data is in webb format...
        for i in range(0,len(WptLatList)):
            d_lat,d_lon = WptLatList[i],WptLonList[i]
            if(options.has_key('ConvertLLfromWebbToDec')):
                if options['ConvertLLfromWebbToDec']==True:
                    d_lat,d_lon = llConv.WebbToDecimalDeg(WptLatList[i], WptLonList[i] )
            coordinate = Kml().create_coordinates(d_lon,d_lat,0)
            # Create a <Point> object
            point=Kml().create_point({'coordinates':coordinate,'altitudemode':'absolute'})
            # Create a <TimeStamp> object
            #timestamp = Kml().create_timestamp({'when':GetKMLTimeString(mytime[i])})
            # Create the <Data> objects and place them in <ExtendedData>
            data = []
            #data.append(Kml().create_data({'name':'eqid','value':Eqid[i]}))
            data.append(Kml().create_data({'name':'lat','value':d_lat}))
            data.append(Kml().create_data({'name':'lon','value':d_lon}))
             
            if WptTimePresent:
                data.append(Kml().create_data({'name':'time','value': '%f'%(WptTimeList[i]) })) #GetKMLTimeString(mytime[i])}))
            if WptRiskPresent:
                data.append(Kml().create_data({'name':'risk','value':'%f'%(WptRiskList[i])}))
            extendeddata=Kml().create_extendeddata({'data':data})
            #Create the <Placemark> object
            if i==0:
                    styleUrl = '#start-wpt-list-style'
                    wpt='Start'
            else:
                if i==len(WptLatList)-1:
                    styleUrl = '#stop-wpt-list-style'
                    wpt = 'Goal'
                else:
                    styleUrl = '#wpt-list-style'
                    wpt = 'W%d'%(i+1)
            wpt_list_placemark.append(Kml().create_placemark({'point':point,
                                                         'extendeddata':extendeddata,
                                                        'styleurl':styleUrl, 'name':wpt}))
            
        for i in range(0,len(WptLatList)):
            d_lat,d_lon = llConv.WebbToDecimalDeg(WptLatList[i],WptLonList[i])
            wpt_line_coods.append((d_lon,d_lat,0))
        
        self.CreateFolderInKml('WptListFolder',wpt_list_placemark)
        self.style.append(Kml().create_style({'id':'line-style','linestyle':Kml().create_linestyle({'width':self.line_width,'color':self.line_color,'colorMode':'normal'})}))
        wpt_line_str = Kml().create_linestring({'tessellate':1,'altitudemode':'absolute','styleurl':'#line-style','coordinates':Kml().create_coordinates(wpt_line_coods)})
        wpt_line_placemark.append(Kml().create_placemark({'linestring':wpt_line_str,'styleurl':'#line-style'}))
        self.CreateFolderInKml('WptLineFolder', wpt_line_placemark )
        
    def SetIconHrefStyle(self,styleName,icon_href):
        #Create the <Icon> object for the <IconStyle>
        #icon_href = 'http://cinaps.usc.edu/gliders/img/glider1.png'
        iconstyleicon = Kml().create_iconstyleicon({'href':icon_href})
        #Create the <IconStyle> object
        iconstyle =Kml().create_iconstyle({'icon':iconstyleicon})
        self.style.append(Kml().create_style({'id':styleName,'iconstyle':iconstyle,'color':'ff0400ff'}))    
       
       
    def CreateFolderInKml(self, folderName, placeMark ):
        self.folder.append(Kml().create_folder({'name':folderName, 'placemark':placeMark }))
            
    def CreateAndSaveKml(self,kmlFileName):
       # Put all folders and styles into a <Document> object
        self.document = Kml().create_document({'folder':self.folder,'style':self.style})
        # Create the Final <Kml> object
        self.kml = Kml().create_kml({'document':self.document})
    
        print "Writing KML file to: %s"%(kmlFileName)
        #Write the Kml object to GPStest.kml
        toFile = open(kmlFileName,'w')
        toFile.write(Utilities().SerializePretty(self.kml))
        toFile.close()
