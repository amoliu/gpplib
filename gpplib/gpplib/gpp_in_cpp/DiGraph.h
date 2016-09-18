/*
 * DiGraph.h
 *
 *  Created on: Jul 6, 2013
 *      Author: Arvind A. de Menezes Pereira
 *      Web   : http://robotics.usc.edu/~ampereir
 *      Email : arvind.pereira [at] gmail.com
 */

#ifndef DIGRAPH_H_
#define DIGRAPH_H_

#include <vector>
#include <list>
#include <map>
#include <iostream>
#include <stdexcept>
#include <cassert>
#include <string>

using namespace std;

template<typename Key, typename Value>
struct State {
	Key id;
	Value U;
	Value Uprime;
	string stateStr;

	friend void swap( State &a, State &b ) {
		std::swap( a.id, b.id );
		std::swap( a.U, b.U );
		std::swap( a.Uprime, b.Uprime );
		std::swap( a.stateStr, b.stateStr );
	}

	friend ostream& operator<< (ostream &os, State<Key,Value> &vert ) {
		os <<"State "<< vert.id << " : " << vert.U<<" : "<< vert.Uprime<<" : "<< vert.stateStr;
		return os;
	}

	State() {}

	State( const State &state ) :
		id( state.id ),
		U( state.U ),
		Uprime( state.Uprime ),
		stateStr( state.stateStr )
	{ }

	State& operator=( State state ) {
		swap( *this, state );
		return *this;
	}

	virtual ~State() {
		cout<<"Deleting "<<(*this)<<'\n';
	}
};


template<typename Key, typename Value, typename EdgetransProb >
struct Transition {
	State<Key,Value>* vVert;
	State<Key,Value>* wVert;
	Key action;
	string transString;
	EdgetransProb  transProb;
	Value     		reward;

	friend void swap( Transition &a, Transition &b ) {
		std::swap( a.vVert, b.vVert );
		std::swap( a.wVert, b.wVert );
		std::swap( a.transProb, b.transProb );
		std::swap( a.reward, b.reward );
	}

	Transition() :
		vVert( NULL ),
		wVert( NULL ),
		transProb( 0 ),
		reward( 0 )
	{}

	Transition( const Transition& de ) :
		vVert( de.vVert ),
		wVert( de.wVert ),
		transProb( de.transProb ),
		action( de.action ),
		transString( de.transString ),
		reward( de.reward )
	{}

	void setTransProb( EdgetransProb prob ) {
		transProb = prob;
	}

	EdgetransProb getTransProb() {
		return transProb;
	}



	Transition& operator=(Transition& de) {
		swap( *this, de );
		return *this;
	}

	friend ostream& operator<< (ostream &os, Transition<Key,Value,EdgetransProb> &edge ) {
		os <<"Edge " << edge.vVert->k <<"->"<< edge.wVert->k << " : " << edge.transProb ;
		return os;
	}

	virtual ~Transition() {
		cout<<"Deleting "<<(*this)<<'\n';
	}
};


/** A Class which defines an edge-weighted digraph */
template <typename Key, typename Value, typename EdgetransProb>
class DiGraph {
	int V;
	int E;
	// Clearly, I love STL maps.
	map<pair<Key,Key>,Transition<Key,Value,EdgetransProb>* > edges;
	map<Key,State<Key,Value>*> states;
	map<Key,vector<Transition<Key,Value,EdgetransProb>*> > inEdges;
	map<Key,vector<Transition<Key,Value,EdgetransProb>*> > outEdges;
	vector<pair<Key,Key> > edgeList;
	vector< Key > StateList;


public:
	DiGraph() : V(0), E(0)
	{}

	friend void swap( DiGraph<Key,Value,EdgetransProb> &a, DiGraph<Key,Value,EdgetransProb> &b ) {
		std::swap( a.V, b.V );
		std::swap( a.E, b.E );
		std::swap( a.edges, b.edges );
		std::swap( a.inEdges, b.inEdges );
		std::swap( a.outEdges, b.outEdges );
		std::swap( a.edgeList, b.edgeList );
		std::swap( a.StateList, b.StateList );
	}

	DiGraph( const DiGraph<Key,Value,EdgetransProb> &dg ) : V(0), E(0)
	{
		// Add all the states from dg
		for( unsigned i=0; i< dg.StateList.size(); i++ ) {
			const Key &State = dg.StateList[i];
			Key k = dg.states.find( State )->second->k;
			Value v = dg.states.find( State )->second->v;

			this->addState( k, v );
		}
		// Add all the edges from dg
		for( unsigned i=0; i< dg.edgeList.size(); i++ ) {
			const pair<Key,Key> &edge = dg.edgeList[i];
			/// Wish there was a way around having to keep finding this over and over...
			Key v = dg.edges.find( edge )->second->vVert->k;
			Key w = dg.edges.find( edge )->second->wVert->k;
			Key transProb = dg.edges.find( edge )->second->transProb;

			this->addEdge( v, w, transProb );
		}
	}

