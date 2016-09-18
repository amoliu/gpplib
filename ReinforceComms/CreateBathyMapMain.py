from MapTools import *
from LatLonZ import *
import bisect
from gpp_in_cpp import ImgMap
from gpp_in_cpp import ImgMapUtils
import time
import scipy.io as sio

def InitImageWithValues(npImg,**kwarg):
    '''    Set ImgHeader.
    '''
    myImg = {}
    myImg['ImgArray']=npImg
    # Force exceptions if we don't have all the information we need.
    myImg['Width']=kwarg['Width']
    myImg['Height']=kwarg['Height']
    myImg['Res']=kwarg['Res']
    myImg['0xDeg']=kwarg['0xDeg']
    myImg['0yDeg']=kwarg['0yDeg']
    myImg['LatDeg']=kwarg['LatDeg']
    myImg['LonDeg']=kwarg['LonDeg']
    myImg['NormVal']=kwarg['NormVal']
    
    myImg['MaxY_Diff']=kwarg['MaxY_Diff']
    myImg['MaxLatDiff']=kwarg['MaxLatDiff']
    myImg['MaxLonDiff']=kwarg['MaxLonDiff']
    myImg['MaxVal']=kwarg['MaxVal']
    myImg['MinVal']=kwarg['MinVal']
    myImg['ImgType']=kwarg['ImgType']
    myImg['ResX']=kwarg['ResX']
    myImg['ResY']=kwarg['ResY']
    myImg['LatDiff']=kwarg['LatDiff']
    myImg['LonDiff']=kwarg['LonDiff']
    return myImg




        

start=time.time()
conf = gpplib.Utils.GppConfig()
'''
#result = np.loadtxt(open(conf.myDataDir+'SCB_Bathy/SCB_CST1-9224_data/SCB_CST1-9224/'+'SCB_CST1-9224.xyz','rb'),delimiter=',',skiprows=0)
#np.save( 'SCB_CST',result)
'''
result = np.load('SCB_CST.npy')
lon, lat, Z = result[:, 0], result[:, 1], result[:, 2]

''' Store the data in a KD-tree for fast Nearest Neighbor lookup '''
#tree=spatial.KDTree(zip(lat.ravel(),lon.ravel()))

''' Let us choose a resolution of lat,lon which is lower than the data we have '''

#latN, latS, lonW, lonE = 33.25, 32.00, -119.0, -117.7
llz = LatLonZ(lat,lon,Z)
lat, lon, Z = llz.FilterLatLonZ_ValuesBetweenLatLonValues()

''' Now create a map with the desired resolution '''
high_res_y = np.unique(lat).shape[0]
high_res_x = np.unique(lon).shape[0]

map_res = 500. # 100 m / pixel
latN,latS = max(lat),min(lat)
lonW,lonE = min(lon),max(lon)

mc = MapConversions(latN,latS,lonW,lonE,map_res)      
pxWidth,pxHeight = mc.pxWidth, mc.pxHeight
bathyImg = np.zeros((pxHeight,pxWidth))


for y in range(0,int(pxHeight)):
    for x in range(0,int(pxWidth)):
        #bathyImg[x,y] = 
        #getNearestZforLatLon 
        latT,lonT = mc.getLatLonFromPxPy(x,y)
        #bathyImg[x,y] = llz.getNearestZforLatLon(latT, lonT)
        bathyImg[y,x] = llz.getNearestZforLatLon(latT, lonT)

np.save('SCB_bathy_NSEW_%.5f_%.5f_%.5f_%.5f_WH_%d_%d_Res_%.1f.npy'%(latN,latS,lonW,lonE,pxWidth,pxHeight,map_res),bathyImg)
stop=time.time()
print 'Took %.3f secs to create the map.'%(stop-start)
nim1=NewImageMap.InitWithImage(bathyImg,latN,latS,lonW,lonE,map_res)
nim1.SaveImageToMat('SCB_bathy_%d.mat'%(int(map_res)))


obsImg = np.where(bathyImg>-5,255.,0.)
nim2=NewImageMap.InitWithImage(obsImg,latN,latS,lonW,lonE,map_res)
nim2.SaveImageToMat('SCB_bin_bathy_%d.mat'%(int(map_res)))

