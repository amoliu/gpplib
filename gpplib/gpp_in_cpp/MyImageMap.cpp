/*!
 * MyImageMap.cpp
 *
 *  Created on: Mar 16, 2011
 *  @author:   Arvind A de Menezes Pereira
 *  @summary:  code for handling map-images for planning. These images are normally created
 *  using Matlab scripts, but can also be easily created by using the ImgMap module which you
 *  get by compiling this program from pgm image files.
 */
/*!
 * MAP9 format:
 * MAP9 [w] [h] [norm-val]
 * w => width
 * h => height
 * norm-val => maximum value to be used for normalization, so maps can be stored as integers
 *
 * MAP5 format:
 * MyImageMap is going to be able to handle comms maps.
 *	From now on the header information is going to be very important.
 *	MAP5 [w] [h] [norm-val] [res] [ox-deg] [oy-deg] [lat_deg] [lon_deg] [lat_diff] [lon_diff]
 *	w => width
 *	h => height
 *	norm-val => normalization value, so maps can be stored as integers
 *	res=> resolution of the map. 1 px = res m eg. 100
 *	ox-deg=> the origin's longitude in degrees eg. -118.8
 *	oy-deg=> the origin's latitude in degrees eg. 33.25
 *	lat_deg=> the conversion factor for the map to convert between m and lat degrees. eg. 110913.73
 *	lon_deg=> the conversion factor for the map to convert between m and lon degrees. eg. 92901.14
 *	lat_diff=> the extents for the y-axis in degrees. eg. 0.8833333
 *	lon_diff=> the extents for the x-axis in degrees. eg. 1.1
 *	TODO: Convert all the exit() calls to Exceptions. Python likes Exceptions.!
 */
#include "MyImageMap.h"
#include <iostream>
#include <string>
#include <cstdlib>
#include <cstring>
#include <float.h>
/*!
 * Definition of the ImgMap BOOST_PYTHON module - Here we wrap our code for use in Python.
 */
BOOST_PYTHON_MODULE(ImgMap)
{
	using namespace boost::python;
	class_<MyImageMap>("ImgMap", init<char*>() )
			.def(init<>())
			.def("OpenMap", &MyImageMap::OpenMapGeneric )
			.def("GetValue", &MyImageMap::GetValue)
			.def("SetValue", &MyImageMap::SetValue)
			.def("OpenPgmMap", &MyImageMap::OpenPgmMapFileNameOnly)
			.def("GetRes",&MyImageMap::getRes )
			.def("GetResX",&MyImageMap::getRes_x )
			.def("GetResY",&MyImageMap::getRes_y )
			.def("GetOxDeg",&MyImageMap::getOx_deg )
			.def("GetOyDeg",&MyImageMap::getOy_deg )
			.def("GetLatDeg",&MyImageMap::getLat_deg )
			.def("GetLonDeg",&MyImageMap::getLon_deg )
			.def("GetLatDiff",&MyImageMap::getLat_diff )
			.def("GetLonDiff",&MyImageMap::getLon_diff )
			.def("GetNormVal",&MyImageMap::getNorm_val )
			.def("SetNormVal",&MyImageMap::setNorm_val )
			.def("GetMaxLatDiff",&MyImageMap::getMax_lat_diff )
			.def("GetMaxLonDiff",&MyImageMap::getMax_lon_diff )
			.def("GetMaxY_Diff",&MyImageMap::getMax_y_diff )
			.def("SetLatDeg",&MyImageMap::setLat_deg )
			.def("SetLatDiff",&MyImageMap::setLat_diff )
			.def("SetLonDeg",&MyImageMap::setLon_deg )
			.def("SetLonDiff",&MyImageMap::setLon_diff )
			.def("SetMaxLatDiff",&MyImageMap::setMax_lat_diff )
			.def("SetMaxLonDiff",&MyImageMap::setMax_lon_diff )
			.def("SetMaxY_Diff",&MyImageMap::setMax_y_diff )
			.def("SetOxDeg",&MyImageMap::setOx_deg )
			.def("SetOyDeg",&MyImageMap::setOy_deg )
			.def("SetRes",&MyImageMap::setRes )
			.def("SetResX",&MyImageMap::setRes_x )
			.def("SetResY",&MyImageMap::setRes_y )
			.def("GetWidth",&MyImageMap::getWidth )
			.def("GetHeight",&MyImageMap::getHeight )
			.def("SetWidth",&MyImageMap::setWidth )
			.def("SetHeight",&MyImageMap::setHeight )
			.def("ReSampleMapXY",&MyImageMap::ReSampleMapXY )
			.def("WritePgm",&MyImageMap::WritePgm)
			.def("WriteMap",&MyImageMap::WriteMap)
			.def("WriteMap5",&MyImageMap::WriteCommsMap)
			.def("ScaleMapToPgm",&MyImageMap::ScaleMapToPgm )
			.def("ScaleMapToMap",&MyImageMap::ScaleMapToMap)
			.def("DuplicateHeader",&MyImageMap::DuplicateHeader )
			.def("LatLonToMapXY",&MyImageMap::LatLonToMapXY)
			.def("MapXYToLatLon",&MyImageMap::MapXYToLatLon)
			.def("InitGaussianMatrix",&MyImageMap::InitGaussianMatrix)
			.def("ConvolveImageGaussian", &MyImageMap::ConvolveImageGaussian )
			.def("GetMaxVal", &MyImageMap::getMaxVal )
			.def("GetMinVal", &MyImageMap::getMinVal )
			.def("SetMaxVal", &MyImageMap::setMaxVal )
			.def("SetMinVal", &MyImageMap::setMinVal )
			.def("GetImageType",&MyImageMap::getImg_type)
			.def("SetImageType",&MyImageMap::setImg_type)
			.def("ExtendBorders",&MyImageMap::ExtendBordersOutByNpixels)
			.def("ReflectBordersOut",&MyImageMap::ExtendBordersOutByReflectingNpixels)
			.def("SetSize",&MyImageMap::SetSize)
			.enable_pickling()
			;
}

