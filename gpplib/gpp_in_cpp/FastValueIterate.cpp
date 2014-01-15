#include <fstream>
#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <algorithm>
#include <boost/unordered_map.hpp>
#include "DiGraph.h"
#include <boost/multi_array.hpp>

using namespace std;


struct StateActionStatePair {
	int state2;
	int action;

	double rwd;
	double transProb;
};


class MDP
{
	multimap<int,StateActionStatePair> rewardsFromState;
	map<int,string>   actionList;
	map<int,string>   statesList;

public:
	MDP()
	{}

	void ReadActions( string actionFileName) {
		ifstream ifs;
		ifs.open( actionFileName.c_str(), ifstream::in );

		const int MAX_LEN = 50;
		char action[ MAX_LEN ], buf[ MAX_LEN ];
		while( ifs.good() ) {
			ifs.getline( action, MAX_LEN );
			cout<< action << endl;
			int actionId, time, x1, y1, x2, y2;
			sscanf( action, "%d=%d,%d,%d,%d,%d",&actionId, &time, &x1, &y1, &x2, &y2 );
			sprintf(buf,"%d,%d,%d,%d,%d",time,x1,y1,x2,y2);
			actionList[ actionId ] = string(buf);
		}
		ifs.close();

		cout<<"Done";
	}

	void ValueIterate( int numIters ) {
		const int MAX_UTILS = 100;

	}

	void PrepareListOfActionsForStates() {
		// For every state, list all the possible string, action
	}

	void ReadRewards( string rewardFileName ) {
		ifstream ifs;
		ifs.open( rewardFileName.c_str(), ifstream::in );

		const int MAX_LEN = 50;
		char rewardStr[ MAX_LEN ], buf[ MAX_LEN ];
		while ( ifs.good() ) {
			ifs.getline( rewardStr, MAX_LEN );
			cout<< rewardStr <<  endl;
			int s2, s1, action; double reward;
			sscanf( rewardStr, "%d,%d,%d=%f", &s2, &s1, &action, &reward );
			sprintf( buf, "%d,%d,%d", s1, action, s2 );
			rewardList[ string(buf) ] = reward;
		}
		ifs.close();

		cout<<"Done";
	}

	void ReadTransitions( string transFileName ) {
		ifstream ifs;
		ifs.open( transFileName.c_str(), ifstream::in );

		const int MAX_LEN = 50;
		char transStr[ MAX_LEN ], buf[ MAX_LEN ];
		while (ifs.good() ) {
			ifs.getline( transStr, MAX_LEN );
			cout<< transStr << endl;
			int s2, s1, action; double prob;
			sscanf( transStr, "%d,%d,%d=%f", &s2, &s1, &action, &prob );
			sprintf( buf, "%d,%d,%d", s1, action, s2 );
			transProbs[ string(buf) ] = prob;
		}
		ifs.close();

		cout<<"Done";
	}


	void ReadStates( string stateFileName ) {
		ifstream ifs;

		ifs.open( stateFileName.c_str(), ifstream::in );

		const int MAX_LEN = 100;
		char state[ MAX_LEN ], buf[ MAX_LEN ];
		while ( ifs.good() ) {
			ifs.getline( state, MAX_LEN );
			cout<<state<<endl;
			int stateId, time, x, y;
			sscanf( state, "%d=%d,%d,%d",&stateId, &time, &x, &y );
			sprintf( buf, "%d,%d,%d", time, x, y );
			this->addState( stateId, string(buf)  );
			statesList[ stateId ] = string(buf);
		}
		ifs.close();

		cout<<"Done.";
	}

	virtual ~MDP() {
	}
};





int main(int argc, char *argv[])
{
	MDP mdp;
	cout<<"Hello World.";

	mdp.ReadStates( "../../GppPython/states.txt" );
	mdp.ReadActions("../../GppPython/actions.txt" );
	mdp.ReadTransitions("../../GppPython/transitions.txt");
	mdp.ReadRewards("../../GppPython/rewards.txt");

	return 0;
}
