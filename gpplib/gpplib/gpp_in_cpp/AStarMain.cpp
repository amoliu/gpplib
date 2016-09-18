/*
 * AStarMain.cpp
 *
 *  Created on: Mar 3, 2011
 *  Author: Arvind Antonio de Menezes Pereira
 */
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <cstring>
#include <cstdlib>
#include "aStarLibrary.h"	// AStar Class
#include "MyImageMap.h"		// Map Class

using namespace std;
#define MAX_DIMS 1200


void PrintUsage(char *prgName)
{
	cout<<"Usage :"<<endl<<"./aStar [risk_map.map] [bathy_map.pgm] [startx] [starty] [targetx] [targety] [mode] [d_max] [eps] [gamma] [comms_map.map]"<<
			endl<<"Where:"<<endl<<"mode can be"<<endl<<"0: shortest path with greedy-subset"<<endl<<
					"1: shortest risk-path with greedy-subset search = 1"<<endl<<
					"2: shortest risk-path with a data-buffer limit > 1"<<endl<<
					"3: minimum (communication_cost * risk) path with a fixed amount of data to be transferred at each surfacing"<<endl<<
					"4: minimum (communication_cost * risk) path with amount of data transferred proportional to distance from previous surfacing."<<endl<<
					"d_max is the maximum distance (in terms of cell distances) between consecutive surfacings. defaults to 1"<<endl<<
					"eps is the minimum risk-value. defaults to 1"<<endl<<
					"gamma is the weighting factor between 0 and 1"<<endl<<
					"comms_map.map is the name of the communication map. defaults to comms_map.map"<<endl<<endl;
}

/*
	Program that runs the A-Star code.
	Here we specify the mode for the code via command line arguments.
	Usage: ./aStar [risk_map.map] [bathy_map.pgm] [startx] [starty] [targetx] [targety] [mode] [d_max] [eps]
	Where:
		mode can be 0: shortest path
					1: shortest risk-path
*/
int main( char argc, char *argv[] )
{
	int w=maxMapWidth, h=maxMapHeight, rw, rh, cw, ch;

	int *map = new int[MAX_DIMS*MAX_DIMS];
	int *risk = new int[MAX_DIMS * MAX_DIMS];
	int *comms_map = new int[MAX_DIMS * MAX_DIMS];
	float gamma_val = 1;
	MyImageMap *riskMap= new MyImageMap(MAX_DIMS,MAX_DIMS);
	MyImageMap *bathyMap= new MyImageMap(MAX_DIMS, MAX_DIMS);

	//riskMap->OpenMap( "risk_map100.map", risk, rw, rh );
	//bathyMap->OpenPgmMap("binarized_bathy100.pgm", map, w, h );
	// MyImageMap *commMap = new MyImageMap( 1200, 1200 );


	int argnum = 0;
	if( argc <7 || argc > 12 ) {
		PrintUsage(argv[argnum]); exit(EXIT_FAILURE);
	}
	argnum++;

	string rmap = argv[argnum++];
	string bmap = argv[argnum++];

	if( strstr((char*)rmap.c_str(),".map")== 0) {
		cout<<endl<<rmap<<" is not a risk map!"; exit(EXIT_FAILURE);
	}

	if( strstr((char*)bmap.c_str(),".pgm") == 0) {
		cout<<endl<<bmap<<" is not a binarized bathy map!"; exit(EXIT_FAILURE);
	}

	riskMap->OpenMap((char *)rmap.c_str(),risk ,rw,rh );
	riskMap->OpenPgmMap((char *)bmap.c_str(),map,w,h);

	if( rw!=w || rh != h ) {
		cout<<endl<<"Map Sizes don't match. Please find Maps with the same size!"; exit(EXIT_FAILURE);
	}

	int sx = atoi(argv[argnum++]),sy= atoi(argv[argnum++]) ,ex = atoi(argv[argnum++]),ey = atoi(argv[argnum++]);

	//OpenRiskMap("risk_map.map",risk ,rw,rh );
	//OpenPgmMap("binarized_bathy.pgm",map,w,h);
	int d_max = 1, eps = 1, mode = 0;

	if( argc > 7 ) { mode = atoi(argv[argnum++]); }
	if( argc > 8 ) { d_max = atoi(argv[argnum++]); }
	if(argc > 9 )	{ eps = atoi(argv[argnum++]); }
	if(argc > 10 ) { gamma_val = atof(argv[argnum++]); }

	AStar *a = new AStar(map, w, h, risk, rw, rh, eps, d_max, gamma_val );

	a->LoadObstacleList("Obstacles.dat");
	//a->LoadTriangleList("TObstacles.dat");
	a->SetRunTimeBlur(false);	// If using a pre-blurred map, don't use a run-time blur.
	// Use a comms-map regardless!!!
	string cmap = "maps/comms_map.map";
	if( !a->OpenCommsMap((char*)cmap.c_str(),comms_map,cw,ch)) {
		cout<<endl<<"Error Opening Comms-Map!!!!"; exit(EXIT_FAILURE);
	}
	a->setUseCommsMap(true);

	a->InitializePathfinder();
	a->FindPath(mode,0,sx,sy,ex,ey);
	cout<<endl<<endl;

	delete [] map;
	delete [] risk;

}
