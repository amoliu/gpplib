#include <aStarLibrary.h>
#include <cstdlib>
#include <cstring>
#include <iostream>


BOOST_PYTHON_MODULE(AStar)
{
	using namespace boost::python;
	class_<AStar>("AStar", init<char*,char*,char*,int,int,float>() )
			.def(init<char*,char*,char*>())
			.def("FindPath",&AStar::FindPath ) /** Finds a path */
			.def("GetRiskMap",&AStar::GetRiskMap )
			.def("GetBathyMap",&AStar::GetBathyMap )
			.def("GetCommsMap",&AStar::GetCommsMap )
			.def("StarStepping",&AStar::StartStepping)
			.def("StopStepping",&AStar::StopStepping)
			.def_readwrite("Walkable",&AStar::walkable)
			.def_readwrite("UnWalkable",&AStar::unwalkable)
			;
}


using namespace std;
/*
 * aStarLibrary.cpp
 *
 *  Created on: Mar 3, 2011
 *      Author: arvind
 *
 *  A-Star class library based upon the A* Pathfinder (Version 1.71a) by Patrick Lester
 */
// --------------------------------------------
// Constructor
AStar::AStar( int *occ_map, int w, int h, int e=1, int d=1, float gamma_val = 1 )
{
	mapHeight = h;
	mapWidth = w;

	for( int i=0,j=0,k=0; i< h; i++ )
		for( j = 0; j < w ; j++ ) {
			this->walkability[j][i]= occ_map[k++];
		}
	notfinished = 0;
	notStarted = 0;// path-related constants
	found = 1;
	nonexistent = 2;
	walkable = 1;
	unwalkable = 0;// walkability array constants
	onClosedList = 10;
	eps = e;
	d_max = d;
	InitGaussianMatrix(1100.0/250.0);
	UseRunTimeBlur = true;
	gammaVal = gamma_val;
	D = 1e3;

	// This is added functionality being provided for visualization
	StepThroughFindPath = false;
	StepLength = 100;

}

/**
 * @Name: Constructor that initializes the obstacle and risk maps.
 * @Desc: Here we are shifting over from using risk map as an array
 * 			to using it as an image-map. The idea is to make the planner truly
 * 			independent of the map-sizes and so on.
 * 	TODO: In the future, we want to move G-cost, H-cost and F-cost calculations
 * 			out of the A* class itself.
  **/
AStar::AStar( char *obsMapFileName, char *riskMapFileName, char *commsMapFileName, int e=1, int d=1, float gamma_val = 1 )
{
	obsMap = new MyImageMap( obsMapFileName );
	commMap = new MyImageMap( commsMapFileName );
	riskMap = new MyImageMap( riskMapFileName );
	mapHeight = commMap->getHeight();
	mapWidth = commMap->getWidth();


	for( int i=0,j=0,k=0; i< mapHeight; i++ )
			for( j = 0; j < mapWidth ; j++ ) {
				this->walkability[j][i]= obsMap->GetValue(j,i);
			}
	for( int i=0,j=0,k=0; i< mapHeight; i++ )
			for( j = 0; j < mapWidth ; j++ ) {
				this->risk[j][i]= riskMap->GetValue(j,i);
			}

	notfinished = 0;
	notStarted = 0;// path-related constants
	found = 1;
	nonexistent = 2;
	walkable = 1;
	unwalkable = 0;// walkability array constants
	onClosedList = 10;
	RWmatSize = 15;
	InitGaussianMatrix(1100.0/250.0);
	eps = e;
	d_max = d;
	UseRunTimeBlur = true;
	gammaVal = gamma_val;
	D = 1e3;
	StepThroughFindPath = false;
	StepLength = 100;
	onOpenList=0; parentXval=0; parentYval=0;
}

//-------------------------------------------------------------------------------
// Name: Constructor that initializes the obstacle and risk maps
// Desc: Allocates memory for the pathfinder
//-------------------------------------------------------------------------------
AStar::AStar(int *obs_map, int w1, int h1, int *risk_map, int w2, int h2, int e=1, int d=1, float gamma_val = 1 )
{
	mapHeight = h1;
	mapWidth = w1;

	for( int i=0, j=0, k=0; i<h2; i++ ) {
		for (j=0; j< w2 ; j++ ) {
			this->risk[j][i] = risk_map[k++]; // /135660;
			//cout<<risk[j][i]<<",";
		}
		//cout<<endl;
	}
	for( int i=0, j=0, k=0; i<h1; i++ )
			for (j=0; j< w1 ; j++ ) {
				this->walkability[j][i] = obs_map[k++];
			}
	notfinished = 0;
	notStarted = 0;// path-related constants
	found = 1;
	nonexistent = 2;
	walkable = 1;
	unwalkable = 0;// walkability array constants
	onClosedList = 10;
	RWmatSize = 15;
	InitGaussianMatrix(1100.0/250.0);
	eps = e; // /135660;
	d_max = d;
	UseRunTimeBlur = true;
	gammaVal = gamma_val;
	D = 1e3;
	commMap = new MyImageMap( 1200, 1200 );
	StepThroughFindPath = false;
	StepLength = 100;
	onOpenList=0; parentXval=0; parentYval=0;
}


void AStar::StartStepping(int stepLength)
{
	this->StepLength = stepLength;
	this->StepThroughFindPath = true;
}

void AStar::StopStepping()
{
	this->StepLength = 1;
	this->StepThroughFindPath = false;
}

AStar::~AStar()
{
	delete commMap;
}

/*
// For VCollide Obstacle Detection
int AStar::LoadTriangleList(char *obsFileName)
{
	FILE *fp = fopen(obsFileName,"r");

	int objNum, x, y, z, i = 0;
	double v[3][3];
	bool done = false;

	vc.NewObject(&obs_id[Obstacles]);
	vector<double> Vx,Vy,Vz;
	do
	{
		if( fscanf(fp,"%d %d %d %d",&objNum,&x,&y,&z) > 1 ) {
			i = i+1;
			Vx.push_back(x); Vy.push_back(y); Vz.push_back(z);
		}
		else done = true;
	}while(!done);

	for( int j = 0; j<i; j+=3 ) {
		v[0][j] =Vx[j]; v[0][j+1] = Vx[j+1]; v[0][j+2] = Vx[j+2];
		v[1][j] =Vy[j]; v[1][j+1] = Vy[j+1]; v[1][j+2] = Vy[j+2];
		v[2][j] =Vz[j]; v[2][j+1] = Vz[j+1]; v[2][j+2] = Vz[j+2];
		vc.AddTri(v[0],v[1],v[2]);
	}

	vc.EndObject();
}


bool AStar::DetectCollisionVC( const Waypoint a, const Waypoint b)
{
	double v1[3],v2[3],v3[3];
	vc.NewObject(&obs_id[Glider]);
	v1[0] = a.getPathx();
	v1[1] = a.getPathy();
	v1[2] = 0;

	v1[0] = b.getPathx();
	v2[1] = b.getPathy();
	v2[2] = 0;

	v3[0] = a.getPathx();
	v3[1] = a.getPathy();
	v3[2] = 1;

	vc.AddTri(v1,v2,v3,0);
	vc.EndObject();

	VCReport report;

	if(report.numObjPairs() > 1 ) {
		cout<<"Detected Collision between objects"<<report.obj1ID(0)<<" and "<<report.obj2ID(0)<<endl;
		vc.DeleteObject(Glider);
		return true;
	}

	vc.DeleteObject(Glider);
	return false;
}
*/