/*!
 * MyImageMap constructor. Sets img_type to Unknown, initializes image-size to (0,0),
 * and the lastMaxVal, lastMinVal values to DBL_MIN and DBL_MAX.
 * This constructor is being specially re-written in order to handle python objects.
 * It accepts as input a file-name and loads up the image file according to the type of
 * image-map file that is being loaded.
 * It accepts files which have the MAP(X) definition in the header.
 */
MyImageMap::MyImageMap()
{
	this->img_type = Unknown;
	this->SetSize(0,0);
	this->lastMaxVal=DBL_MIN;
	this->lastMinVal=DBL_MAX;
}

/*!
 * @param mapFileName: (char*) file-name for the map. Will use strings soon.
 */
MyImageMap::MyImageMap(char *mapFileName)
{
	this->OpenMapGeneric(mapFileName);
	this->lastMaxVal=DBL_MIN;
	this->lastMinVal=DBL_MAX;
}

/*!
 * Helps copy another image to this one.
 * TODO: Might need to implement reference counting.
 * @param map2 -> a reference to a MyImageMap instance.
 * @return (*this) -> a reference to myself.
 */
MyImageMap& MyImageMap::operator=(MyImageMap &map2)
{
	if( &map2 == this ) //trying to assign yourself to yourself isn't allowed!
		throw OutOfRange("Pointer out of range. Self Assignment attempted.");

	this->DuplicateHeader(map2);
	map = map2.getArray();
	return *this;
}

/*!
 *
 * @param mapArray
 * @return
 */
bool MyImageMap::setArray(array2D mapArray)
{
	if( std::equal(map.shape(),map.shape()+map.num_dimensions(),mapArray.shape())) {
		map = mapArray;
		return true;
	}
	else cerr<<"Images are not of the same size!";
	return false;
}

MyImageMap::array2D MyImageMap::getArray()
{
	return this->map;
}


void MyImageMap::DuplicateHeader( MyImageMap m )
{
	this->lat_deg = m.getLat_deg();
	this->lon_deg = m.getLon_deg();
	this->img_type = m.getImg_type();
	this->width = m.getWidth();
	this->height = m.getHeight();
	this->norm_val = m.getNorm_val();
	this->lat_diff = m.getLat_diff();
	this->lon_diff = m.getLon_diff();
	this->max_lat_diff = m.getMax_lat_diff();
	this->max_lon_diff = m.getMax_lon_diff();
	this->max_y_diff = m.getMax_y_diff();
	this->res = m.getRes();
	this->ox_deg = m.getOx_deg();
	this->oy_deg = m.getOy_deg();
	map.resize(boost::extents[width][height]);
	res_x = res;
	res_y = res;
	res_lat = res_y / lat_deg;
	res_lon = res_x / lon_deg;
	max_lat_diff = lat_diff / res_lat;
	max_lon_diff = lon_diff / res_lon;
	max_y_diff = ceil( lat_diff * lat_deg / res_y);

}


