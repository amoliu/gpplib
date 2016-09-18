/*
 * GetCommsMap.cpp
 *
 * This program pre-computes and stores the comms-map for communication in a given region.
 * Some of the salient features of this are that it is:
 * 1. Capable of
 *  Created on: Apr 21, 2011
 *      Author: arvind
 */

#include "MyImageMap.h"
#include "Waypoint.h"
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <cmath>

using namespace std;

std::vector<Waypoint> bs_list;
const int MAX_SIZE = 1200;
int w1= MAX_SIZE,h1 = MAX_SIZE, w2, h2;

int *map;
MyImageMap *cmap;
MyImageMap *bathy;

int map_res = 100;

void InitializeBaseStations( MyImageMap &m )
{

	double bs_catalina_lon = -118.47815, bs_catalina_lat = 33.446742, bs_catalina_x, bs_catalina_y; //  33.446742, -118.478150
	double bs_ptfermin_lon = -118.294006, bs_ptfermin_lat = 33.704898, bs_ptfermin_x, bs_ptfermin_y;
	double bs_oil_plat_lon = -118.129778, bs_oil_plat_lat = 33.581496, bs_oil_plat_x, bs_oil_plat_y;
	double bs_redondo_lon = -118.3979, bs_redondo_lat = 33.857005, bs_redondo_x, bs_redondo_y;
	double bs_dockweiler_lon = -118.442375, bs_dockweiler_lat =  33.943291, bs_dockweiler_x, bs_dockweiler_y;
	double bs_newport_lon = -117.958950, bs_newport_lat = 33.635207, bs_newport_x, bs_newport_y;
	double bs_newport_pier_lon = -117.931404, bs_newport_pier_lat =  33.605912, bs_newport_pier_x, bs_newport_pier_y;
	double bs_mdelray_lat = 33.981464, bs_mdelray_lon = -118.441586, bs_mdelray_x, bs_mdelray_y;
	double bs_malibu_lat =  34.033223, bs_malibu_lon = -118.733722, bs_malibu_x, bs_malibu_y;

	m.LatLonToMapXY(bs_catalina_lat,bs_catalina_lon, bs_catalina_x, bs_catalina_y );
	m.LatLonToMapXY(bs_ptfermin_lat,bs_ptfermin_lon, bs_ptfermin_x, bs_ptfermin_y );
	m.LatLonToMapXY(bs_oil_plat_lat,bs_oil_plat_lon, bs_oil_plat_x, bs_oil_plat_y );
	m.LatLonToMapXY(bs_redondo_lat,bs_redondo_lon, bs_redondo_x, bs_redondo_y );
	m.LatLonToMapXY(bs_dockweiler_lat,bs_dockweiler_lon, bs_dockweiler_x, bs_dockweiler_y );
	m.LatLonToMapXY(bs_newport_lat,bs_newport_lon, bs_newport_x, bs_newport_y );
	m.LatLonToMapXY(bs_newport_pier_lat,bs_newport_pier_lon, bs_newport_pier_x, bs_newport_pier_y );
	m.LatLonToMapXY(bs_mdelray_lat, bs_mdelray_lon, bs_mdelray_x, bs_mdelray_y);
	m.LatLonToMapXY(bs_malibu_lat, bs_malibu_lon, bs_malibu_x, bs_malibu_y);

	Waypoint bs_catalina(bs_catalina_x,bs_catalina_y); bs_catalina.setHeight(70);
	Waypoint bs_ptfermin(bs_ptfermin_x,bs_ptfermin_y); bs_ptfermin.setHeight(36);
	Waypoint bs_oil_plat(bs_oil_plat_x,bs_oil_plat_y); bs_oil_plat.setHeight(15);
	Waypoint bs_redondo(bs_redondo_x,bs_redondo_y);		bs_redondo.setHeight(25);
	Waypoint bs_dockweiler(bs_dockweiler_x,bs_dockweiler_y);	bs_dockweiler.setHeight(10);
	Waypoint bs_newport(bs_newport_x,bs_newport_y);				bs_newport.setHeight(10);
	Waypoint bs_newport_pier(bs_newport_pier_x,bs_newport_pier_y); bs_newport_pier.setHeight(7);
	Waypoint bs_mdelray(bs_mdelray_x,bs_mdelray_y);	bs_mdelray.setHeight(25);
	Waypoint bs_malibu(bs_malibu_x, bs_malibu_y);	bs_malibu.setHeight(10);

	bs_list.push_back(bs_catalina);
	bs_list.push_back(bs_ptfermin);
	bs_list.push_back(bs_oil_plat);
	bs_list.push_back(bs_redondo);
	bs_list.push_back(bs_dockweiler);
	bs_list.push_back(bs_newport_pier);
	bs_list.push_back(bs_newport);
	bs_list.push_back(bs_mdelray);
	bs_list.push_back(bs_malibu);

}