// For faster collision detection
int AStar::LoadObstacleList(char *obsFileName )
{
	FILE *fp = fopen(obsFileName,"r");

	enum obs_lines { LA_Lines, Catalina_Lines };

	int objNum, x, y;
	int done = 0;
	do
	{
		if( fscanf(fp,"%d %d %d",&objNum,&x,&y)>1 ) {
			if( objNum == LA_Lines ) {
				LA_x.push_back(x);
				LA_y.push_back(y);
			}else if(objNum == Catalina_Lines ){
				Cat_x.push_back(x);
				Cat_y.push_back(y);
			}
		}
		else {
			done = 1;
		}
	}while(!done);

	// Test if we loaded everything...

	for( int i = 0; i < LA_x.size(); i++ ) {
		cout<<"LA(x,y)=("<<LA_x[i]<<","<<LA_y[i]<<")"<<endl;
	}
	for( int i = 0; i < Cat_x.size(); i++ ) {
			cout<<"Cat(x,y)=("<<Cat_x[i]<<","<<Cat_y[i]<<")"<<endl;
	}

	fclose(fp);
}


int AStar::OpenCommsMap(char *mapFileName, int *map1d, int &w, int &h)
{
	return commMap->OpenCommsMap(mapFileName,map1d,w,h);
}

//-----------------------------------------------------------------------------
// Name: InitializePathfinder
// Desc: Allocates memory for the pathfinder.
//-----------------------------------------------------------------------------
void AStar::InitializePathfinder (void)
{
	for (int x = 0; x < numberPeople+1; x++)
		pathBank [x] = (int*) malloc(4);
}


//-----------------------------------------------------------------------------
// Name: EndPathfinder
// Desc: Frees memory used by the pathfinder.
//-----------------------------------------------------------------------------
void AStar::EndPathfinder (void)
{
	for (int x = 0; x < numberPeople+1; x++)
	{
		free (pathBank [x]);
	}
}

//-----------------------------------------------------------------------------
//	Name: GetRisk[a][b]
//  Desc: A weighted filtered version for getting the risk at a given cell.
// 		 We weight the pixels by a 2^x power with the mid-point getting
//		 the highest weight and the weight falling off with each cell around it.
//		 This weighting matrix is in RWmat
//-----------------------------------------------------------------------------
float AStar::GetRisk( int a, int b )
{
	int mid = RWmatSize/2;
	double tempRisk= 0, tot_div = 0,  tempMaxRisk = 0;
	// We Convolve the RWMatrix with the risks at the given location

	if( this->UseRunTimeBlur ) {

		int i,j, x, y;
		for(  i = a-mid, x=0; x<RWmatSize ; i++, x++ ) {
				for (  j = b-mid, y=0 ; y<RWmatSize ; j++, y++ ) {
					if( i >= 0 && j >= 0 && i < this->mapHeight  && j<this->mapWidth ) {
						// Only consider cells on the map
						tempRisk+=risk[i][j]*RWMatrix[x][y];
						tot_div +=RWMatrix[x][y];
						//cout<<endl<<a<<","<<b<<","<<i<<","<<j<<","<<x<<","<<y
						//		<<","<<tempRisk<<","<<risk[i][j]<<","<<RWMatrix[x][y];
						if( tempMaxRisk < tempRisk )
							tempMaxRisk = tempRisk;
					}
				}
			}

		if( tot_div > 0 ) {
			tempRisk = tempRisk/tot_div;
		}
		/*if( risk[a][b] != tempRisk ) {
			cout<<"Risk(a,b)="<<risk[a][b]<<"GetRisk(a,b)="<<tempRisk<<"MaxRisk(a,b)="<<tempMaxRisk<<endl;
		}*/
	}
	else tempRisk = risk[a][b];


	return tempRisk;
}

//-----------------------------------------------------------------------------
// Name: CalcGcost
//
//-----------------------------------------------------------------------------
double AStar::CalcGcost( int mode, int a, int b, int parentXval, int parentYval, int id )
{
	double addedGCost, tempGcost;
	double data_acc_rate = gammaVal;
	if( gammaVal == 0 )
		data_acc_rate = 0.1;
	Waypoint wk, wkm1; wk.setPathx(a); wk.setPathy(b); wkm1.setPathx(parentXval); wkm1.setPathy(parentYval);
	double dist = this->GetDist(wk,wkm1) * 100.0;

	switch(mode) {
		case AStarShortestPath:
			if (abs(a-parentXval) == 1 && abs(b-parentYval) == 1)
						addedGCost = 14;//cost of going to diagonal squares
					else
						addedGCost = 10;//cost of going to non-diagonal squares
					tempGcost = Gcost[parentXval][parentYval] + addedGCost;
			break;
		case MinRiskPath: // Here we only do a shortest risk-search using the map without data
				addedGCost = this->GetRisk(a,b) + eps;
				tempGcost = Gcost[parentXval][parentYval] + addedGCost;
			break;
		case SRPathUsingDataBuffer:
			addedGCost = this->GetRisk(a,b) + eps; // this->risk[a][b];	// Risk at the current location
			//Gcost[a][b] = Gcost[parentXval][parentYval] + addedGCost;
			tempGcost = Gcost[parentXval][parentYval] + addedGCost;
			break;
		case SRPathUsingCommRate:
			addedGCost =  (data_acc_rate * (d_max * 100.0) * CalcCommCost(a,b)/1000.0) * (GetRisk(a,b)+eps); // d_max is in cell-dist. Needs to be multiplied to be converted into meters.
			tempGcost = Gcost[parentXval][parentYval] + addedGCost;
			break;
		case MinRiskUsingCommRate:
			addedGCost = (data_acc_rate * dist)*CalcCommCost(a,b)/1000.0 * (GetRisk(a,b)+eps);
			tempGcost = Gcost[parentXval][parentYval] + addedGCost;
			break;
		default:
			break;
	}
	return tempGcost;
}

//-----------------------------------------------------------------------------
// Name: CalcHcost()
// Desc:
//-----------------------------------------------------------------------------
double AStar::CalcHcost( int mode, int a, int b, int m, int parentXval, int parentYval,  int targetX, int targetY )
{
	float data_acc_rate = gammaVal;
	if( gammaVal == 0)
		data_acc_rate = 0.1;
	float ThrMax = 5.5;

	Waypoint wk, we;
	wk.setPathx(a); wk.setPathy(b); we.setPathx(targetX); we.setPathy(targetY);
	double dist = this->GetDist(wk,we) * 100;

	switch(mode) {
		case AStarShortestPath:
			Hcost[openList[m]] = 10*(abs(a - targetX) + abs(b - targetY));
			break;
		case MinRiskPath:
			Hcost[openList[m]] = eps * int(dist/d_max);
			break;
		case SRPathUsingDataBuffer:
			Hcost[openList[m]] = eps * int(dist/d_max);
			break;
		case SRPathUsingCommRate:
			Hcost[openList[m]] = dist * data_acc_rate/ThrMax * eps;
			break;
		case MinRiskUsingCommRate:
			Hcost[openList[m]] = dist * data_acc_rate/ThrMax * eps;
			break;
		default:
			break;
	}
}

//-----------------------------------------------------------------------------
// Name: CalcFcost()
// Desc:
//-----------------------------------------------------------------------------
double AStar::CalcFcost( int mode, int a, int b, int m )
{
	switch(mode) {
		case AStarShortestPath:
			Fcost[openList[m]] = Gcost[a][b] + Hcost[openList[m]];
			break;
		case MinRiskPath:
			Fcost[openList[m]] = Gcost[a][b] + Hcost[openList[m]];
			break;
		case SRPathUsingDataBuffer:
			Fcost[openList[m]] = Gcost[a][b] + Hcost[openList[m]];
			break;
		case SRPathUsingCommRate:
			Fcost[openList[m]] = Gcost[a][b] + Hcost[openList[m]];
			break;
		default:
			Fcost[openList[m]] = Gcost[a][b] + Hcost[openList[m]];
			break;
	}
}