MyImageMap::MyImageMap( int w, int h ) : map( boost::extents[w][h] )
{
	width = w;
	height = h;
	InitGaussianMatrix(1100.0/250.0);
	this->img_type = ::Unknown;

	// Map Conversion data
	// TODO: In the future, this should be part of the map data itself. Include it in the header information.
	lat_deg = 110913.73;
	lon_deg = 92901.14;

	ox_deg = -118.8;
	oy_deg = 33.25;

	res = 100;	// 1 cell = 100 m

	res_x = res;
	res_y = res;

	res_lat = res_y / lat_deg;
	res_lon = res_x / lon_deg;

	    // These are values for the region we are interested in.
	lat_diff = 0.8833333;
	lon_diff = 1.1;

	max_lat_diff = lat_diff / res_lat;
	max_lon_diff = lon_diff / res_lon;

	max_y_diff = ceil( lat_diff * lat_deg / res_y);
}

MyImageMap::~MyImageMap() {
	// TODO Auto-generated destructor stub

}

// Open Risk Map
int MyImageMap::OpenMap( char *mapFileName, int *map1d, int &w, int &h )
{
	unsigned char img_type[10], temp_buf[10];
	int b;


	FILE *fp = fopen( mapFileName, "r" );
	if (fp == NULL)
		return 0;

	this->img_type = ::MapImg;

	fscanf( fp,"%s %d %d %d\n",img_type, &w, &h, &b );
	//map.resize(boost::extents[w][h]);

	for ( int i = 0, j=0,k=0; i<h; i++ ) {
		for (j=0;j<w;j++ ) {
			fread(temp_buf,1,sizeof(int),fp);
			this->map[j][i] =  *((int*)temp_buf);
			//this->map[i][j] = abs( *((int*)temp_buf) ); // This is what was done for risk-maps earlier!
			//map1d[k++] = this->map[i][j];
			map1d[k++] = this->map[j][i];
			cout<<map[j][i]<<" ";
		}
		cout<<endl;
	}
	fclose(fp);

	width = w;
	height = h;

	return 1;
}

int MyImageMap::OpenCommsMap(char *mapFileName, int *map1d, int &w, int &h )
{
	unsigned char img_type[10], temp_buf[10];
	int b;


	FILE *fp = fopen( mapFileName, "r" );
	if (fp == NULL)
		return 0;

	this->img_type = ::CommsMap;

	fscanf( fp,"%s %d %d %d %lf %lf %lf %lf %lf %lf %lf\n",img_type, &w, &h, &norm_val,
			&res, &ox_deg, &oy_deg, &lat_deg, &lon_deg, &lat_diff, &lon_diff );
	//map.resize(boost::extents[w][h]);
	for ( int i = 0, j=0,k=0; i<h; i++ ) {
		for (j=0;j<w;j++ ) {
			fread(temp_buf,1,sizeof(int),fp);
			this->map[j][i] =  *((int*)temp_buf);
			map1d[k++] = this->map[j][i];
		}
	}
	fclose(fp);

	width = w;
	height = h;

	return 1;
}


// Open PGM Map
int MyImageMap::OpenPgmMap(char *mapFileName, int *map1d, int &w, int &h )
{
	unsigned char img_type[10], temp_buf[10];
	int b;

	this->img_type = ::PgmImg;

	FILE *fp = fopen( mapFileName,"r");
	if( fp == NULL)
		return 0;

	fscanf(fp,"%s %d %d %d",img_type, &w,&h,&b);
	for( int i=0,j=0,k=0;i<h;i++) {
		for(j=0;j<w;j++) {
			fread(temp_buf,1,1,fp);
 			this->map[j][i] = temp_buf[0];
 			map1d[k++]=this->map[j][i];
		}
	}
	fclose(fp);

	width = w;
	height = h;

	return 1;
}


