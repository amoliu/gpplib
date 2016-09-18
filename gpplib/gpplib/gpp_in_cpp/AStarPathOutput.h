/*
 * AStarPathOutput.h
 *
 *  Created on: Jun 3, 2011
 *      Author: Arvind Antonio de Menezes Pereira
 *
 *      Desc: This class is designed to be a container for the path being planned.
 *      		The primary reason for creating this class is to provide a way of passing
 *      		the planned path back to Python.
 */

#ifndef ASTARPATHOUTPUT_H_
#define ASTARPATHOUTPUT_H_

#include <vector>
#include <string>
#include <iostream>
#include <sstream>
#include <exception>

using std::vector;
using std::iterator;
using std::string;
using std::cout;
using std::endl;
using std::ostringstream;
using std::exception;

class AStarPathOutput {
	vector<int> x;
	vector<int> y;
	vector<int> t;
	vector<double> riskCost;
	vector<double> totalRiskCost;
	vector<double> commCost;
	vector<double> totalCommCost;
	vector<double> gCost;
	vector<double> totalGCost;
public:
	AStarPathOutput();
	virtual ~AStarPathOutput();
	void addElement(int x, int y, double rCost, double totRiskCost, double commCost, double totCommCost, double gCost, double totGCost);
	void addElementT(int x, int y, int t, double rCost, double totRiskCost, double commCost, double totCommCost, double gCost, double totGCost);
	double getCommCost(int index);
	double getTotalCommCost(int index);
	double getGCost(int index);
	double getTotalGCost(int index);
	double getRiskCost(int index);
	double getTotalRiskCost(int index);
	int getX(int index);
	int getY(int index);
	int getT(int index);
	string displayXY(string s);
	void setX(int index, int x);
	void setY(int index, int y);
	void setT(int index, int t);
	void setCommCost(int index, double val);
	void setTotalCommCost(int index, double val);
	void setGCost(int index, double val);
	void setTotalGCost(int index, double val);
	void setRiskCost(int index, double val);
	void setTotalRiskCost(int index, double val);
	void clearPath();
	int  getPathSize();

	// Other useful general variables go here
	long numNodesExpanded;


};

#endif /* ASTARPATHOUTPUT_H_ */