//	Reinitialze Search by clearing out the Cost arrays
//
//
void AStar::ReInitializeSearch()
{
	int risk[maxMapWidth][maxMapHeight];
	int openList[maxMapWidth*maxMapHeight+2]; //1 dimensional array holding ID# of open list items
	int whichList[maxMapWidth+1][maxMapHeight+1];  //2 dimensional array used to record
// 		whether a cell is on the open list or on the closed list.
	int openX[maxMapWidth*maxMapHeight+2]; //1d array stores the x location of an item on the open list
	int openY[maxMapWidth*maxMapHeight+2]; //1d array stores the y location of an item on the open list
	int parentX[maxMapWidth+1][maxMapHeight+1]; //2d array to store parent of each cell (x)
	int parentY[maxMapWidth+1][maxMapHeight+1]; //2d array to store parent of each cell (y)
	int Fcost[maxMapWidth*maxMapHeight+2];	//1d array to store F cost of a cell on the open list
	int Gcost[maxMapWidth+1][maxMapHeight+1]; 	//2d array to store G cost for each cell.
	int Hcost[maxMapWidth*maxMapHeight+2];	//1d array to store H cost of a cell on the open list
	int pathLength[numberPeople+1];     //stores length of the found path for critter
	int pathLocation[numberPeople+1];   //stores current position along the chosen path for critter

	for( int i = 0; i< maxMapHeight; i++ )
		for (int j = 0 ; j< maxMapWidth; j++ ) {
			this->Gcost[j][i] = 0;
			this->openList[i*maxMapWidth + j] = 0;
			this->whichList[j][i] = 0;
			this->openX[i*maxMapWidth + j] = 0;
			this->openY[i*maxMapWidth + j] = 0;
			this->parentX[j][i] = 0;
			this->parentY[j][i] = 0;
			this->Fcost[i*maxMapWidth +j] = 0;
			this->Hcost[i*maxMapWidth +j] = 0;
		}

	for (int i = 0; i < numberPeople; i++ ) {
		pathLength[i] = 0;
		pathLocation[i] = 0;
	}
}




void AStar::BinHeapSort(int & m, int & temp)
{
    //Move the new open list item to the proper place in the binary heap.
    //Starting at the bottom, successively compare to parent items,
    //swapping as needed until the item finds its place in the heap
    //or bubbles all the way to the top (if it has the lowest F cost).
    while(m != 1)//While item hasn't bubbled to the top (m=1)
    {
        //Check if child's F cost is < parent's F cost. If so, swap them.
        if(Fcost[openList[m]] <= Fcost[openList[m / 2]]){
            temp = openList[m / 2];
            openList[m / 2] = openList[m];
            openList[m] = temp;
            m = m / 2;
        }else
            break;

    }
}

void AStar::InitializeSearch()
{
	onOpenList=0; parentXval=0; parentYval=0;
	a=0; b=0; m=0; u=0; v=0; temp=0; corner=0; numberOfOpenListItems=0;
	addedGCost=0; tempGcost = 0;
	path = 0; newOpenListItemID=0;
	nodes_expanded = 0;
}


