/*
 * Waypoint.h
 *
 *  Created on: Apr 21, 2011
 *      Author: arvind
 */

#ifndef WAYPOINT_H_
#define WAYPOINT_H_

class Waypoint{
private:
	int pathx;
	int pathy;
	int patht;
	double node_cost;
	double path_cost;
	double comm_cost;
	double path_comm_cost;
	double height;
	double lat;
	double lon;
	double node_g_cost;
	double path_g_cost;

public:
	Waypoint() {}
	Waypoint( int px, int py, int nc, int pc) { pathx = px; pathy = py; node_cost = nc; path_cost = pc; }
	Waypoint( int px, int py, int pt, int nc, int pc) { pathx = px; pathy = py; patht = pt; node_cost = nc; path_cost = pc; }
	Waypoint( int px, int py) { pathx = px; pathy = py; }
	Waypoint( int px, int py, int nc ) { pathx = px; pathy = py; node_cost = nc; }
	//Waypoint( int px, int py, int pt, int nc) { pathx= px; pathy = py; patht = pt; node_cost = nc; }
    double getNode_cost() const
    {
        return node_cost;
    }

    double getPath_cost() const
    {
        return path_cost;
    }

    int getPathx() const
    {
        return pathx;
    }

    int getPathy() const
    {
        return pathy;
    }

    int getPatht() const
    {
    	return patht;
    }

    void setNode_cost(double node_cost)
    {
        this->node_cost = node_cost;
    }

    void setPath_cost(double path_cost)
    {
        this->path_cost = path_cost;
    }

    void setPathx(int pathx)
    {
        this->pathx = pathx;
    }

    void setPathy(int pathy)
    {
        this->pathy = pathy;
    }

    void setPatht(int pt)
    {
    	this->patht = pt;
    }

    // A few Member Functions
	bool operator < ( const Waypoint B) {
		if( this->node_cost < B.getNode_cost() )
			return true;
		else return false;
	}
	bool operator > ( const Waypoint B) {
		if( this->node_cost > B.getNode_cost() )
			return true;
		else return false;
	}
	bool operator == ( const Waypoint B) {
		if( this->pathx == B.getPathx() && this->pathy == B.getPathy() && this->node_cost == B.getNode_cost() ) {
			return true;
		}
		else return false;
	}

	double getComm_cost() const
	{
	    return comm_cost;
	}

	double getPath_comm_cost() const
	{
	    return path_comm_cost;
	}

	void setComm_cost(double comm_cost)
	{
	    this->comm_cost = comm_cost;
	}

	void setPath_comm_cost(double path_comm_cost)
	{
	    this->path_comm_cost = path_comm_cost;
	}

    double getHeight() const
    {
        return height;
    }

    double getLat() const
    {
        return lat;
    }

    double getLon() const
    {
        return lon;
    }

    void setHeight(double height)
    {
        this->height = height;
    }

    void setLat(double lat)
    {
        this->lat = lat;
    }

    void setLon(double lon)
    {
        this->lon = lon;
    }

    double getPath_g_cost() const
    {
        return path_g_cost;
    }

    void setPath_g_cost(double path_g_cost)
    {
        this->path_g_cost = path_g_cost;
    }

    double getNode_g_cost() const
    {
        return node_g_cost;
    }

    void setNode_g_cost(double node_g_cost)
    {
        this->node_g_cost = node_g_cost;
    }

};

#endif /* WAYPOINT_H_ */
