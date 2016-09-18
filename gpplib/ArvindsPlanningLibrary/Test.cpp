#include <iostream>
#include <fstream>
#include "DiGraph.h"

using namespace std;

int main() {

	ifstream fin ("tinyDG.txt", std::ifstream::in );

	cout<<"Hello World!"<<endl;

	EdgeWeightedDigraph dg(cin);

	fin.close();

	return 0;
}