//-----------------------------------------------------------------------------
// Name: FindPath
// Desc: Finds a path using A*
//-----------------------------------------------------------------------------
int AStar::FindPath (int mode, int pathfinderID,int startingX, int startingY,
			  int targetX, int targetY)
{
	static long num_runs = 0;

	if( this->StepThroughFindPath ) { // We want to continue with our path-search...
		if( num_runs > 0 ) {
			goto skip_inits;
		}
	}

	InitializeSearch();

	startX = startingX/tileSize;
	startY = startingY/tileSize;
	targetX = targetX/tileSize;
	targetY = targetY/tileSize;

//2.Quick Path Checks: Under the some circumstances no path needs to
//	be generated ...

//	If starting location and target are in the same location...
	if (startX == targetX && startY == targetY && pathLocation[pathfinderID] > 0)
		return found;

	if (startX == targetX && startY == targetY && pathLocation[pathfinderID] == 0)
		return nonexistent;

//	If target square is unwalkable, return that it's a nonexistent path.
	if (walkability[targetX][targetY] == unwalkable) {
		cout<<" Target unwalkable. Target="<<walkability[targetX][targetY]<<" ";
		goto noPath;
	}

//3.Reset some variables that need to be cleared
	if (onClosedList > 100000000) //reset whichList occasionally
	{
		for (int x = 0; x < mapWidth;x++) {
			for (int y = 0; y < mapHeight;y++)
				whichList [x][y] = 0;
		}
		onClosedList = 10;
	}
	onClosedList = onClosedList+2; //changing the values of onOpenList and onClosed list is faster than redimming whichList() array
	onOpenList = onClosedList-1;
	pathLength [pathfinderID] = notStarted;//i.e, = 0
	pathLocation [pathfinderID] = notStarted;//i.e, = 0
	Gcost[startX][startY] = 0; //reset starting square's G value to 0

//4.Add the starting location to the open list of squares to be checked.
	numberOfOpenListItems = 1;
	openList[1] = 1;//assign it as the top (and currently only) item in the open list, which is maintained as a binary heap (explained below)
	openX[1] = startX ; openY[1] = startY;

//5.Do the following until a path is found or deemed nonexistent.
	do
	{
skip_inits:
//6.If the open list is not empty, take the first cell off of the list.
//	This is the lowest F cost cell on the open list.
	if (numberOfOpenListItems != 0)
	{

//7. Pop the first item off the open list.
	parentXval = openX[openList[1]];
	parentYval = openY[openList[1]]; //record cell coordinates of the item
	whichList[parentXval][parentYval] = onClosedList;//add the item to the closed list

//	Open List = Binary Heap: Delete this item from the open list, which
//  is maintained as a binary heap. For more information on binary heaps, see:
//	http://www.policyalmanac.org/games/binaryHeaps.htm
	numberOfOpenListItems = numberOfOpenListItems - 1;//reduce number of open list items by 1

//	Delete the top item in binary heap and reorder the heap, with the lowest F cost item rising to the top.
	openList[1] = openList[numberOfOpenListItems+1];//move the last item in the heap up to slot #1
	v = 1;

//	Repeat the following until the new item in slot #1 sinks to its proper spot in the heap.
	do
	{
	u = v;
	if (2*u+1 <= numberOfOpenListItems) //if both children exist
	{
	 	//Check if the F cost of the parent is greater than each child.
		//Select the lowest of the two children.
		if (Fcost[openList[u]] >= Fcost[openList[2*u]])
			v = 2*u;
		if (Fcost[openList[v]] >= Fcost[openList[2*u+1]])
			v = 2*u+1;
	}
	else
	{
		if (2*u <= numberOfOpenListItems) //if only child #1 exists
		{
	 	//Check if the F cost of the parent is greater than child #1
			if (Fcost[openList[u]] >= Fcost[openList[2*u]])
				v = 2*u;
		}
	}

	if (u != v) //if parent's F is > one of its children, swap them
	{
		temp = openList[u];
		openList[u] = openList[v];
		openList[v] = temp;
	}
	else
		break; //otherwise, exit loop

	}
	while (true);//reorder the binary heap


//7.Check the adjacent squares. (Its "children" -- these path children
//	are similar, conceptually, to the binary heap children mentioned
//	above, but don't confuse them. They are different. Path children
//	are portrayed in Demo 1 with grey pointers pointing toward
//	their parents.) Add these adjacent child squares to the open list
//	for later consideration if appropriate (see various if statements
//	below).

	int d = 1;
	if( mode == ::SRPathUsingDataBuffer  || mode == ::SRPathUsingCommRate || mode == ::MinRiskUsingCommRate )
		d=d_max;

	for (b = parentYval-d; b <= parentYval+d; b++){
	for (a = parentXval-d; a <= parentXval+d; a++){

//	If not off the map (do this first to avoid array out-of-bounds errors)
	if (a >0 && b >0 && a < mapWidth && b < mapHeight){

//	If not already on the closed list (items on the closed list have
//	already been considered and can now be ignored).
//	if( (mode != :: SRPathUsingDataBuffer && mode != SRPathUsingCommRate && mode != MinRiskUsingCommRate) || whichList[a][b] != onClosedList  ) {
	if (whichList[a][b] != onClosedList) {

//	If not a wall/obstacle square.
	if (walkability [a][b] != unwalkable) {

//	Don't cut across corners
	corner = walkable;
	if (a == parentXval-1)
	{
		if (b == parentYval-1)
		{
			if (walkability[parentXval-1][parentYval] == unwalkable
				|| walkability[parentXval][parentYval-1] == unwalkable) \
				corner = unwalkable;
		}
		else if (b == parentYval+1)
		{
			if (walkability[parentXval][parentYval+1] == unwalkable
				|| walkability[parentXval-1][parentYval] == unwalkable)
				corner = unwalkable;
		}
	}
	else if (a == parentXval+1)
	{
		if (b == parentYval-1)
		{
			if (walkability[parentXval][parentYval-1] == unwalkable
				|| walkability[parentXval+1][parentYval] == unwalkable)
				corner = unwalkable;
		}
		else if (b == parentYval+1)
		{
			if (walkability[parentXval+1][parentYval] == unwalkable
				|| walkability[parentXval][parentYval+1] == unwalkable)
				corner = unwalkable;
		}
	}

//  Collision detection
	Waypoint w1(parentXval,parentYval), w2(a,b);
	// w1.setPathx(parentXval); w1.setPathy(parentYval); w2.setPathx(a); w2.setPathy(b);

	//if (corner == walkable ) {
	//if( corner == walkable && !DetectCollision3(parentXval, parentYval, a, b ) ) {
	if (corner == walkable && !this->DetectCollision2(w1,w2,2)) {
	//if (corner == walkable && !this->DetectCollisionVC(w1,w2)) {
	//if (corner == walkable && !this->DetectCollision(w1,w2)) {

		nodes_expanded++;
//	If not already on the open list, add it to the open list.
	if (whichList[a][b] != onOpenList)
	{
		//Create a new open list item in the binary heap.
		newOpenListItemID = newOpenListItemID + 1; //each new item has a unique ID #
		m = numberOfOpenListItems+1;
		openList[m] = newOpenListItemID;//place the new open list item (actually, its ID#) at the bottom of the heap
		openX[newOpenListItemID] = a;
		openY[newOpenListItemID] = b;//record the x and y coordinates of the new item

		Gcost[a][b] = CalcGcost( mode, a, b, parentXval, parentYval, pathfinderID );

		this->CalcHcost(mode, a, b, m, parentXval, parentYval, targetX, targetY );
		this->CalcFcost( mode, a, b, m );

		parentX[a][b] = parentXval ; parentY[a][b] = parentYval;
	    BinHeapSort(m, temp);
	    numberOfOpenListItems = numberOfOpenListItems+1;//add one to the number of items in the heap

		//Change whichList to show that the new item is on the open list.
		whichList[a][b] = onOpenList;
	}

//8.If adjacent cell is already on the open list, check to see if this
//	path to that cell from the starting location is a better one.
//	If so, change the parent of the cell and its G and F costs.
	else //If whichList(a,b) = onOpenList
	{
		//Figure out the G cost of this possible new path
		tempGcost = this->CalcGcost(mode, a,b,parentXval, parentYval, pathfinderID );
		//If this path is shorter (G cost is lower) then change
		//the parent cell, G cost and F cost.
		if (tempGcost < Gcost[a][b]) //if G cost is less,
		{
			parentX[a][b] = parentXval; //change the square's parent
			parentY[a][b] = parentYval;
			Gcost[a][b] = tempGcost;//change the G cost

			//Because changing the G cost also changes the F cost, if
			//the item is on the open list we need to change the item's
			//recorded F cost and its position on the open list to make
			//sure that we maintain a properly ordered open list.
			for (int x = 1; x <= numberOfOpenListItems; x++) //look for the item in the heap
			{
			if (openX[openList[x]] == a && openY[openList[x]] == b) //item found
			{
				Fcost[openList[x]] = Gcost[a][b] + Hcost[openList[x]];//change the F cost

				//See if changing the F score bubbles the item up from it's current location in the heap
				m = x;
			    BinHeapSort(m, temp);
			    break; //exit for x = loop
			} //If openX(openList(x)) = a
			} //For x = 1 To numberOfOpenListItems
		}//If tempGcost < Gcost(a,b)

	}//else If whichList(a,b) = onOpenList
	}//If not cutting a corner
	}//If not a wall/obstacle square.
	}//If not already on the closed list
	}//If not off the map
	}//for (a = parentXval-1; a <= parentXval+1; a++){
	}//for (b = parentYval-1; b <= parentYval+1; b++){

	}//if (numberOfOpenListItems != 0)

//9.If open list is empty then there is no path.
	else
	{
		path = nonexistent; cout<<" open-list-empty";	break;
	}

	//If target is added to open list then path has been found.
	if (whichList[targetX][targetY] == onOpenList)
	{
		path = found; break;
	}

	num_runs++;
	if( (num_runs % this->StepLength) == 0 && this->StepThroughFindPath == true)
		break;
	}
	while (1);//Do until path is found or deemed nonexistent

//10.Save the path if it exists.
	if (path == found)
	{

//a.Working backwards from the target to the starting location by checking
//	each cell's parent, figure out the length of the path.
	pathX = targetX; pathY = targetY;
	do
	{
		//Look up the parent of the current cell.
		tempx = parentX[pathX][pathY];
		pathY = parentY[pathX][pathY];
		pathX = tempx;

		//Figure out the path length
		pathLength[pathfinderID] = pathLength[pathfinderID] + 1;
	}
	while (pathX != startX || pathY != startY);

//b.Resize the data bank to the right size in bytes
	pathBank[pathfinderID] = (int*) realloc (pathBank[pathfinderID],
		pathLength[pathfinderID]*8);

//c. Now copy the path information over to the databank. Since we are
//	working backwards from the target to the start location, we copy
//	the information to the data bank in reverse order. The result is
//	a properly ordered set of path data, from the first step to the
//	last.
	pathX = targetX ; pathY = targetY;
	double TotRisk = 0;
	cellPosition = pathLength[pathfinderID]*2;//start at the end
	do
	{
	cellPosition = cellPosition - 2;//work backwards 2 integers
	pathBank[pathfinderID] [cellPosition] = pathX;
	pathBank[pathfinderID] [cellPosition+1] = pathY;
	TotRisk += this->GetRisk(pathX,pathY);
	cout<<pathX<<","<<pathY<<","<<Gcost[pathX][pathY]<<","<<TotRisk<<endl;
	Waypoint wp;
	wp.setPathx(pathX);
	wp.setPathy(pathY);
	wp.setComm_cost(this->CalcCommCost(pathX,pathY) );
	wp.setPath_comm_cost(0);
	wp.setNode_cost(this->GetRisk(pathX,pathY)); // .node_cost = this->GetRisk(pathX,pathY);
	wp.setPath_cost(0);
	wp.setNode_g_cost(this->Gcost[pathX][pathY]);
	wp.setPath_g_cost(0);
	pathV.push_back(wp);

//d.Look up the parent of the current cell.
	tempx = parentX[pathX][pathY];
	pathY = parentY[pathX][pathY];
	pathX = tempx;

//e.If we have reached the starting square, exit the loop.
	}
	while (pathX != startX || pathY != startY);

	cout<<endl<<"Nodes Expanded "<<nodes_expanded<<endl;
	Waypoint wp;
	wp.setPathx(pathX); //.pathx = pathX;
	wp.setPathy(pathY); //.pathy = pathY;
	wp.setComm_cost(this->CalcCommCost(pathX,pathY));
	wp.setPath_comm_cost(0);
	wp.setNode_cost(this->GetRisk(pathX,pathY)); //node_cost = this->GetRisk(pathX,pathY);
	wp.setPath_cost(0); //.path_cost = 0;
	wp.setNode_g_cost(this->Gcost[pathX][pathY]);
	wp.setPath_g_cost(0);
	pathV.push_back(wp);
	// Reverse the path-vector
	std::reverse(pathV.begin(),pathV.end());
// Call Dynamic search to find the best subset of points to stop at.
	FindSubsetPathUsingDynamicProgramming(eps,d_max);
	//FindSubsetPathGreedily(eps,d_max);

//11.Read the first path step into xPath/yPath arrays
	ReadPath(pathfinderID,startingX,startingY,1);

	}
	if (path == nonexistent )
	{
		cout<<"Looked through, but no path."<<endl;
		goto noPath;
	}

	return path;


//13.If there is no path to the selected target, set the pathfinder's
//	xPath and yPath equal to its current location and return that the
//	path is nonexistent.
noPath:
	cout<<"start: ("<<startX<<","<<startY<<") ="
		<<walkability[startingX][startingY]<<
		" target: ("<<targetX<<","<<targetY<<")="<<walkability[targetX][targetY];
	cout<<"No Path";
	xPath[pathfinderID] = startingX;
	yPath[pathfinderID] = startingY;
	return nonexistent;
}