	DiGraph& operator=( DiGraph dg ) {
		swap( *this, dg );
		return *this;
	}

	void addState( Key id, Value U ) {
		if( states.find( id ) == states.end() ) {
			states[ id ] = new State<Key,Value>();
			this->V++; //increase number of states.
			StateList.push_back( id );
			vector<Transition<Key,Value,EdgetransProb>* > inEdgeList;
			inEdges[ id ] = inEdgeList;
			vector<Transition<Key,Value,EdgetransProb>* > outEdgeList;
			outEdges[ id ] = outEdgeList;
		}
		states[ id ]->id = id;
		states[ id ]->U = U;
	}

	bool hasState( Key k ) {
		return states.find( k )!= states.end();
	}

	void addEdge( Key v, Key w, Key action, Value rwd, EdgetransProb transProb ) {
		assert( this->hasState(v) && this->hasState(w) );

		if( hasEdge( v, w, action ) ) {
			edges[ pair<Key,Key>(v,w) ] = new Transition<Key,Value,EdgetransProb>();
			this->E++; // Increase number of edges.
			edgeList.push_back( pair<Key,Key>(v,w) );
			// Update the outEdges for the State v
			outEdges[ v ].push_back( edges[ pair<Key,Key>(v,w) ] );
			inEdges [ w ].push_back( edges[ pair<Key,Key>(v,w) ] );
		}
		edges[ pair<Key,Key>(v,w) ]->transProb = transProb;
		edges[ pair<Key,Key>(v,w) ]->vVert = states[ v ];
		edges[ pair<Key,Key>(v,w) ]->wVert = states[ w ];
	}

	bool hasEdge( Key v, Key w, Key action ) {
		if( edges.find( pair<Key,Key>(v,w) ) != edges.end() ) {
			if ( edges[ pair<Key,Key>(v,w) ]->action == action ) {
				return true;
			}
			else return false;
		}
		else return false;
	}

	EdgetransProb getTransProb( Key v, Key w, Key action ) {
		if( this->hasEdge( v, w ) )
			return edges[ pair<Key,Key>(v,w) ]->transProb;
		else
			throw runtime_error("Edge not found");
	}

	void updateRewardOfEdge( Key v, Key w, Key action, Value _reward ) {
		if( this->hasEdge(v,w) )
			edges[ pair<Key,Key>(v,w) ]->reward = _reward;
		else
			throw runtime_error("Edge not found");
	}

	void updateTransProbOfEdge( Key v, Key w, Key action, EdgetransProb _prob ) {

	}

	vector<Transition<Key,Value,EdgetransProb>*>& getOutEdges( Key k ) {
		return this->outEdges[ k ];
	}

	vector<Transition<Key,Value,EdgetransProb>*>& getInEdges( Key k ) {
		return this->inEdges[ k ];
	}

	State<Key, Value>* getState( Key k ) {
		return *states.find(k);
	}

	Transition<Key,Value,EdgetransProb>* getEdge( Key v, Key w ) {
		return *edges.find(pair<Key,Key>(v,w));
	}

	vector<pair<Key,Key> > getEdgeList() const
	{
		return this->edgeList;
	}

	vector< Key > getStateList() const
	{
		return this->StateList;
	}

	int getNumstates() {
		return V;
	}

	int getNumEdges() {
		return E;
	}

	virtual ~DiGraph() {
		// Delete all the edges
		for( int i=0; i< edgeList.size(); i++ ) {
			delete edges[ edgeList[i] ];
		}
		// Delete all the states
		for( int i=0; i< StateList.size(); i++ ) {
			delete states[ StateList[i] ];
		}
	}


	friend istream& operator >> ( istream& is, DiGraph<Key,Value,EdgetransProb> &dg ) {
		int numstates = 0;
		is>>numstates;
		if( numstates < 0 ) throw invalid_argument( "Error. Number of states cannot be less than zero." );
		Key key; Value value;
		for( int i=0; i<numstates; i++ ) {
			if( !(is>>key>>value) ) throw invalid_argument( "Error parsing file. Expected Key Value pair." );
			dg.addState( key, value );
		}
		/// Now read in and add the edges.
		Key v, w; EdgetransProb transProb;
		while( is>>v>>w>>transProb ) {
			dg.addEdge( v, w, transProb );
		}

		return is;
	}
};





#endif /* DIGRAPH_H_ */
