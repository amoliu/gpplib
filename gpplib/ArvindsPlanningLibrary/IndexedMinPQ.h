/*
 * IndexMinPQ.h
 *
 *  Created on: Jul 8, 2013
 *      Author: Arvind de Menezes Pereira
 */
#ifndef INDEXMINPQ_H_
#define INDEXMINPQ_H_

#include <vector>
#include <iostream>
#include <stdexcept>

using namespace std;

template<typename Key>
class IndexMinPQ {
	int N_;
	int NMAX;
	vector <int> pq;
	vector <int> qp;
	vector <Key> keys;

	// -- Protected Methods --
	void swim( int k ) {
		while ( k>1 && greater(k/2,k) ) {
			exch( k, k/2 );
			k = k/2;
		}
	}

	void sink( int k ) {
		while( 2*k <= N_ ) {
			int j = 2*k;
			if( j < N_ && greater( j, j+1) ) j++;
			if( !greater( k, j )) break;
			exch( k, j );
			k = j;
 		}
	}

	bool greater( int i, int j ) {
		return keys[ pq[i] ] > keys[ pq[j] ];
	}

	void exch( int i, int j ) {
		int swap = pq[i]; pq[i] = pq[j]; pq[j] = swap;
		qp[pq[i]] = i; qp[pq[j]] = j;
	}


public:
	/** Create an empty indexed priority queue */
	IndexMinPQ( int _MAX )
	{
		N_ = 0;
		if( _MAX < 0 ) throw invalid_argument( "Priority Queue size cannot be negative." );
		NMAX = _MAX;
		pq.resize( _MAX+1 );
		qp.resize( _MAX+1 );
		keys.resize( _MAX+1 );
		for ( int i=0; i<= NMAX; qp[i++] = -1 ); // Initialize everything in inverse of pq to -1
	}

	/** Is priority queue empty? */
	bool isEmpty() { return N_ ==0; }

	/** Get the number of keys on the priority queue */
	int size() { return N_; }

	/** Is i an index on the priority queue?
	 *
	 * @param i
	 */
	bool contains( int i ) {
		if( i<0 || i >=NMAX ) throw out_of_range("Index i is out of range.");
		return qp[i] != -1;
	}

	/** Associate key with index i.
	 *	@throws out_of_range unless 0 <= i < MAX
	 *	@throws invalid_argument if there is already an item associated with the index i.
	 */
	void insert( int i, Key key ) {
		if( i<0 || i>=NMAX ) throw out_of_range("Index out of range.");
		if( contains(i) ) throw invalid_argument("Index is already in the priority queue.");
		N_++;
		qp[ i ] = N_;
		pq[ N_ ] = i;
		keys[ i ] = key;
		swim( N_ );
	}

	/** Return the index associated with a minimal key.
	 * @throws underflow_error if priority queue is empty
	 */
	int minIndex() {
		if( N_ ==0 ) throw underflow_error("Priority queue underflow");
		return pq[1];
	}

	/** Return the minimal key.
	 * @throws underflow_error if priority queue is empty
	 */
	Key minKey() {
		if( N==0 ) throw underflow_error("Priority queue underflow");
		return keys[pq[1]];
	}

	/** Delete a minimal key and return its associated index.
	 * @throws underflow_error if priority queue is empty
	 */
	int delMin() {
		if( N_ ==0 ) throw underflow_error("Priority queue underflow");
		int min = pq[1];
		exch( 1, N_ -- );
		sink( 1 );
		qp[min] = -1; // delete
		// keys[pq[N+1]] = NULL; // remove it.
		pq[N_ +1] = -1;
		return min;
	}

	/** Return the key associated with index i.
	 * @throws out_of_range unless 0<= i < MAX
	 * @throws invalid_argument if no key is associated with index i
	 */
	Key keyOf( int i ) {
		if( i<0 || i>= NMAX ) throw out_of_range("Index i is out of range.");
		if( !contains(i) ) throw invalid_argument("Index i is not in the priority queue.");
		else return keys[ i ];
	}


	/** Return the key associated with index pq[i].
	 * @throws out_of_range unless 0<=i <MAX
	 * @throws invalid_argument if no key is associated with index i
	 */
	Key keyOfPq( int i ) {
		return keyOf( pq[i] );
	}


	/** Change the key associated with index i to the specified value.
	 * @throws out_of_range unless 0<= i < MAX
	 * @throws invalid_argument if no key is associated with index i
	 */
	void changeKey( int i, Key key ) {
		if( i<0 || i>= NMAX ) throw out_of_range("Index i is out of range.");
		if( !contains(i) ) throw invalid_argument("Index i is not in the priority queue.");
		keys[ i ] = key;
		swim( qp[i] );
		sink( qp[i] );
	}

	/** Decrease the key associated with index i to the specified value.
	 * @throws out_of_range unless 0<= i < MAX
	 * @throws invalid_argument if key >= key associated with index i
	 * @throws invalid_argument if no key is associated with index i
	 */
	void decreaseKey( int i , Key key ) {
		if( i<0 || i>= NMAX ) throw out_of_range("Index i is out of range.");
		if( !contains(i)) throw invalid_argument("Index i is not in the priority queue.");
		if( keys[i]<= key ) throw invalid_argument("Calling decrease_key() with given argument would not strictly decrease the key.");
		keys[ i ] = key;
		swim( qp[i] );
	}

	/** Increase the key associated with the index i to the specified value.
	 * @throws out_of_range unless 0<= i < MAX
	 * @throws invalid_argument if key >= key associated with index i
	 * @throws invalid_argument if no key is associated with index i
	 */
	void increaseKey( int i, Key key ) {
		if( i<0 || i>= NMAX ) throw out_of_range("Index i is out of range.");
		if( !contains(i) ) throw invalid_argument("Index i is not in the priority queue.");
		if( keys[i]>=key ) throw invalid_argument("Calling increase_key() with given argument would not strictly increase the key.");
		keys[ i ] = key;
		sink( qp[i] );
	}

	/** Delete the key associated with index i.
	 * @throws out_of_range unless 0<= i < MAX
	 * @throws invalid_argument if no key is associated with index i
	 */
	void deleteKey( int i ) {
		if( i<0 || i>= NMAX ) throw out_of_range("Index i is out of range.");
		if( !contains(i) ) throw invalid_argument("Index i is not in the priority queue.");
		int index = qp[ i ];
		exch( index, N_ -- );
		swim( index );
		sink( index );
		qp[ i ] = -1;
	}

};

#endif /* INDEXMINPQ_H_ */