//==========================================================
//READ PATH DATA: These functions read the path data and convert
//it to screen pixel coordinates.
void AStar::ReadPath(int pathfinderID,int currentX,int currentY,
			  int pixelsPerFrame)
{
	int ID = pathfinderID; //redundant, but makes the following easier to read

	//If a path has been found for the pathfinder	...
	if (pathStatus[ID] == found)
	{

		//If path finder is just starting a new path or has reached the
		//center of the current path square (and the end of the path
		//hasn't been reached), look up the next path square.
		if (pathLocation[ID] < pathLength[ID])
		{
			//if just starting or if close enough to center of square
			if (pathLocation[ID] == 0 ||
				(abs(currentX - xPath[ID]) < pixelsPerFrame && abs(currentY - yPath[ID]) < pixelsPerFrame))
					pathLocation[ID] = pathLocation[ID] + 1;
		}

		//Read the path data.
		xPath[ID] = ReadPathX(ID,pathLocation[ID]);
		yPath[ID] = ReadPathY(ID,pathLocation[ID]);

		//If the center of the last path square on the path has been
		//reached then reset.
		if (pathLocation[ID] == pathLength[ID])
		{
			if (abs(currentX - xPath[ID]) < pixelsPerFrame
				&& abs(currentY - yPath[ID]) < pixelsPerFrame) //if close enough to center of square
					pathStatus[ID] = notStarted;
		}
	}

	//If there is no path for this pathfinder, simply stay in the current
 	//location.
	else
	{
		xPath[ID] = currentX;
		yPath[ID] = currentY;
	}
}


//The following two functions read the raw path data from the pathBank.
//You can call these functions directly and skip the readPath function
//above if you want. Make sure you know what your current pathLocation
//is.

//-----------------------------------------------------------------------------
// Name: ReadPathX
// Desc: Reads the x coordinate of the next path step
//-----------------------------------------------------------------------------
int AStar::ReadPathX(int pathfinderID,int pathLocation)
{
	int x;
	if (pathLocation <= pathLength[pathfinderID])
	{

	//Read coordinate from bank
	x = pathBank[pathfinderID] [pathLocation*2-2];

	//Adjust the coordinates so they align with the center
	//of the path square (optional). This assumes that you are using
	//sprites that are centered -- i.e., with the midHandle command.
	//Otherwise you will want to adjust this.
	x = tileSize*x + .5*tileSize;

	}
	return x;
}


//-----------------------------------------------------------------------------
// Name: ReadPathY
// Desc: Reads the y coordinate of the next path step
//-----------------------------------------------------------------------------
int AStar::ReadPathY(int pathfinderID,int pathLocation)
{
	int y;
	if (pathLocation <= pathLength[pathfinderID])
	{

	//Read coordinate from bank
	y = pathBank[pathfinderID] [pathLocation*2-1];

	//Adjust the coordinates so they align with the center
	//of the path square (optional). This assumes that you are using
	//sprites that are centered -- i.e., with the midHandle command.
	//Otherwise you will want to adjust this.
	y = tileSize*y + .5*tileSize;

	}
	return y;
}




int max( int a, int b ) {
	return (a>b)?a:b;
}

int AStar::InitWeightMatrix(int mat_size)
{
	if ( mat_size>wMatSize ) {
		mat_size = wMatSize;
	}
	if (mat_size%2 == 0)
		mat_size=mat_size+1;

	int mid = mat_size/2;

	for( int i=0; i< mat_size; i++ ) {
		//cout<<endl;
		for ( int j = 0 ; j < mat_size ; j++ ) {
			RWMatrix[i][j]=pow(2,double(mid-max(abs(i-mid),abs(j-mid))) );
			RWDivisor+=RWMatrix[i][j];
			//cout<<RWMatrix[i][j]<<",";
		}
	}
	// cout<<endl<<RWDivisor<<endl;

	return RWDivisor;
}


//-------------------------------------------------------------------
//	Desc: A Function that creates a Gaussian Kernel based upon sigma.
//
//-------------------------------------------------------------------
int AStar::InitGaussianMatrix( float sigma )
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


//----------------------------------------------------------------------------------
// Desc: This member function greedily finds the shortest path with the lowest cost
//		 for node traversal, by working its way backward from the path-vector
//		 to find the minimum cost upto d-max. The path being selected in this subset
//		 should be not violate any of the constraints on the bathymetry map.
int AStar::FindSubsetPathGreedily(int e,int d)
{
	int i = 0, j = 0, tot_cost = 0, run_total =0;

	cout<<"--------- Actual Path ----------"<<endl;
	std::vector<Waypoint>::iterator wpt = pathV.begin();
	for ( i = 0, run_total = 0; i < pathV.size(); i++, wpt++ ) {
		run_total += wpt->getNode_cost() + eps;
		wpt->setPath_cost(run_total);
	}

	for ( i = 0; i < pathV.size(); i++ ) {
		cout<<endl<<"A("<<pathV[i].getPathx()<<","<<pathV[i].getPathy()<<
				")="<<pathV[i].getNode_cost()<<", Total-cost="<<pathV[i].getPath_cost();
	}

	pathS.clear();
	if( !pathV.empty() ) {
		i = 0; Waypoint w;
		w = pathV.front();
		tot_cost += pathV[i].getNode_cost();
		pathS.push_back(w);

		int min = pathV[i].getNode_cost(), min_indx = 0; // We are at the start
		do {
				min = pathV[i].getNode_cost();
				// For starters let us do a naive add, without bathymetric checks
				min_indx = 0;
				for( j = 0; j< abs( d_max ) && (i+j) < pathV.size() && !DetectCollision2(pathV[i],pathV[i+j],2); j++ ) {
					if( min >= pathV[i+j].getNode_cost() ) {
						min=pathV[i+j].getNode_cost();
						min_indx = j;
					}
				}
				if(min_indx > 0)
					i = i + min_indx;
				else
					i++;
				if( i < pathV.size()) {
					Waypoint w = pathV[i];
					tot_cost += pathV[i].getNode_cost();
					w.setPath_cost(tot_cost);
					pathS.push_back(w);
				}
		}while(i < pathV.size());
		Waypoint Se = pathS.back(), Ve= pathV.back();
		if( (Se.getPathx() != Ve.getPathx()) && (Se.getPathy() != Ve.getPathy()) ) {
			Waypoint w;
			w = pathV.back();
			tot_cost += pathV[i].getNode_cost();
			pathS.push_back(w);
		}
		std::vector<Waypoint>::iterator wpt = pathS.begin();
		for ( i = 0, run_total = 0; i < pathS.size(); i++, wpt++ ) {
				run_total += wpt->getNode_cost() + eps;
				wpt->setPath_cost(run_total);
		}

		// Display this subset path:
		cout<<endl<<"--------- Subset Path ----------"<<endl;
		for ( i = 0; i < pathS.size(); i++ ) {
			cout<<endl<<"S("<<pathS[i].getPathx()<<","<<pathS[i].getPathy()<<
					")="<<pathS[i].getNode_cost()<<", Total-cost="<<pathS[i].getPath_cost();
		}
	}


}