int MyImageMap::OpenMapGeneric(const char *mapFileName)
{
	int w,h;
	char imgType[20]; unsigned char temp_buf[20];

	// Map Conversion data
	// TODO: In the future, this should be part of the map data itself. Include it in the header information.
	lat_deg = 110913.73;
	lon_deg = 92901.14;

	ox_deg = -118.8;
	oy_deg = 33.25;

	res = 100;	// 1 cell = 100 m

	// Some more random initializations
	this->img_type = ::Unknown;
	InitGaussianMatrix(1100.0/250.0);


	FILE *fp = fopen( mapFileName, "r" );
	if (fp == NULL) {
		fprintf( stderr,"Error opening Map %s",mapFileName );
		exit(EXIT_FAILURE);
	}
	fscanf( fp,"%s",imgType);
	cout<<endl<<"Image Type="<<imgType<<endl;
	if( strncmp(imgType,"MAP9",4)==0 ) {
		fscanf( fp,"%d %d %lf", &w, &h, &norm_val );

	}
	else if( strncmp(imgType,"P5",2)==0 ) {
		fscanf( fp,"%d %d %lf", &w, &h, &norm_val );
		fclose(fp);
		return this->OpenPgmMapFileNameOnly( (char*) mapFileName );
	}
	else if( strncmp(imgType,"MAP5",4)==0 ) {
		fscanf( fp,"%d %d %lf %lf %lf %lf %lf %lf %lf %lf\n", &w, &h, &norm_val,
				&res, &ox_deg, &oy_deg, &lat_deg, &lon_deg, &lat_diff, &lon_diff );
		cout<<"Map Resolution ="<<res<<endl;
		cout<<"Width="<<w<<", Height="<<h<<", N.Val="<<norm_val<<
				", OxDeg="<<ox_deg<<", OyDeg="<<oy_deg<<", LatDeg="<<lat_deg<<", LonDeg="<<lon_deg<<
				", Lat_diff="<<lat_diff<<", Lon_diff="<<lon_diff<<endl;
	}
	else {
		fprintf( stderr,"Unknown Map Type in %s",mapFileName );
		exit(EXIT_FAILURE);
	}

	map.resize(boost::extents[w][h]);
	width = w;
	height = h;
	res_x = res;
	res_y = res;

	res_lat = res_y / lat_deg;
	res_lon = res_x / lon_deg;

	// These are values for the region we are interested in.
	lat_diff = 0.8833333;
	lon_diff = 1.1;

	max_lat_diff = lat_diff / res_lat;
	max_lon_diff = lon_diff / res_lon;

	max_y_diff = ceil( lat_diff * lat_deg / res_y);
	if(norm_val==0)
		norm_val = 1;

	for ( int i = 0, j=0,k=0; i<h; i++ ) {
		for (j=0;j<w;j++ ) {
			fread(temp_buf,1,sizeof(int),fp);
			this->map[j][i] =  (*((int*)temp_buf));
		}
		//cout<<endl;
	}
	fclose(fp);
	lastMaxVal = getMaxVal(true);
	lastMinVal = getMinVal(true);
}

int MyImageMap::OpenPgmMapFileNameOnly(char *mapFileName)
{
	unsigned char img_type[10], temp_buf[10];
	int b, w, h;

	this->img_type = ::PgmImg;

	FILE *fp = fopen( mapFileName,"r");
	if( fp == NULL)
		return 0;

	fscanf(fp,"%s %d %d %d",img_type, &w,&h,&b);
	map.resize(boost::extents[w][h]);
	for( int i=0,j=0,k=0;i<h;i++) {
		for(j=0;j<w;j++) {
			fread(temp_buf,1,1,fp);
			this->map[j][i] = temp_buf[0];
			//cout<<map[j][i]<<" ";
		}
	}
	fclose(fp);

	width = w;
	height = h;

	return 1;
}

int MyImageMap::WriteMap( char *mapFileName )
{
	unsigned char img_type[10], temp_buf[10];
	int b = 1e31;

	FILE *fp = fopen( mapFileName, "w" );

	if (fp == NULL)
		return 0;
	fprintf( fp,"MAP9 %d %d %d\n", this->width, this->height, b );

	for ( int i = 0, j=0; i<this->height; i++ ) {
		for (j=0;j<this->width;j++ ) {
			//int val = this->map[i][j];
			int val = this->map[j][i];
			memcpy(temp_buf,&val,sizeof(int));
			fwrite(temp_buf,1,sizeof(int),fp);
		}
	}
	fclose(fp);

	return 1;
}

