/*
;===================================================================
;A* Pathfinder (Version 1.71a) by Patrick Lester. Used by permission.
;===================================================================
;Last updated 06/16/03 -- Visual C++ version
 */
#ifndef __ASTAR_LIBRARY_H__
#define __ASTAR_LIBRARY_H__

#include <iostream>
#include <math.h>
#include <cstdlib>
#include <algorithm>
#include <vector>
#include "Waypoint.h"
#include "MyImageMap.h"
//#include "VCollide.H"
#include <boost/python.hpp>
//#include <boost/python/class.hpp>
//#include <boost/python/def.hpp>
//#include <boost/python/module.hpp>

using namespace boost::python;

const int debugMode = 1; // 1 = verbose, 0 = silent

const int maxMapWidth = 1200, maxMapHeight = 1200;
const int tileSize = 1, numberPeople = 3, wMatSize = 101;

enum {
	AStarShortestPath, MinRiskPath, SRPathUsingDataBuffer,
	SRPathUsingCommRate, MinRiskUsingCommRate
};

enum {
	Obstacles, Glider
};

class AStar
{
	float eps;	// Minimum Risk value throughout the map
	int d_max;
	float gammaVal;
	float D;

	//Declare constants
	unsigned long onClosedList;
	int mapWidth;
	int mapHeight;
	int notfinished, notStarted;// path-related constants
	int found, nonexistent;

	// Obstacles
	//VCollide vc;
	//int obs_id[2];
	std::vector<int> LA_x, LA_y, Cat_x, Cat_y;

	//Create needed arrays
	int    walkability [maxMapWidth][maxMapHeight];
	float  risk[maxMapWidth][maxMapHeight];
	int    openList[maxMapWidth*maxMapHeight+2]; //1 dimensional array holding ID# of open list items
	int    whichList[maxMapWidth+1][maxMapHeight+1];  //2 dimensional array used to record
													// whether a cell is on the open list or on the closed list.
	int    openX[maxMapWidth*maxMapHeight+2]; //1d array stores the x location of an item on the open list
	int    openY[maxMapWidth*maxMapHeight+2]; //1d array stores the y location of an item on the open list
	int    parentX[maxMapWidth+1][maxMapHeight+1]; //2d array to store parent of each cell (x)
	int    parentY[maxMapWidth+1][maxMapHeight+1]; //2d array to store parent of each cell (y)
	double Fcost[maxMapWidth*maxMapHeight+2];	//1d array to store F cost of a cell on the open list
	double Gcost[maxMapWidth+1][maxMapHeight+1]; 	//2d array to store G cost for each cell.
	double Hcost[maxMapWidth*maxMapHeight+2];	//1d array to store H cost of a cell on the open list
	int    pathLength[numberPeople+1];     //stores length of the found path for critter
	int    pathLocation[numberPeople+1];   //stores current position along the chosen path for critter
	int*   pathBank [numberPeople+1];

	// Other A* related data, that used to be private earlier. This stuff is considered "Under the Hood".
	int onOpenList, parentXval, parentYval;
	int a, b, m, u, v, temp, corner, numberOfOpenListItems;
	double addedGCost, tempGcost;
	int path, tempx, pathX, pathY, cellPosition, newOpenListItemID;
	unsigned long nodes_expanded;
	int startX, startY;

	// Some Maps...
	MyImageMap *obsMap;		// Obstacles Map
	MyImageMap *commMap;	// Comms Map
	MyImageMap *riskMap;	// Risk Map

	//Path reading variables
	int pathStatus[numberPeople+1];
	int xPath[numberPeople+1];
	int yPath[numberPeople+1];

	// Other stuff that Arvind added
	double RWMatrix[wMatSize][wMatSize];
	double RWDivisor;
	int RWmatSize;

	bool UseRunTimeBlur;
	bool UseCommsMap;
	bool StepThroughFindPath;
	int	 StepLength;

	std::vector<Waypoint> pathV;	// Entire path with consecutive locations
	std::vector<Waypoint> pathS;	// Path with a subset of nodes upto d_max
    //void InitializeBaseStations(std::vector<Waypoint> & bs_list);
public:
	AStar( char *obsMapFileName, char *riskMapFileName, char *commsMapFileName, int e, int d, float gamma_val );
	AStar(int *occ_map, int w, int h, int e, int d, float gamma_val );
	AStar(int *obs_map, int w1, int h1, int *risk_map, int w2, int h2, int e, int d, float gamma_val );
	~AStar();
	int OpenCommsMap(char *mapFileName, int *map1d, int &w, int &h);
	void InitializePathfinder (void);
	void ReadPath(int pathfinderID,int currentX,int currentY,
			int pixelsPerFrame);
	int  ReadPathX(int pathfinderID,int pathLocation);
	int  ReadPathY(int pathfinderID,int pathLocation);
	void EndPathfinder (void);
	int  FindPath (int mode, int pathfinderID,int startingX, int startingY,
				  int targetX, int targetY);
	double CalcGcost(int mode, int a, int b, int parentXval, int parentYval, int id );
	double CalcHcost( int mode, int a, int b, int m, int parentXval, int parentYval,  int targetX, int targetY );
	double CalcFcost(  int mode, int a, int b, int m );
	void ReInitializeSearch();
    int  InitWeightMatrix( int mat_size );
    int  InitGaussianMatrix( float sigma );
    int FindSubsetPathGreedily(int eps,int d_max);
    int FindSubsetPathUsingDynamicProgramming(int eps, int d_max);
    void SetRunTimeBlur(bool val);
    bool  DetectCollision2( const Waypoint a, const Waypoint b, const int rad );
    double CalcCommCost(int x, int y);
    bool getUseCommsMap() const;
    void setUseCommsMap(bool UseCommsMap);
    int LoadObstacleList(char *obsFileName );
    //int LoadTriangleList(char *obsFileName);
    bool DetectCollision3(int x1, int y1, int x2, int y2 );
    //bool DetectCollisionVC( const Waypoint a, const Waypoint b);
    MyImageMap GetRiskMap();
    MyImageMap GetBathyMap();
    MyImageMap GetCommsMap();

    void InitializeSearch();
    void StartStepping(int stepLength);
    void StopStepping();

    int walkable, unwalkable;// walkability array constants

protected:
    void BinHeapSort(int & m, int & temp);
    float  GetRisk( int a, int b );
    float GetDist( Waypoint &a, Waypoint &b );
    bool GetObs( int x, int y );
    bool GetObs( int x, int y, int r );
    bool  DetectCollision( const Waypoint a, const Waypoint b );
    bool TestIntersectionOfSegments( float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2 );
    double GetCommRate( int x, int y );

};

/*
BOOST_PYTHON_MODULE(AStar)
{
	class_<AStar>("AStar",init<int*,int,int,int*,int,int,int,int,float>())
			.def("FindPath", &AStar::FindPath )
			;
}
*/

#endif

	