void AStar::SetRunTimeBlur(bool val)
{
	this->UseRunTimeBlur = val;
}


inline float AStar::GetDist( Waypoint &a, Waypoint &b )
{
	double xdiff = a.getPathx() - b.getPathx();
	double ydiff = a.getPathy() - b.getPathy();
	return sqrt(xdiff*xdiff + ydiff * ydiff);
	//return (sqrt(pow(a.getPathx() - b.getPathx(),double(2)) + pow(a.getPathy()-b.getPathy(),double(2))));
}

// Returns whether cell (x,y) is an obstacle cell or not.
bool AStar::GetObs( int x, int y )
{
	return this->walkability[x][y]==unwalkable;
}


// Detect collisions based on calculating the perpendicular distance between
// the edge and the point
bool AStar::DetectCollision( const Waypoint a, const Waypoint b )
{
	// we are using the perp-dist between each point we are testing for
	// and this location on the line to determine collisions.
	const float minColDetectDist = 2;
	int x1 = a.getPathx(), x2 = b.getPathx(), y1 = a.getPathy(), y2 = b.getPathy();

	if( x2 == x1 && y2 == y1 )
		return GetObs(x1,y1);

	int sx = (x1<x2)?x1:x2 - minColDetectDist;
	int sy = (y1<y2)?y1:y2 - minColDetectDist;
	int ex = (x1>x2)?x1:x2 + minColDetectDist;
	int ey = (y1>y2)?y1:y2 + minColDetectDist;

	for( int x0 = sx; x0<ex; x0++ ) {
		for( int y0 = sy; y0 < ey; y0++ ) {
			if( x0 >= 0 && y0 >= 0 && x0 < mapWidth && y0 < mapHeight ) {
				if( GetObs(x0,y0) ) {	// Yes, this is an obstacle, test how far we are from it...
					float perp_dist = abs((x2-x1)*(y1-y0) - (y2-y1)*(x1-x0))/sqrt(pow(x2-x1,double(2))+pow(y2-y1,double(2)));
					if( perp_dist < minColDetectDist )
						return true;
				}
			}
		}
	}
	return false;	// None of these collided!
}


bool AStar::GetObs( int x, int y, int r )
{
	for (int a = x - r; a < x+r;  a++ ) {
		for( int b = y - r; b< y+r ; b++ ) {
			if(b>=0 && a >=0 && a< mapWidth && b < mapHeight ) {
				if( this->walkability[a][b]==unwalkable )
					return true;
			}
		}
	}
	return false;
}


// Previous collision detection method using perpendiculars is too slow!!! :(
bool AStar::DetectCollision2( const Waypoint a, const Waypoint b, const int rad )
{
	// we are using the perp-dist between each point we are testing for
	// and this location on the line to determine collisions.
	int x1 = a.getPathx(), x2 = b.getPathx(), y1 = a.getPathy(), y2 = b.getPathy();

	if( x2 == x1 && y2 == y1 )
		return GetObs(x1,y1);

	int sx, sy, ex, ey;
	if( x1 < x2 ) {	sx = x1; ex = x2; } else { sx = x2; ex = x1; }
	if( y1 < y2 ) { sy = y1; ey = y2; } else { sy = y2; ey = y1; }

	if( x1 != x2 ) {
		float  m1 = (y2-y1)/(x2-x1);
		for( int x = sx; x < ex ; x++ )  {
			int y = m1*(x-x1) + y1;
				if( GetObs(x,y,rad) )
					return true;
		}
	}
	if( y1 != y2) { // Line has better range vertically
		float m2 = (x2 - x1)/(y2 - y1);
		for( int y = sy; y < ey; y++ ) {
			int x = m2 * (y - y1) + x1;
			if( GetObs(x,y,rad) )
				return true;
		}
	}

	return false;	// Nothing collided!
}



// Line Segment Intersection from Algorithms by CLRS
double cross_product ( float x1, float y1, float x2, float y2 )
{
	// p1 x p2
	return x1 * y2 - x2 * y1;
}

double getDirection( float a1, float a2, float b1, float b2, float c1, float c2 )
{
	return (cross_product( (c1-a1), (c2-a2), (b1-a1), (b2-a2) ));
}

bool OnSegment( float a1, float a2, float b1, float b2, float c1, float c2 )
{
	double min_ab1 = a1<b1?a1:b1;
	double min_ab2 = a2<b2?a2:b2;
	double max_ab1 = a1>b1?a1:b1;
	double max_ab2 = a2>b2?a2:b2;

	if( min_ab1<= c1 && max_ab1>= c1 && min_ab2 <=c2 && max_ab2 >= c2 )
		return true;
	else return false;
}

bool AStar::TestIntersectionOfSegments( float a1, float a2, float b1, float b2, float c1, float c2, float d1, float d2 )
{
	double dir1 = getDirection( c1, c2, d1, d2, a1, a2 );
	double dir2 = getDirection( c1, c2, d1, d2, b1, b2 );
	double dir3 = getDirection( a1, a2, b1, b2, c1, c2 );
	double dir4 = getDirection( a1, a2, b1, b2, d1, d2 );

	if( ((dir1 > 0 && dir2 < 0) || (dir1 < 0 && dir2 > 0 )) &&
			((dir3>0 && dir4<0) || (dir3<0 && dir4>0)) )
			return true;
	else if(dir1==0 && OnSegment(c1,c2, d1,d2, a1,a2 ))
			return true;
	else if(dir2==0 && OnSegment(c1,c2,d1,d2,b1,b2))
			return true;
	else if(dir3==0 && OnSegment(a1,a2,b1,b2,c1,c2))
			return true;
	else if(dir4==0 && OnSegment(a1,a2,b1,b2,d1,d2))
			return true;
	else return false;
}

// Even faster collision detection based upon CLRS - Algorithms Chpt 33.1.
bool AStar::DetectCollision3(int x1, int y1, int x2, int y2 )
{
	// We look for intersections between the line defined by (x1,y1) and (x2,y2)
	// with any of those specifying the two obstacle regions.
	for( int i = 0; i<LA_x.size() - 1; i++ ) {
		if( TestIntersectionOfSegments(x1,y1,x2,y2,LA_x[i],LA_y[i],LA_x[i+1],LA_y[i+1] ) )
			return true;
	}

	for( int i = 0; i<Cat_x.size() - 1; i++ ) {
		if( TestIntersectionOfSegments(x1,y1,x2,y2,Cat_x[i],Cat_y[i],Cat_x[i+1],Cat_y[i+1]) )
			return true;
	}

	return false; // Nothing collided!
}