int MyImageMap::WritePgm(char *mapFileName )
{
	unsigned char temp_buf[10];
	int b;

	FILE *fp = fopen( mapFileName, "w" );

	if (fp == NULL)
		return 0;

	fprintf( fp,"P5 %d %d %d\n",this->width , this->height, 255 );

	for ( int i = 0, j=0; i<height; i++ ) {
		for (j=0;j<width;j++ ) {
			//int val = this->map[i][j];
			int val = this->map[j][i];
			if( val > 255 ) val = 255;
			if( val < 0 ) val = 0;
			temp_buf[0] = val;
			//cout<<val<<" ";
			//this->map[j][i] = abs( *((int*)temp_buf) );
			fwrite(temp_buf,1,1,fp);
		}
		// cout<<endl;
	}
	fclose(fp);

	return 1;
}

#ifndef __linux__
#ifndef isnan
inline bool isnan(double x) {
    return x != x;
}
#endif
#endif

int MyImageMap::WriteCommsMap(char *mapFileName )
{
	unsigned char temp_buf[10];
	int b;

	FILE *fp = fopen( mapFileName, "w" );

	if( fp==NULL )
		return 0;

	fprintf( fp, "MAP5 %d %d %lf %lf %lf %lf %lf %lf %lf %lf\n", this->width, this->height,
			this->norm_val, this->res, this->ox_deg, this->oy_deg, this->lat_deg,
			this->lon_deg, this->lat_diff, this->lon_diff );
	for ( int i = 0, j=0; i<height; i++ ) {
			for (j=0;j<width;j++ ) {
				//int val = this->map[i][j];
				int val = this->map[j][i];
				memcpy(temp_buf,&val,sizeof(int));
				fwrite(temp_buf,1,sizeof(int),fp);
			}
		}
	fclose(fp);

	return 1;
}


double MyImageMap::getMaxVal(bool searchAgain=false)
{
	if( searchAgain == true || lastMaxVal == DBL_MIN ) {
		double MaxVal = GetValue(0,0);
		for (int x=0; x< this->width; x++ ) {
			for(int y=0;y<this->width;y++) {
				if(GetValue(x,y)>MaxVal)
					MaxVal=GetValue(x,y);
			}
		}
		this->lastMaxVal = MaxVal;
		cout<<endl<<"MaxVal="<<lastMaxVal;
	}

	return lastMaxVal;
}

double MyImageMap::getMinVal(bool searchAgain=false)
{
	if( searchAgain == true || lastMinVal == DBL_MAX ) {
		double MinVal=GetValue(0,0);
		for (int x=0; x< this->width; x++ ) {
			for(int y=0;y<this->width;y++) {
				if(GetValue(x,y)<MinVal)
					MinVal=GetValue(x,y);
			}
		}
		this->lastMinVal = MinVal;
		cout<<endl<<"MinVal="<<lastMinVal;
	}
	return this->lastMinVal;
}


double MyImageMap::GetValue( int x, int y )
{
	if( x < this->width && y < this->height && x>=0 && y>=0 )
		return this->map[x][y];
	else return 0;
}

void MyImageMap::SetValue( int x, int y, double val )
{
	if( x < this->width && y < this->height )
		this->map[x][y] = val;
}

//-------------------------------------------------------------------
//	Desc: A Function that creates a Gaussian Kernel based upon sigma.
//
//-------------------------------------------------------------------
int MyImageMap::InitGaussianMatrix( float sigma )
{
	int mat_size = int((2 * 3 * fabs(sigma)+1));
	if( mat_size % 2 == 0 )
		mat_size +=1;

	RWmatSize = mat_size;

	int mid = mat_size/2;

	//cout<<"Matrix size="<<mat_size<<"Mid="<<mid<<endl;

	double term;
	double two_sigma2 = 2 * sigma * sigma;
	double inv_two_pi_sigma2 = 1/(two_sigma2 * 3.1415926535);

	for( int i = 0 ; i < mat_size ; i++ ) {
		for( int j = 0 ; j< mat_size; j++ ) {
			term = exp( - ((mid-i)*(mid-i)+ (mid-j)*(mid-j))/(two_sigma2) ) * inv_two_pi_sigma2;
			RWMatrix[i][j]= term;
			//cout<<RWMatrix[i][j]<<",";
		}
		//cout<<endl;
	}
	return 1;
}

