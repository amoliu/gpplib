/*
 * MyImageMap.h
 *
 *  Created on: Mar 16, 2011
 *      Author: arvind
 */
//#include <boost/python.hpp>
#include <boost/multi_array.hpp>
#include <stdio.h>
#include <iostream>
#include <cmath>
#include <string>
#include <cstdlib>
#include <boost/python.hpp>

using namespace std;

#ifndef MAX_DIMS
#define MAX_DIMS 1200
#endif

#ifndef MYIMAGEMAP_H_
#define MYIMAGEMAP_H_

enum ImgType { MapImg, PgmImg, CommsMap, BathyMap, Unknown, MDPUtility };

class MyImageMap {
protected:
	typedef boost::multi_array<double, 2> array2D;
	array2D map;
	float RWMatrix[200][200];
	int RWmatSize;
	int width;
	int height;
	int img_type;

	// Some Map Conversion variables
	double norm_val;
	double res;
	double lat_deg;
	double lon_deg;
	double ox_deg;
	double oy_deg;
	double res_x;
	double res_y;
	double res_lat;
	double res_lon;
	double lat_diff;
	double lon_diff;
	double max_lat_diff;
	double max_lon_diff;
	double max_y_diff;
	double lastMaxVal;
	double lastMinVal;

public:
	MyImageMap();
	MyImageMap(char *mapFileName);
	MyImageMap(int w, int h);
	virtual ~MyImageMap();

	void DuplicateHeader( MyImageMap m );
	int OpenMap( char *mapFileName, int *map, int &w, int &h );
	int OpenPgmMap( char *mapFileName, int *map, int &w, int &h );
	int OpenCommsMap( char *mapFileName, int *map, int &w, int &h );
	int OpenMapGeneric(const char *mapFileName);
	int OpenPgmMapFileNameOnly(char *mapFileName);

	double GetValue( int x, int y );
	void SetValue( int x, int y, double val );
	void SetSize( int w, int h);
    int  InitGaussianMatrix( float sigma );
    int ConvolveImageGaussian( MyImageMap &out, float );
    int ScaleMapToPgm( MyImageMap &out, double low_lim, double high_lim );
    int ScaleMapToMap( MyImageMap &out, double low_lim,
    		double high_lim, double lowClip, double highClip );
    int WriteMap(char *mapFileName );
    int WritePgm(char *mapFileName );
    int WriteCommsMap(char *mapFileName );
    int getImg_type() const;
    void setImg_type(int img_type);
    int getHeight() const;
    int getWidth() const;
    void setHeight(int height);
    void setWidth(int width);
    // Assignment
    MyImageMap& operator=(MyImageMap &map2);

    // Map Co-od transformation methods
    void LatLonToMapXY(const double lat, const double lon, double &x, double &y );
    void MapXYToLatLon( const double x, const double y, double &lat, double &lon );
    double getLat_deg() const;
    double getLat_diff() const;
    double getLon_deg() const;
    double getLon_diff() const;
    double getMax_lat_diff() const;
    double getMax_lon_diff() const;
    double getMax_y_diff() const;
    double getNorm_val() const;
    double getOx_deg() const;
    double getOy_deg() const;
    double getRes() const;
    double getRes_lat() const;
    double getRes_lon() const;
    double getRes_x() const;
    double getRes_y() const;
    void setLat_deg(double lat_deg);
    void setLat_diff(double lat_diff);
    void setLon_deg(double lon_deg);
    void setLon_diff(double lon_diff);
    void setMax_lat_diff(double max_lat_diff);
    void setMax_lon_diff(double max_lon_diff);
    void setMax_y_diff(double max_y_diff);
    void setNorm_val(int norm_val);
    void setOx_deg(double ox_deg);
    void setOy_deg(double oy_deg);
    void setRes(double res);
    void setRes_lat(double res_lat);
    void setRes_lon(double res_lon);
    void setRes_x(double res_x);
    void setRes_y(double res_y);
    void ReSampleMapXY( MyImageMap &out, int h, int w );
    double getMaxVal(bool searchAgain );
    double getMinVal(bool searchAgain );
    void setMaxVal(double maxVal);
    void setMinVal(double minVal);
    bool ExtendBordersOutByNpixels(unsigned n);
    bool ExtendBordersOutByReflectingNpixels(unsigned n);
    bool setArray(array2D mapArray);
    array2D getArray();
protected:
    double GetRisk( int a, int b );

};

struct OutOfRange
{
	string desc;
	OutOfRange(string e) { this->desc=e; }
	OutOfRange() {}
};

#endif /* MYIMAGEMAP_H_ */