//----------------------------------------------------------------------------------
// Desc: This member function greedily finds the shortest path with the lowest cost
//		 for node traversal, by working its way backward from the path-vector
//		 to find the minimum cost upto d-max. The path being selected in this subset
//		 should be not violate any of the constraints on the bathymetry map.
int AStar::FindSubsetPathUsingDynamicProgramming(int e,int d)
{
	int i = 0, j = 0;
	double total_cost = 0, run_total =0, min_node;
	float min, comm_total = 0;
	double g_total =0;

	std::vector <int> ParentNode;
	std::vector <int> open_list;
	std::vector <int> closed_list;
	std::vector <int> neighbor_list;
	std::vector <double> g_cost;
	std::vector <double> h_cost;
	std::vector <double> f_cost;
	std::vector<Waypoint>::iterator wp=pathV.begin();
	std::vector<double>::iterator min_it;

	cout<<"--------- Actual Path ----------"<<endl;
		std::vector<Waypoint>::iterator wpt = pathV.begin();
		for ( i = 0, run_total = 0; i < pathV.size(); i++, wpt++ ) {
			run_total += wpt->getNode_cost() + eps;
			comm_total += wpt->getComm_cost();
			g_total += wpt->getNode_g_cost();
			wpt->setPath_cost(run_total);
			wpt->setPath_comm_cost(comm_total);
			wpt->setPath_g_cost(g_total);
		}

		for ( i = 0; i < pathV.size(); i++ ) {
			cout<<endl<<"A("<<pathV[i].getPathx()<<","<<pathV[i].getPathy()<<
					")="<<pathV[i].getNode_cost()<<", Total-cost="<<pathV[i].getPath_cost()
					<<", Comm-cost="<<pathV[i].getComm_cost()<<", Total-Comm-cost="<<pathV[i].getPath_comm_cost()
					<<", G-cost="<<pathV[i].getNode_g_cost()<<", Total-G-cost="<<pathV[i].getPath_g_cost();
			//cout<<endl<<i;
		}

	cout<<endl<<"Subset-Find-AStar"; cout.flush();
	// Populate the vectors
	for( i=0, total_cost = 0; wp< pathV.end() ; wp++, i++ ) {
		h_cost.push_back( int(this->GetDist(pathV[i],*(pathV.end()))/d) * eps );
		total_cost += pathV[i].getNode_cost() + eps;
		pathV[i].setPath_cost(total_cost);
		g_cost.push_back(total_cost);
		f_cost.push_back(( h_cost[i] + g_cost[i] ));
		ParentNode.push_back(i-1);
		// cout<<endl<<"g_cost["<<i<<"]="<<g_cost[i]<<", h_cost="<<h_cost[i]<<" , f_cost="<<f_cost[i]<<" , parent_node="<<ParentNode[i];
	}
	cout<<endl<<"Done populating vectors..."; cout.flush();

	// Ready to start running A*
	open_list.push_back(0);	// Start node is on the open-list
	Waypoint prev;
	std::vector<int>::iterator min_indx, indx = open_list.begin();
	int loops = 0;

	do {
		// Find the lowest f-cost node
		//cout<<" Finding lowest f-cost node"; cout.flush();
		min = f_cost[open_list[0]];
		min_node = *open_list.begin();
		indx = open_list.begin(); min_indx = indx;
		for( i = 1 ; i < open_list.size(); i++ , indx++ ) {
			if( f_cost[ open_list[i] ] < min ) {
				min = f_cost[open_list[i]];
				min_node = open_list[i];
				min_indx = indx;
			}
		}
		// cout<<endl<<"Lowest F-cost node = "<<min_node<<" with an f-cost of "<<min<<". open_list.size()="<<open_list.size()<<endl; cout.flush();
		if ( min_node == (pathV.size()-1) ) { // If the minimum node is the goal-node
			int x = min_node;
			do
			{
				prev =pathV[ParentNode[x]];
				pathS.push_back(pathV[x]);
				x = ParentNode[x];
			}
			while( prev.getPathx() != pathV.begin()->getPathx() && prev.getPathy() != pathV.begin()->getPathy() );
			pathS.push_back(pathV[x]);
		}
		// Remove min from openset and place it in the openset
		if( open_list.size()>1 )
		{
			//for( int i = 0; i<open_list.size(); i++ ) {
			//	cout<<"open_list["<<i<<"]="<<open_list[i]<<endl;
			//}
			//cout<<endl<<"Erasing open_list["<<min_node<<"]="<<open_list[min_node]; cout.flush();
			open_list.erase(min_indx);
			//cout<<"After Erase..."; cout.flush();
		}
		else {
			cout<<endl<<"Clearing entire open_list"; cout.flush();
			open_list.clear();
		}
		closed_list.push_back(min_node);
		// Find neighbor nodes to this min-node (Remember they are all going to be ahead of it).
		neighbor_list.clear();
		Waypoint wp1 = pathV[min_node];
		//cout<<endl<<"Getting neighbors of min_node "<<min_node<<" :"; cout.flush();
		for( j = min_node + 1; j<pathV.size(); j++ ) {
		//for( j = 0; j<pathV.size(); j++ ) {
			if ( this->GetDist(wp1,pathV[j]) < d && !this->DetectCollision2(wp1,pathV[j],2)) {
				neighbor_list.push_back(j);
				//cout<<" , "<<j;
			}

		}
		// For each y in the neighborhood:
			std::vector<int>::iterator found;
			float tentative_g_cost;
			bool tentative_is_better = false;
			for( j = 0; j< neighbor_list.size(); j++ ) {
				found = ::find( closed_list.begin(), closed_list.end(), neighbor_list[j] );
				if( !(found == closed_list.end() && *found != neighbor_list[j]) ) {
					//cout<<endl<<"Found "<<neighbor_list[j]<<" in closed_list. Skipping...";
					//cout.flush();
					continue; // If y is in closedset, continue
				}
				tentative_g_cost = g_cost[min_node] + pathV[neighbor_list[j]].getNode_cost(); // + eps;

				// If y not in openset, add y to openset
				found = ::find( open_list.begin(), open_list.end(), neighbor_list[j] );
				if( found==open_list.end() && *found!=neighbor_list[j] ) {
					//cout<<"Did not find neighbor_list["<<j<<"] in open_list."<<endl;
					open_list.push_back(neighbor_list[j]);
					tentative_is_better = true;
				}
				else {
					//cout<<"Found neighbor_list["<<j<<"] = "<<neighbor_list[j]<<endl; cout.flush();
					if( (tentative_g_cost) < g_cost[neighbor_list[j]] ) {
						tentative_is_better = true;
					}
					else
						tentative_is_better = false;
				}
				// If tentative is better...
				if( tentative_is_better ) {
					//cout<<endl<<"Tentative is better. g_cost[neighbor_list["<<j<<"]]="<<g_cost[neighbor_list[j]]; cout.flush();
					ParentNode[neighbor_list[j]] = min_node;
					tentative_is_better = false;

					g_cost[neighbor_list[j]] =tentative_g_cost + eps;
					h_cost[neighbor_list[j]] = int(this->GetDist(pathV[min_node],*(pathV.end()))*float(this->commMap->getRes())/d) * eps;
					f_cost[neighbor_list[j]] =g_cost[neighbor_list[j]] + f_cost[neighbor_list[j]];
					i = neighbor_list[j];
					//cout<<endl<<"g_cost["<<i<<"]="<<g_cost[i]<<", h_cost="<<h_cost[i]<<" , f_cost="<<f_cost[i]<<" , parent_node="<<ParentNode[i]<<
					//		", neighbor_list["<<j<<"]="<<neighbor_list[j]<<", min_node ="<<min_node<<endl;
				}
			}
	}while( !open_list.empty() );


	// Display this subset path:
	cout<<endl<<"--------- Subset Path ----------"<<endl;
	total_cost = 0;
	double total_comm_cost = 0;
	// Reverse the subset path...
	::reverse(pathS.begin(),pathS.end());
	// Display it...
	for ( i = 0; i < pathS.size(); i++ ) {
			pathS[i].setNode_cost(this->GetRisk(pathS[i].getPathx(),pathS[i].getPathy()));
			pathS[i].setComm_cost(this->CalcCommCost(pathS[i].getPathx(),pathS[i].getPathy()));
			total_cost += pathS[i].getNode_cost() + eps;
			total_comm_cost += pathS[i].getComm_cost();
			pathS[i].setPath_cost(total_cost);
			pathS[i].setPath_comm_cost(total_comm_cost);
			cout<<endl<<"S("<<pathS[i].getPathx()<<","<<pathS[i].getPathy()<<
					")="<<pathS[i].getNode_cost()<<", Total-cost="<<pathS[i].getPath_cost()<<", Comm-cost="<<pathS[i].getComm_cost()
					<<", Total-Comm-cost="<<pathV[i].getPath_comm_cost();
	}

}