//---------------------------------------------------------------------------------
// Desc: Convolve the Image with the Gaussian and put the result in the output Img
//---------------------------------------------------------------------------------
int MyImageMap::ConvolveImageGaussian( MyImageMap &out, float gamma )
{
	out.SetSize( width, height );
	// We use the RWMatrix to convolve MyImageMap
	for(int i = 0 ; i < this->height ; i++ ) {
		for( int j = 0; j < this->width ; j++ ) {
				out.SetValue(j,i,this->GetRisk(j,i) * gamma );
			}
			cout<<"."; cout.flush();
		}

	return 1;
}

int MyImageMap::ScaleMapToPgm( MyImageMap &out, double low_lim, double high_lim )
{
	out.DuplicateHeader(*this);
	out.SetSize( width, height );
	//map.resize(boost::extents[width][height]);

	double dyn_range = abs(high_lim - low_lim);
	double scale = 255/dyn_range;
	double scaled_val = 0;

	// We are going to scale the low-lim to 0 and the high-lim to 255
	for(int i = 0 ; i < this->height ; i++ ) {
			for( int j = 0; j < this->width ; j++ ) {
					if( map[j][i] <= low_lim )
						scaled_val = 0;
					else
					if( map[j][i] >= high_lim )
							scaled_val = 255;
					else {
							scaled_val =  ( map[j][i] - low_lim ) * scale;
					}
					out.SetValue(j,i,  scaled_val  );
				}
				cout<<"."; cout.flush();
			}

	return 1;
}

int MyImageMap::ScaleMapToMap( MyImageMap &out, double low_lim, double high_lim, double lowClip, double highClip )
{
	out.DuplicateHeader(*this);
	out.SetSize( width, height );
	//map.resize(boost::extents[width][height]);

	double dyn_range = abs(high_lim - low_lim);
	double scale = (highClip-lowClip)/dyn_range;
	double scaled_val = 0;

	// We are going to scale the low-lim to 0 and the high-lim to 255
	for(int i = 0 ; i < this->height ; i++ ) {
			for( int j = 0; j < this->width ; j++ ) {
					if( map[j][i] <= low_lim )
						scaled_val = lowClip;
					else
					if( map[j][i] >= high_lim )
							scaled_val = highClip;
					else {
							scaled_val =  lowClip+( map[j][i] - low_lim ) * scale;
					}
					out.SetValue(j,i,  scaled_val  );
				}
				cout<<"."; cout.flush();
			}

	return 1;
}



int MyImageMap::getImg_type() const
{
    return img_type;
}

void MyImageMap::setImg_type(int img_type)
{
    this->img_type = img_type;
}

int MyImageMap::getHeight() const
{
    return height;
}

int MyImageMap::getWidth() const
{
    return width;
}

void MyImageMap::setHeight(int height)
{
    this->height = height;
}

void MyImageMap::setWidth(int width)
{
    this->width = width;
}

double MyImageMap::getLat_deg() const
{
    return lat_deg;
}

double MyImageMap::getLat_diff() const
{
    return lat_diff;
}

double MyImageMap::getLon_deg() const
{
    return lon_deg;
}

double MyImageMap::getLon_diff() const
{
    return lon_diff;
}

double MyImageMap::getMax_lat_diff() const
{
    return max_lat_diff;
}

double MyImageMap::getMax_lon_diff() const
{
    return max_lon_diff;
}

double MyImageMap::getMax_y_diff() const
{
    return max_y_diff;
}

double MyImageMap::getNorm_val() const
{
    return norm_val;
}

double MyImageMap::getOx_deg() const
{
    return ox_deg;
}

double MyImageMap::getOy_deg() const
{
    return oy_deg;
}

double MyImageMap::getRes() const
{
    return res;
}

double MyImageMap::getRes_lat() const
{
    return res_lat;
}

double MyImageMap::getRes_lon() const
{
    return res_lon;
}

double MyImageMap::getRes_x() const
{
    return res_x;
}

double MyImageMap::getRes_y() const
{
    return res_y;
}

void MyImageMap::setLat_deg(double lat_deg)
{
    this->lat_deg = lat_deg;
}

void MyImageMap::setLat_diff(double lat_diff)
{
    this->lat_diff = lat_diff;
}

void MyImageMap::setLon_deg(double lon_deg)
{
    this->lon_deg = lon_deg;
}

