/*
 * AStarPathOutput.cpp
 *
 *  Created on: Jun 3, 2011
 *      Author: Arvind Antonio de Menezes Pereira
 */

#include "AStarPathOutput.h"
#include <boost/python.hpp>

BOOST_PYTHON_MODULE(PathOutput)
{
	using namespace boost::python;
	class_<AStarPathOutput>("PathOutput", init<>() )
			.def("addElement",&AStarPathOutput::addElement )
			.def("addElementT",&AStarPathOutput::addElementT)
			.def("getCommCost",&AStarPathOutput::getCommCost )
			.def("getTotalCommCost",&AStarPathOutput::getTotalCommCost )
			.def("getGCost",&AStarPathOutput::getGCost )
			.def("getTotalGCost",&AStarPathOutput::getTotalGCost)
			.def("getRiskCost",&AStarPathOutput::getRiskCost)
			.def("getTotalRiskCost",&AStarPathOutput::getTotalRiskCost)
			.def("getX",&AStarPathOutput::getX)
			.def("getY",&AStarPathOutput::getY)
			.def("getT",&AStarPathOutput::getT)
			.def("setX",&AStarPathOutput::setX)
			.def("setY",&AStarPathOutput::setY)
			.def("setCommCost",&AStarPathOutput::setCommCost)
			.def("setTotalCommCost",&AStarPathOutput::setTotalCommCost)
			.def("setGCost",&AStarPathOutput::setGCost)
			.def("setTotalGCost",&AStarPathOutput::setTotalGCost)
			.def("setRiskCost",&AStarPathOutput::setRiskCost)
			.def("setTotalRiskCost",&AStarPathOutput::setTotalRiskCost)
			.def("displayXY",&AStarPathOutput::displayXY)
			.def("clearPath",&AStarPathOutput::clearPath)
			.def("getPathSize",&AStarPathOutput::getPathSize)
			.def_readonly("numNodesExpanded",&AStarPathOutput::numNodesExpanded)
			;
}

AStarPathOutput::AStarPathOutput() {
	// TODO Auto-generated constructor stub

}

AStarPathOutput::~AStarPathOutput() {
	// TODO Auto-generated destructor stub
}

int AStarPathOutput::getPathSize()
{
	return x.size();
}

string AStarPathOutput::displayXY(string s="")
{
	string s2;
	ostringstream oss;
	for(int i=0; i<this->x.size(); i++ ) {
		try{
			oss<<s<<"("<<this->x[i]<<","<<this->y[i]<<")="<<this->riskCost[i]<<", Total-cost="<<this->totalRiskCost[i]<<", Comm-cost="<< this->commCost[i]
			   <<", Total-Comm-cost="<<this->totalCommCost[i]<<", G-cost="<<this->gCost[i]<<", Total-G-cost="<<this->totalGCost[i]<<endl;
		}
		catch (exception &e)
		{
			cout<<"Error. "<< e.what() << endl;
		}
	}
	s2 = oss.str();
	return s2;
}

void AStarPathOutput::clearPath()
{
	this->x.clear();
	this->y.clear();
	this->t.clear();
	this->riskCost.clear();
	this->totalRiskCost.clear();
	this->commCost.clear();
	this->totalCommCost.clear();
	this->gCost.clear();
	this->totalGCost.clear();
}

void AStarPathOutput::addElement(int x, int y, double rCost, double totRiskCost, double commCost, double totCommCost, double gCost, double totGCost )
{
	this->x.push_back(x);
	this->y.push_back(y);
	this->riskCost.push_back(rCost);
	this->totalRiskCost.push_back(totRiskCost);
	this->commCost.push_back(commCost);
	this->totalCommCost.push_back(totCommCost);
	this->gCost.push_back(gCost);
	this->totalGCost.push_back(totGCost);
}

void AStarPathOutput::addElementT(int x, int y, int t, double rCost, double totRiskCost, double commCost, double totCommCost, double gCost, double totGCost)
{
	this->x.push_back(x);
	this->y.push_back(y);
	this->t.push_back(t);
	this->riskCost.push_back(rCost);
	this->totalRiskCost.push_back(totRiskCost);
	this->commCost.push_back(commCost);
	this->totalCommCost.push_back(totCommCost);
	this->gCost.push_back(gCost);
	this->totalGCost.push_back(totGCost);
}

double AStarPathOutput::getCommCost(int index)
{
	if( index >= this->commCost.size() ) {
		throw std::exception();
	}
	else return commCost[index];
}

double AStarPathOutput::getTotalCommCost(int index)
{
	if( index >= this->commCost.size() ) {
			throw std::exception();
	}
	else
		return this->totalCommCost[index];
}

double AStarPathOutput::getGCost(int index)
{
	if( index >= this->commCost.size() ) {
			throw std::exception();
	}
	else
		return this->gCost[index];
}

double AStarPathOutput::getTotalGCost(int index)
{
	if( index >= this->commCost.size() ) {
			throw std::exception();
	}
	else
		return this->totalGCost[index];
}

double AStarPathOutput::getRiskCost(int index)
{
	if( index >= this->commCost.size() ) {
			throw std::exception();
	}
	else return this->riskCost[index];
}

double AStarPathOutput::getTotalRiskCost(int index)
{
	return this->totalRiskCost[index];
}

int AStarPathOutput::getX(int index)
{
	return this->x[index];
}

int AStarPathOutput::getY(int index)
{
	return this->y[index];
}

int AStarPathOutput::getT(int index)
{
	return this->t[index];
}

void AStarPathOutput::setX(int index, int x)
{
	if(this->x[index]>=0 && x< this->x.size())
		this->x[index] = x;
}

void AStarPathOutput::setY(int index, int y)
{
	if(this->y[index]>=0 && y<this->y.size())
		this->y[index] = y;
}

void AStarPathOutput::setT(int index, int t)
{
	if(this->t[index]>=0 && t<this->t.size())
		this->t[index] = t;
}

void AStarPathOutput::setCommCost(int index, double val )
{
	this->commCost[index] = val;
}

void AStarPathOutput::setTotalCommCost(int index, double val )
{
	this->totalCommCost[index]= val;
}

void AStarPathOutput::setGCost(int index, double val )
{
	this->gCost[index] = val;
}

void AStarPathOutput::setTotalGCost(int index, double val )
{
	this->totalGCost[index] = val;
}

void AStarPathOutput::setRiskCost(int index, double val )
{
	this->riskCost[index] = val;
}

void AStarPathOutput::setTotalRiskCost(int index, double val )
{
	this->totalRiskCost[index] = val;
}