/*
void LatLonToMapXY(const double lat, const double lon, double &x, double &y, const int res = 100 )
{
	double lat_deg = 110913.73;
	double lon_deg = 92901.14;

	double ox_deg = -118.8;
	double oy_deg = 33.25;

	double res_x = res;
	double res_y = res;

	double res_lat = res_y / lat_deg;
	double res_lon = res_x / lon_deg;

    // These are values for the region we are interested in.
	double lat_diff = 0.8833333;
	double lon_diff = 1.1;

	double max_lat_diff = lat_diff / res_lat;
	double max_lon_diff = lon_diff / res_lon;

	double max_y_diff = ceil( lat_diff * lat_deg / res_y);


	// Actual code for conversion
	x = ( lon - ox_deg ) / res_lon;
	y = max_y_diff - ( lat - oy_deg ) / res_lat;

	// lat = (max_y_diff-y) * res_lat + o_y_deg
}

void MapXYToLatLon( const double x, const double y, double &lat, double &lon, const int res = 100  )
{
	double lat_deg = 110913.73;
	double lon_deg = 92901.14;

	double ox_deg = -118.8;
	double oy_deg = 33.25;

	double res_x = res;
	double res_y = res;

	double res_lat = res_y / lat_deg;
	double res_lon = res_x / lon_deg;

    // These are values for the region we are interested in.
	double lat_diff = 0.8833333;
	double lon_diff = 1.1;

	double max_lat_diff = lat_diff / res_lat;
	double max_lon_diff = lon_diff / res_lon;

	double max_y_diff = ceil( lat_diff * lat_deg / res_y);

	// Actual code for conversion
	  lat = ( (max_y_diff - y) * res_lat ) + oy_deg;
	  lon = ( x * res_lon ) + ox_deg;
}
*/


bool AStar::getUseCommsMap() const
{
    return UseCommsMap;
}

void AStar::setUseCommsMap(bool UseCommsMap)
{
    this->UseCommsMap = UseCommsMap;
}

double AStar::GetCommRate(int x, int y)
{
	std::vector<Waypoint> bs_list;
	double bs_catalina_lon = -118.47815, bs_catalina_lat = 33.446742, bs_catalina_x, bs_catalina_y;
	double bs_ptfermin_lon = -118.294006, bs_ptfermin_lat = 33.704898, bs_ptfermin_x, bs_ptfermin_y;
	double bs_oil_plat_lon = -118.129778, bs_oil_plat_lat = 33.581496, bs_oil_plat_x, bs_oil_plat_y;
	double bs_redondo_lon = -118.3979, bs_redondo_lat = 33.857005, bs_redondo_x, bs_redondo_y;
	double bs_dockweiler_lon = -118.439084, bs_dockweiler_lat = 33.946853, bs_dockweiler_x, bs_dockweiler_y;
	double bs_newport_lon = -117.955029, bs_newport_lat = 33.6327, bs_newport_x, bs_newport_y;
	double bs_newport_pier_lon = -117.927026, bs_newport_pier_lat = 33.607713, bs_newport_pier_x, bs_newport_pier_y;
	double bs_mdelray_lat = 33.981464, bs_mdelray_lon = -118.441586, bs_mdelray_x, bs_mdelray_y;
	double bs_malibu_lat =  34.033223, bs_malibu_lon = -118.733722, bs_malibu_x, bs_malibu_y;

	commMap->LatLonToMapXY(bs_catalina_lat,bs_catalina_lon, bs_catalina_x, bs_catalina_y );
	commMap->LatLonToMapXY(bs_ptfermin_lat,bs_ptfermin_lon, bs_ptfermin_x, bs_ptfermin_y );
	commMap->LatLonToMapXY(bs_oil_plat_lat,bs_oil_plat_lon, bs_oil_plat_x, bs_oil_plat_y );
	commMap->LatLonToMapXY(bs_redondo_lat,bs_redondo_lon, bs_redondo_x, bs_redondo_y );
	commMap->LatLonToMapXY(bs_dockweiler_lat,bs_dockweiler_lon, bs_dockweiler_x, bs_dockweiler_y );
	commMap->LatLonToMapXY(bs_newport_lat,bs_newport_lon, bs_newport_x, bs_newport_y );
	commMap->LatLonToMapXY(bs_newport_pier_lat,bs_newport_pier_lon, bs_newport_pier_x, bs_newport_pier_y );
	commMap->LatLonToMapXY(bs_mdelray_lat, bs_mdelray_lon, bs_mdelray_x, bs_mdelray_y);
	commMap->LatLonToMapXY(bs_malibu_lat, bs_malibu_lon, bs_malibu_x, bs_malibu_y);

	Waypoint bs_catalina(bs_catalina_x,bs_catalina_y);
	Waypoint bs_ptfermin(bs_ptfermin_x,bs_ptfermin_y);
	Waypoint bs_oil_plat(bs_oil_plat_x,bs_oil_plat_y);
	Waypoint bs_redondo(bs_redondo_x,bs_redondo_y);
	Waypoint bs_dockweiler(bs_dockweiler_x,bs_dockweiler_y);
	Waypoint bs_newport(bs_newport_x,bs_newport_y);
	Waypoint bs_newport_pier(bs_newport_pier_x,bs_newport_pier_y);
	Waypoint bs_mdelray(bs_mdelray_x,bs_mdelray_y);
	Waypoint bs_malibu(bs_malibu_x, bs_malibu_y);

	bs_list.push_back(bs_catalina);
	bs_list.push_back(bs_ptfermin);
	bs_list.push_back(bs_oil_plat);
	bs_list.push_back(bs_redondo);
	bs_list.push_back(bs_dockweiler);
	bs_list.push_back(bs_newport_pier);
	bs_list.push_back(bs_newport);
	bs_list.push_back(bs_mdelray);
	bs_list.push_back(bs_malibu);


	Waypoint cur_loc(x,y);

	double range = 12e3;
	double comm_rate = 0, temp_comm_rate = 0;

	for ( int i = 0 ; i < bs_list.size(); i++ ) {
		double temp_range = this->GetDist(cur_loc,bs_list[i]) * 100;
		if( temp_range < 2e3 )
			temp_comm_rate = 5.5;
		else
		if( temp_range < range ) {
			range = temp_range;
			temp_comm_rate = -6.5e-12 * pow(range,3) + 2.2e-7 * pow(range,2) -0.0024*range + 9.4;
		}
		else {
			temp_comm_rate = 0;
		}
		if( temp_comm_rate > comm_rate ) {
			comm_rate = temp_comm_rate;
		}
	}

	if( range > 16e3 )
		comm_rate = 0;

	//if( comm_rate > 0)
	//	cout<<"Commrate="<<comm_rate<<endl;

	if( comm_rate <= 0 )
		return 0.25;

	else if( comm_rate > 5.5 )
		return 5.5;
	else
		return comm_rate;
}

double AStar::CalcCommCost(int x, int y)
{
	//if( this->getUseCommsMap() )
	return commMap->GetValue(x,y);
	/*else
		return D/GetCommRate(x,y);
		*/
}

MyImageMap AStar::GetRiskMap()
{
	return *riskMap;
}

MyImageMap AStar::GetCommsMap()
{
	return *commMap;
}

MyImageMap AStar::GetBathyMap()
{
	return *obsMap;
}