void MyImageMap::setLon_diff(double lon_diff)
{
    this->lon_diff = lon_diff;
}

void MyImageMap::setMax_lat_diff(double max_lat_diff)
{
    this->max_lat_diff = max_lat_diff;
}

void MyImageMap::setMax_lon_diff(double max_lon_diff)
{
    this->max_lon_diff = max_lon_diff;
}

void MyImageMap::setMax_y_diff(double max_y_diff)
{
    this->max_y_diff = max_y_diff;
}

void MyImageMap::setNorm_val(int norm_val)
{
    this->norm_val = norm_val;
}

void MyImageMap::setOx_deg(double ox_deg)
{
    this->ox_deg = ox_deg;
}

void MyImageMap::setOy_deg(double oy_deg)
{
    this->oy_deg = oy_deg;
}

void MyImageMap::setRes(double res)
{
    this->res = res;
}

void MyImageMap::setRes_lat(double res_lat)
{
    this->res_lat = res_lat;
}

void MyImageMap::setRes_lon(double res_lon)
{
    this->res_lon = res_lon;
}

void MyImageMap::setRes_x(double res_x)
{
    this->res_x = res_x;
}

void MyImageMap::setRes_y(double res_y)
{
    this->res_y = res_y;
}

void MyImageMap::setMaxVal(double maxVal)
{
	this->lastMaxVal = maxVal;
}

void MyImageMap::setMinVal(double minVal)
{
	this->lastMinVal = minVal;
}


// ------ Private function ------
double MyImageMap::GetRisk( int a, int b )
{
	int mid = RWmatSize/2;

	double tempRisk= 0, tot_div = 0,  tempMaxRisk = 0;
	// We Convolve the RWMatrix with the risks at the given location

	int i,j, x, y;
	for(  i = a-mid, x=0; x<RWmatSize ; i++, x++ ) {
			for (  j = b-mid, y=0 ; y<RWmatSize ; j++, y++ ) {
				if( i >= 0 && j >= 0 && i < this->width  && j<this->height ) {
					// Only consider cells on the map
					tempRisk+=map[i][j]*RWMatrix[x][y];
					tot_div +=RWMatrix[x][y];
					//cout<<endl<<a<<","<<b<<","<<i<<","<<j<<","<<x<<","<<y
						//	<<","<<tempRisk<<","<<map[i][j]<<","<<RWMatrix[x][y];
					if( tempMaxRisk < tempRisk )
						tempMaxRisk = tempRisk;
				}
			}
		}

	// This might be a big bug in my code so far!!!
	//if( tot_div > 0 ) {
	//	tempRisk = tempRisk/tot_div;
	//}
	/*if( risk[a][b] != tempRisk ) {
		cout<<"Risk(a,b)="<<risk[a][b]<<"GetRisk(a,b)="<<tempRisk<<"MaxRisk(a,b)="<<tempMaxRisk<<endl;
	}*/

	return tempRisk;
}

void MyImageMap::SetSize( int w, int h)
{
	width = w;
	height = h;
	try {
	map.resize(boost::extents[width][height]);
	}
	catch(...)
	{	cerr<<"Error setting Image size!";
	}
}

bool MyImageMap::ExtendBordersOutByNpixels(unsigned n)
{
	int temp_width = this->width + 2*n;
	int temp_height= this->height+ 2*n;
	array2D tempImage;
	try{	tempImage.resize(boost::extents[temp_width][temp_height]);	}
	catch(...)	{	cerr<<"Error creating temporary Image.";	}
	// Copy the image into the temporary image first.
	for (int j=0; j<this->height; j++ ) {
		for( int i=0; i<this->width; i++ ) {
			tempImage[i+n][j+n] = map[i][j];
		}
	}
	// Now let us replicate the rows outward...
	for( int y1=n, y2=this->height+n-1; y1>=0; y1--, y2++ ) {
		for (int x=0; x<this->width; x++ ) {
			tempImage[x+n][y1]=map[x][1];
			tempImage[x+n][y2]=map[x][this->height-1];
		}
	}
	// Now we replicate the columns outward...
	for( int x1 = n, x2=this->width+n-1; x2 < temp_width; x1--, x2++ ) {
		for( int y = 0; y<temp_height; y++ ) {
			tempImage[x1][y]=tempImage[n][y];
			tempImage[x2][y]=tempImage[width+n-1][y];
		}
	}
	// Now we resize map to the same size as the temporary image and copy the contents.
	try{	map.resize(boost::extents[temp_width][temp_height]);	}
	catch(...)	{	cerr<<"Error resizing Image.";	}
	map=tempImage;
	this->width = temp_width;
	this->height = temp_height;

	return true;
}

