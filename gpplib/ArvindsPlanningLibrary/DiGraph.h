#ifndef __ARVIND_DI_GRAPH_H__
#define __ARVIND_DI_GRAPH_H__

#include <string>
#include <cstdio>
#include <stack>
#include <vector>
#include <cstdlib>
#include <time.h>
#include <iostream>
#include <fstream>

using namespace std;

class DirectedEdge {
	int v;
	int w;
	double weight;
	char edgeStr[256];

public:
	DirectedEdge ( int _v, int _w, double _weight ) : v(v), w(_w), weight(_weight)
	{	sprintf(edgeStr,"%d -> %d = %5.2f",v,w,weight);		}

	int from() { return v; }

	int to() { return w; }

	double getWeight() { return weight; }

	char *getEdgeStr() {
		return edgeStr;
	}
};

class EdgeWeightedDigraph {
	int V;
	int E;
	vector<vector <DirectedEdge> > adj;

public:
	/** EdgeWeightedDigraph( int V )
	  @param _V The number of vertices in the Graph
	*/
	EdgeWeightedDigraph(int _V) : V(_V) {
		InitializeDigraph(_V);
	}

	void InitializeDigraph(int _V) {
		if( _V<0 ) throw _V; // Illegal Argument.

		for( int v=0; v<V; v++ ) {
			vector<DirectedEdge> listOfEdges;
			adj.push_back(listOfEdges);
		}
	}

	/**	Create a random edge-weighted digraph with V vertices and E edges.
	*
	*/
	EdgeWeightedDigraph(int _V, int _E) {
		if( _V< 0 ) throw _V;
		this->InitializeDigraph(_V);

		srand(time(NULL));
		if( _E<0 ) throw _E;
		for ( int i=0; i<E; i++ ) {
			int v = rand() % V;
			int w = rand() % V;
			double weight = (rand() %100)/100.0;
			DirectedEdge e( v, w, weight );
			addEdge( e );
		}
	}

	/** Create an Edge-weighted digraph from an input stream.
	*
	*/
	EdgeWeightedDigraph( istream& In ) {
		int _V; In>>_V; if (_V<0) throw _V;
		cout<<_V<<endl;

		this->InitializeDigraph(_V);

		int _E; In>>_E; if( _E<0 ) throw _E;
		cout<<_E<<endl;
		for( int i=0; i< _E; i++ ) {
			int v, w; double weight;
			In>>v>>w>>weight;
			cout<<v<<","<<w<<","<<weight<<endl;
			DirectedEdge e(v,w,weight);
			addEdge( e );
		}
	}

	EdgeWeightedDigraph(EdgeWeightedDigraph& G) {
		this->InitializeDigraph(G.getV());

		E = G.getE();
		for( int v=0; v<G.getV(); v++ ) {
			stack<DirectedEdge> reverse;
			vector<DirectedEdge> adjG = G.getAdj(v);
			for( unsigned i=0; i<adjG.size(); i++) {
				reverse.push(adjG[i]);
			}
			for( unsigned i=0; i<reverse.size(); i++ ) {
				adj[v].push_back(reverse.top()); reverse.pop();
			}
		}
	}

	/** Get the number of vertices */
	int getV() { return V; }

	/** Get the number of edges */
	int getE() { return E; }

	/** Get the adjacency list for a given vertex */
	vector<DirectedEdge> getAdj( int v ) { return adj[v]; }


	/** Add the directed edge e to this graph */
	void addEdge( DirectedEdge e ) {
		int v = e.from();
		adj[v].push_back(e);
		E++;
	}

	/** Return all edges in this digraph */
	vector<vector<DirectedEdge> >::iterator getEdges() {
		vector<vector<DirectedEdge> > list;
		for(int v=0;v<V;v++) {
			vector<DirectedEdge> adj = getAdj(v);
			list.push_back(adj);
		}

		return list.begin();
	}

	/** Return the number of edges incident from v. */
	int outdegree( int v ) {
		return adj[v].size();
	}

};






#endif