double getDist(double x1, double y1, double x2, double y2 )
{
	return sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1));
}

float GetDist( Waypoint &a, Waypoint &b )
{
	return (sqrt(pow(double(a.getPathx() - b.getPathx()),2) + pow(double(a.getPathy()-b.getPathy()),2)));
}

/*
 * Reference => "Map Projections - A Working Manual", John P. Snyder,
 * US Geological Survey Professional Paper 1395,
 * US Gov. Printing Office, Washington DC, 1987
 */

double GetEarthsRadius(double lat)
{
	double a = 6378e3;		// Earth's equatorial radius
	double e = 0.081082;	// Earth's Eccentricity
	double b = 6357e3;		// Earth's polar radius

	e = sqrt( 1 - (b*b)/(a*a));

	double R = a*(1-e*e)/(1-e*e*sin(lat)*sin(lat));
	double N = a/sqrt(1-e*e*sin(lat)*sin(lat));

	cout.precision(8);
	cout<<"The Earth's Radius at "<<lat<<" degrees is :"<<R<<endl;

	return R;
}

double GetCommRange_UsingBathy( MyImageMap bathy, const Waypoint bs, const Waypoint gLoc )
{
	double bs_height = bs.getHeight(); //bathy.GetValue(bs.getPathx(), bs.getPathy()) + 3; // bathy.map[bs.pathx][bs.pathy];
	double gLoc_height = bathy.GetValue(gLoc.getPathx(), gLoc.getPathy()); //map[gLoc.pathx][gLoc.pathy];

	double R = 6375142.6;	// The Earth's Radius at 33.25 degrees is :6375142.6

	double dist_bs = sqrt(2* R* bs_height + bs_height*bs_height);

	return dist_bs;
}

// | a b |
// | c d |
double GetDet2d( double a, double b, double c, double d )
{
	return (a*d-b*c);
}

bool LinSolve2d( double a1, double a2, double b1, double b2, double c1, double c2, double &x, double &y )
{
	// Here the equations being solved are:
	// a1 x + b1 y = c1
	// a2 x + b2 y = c2
	// We are solving this using Cramers rule
	// If there is a solution, this is returned in x and y, with a return value of true
	// If there is no solution, we return false

	double det = GetDet2d(a1,b1,a2,b2);
	double y_det = GetDet2d(a1,c1,a2,c2);
	double x_det = GetDet2d(c1,b1,c2,b2);

	if( det == 0 )
		return false;
	else {
		x = x_det/det;
		y = y_det/det;
		return true;
	}
}

// This function returns true if the path being tested has LOS with the desired location
// We provide it with the base-station height, location height
// Distance of distance of location = d1, distance of glider = d2
// returns false if there is no LOS
bool ObstacleIsTaller( double bs_h, double loc_h, double d1, double d2 )
{
	// d1 is the distance to the obstacle
	// d2 is the distance to the glider
	double R = 6375142.6;

	double a1,a2,b1,b2,c1,c2;

	a1 = 1.0/tan(d1/R);	// Equation 17 in ISRR paper
	b1 = -1;
	c1 = 0;
	a2 = ((R+0.3)*cos( d2/R )-(R+bs_h))/((R+0.3)*sin(d2/R));
	b2 = -1;
	c2 = -(R+bs_h);

	double x3,y3;
	if( LinSolve2d( a1, a2, b1,b2, c1,c2,x3,y3) ) {
		double x2 = R*sin(d1/R), y2 = R*cos(d1/R);
		double obs_h = getDist(x3, y3, x2, y2 );
		//cout<<"d1 ="<<d1<<", d2="<<d2;
		//cout<<"obs_h="<<obs_h<<", loc_h="<<loc_h<<"(x2,y2)="<<"("<<x2<<","<<y2<<")"<<", "<<"(x3,y3)="<<"("<<x3<<","<<y3<<")"<<endl;
		if( obs_h < loc_h )	// Obstacle height is more!!!! Cannot communicate!!!
		{
				//cout<<endl<<"Obstacle is taller, cannot communicate."<<endl;
				return true;
		}
		else if( x3<x2 && y3<y2 ) {
				//cout<<endl<<"Hit Horizon, cannot communicate."<<endl;
				return true;
		}
		else {
			//cout<<endl<<"Obstacle is shorter, and didn't hit horizon, so can communicate."<<endl;
			return false;
		}
	}
	else {
		cout<<"Error LinSolving..."<<endl;
		return true;
	}

}