bool MyImageMap::ExtendBordersOutByReflectingNpixels(unsigned n)
{
	int temp_width = this->width + 2*n;
	int temp_height= this->height+ 2*n;
	array2D tempImage;
	try{	tempImage.resize(boost::extents[temp_width][temp_height]);	}
	catch(...)	{	cerr<<"Error creating temporary Image.";	}
	// Copy the image into the temporary image first.
	for (int j=0; j<this->height; j++ ) {
		for( int i=0; i<this->width; i++ ) {
			tempImage[i+n][j+n] = map[i][j];
		}
	}
	// Now let us replicate the rows outward...
	for( int y1=n, y2=this->height+n-1,y3 = 0; y1>=0; y1--, y2++,y3++ ) {
		for (int x=0; x<this->width; x++ ) {
			tempImage[x+n][y1]=map[x][y3];
			tempImage[x+n][y2]=map[x][this->height-1-y3];
		}
	}
	// Now we replicate the columns outward...
	for( int x1 = n, x2=this->width+n-1,x3=0; x2 < temp_width; x1--, x2++,x3++ ) {
		for( int y = 0; y<temp_height; y++ ) {
			tempImage[x1][y]=tempImage[n+x3][y];
			tempImage[x2][y]=tempImage[width+n-1-x3][y];
		}
	}
	// Now we resize map to the same size as the temporary image and copy the contents.
	try{	map.resize(boost::extents[temp_width][temp_height]);	}
	catch(...)	{	cerr<<"Error resizing Image.";	}
	map=tempImage;
	this->width = temp_width;
	this->height = temp_height;

	return true;
}


void MyImageMap::MapXYToLatLon( const double x, const double y, double &lat, double &lon  )
{
	  lat = ( (max_y_diff - y) * res_lat ) + oy_deg;
	  lon = ( x * res_lon ) + ox_deg;
}

void MyImageMap::LatLonToMapXY(const double lat, const double lon, double &x, double &y )
{
	x = ( lon - ox_deg ) / res_lon;
	y = max_y_diff - ( lat - oy_deg ) / res_lat;
}

/*
 * When the map is re-sized, it re-samples the map.
 */
void MyImageMap::ReSampleMapXY( MyImageMap &out, int h, int w )
{
	if( h<=0 ) throw OutOfRange("Height Out of Range.");
	if( w<=0 ) throw OutOfRange("Width Out of Range.");

	float ratio_x = this->width/double(w);
	float ratio_y = this->height/double(h);

	out.DuplicateHeader(*this);
	out.SetSize(h,w);
	out.setRes(this->res/(double(w)/this->width));
	out.setRes_x(this->res_x/(double(w)/this->width));
	out.setRes_y(this->res_y/(double(h)/this->height));


		for(int i=0; i< h; i++ ) {
			for(int j=0; j<w; j++ ) {
					// Compute the value of this location from the nearest values in the original image
					float x = (j+0.5) * ratio_x;
					float y = (i+0.5) * ratio_y;
					float x1 = floor(j * ratio_x), x2 = floor((j+1)*ratio_x), y1 = floor(i * ratio_y), y2 = floor((i+1)*ratio_y);
					float Q11 = this->GetValue(x1,y2), Q12 = this->GetValue(x1,y1), Q22 = this->GetValue(x2,y1), Q21 = this->GetValue(x2,y2);
					// Use Bilinear Interpolation (See http://en.wikipedia.org/wiki/Bilinear_interpolation )
					if( x1 != x2 && y1 != y2 ) {
						double val = Q11 * (x2-x) *(y2-y)/((x2-x1)*(y2-y1)) + Q21 * (x-x1)*(y2-y)/((x2-x1)*(y2-y1)) +
							Q12 *(x2-x)*(y-y1)/((x2-x1)*(y2-y1)) + Q22*(x-x1)*(y-y1)/((x2-x1)*(y2-y1));
						out.SetValue(j,i,val);
					}
					else {
						out.SetValue(j,i,this->GetValue(x,y));
					}
				}
				cout<<".";
			}
		cout<<endl;
}
