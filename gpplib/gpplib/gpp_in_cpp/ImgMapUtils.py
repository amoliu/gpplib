'''
ImgMap wrapper
'''
import numpy as np
import ImgMap
import shelve

class ImgMapUtil():
    def __init__(self):
            self.img = None
            self.UtilImg = None
    
    def ConvImgMapToDict(self,img,options={}):
            self.UtilImg={}
            if(options.has_key('ReflectImage')):
                npImg = self.ReflectImage(img)
            else:
                npImg=self.GetImage(img)
            self.UtilImg['ImgArray']=npImg
            self.UtilImg['Width']=img.GetWidth()
            self.UtilImg['Height']=img.GetHeight()
            self.UtilImg['Res']=img.GetRes()
            self.UtilImg['0xDeg']=img.GetOxDeg()
            self.UtilImg['0yDeg']=img.GetOyDeg()
            self.UtilImg['LatDeg']=img.GetLatDeg()
            self.UtilImg['LonDeg']=img.GetLonDeg()
            self.UtilImg['NormVal']=img.GetNormVal()
            self.UtilImg['MaxY_Diff']=img.GetMaxY_Diff()
            self.UtilImg['LatDiff']=img.GetLatDiff()
            self.UtilImg['LonDiff']=img.GetLonDiff()
            self.UtilImg['MaxLatDiff']=img.GetMaxLatDiff()
            self.UtilImg['MaxLonDiff']=img.GetMaxLonDiff()
            self.UtilImg['MaxVal']=img.GetMaxVal(True)
            self.UtilImg['MinVal']=img.GetMinVal(True)
            self.UtilImg['ImgType']=img.GetImageType()
            self.UtilImg['ResX'] = img.GetResX()
            self.UtilImg['ResY'] = img.GetResY()
            return self.UtilImg
        
    def ConvImageDictToImgMap(self, UtilImg ):
            self.img = ImgMap.ImgMap()
            self.img.SetWidth(UtilImg['Width'])
            self.img.SetHeight(UtilImg['Height'])
            self.img.SetSize(UtilImg['Width'],UtilImg['Height'])
            for y in range(0,UtilImg['Height']):
                for x in range(0,UtilImg['Width']):
                    self.img.SetValue(x,y,UtilImg['ImgArray'][x][y])
            self.img.SetRes(UtilImg['Res'])
            self.img.SetOxDeg(UtilImg['0xDeg'])
            self.img.SetOyDeg(UtilImg['0yDeg'])
            self.img.SetLatDeg(UtilImg['LatDeg'])
            self.img.SetLonDeg(UtilImg['LonDeg'])
            self.img.SetNormVal(int(UtilImg['NormVal']))
            self.img.SetMaxY_Diff(UtilImg['MaxY_Diff'])
            self.img.SetMaxLatDiff(UtilImg['MaxLatDiff'])
            self.img.SetMaxLonDiff(UtilImg['MaxLonDiff'])
            self.img.SetMaxVal(UtilImg['MaxVal'])
            self.img.SetMinVal(UtilImg['MinVal'])
            self.img.SetImageType(int(UtilImg['ImgType']))
            self.img.SetResX(UtilImg['ResX'])
            self.img.SetResY(UtilImg['ResY'])
            self.img.SetLatDiff(UtilImg['LatDiff'])
            self.img.SetLonDiff(UtilImg['LonDiff'])
            return self.img
            
    def ReflectImage(self, img):
        npImg=np.zeros((img.GetHeight(),img.GetWidth()))
        for y in range(0,img.GetHeight()): 
            for x in range(0,img.GetWidth()):
                npImg[y][x]=(img.GetValue(x,y))
        return npImg
    
    def GetImage(self,img):
        npImg=np.zeros((img.GetWidth(),img.GetHeight()))
        for y in range(0,img.GetHeight()): 
            for x in range(0,img.GetWidth()):
                npImg[x][y]=(img.GetValue(x,y))
        return npImg