bool HasNoLOS( const Waypoint bs, const Waypoint gLoc )
{
	// we are using the perp-dist between each point we are testing for
	// and this location on the line to determine collisions.
	int x1 = bs.getPathx(), x2 = gLoc.getPathx(), y1 = bs.getPathy(), y2 = gLoc.getPathy();

	//if( x2 == x1 && y2 == y1 )
	//	return GetObs(x1,y1);

	double bs_h = bathy->GetValue(x1,y1) + 3;
	//if( bs_h < 50 )
	//	bs_h = 50;
	// When the base-station is shorter than 70 m, let us set it to 70 m to emulate Catalina

	double loc_h;
	double d2 = getDist(bs.getPathx(), bs.getPathy(), gLoc.getPathx(), gLoc.getPathy()) * map_res;

	int sx, sy, ex, ey;
	if( x1 < x2 ) {	sx = x1; ex = x2; } else { sx = x2; ex = x1; }
	if( y1 < y2 ) { sy = y1; ey = y2; } else { sy = y2; ey = y1; }
	if( x1 != x2 ) {
		float  m1 = (y2-y1)/(x2-x1);
		for( int x = sx; x < ex ; x++ )  {
			int y = m1*(x-x1) + y1;
				loc_h = bathy->GetValue(x,y);
				double d1 = getDist(x,y,bs.getPathx(),bs.getPathy()) * map_res;
				// Now for this location and height, test if we can communicate with the glider
				// successfully, given there might be obstacles along the way...

				//if( GetObs(x,y,rad) )
				if( ObstacleIsTaller( bs_h, loc_h, d1, d2 ) )
					return true;
		}
	}
	if( y1 != y2) { // Line has better range vertically
		float m2 = (x2 - x1)/(y2 - y1);
		for( int y = sy; y < ey; y++ ) {
			int x = m2 * (y - y1) + x1;
			loc_h = bathy->GetValue(x,y);
			double d1 = getDist(x,y,bs.getPathx(),bs.getPathy()) * map_res;
			//if( GetObs(x,y,rad) )
			if( ObstacleIsTaller( bs_h, loc_h, d1, d2 ) )
				return true;
		}
	}

	return false;	// Nothing collided! We could communicate!!!
}


// Tests if the current location has line-of-sight with a base-station
double GetMaxRateIfHasLOS( int x, int y )
{
	Waypoint g(x,y);
	// For each base-station
	// 	For each location between the current location and the base-station
	//		Test if we are blocked along the way to this base-station
	double comm_rate = 0;
	double R = 6375142.6;

	for( int i=0; i< bs_list.size(); i++ ) {
		double range = GetDist( g, bs_list[i] ) * map_res;	// Distance in meters to the base-station. Also the length of the arc.
		// Test all locations in between me and the base-station
		// Equation of line joining this and base-station is:
		if( !HasNoLOS(bs_list[i],g) ) { 	// If the base-station has LOS, then compute the rate
			double temp_comm_rate = 0;
			// if( range < 15e3 && range > 2e3 )
				temp_comm_rate = -6.5e-12 *pow(range,3) + 2.2e-7 * pow(range,2) -0.0024*range + 9.4;
			if( range < 2e3 )
				temp_comm_rate = 5.5;
			double bs_h = bs_list[i].getHeight();
			double dist_bs = sqrt(2* R* bs_h + bs_h*bs_h);
			if( range > dist_bs )	// Out of range!!!
				temp_comm_rate = 0.24;

			if( temp_comm_rate < 0.24 )
				temp_comm_rate = 0.24;
			if( temp_comm_rate > 5.5 )
				temp_comm_rate = 5.5;

			if( temp_comm_rate > comm_rate ) {
				comm_rate = temp_comm_rate;
			}
		}
		//cout<<".";
	}
	if( comm_rate > 5.5 )
		comm_rate = 5.5;
	if( comm_rate <= 0 )
		comm_rate = 0.24;

	// cout<<comm_rate<<"  ";

	return	comm_rate;
}

void CreateCommsMap()
{
	//cout<<"cmap height, width ="<<cmap->getHeight()<<", "<<cmap->getWidth()<<endl; exit(EXIT_FAILURE);

	for ( int i = 0, j=0; i<cmap->getHeight(); i++ ) {
			for (j=0;j<cmap->getWidth(); j++ ) {
				//cmap->SetValue(j,i,(1e3/GetMaxRateIfHasLOS(j, i)));
				//cmap.SetValue(j,i,(1e3/GetCommRate( bathy, j, i )/cmap.getNorm_val() * 255));
				cmap->SetValue(j,i,int(1e3/GetMaxRateIfHasLOS( j, i )));
			}
			cout<<"."; cout.flush();
		}
}



