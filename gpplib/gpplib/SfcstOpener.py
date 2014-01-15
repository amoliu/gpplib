import scipy.io as sio
import numpy as np

class SfcstOpen(object):
	def __init__(self,sfcst_dir=None):
		self.sfcst_dir = sfcst_dir
		self.yy,self.mm,self.dd = 2011,1,1 # Just start off with something.
		
	def openSfcstForDate( self,yy,mm,dd, userDir = '' ):
		if userDir == '':
			self.fileName = '%s/sfcst_%04d%02d%02d'%(self.sfcst_dir,yy,mm,dd)
		else:
			self.fileName = '%s/sfcst_%04d%02d%02d'%(userDir,yy,mm,dd)
			self.sfcst_dir = userDir
		self.LoadFile( self.fileName )
		
	def openSfcstFileName( self,fileName ):
		self.fileName = fileName	
		self.LoadFile( self.fileName )
		
	def LoadFile( self,fileName ):
		temp_sfcst = sio.loadmat( fileName )	
		if temp_sfcst.has_key('forecast'):
			forecast = temp_sfcst['forecast'][0]
			if forecast.dtype==object:
				u = forecast[0].u[0,0].u
				v = forecast[0].v[0,0].v
				depth = forecast[0].depth
				time = forecast[0].time
				lat = forecast[0].lat
				lon = forecast[0].lon
			else:
				u = forecast['u'][0]['u'][0][0]
				v = forecast['v'][0]['v'][0][0]
				depth = forecast['depth'][0]
				time = forecast['time'][0]
				lat = forecast['lat'][0]
				lon = forecast['lon'][0]
			return u,v,time,depth,lat,lon


class SfcstGPOpen(SfcstOpen):
	def __init__(self,sfcst_dir=None):
		super(SfcstGPOpen,self).__init__(sfcst_dir)
		
	def LoadFile(self,fileName):
		temp_sfcst=sio.loadmat(fileName)
		if temp_sfcst.has_key('forecast'):
			forecast = temp_sfcst['forecast'][0]
			if forecast.dtype==object:
					u = forecast[0].u[0,0].u
					v = forecast[0].v[0,0].v
					u_iv=foreacast[0].u[0,0].iv
					v_iv=forecast[0].v[0,0].iv
					u_gp=forecast[0].u[0,0].ugp
					v_gp=forecast[0].v[0,0].vgp
					u_kv=forecast[0].u[0,0].kv
					v_kv=forecast[0].v[0,0].kv
					depth = forecast[0].depth
					time = forecast[0].time
					lat = forecast[0].lat
					lon = forecast[0].lon
			else:
					u = forecast['u'][0]['u'][0][0]
					v = forecast['v'][0]['v'][0][0]
					u_iv=forecast['u'][0]['iv'][0][0]
					v_iv=forecast['v'][0]['iv'][0][0]
					u_gp=forecast['u'][0]['ugp'][0][0]
					v_gp=forecast['v'][0]['vgp'][0][0]
					u_kv=forecast['u'][0]['kv'][0][0]
					v_kv=forecast['v'][0]['kv'][0][0]
					depth = forecast['depth'][0]
					time = forecast['time'][0]
					lat = forecast['lat'][0]
					lon = forecast['lon'][0]
			return u,v,time,depth,lat,lon,u_iv,v_iv,u_gp,v_gp,u_kv,v_kv