double GetCommRate( int x, int y )
{
	Waypoint cur_loc(x,y);

	double range = 16e3;
	double R = 6375142.6;
	double comm_rate = 0, temp_comm_rate = 0;

	for ( int i = 0 ; i < bs_list.size(); i++ ) {
		double temp_range = GetDist(cur_loc,bs_list[i]) * map_res;
		if( temp_range < 2e3 )
			temp_comm_rate = 5.5;
		else
		if( temp_range < range ) {
			range = temp_range;
			temp_comm_rate = 2; //temp_comm_rate = -6.5e-12 * pow(range,3) + 2.2e-7 * pow(range,2) -0.0024*range + 9.4;
		}
		else {
			temp_comm_rate = 0;
		}
		if( temp_comm_rate > comm_rate ) {
			comm_rate = temp_comm_rate;
		}
	}

	//if( range > 12e3 )
	//		comm_rate = 0;

	if( comm_rate > 0)
		cout<<"Commrate="<<comm_rate<<endl;

	if( comm_rate <= 0 )
		return 0.25;

	else if( comm_rate > 5.5 )
		return 5.5;
	else
		return comm_rate;
}


/*
void ExtractOptArgs(int argc, float & sigma, char *argv[], float & gamma, float & obs_max_val)
{
    if(argc > 4)
        sigma = atof(argv[4]);

    if(sigma < 0)
        sigma = 4.4; // The default value 1100/250.

    if(argc > 5)
        gamma = fabs(atof(argv[5]));

    if(argc > 6)
        obs_max_val = fabs(atof(argv[6]));

}
*/


void print_usage(char *argv[])
{
	cout<<endl<<"Usage: "<<argv[0]<<" [comms_map.map] [bathy_map.map] [obs-max-val]";
	cout<<endl<<"Where: comms_map.map is the map file we want.";
	cout<<endl<<"And  : bathy_map.map is the map file containing the bathymetry of the region";
	cout<<endl<<"And  : obs-max-val is the value to be used as an obstacle from the bathy_map.map. Default=1e3";
	cout<<endl<<endl;
}

int main(int argc, char *argv[])
{
	// Initialize all the Base-stations
	cmap = new MyImageMap(MAX_SIZE, MAX_SIZE);
	//bathy = new MyImageMap(MAX_SIZE, MAX_SIZE);
	map = new int[ MAX_SIZE * MAX_SIZE ];


	if( argc<2 || argc> 4  ) { print_usage( argv ); exit(EXIT_FAILURE); }

	if( argc <= 3 ) {
			bathy = new MyImageMap(argv[2]);
			/*
			if( bathy->OpenMap(argv[2],map,w2,h2) ) {
			}
			else {
				cout<<endl<<"Unable to open "<<argv[2]<<" bathymetric map. Quitting..."<<endl<<endl<<endl;
				exit(EXIT_FAILURE);
			}*/
	}

	// Allocations

	cmap->setWidth(bathy->getWidth());  // cmap->setWidth(1022);
	cmap->setHeight(bathy->getHeight()); // cmap->setHeight(980);
	cmap->setImg_type( ::CommsMap );
	cmap->DuplicateHeader(*bathy);
	map_res = cmap->getRes();
	InitializeBaseStations( *cmap );

	CreateCommsMap();

	cmap->WriteCommsMap( argv[1] );

	double x,y;
	//if( LinSolve2d( 5,4 ,2 ,-8 ,4 ,6 , x, y ) )
	//if( LinSolve2d( 1,1 ,1 ,-1 ,2 ,3 , x, y ) )
	//	cout<<"x="<<x<<", y="<<y<<endl;
	GetEarthsRadius(33.25);

	//cout<<endl<<"Points behind Catalina."<<GetMaxRateIfHasLOS(250,827)<<", "<<GetMaxRateIfHasLOS(257,833);
	//cout<<endl<<"Points in front of Base station "<<GetMaxRateIfHasLOS(346,730)<<","<<GetMaxRateIfHasLOS(333,726);
	//cout<<endl<<"Points near Avalon and under Catalina "<<GetMaxRateIfHasLOS(389,933)<<","<<GetMaxRateIfHasLOS(471,922);
	//cout<<endl;

	// Be polite!
	cout<<endl<<endl;

	return EXIT_SUCCESS;
}
