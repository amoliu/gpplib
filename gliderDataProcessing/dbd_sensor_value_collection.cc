// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_value_collection.cc

24-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
26-Sep-01 tc@DinkumSoftware.com support for doubles
31-Dec-03 trout.r@comcast.net Added filter_data(dbd_sensor_value_collection&,
    				                            const vector<bool>&)
30-Jan-04 trout.r@comcast.net Added is_valid(vector<dbd_sensor_info> &,
                                             const string)
24-Sep-09 tc@DinkumSoftware.com Made lookup_as_double const
25-Sep-09 tc@DinkumSoftware.com Added lookup()
 */

#include "dbd_sensor_value_collection.h"
#include "dbd_sensor_cycle_state.h"
#include "dbdfrmat.h"

using namespace dinkum_binary_data ;

/// constructor, makes empty collection from binary header
/*
\param hdr Binary header, describes the sensors to be read
 */

dbd_sensor_value_collection::dbd_sensor_value_collection(const dbd_header & hdr)
  :
  sensors_per_cycle(hdr.sensors_per_cycle)
{

  // Just set the size of our vector
  reserve( sensors_per_cycle ) ;

  // Init all our elements
  reset() ;
  for ( int i=0 ; i < sensors_per_cycle ; i++)
    (*this)[i].reset() ;

}


/// constructor, makes empty collection from ascii header
/*
\param hdr Ascii header, describes the sensors to be read
 */

dbd_sensor_value_collection::dbd_sensor_value_collection(const dbd_asc_header & hdr)
  :
  sensors_per_cycle(hdr.sensors_per_cycle)
{

  // Just set the size of our vector
  reserve( sensors_per_cycle ) ;

  // Init all our elements
  reset() ;

}


/// Reads a single cycles worth of binary sensor data
/**
   \param hdr Describes data to be read
   \param ins where to read it from
   \param all_sensors_must_be_present true means all sensors must be in file

\return Normally returns true, returns false on end of data or EOF

Throws an exception on any kind of error

 */

bool dbd_sensor_value_collection::read_bin ( const dbd_header & hdr, istream & ins,
                                             bool all_sensors_must_be_present) 
                                             throw (dbd_error)
{
  // Read the start of cycle tag
  // Returns true if sees ENDFILE_CYCLE_TAG
  if (read_cycle_tag( ins, DATA_CYCLE_TAG ) )
    return false ; // We ran out of data

  // Figure out what changed this cycle by reading it from the file
  dbd_sensor_cycle_state state(hdr) ;
  ins >> state ;

  // Loop over each sensor
  for ( int i = 0 ; i < sensors_per_cycle ; i++)
    {
      // The element in question
      dbd_sensor_value & elem = (*this)[i] ;
      
      // Figure out how we get it's value
      if ( state.in_data_stream(i) )
        {
          // read and store it
          elem.read_sensor_value( ins, hdr.infile_sensor_list[i],
                                  hdr.swab_info ) ;

        }
      else if ( all_sensors_must_be_present )
        {
          // Caller said it was in data stream and it's not
          ostringstream emsg ;
          emsg << "sensor " << hdr.infile_sensor_list[i].name
               << ": not in input file (initial line missing?)" ;
          throw ( dbd_error (emsg) ) ;
        }
      else if ( state.updated_with_same_value(i) )
        {
          // It's there from last time
          // But it could be invalid if we had interventing cycles
          // where it wasn't updated
          elem.validate() ;
        }
      else if ( state.not_updated(i) )
        {
          // Are we suppose to use the last value?
          if ( ! hdr.are_filling() )
            {
              // Nope, invalidate the value
              elem.reset() ;
            }
        }
      else
        {
          // We shouldn't be here
          throw (dbd_error("dbd_sensor_value_collection::read() software error") ) ;
        }
    }


  // Tell um if we ran out of file
  return ! ins.eof() ;

}


/// Reads a cycle of ascii data
/**

\param ins stream to read from

\return Normally returns true, returns false on EOF

*/

bool dbd_sensor_value_collection::read_asc( istream & ins ) throw (dbd_error)
{

  // Loop over each sensor
  for ( int i = 0 ; i < sensors_per_cycle ; i++)
    {
      // The element in question
      dbd_sensor_value & elem = (*this)[i] ;
      
      // Read everything as a double
      elem.read_asc_double( ins ) ;

    }

  // Tell um if we ran out of file
  return !ins.eof() ;

}


/// Reads a cycle of ascii data
/**

\param str string to read from

\return Normally returns false, returns true on error

*/

bool dbd_sensor_value_collection::read_asc( string  & str ) throw (dbd_error)
{

  bool return_value = false ; // what we return, true means error

  // Loop over each sensor
  for ( int i = 0 ; i < sensors_per_cycle ; i++)
    {
      // The element in question
      dbd_sensor_value & elem = (*this)[i] ;
      
      // Parse out one token
      char c ;
      string token ;
      do   // consume whitespace
        {
          c = str[0] ;      // extract first char
          str.erase(0,1) ;  // then remove it
        }
      while ( isspace(c) ) ;

      // init to first non-whitespace and copy til whitespace
      token = c ; 
      while ( !isspace( str[0] ) )
        {
          token += str[0] ;  // copy first char
          str.erase(0,1) ;  // then remove it          
        }

      // Read everything as a double
      elem.read_asc_double( token ) ;

      // Remember any errors
      return_value |= !elem.is_valid() ;

    }

  // tell um how it went
  return return_value ;
}




/// Writes a cycles worth of ascii data
/**

   \param ahdr Describes the data to be written
   \param outs Where to write the data

 */

void dbd_sensor_value_collection::write_asc( const dbd_asc_header & ahdr, ostream & outs )
{

  // Loop over each sensor
  for ( int i = 0 ; i < sensors_per_cycle ; i++)
    {
      // The element in question
      dbd_sensor_value & elem = (*this)[i] ;
      
      // Write it
      if ( !elem.is_valid() )
        {
          outs << invalid_sensor_str() ;
        }
      else if ( elem.is_int() )
        {
          outs << elem.get_int() ;
        }
      else if ( elem.is_float() )
        {
          outs << elem.get_float() ;
        }
      else if ( elem.is_double() )
        {
          // Change the formatting to get all the digits
          const streamsize prev_precision = outs.precision(DBL_DIG) ;
          outs << elem.get_double() ;
          outs.precision(prev_precision) ; // restore it

        }
      else
        {
          // Shouldn't be here
          throw (dbd_error("dbd_sensor_value_collection::write_asc() software error") ) ;
        }

      outs << ahdr.fill_char() ;

    }

  // close the line off
  outs << endl ;
}




/// Looks up sensor_name in sensor_list and returns its value
/**
   \param sensor_list  Where to lookup the name
   \param sensor_name  What to lookup

   \return Returns the value of sensor_name as a double


 */
double dbd_sensor_value_collection::lookup_as_double(
                const vector<dbd_sensor_info> & sensor_list,
                const string sensor_name) const
  throw (dbd_error)
{

  // scan all the sensors looking for a match by name
  for (int s=0 ; s < sensors_per_cycle ; s++)
    {
      // Look thru the list of names for a match
      if (sensor_list[s].name == sensor_name )
        {
          // We found the sensor, make a reference to it
          const dbd_sensor_value & elem =  (*this)[s] ;

          // covert it's type to double and return it
          if      ( elem.is_double()) return elem.get_double() ;
          else if ( elem.is_float ()) return elem.get_float () ;
          else if ( elem.is_int   ()) return elem.get_int   () ;
          else
            {
              // Unknown type of data
              ostringstream emsg ;
              emsg << "lookup_as_double(): Unknown sensor_value type: "
                   << sensor_list[s].name ;
              throw (dbd_error(emsg)) ;
            }
        }
    }

  // If we got here, we didn't find the sensor
  ostringstream emsg ;
  emsg << "lookup_as_double(): Unknown sensor: "
       << sensor_name ;
  throw (dbd_error(emsg)) ;    // die
  
}


/// Looks up sensorr_name in sensor_list and returns a reference
/**
   \param sensor_list  Where to lookup the name
   \param sensor_name  What to lookup

   \return Reference to the value


 */
dbd_sensor_value & dbd_sensor_value_collection::lookup(
                                                             vector<dbd_sensor_info> & sensor_list,
                                                       const string sensor_name)
  throw (dbd_error)
{

  // scan all the sensors looking for a match by name
  for (int s=0 ; s < sensors_per_cycle ; s++)
    {
      // Look thru the list of names for a match
      if (sensor_list[s].name == sensor_name )
        {
          // We found the sensor, return a reference to it
          return (*this)[s] ;
        }
    }

  // If we got here, we didn't find the sensor
  ostringstream emsg ;
  emsg << "lookup(): Unknown sensor: "
       << sensor_name ;
  throw (dbd_error(emsg)) ;    // die
  
}



/* filter_data

Purpose:  Copies sensor values with corresponding true elements in
		  pass_through_mask from old value collection to new value collection.
Preconditions: None.
Postconditions: The parameter filtered_data_collection contains the
				sensor values from the old value collection that have
				corresponding true elements in pass_through_mask.
                sensors_per_cycle is changed to reflect the size of
                the new value collection.
History:
31-Dec-03 trout.r@comcast.net Initial

*/

void dbd_sensor_value_collection::filter_data(
		dbd_sensor_value_collection& filtered_data_collection,
		const vector<bool>& pass_through_mask)
{
  filtered_data_collection.clear();
  for (int sensor_index = 0 ; sensor_index < sensors_per_cycle ; sensor_index++)
  {
    if(pass_through_mask[sensor_index])
    {
      filtered_data_collection.push_back((*this)[sensor_index]);
    }
  }
  filtered_data_collection.sensors_per_cycle = filtered_data_collection.size();
}

/* is_valid

Purpose:  Tests that the passed sensor name's value is valid.
Preconditions: None.
Postconditions: None
History:
30-Jan-04 trout.r@comcast.net Initial

*/

bool dbd_sensor_value_collection::is_valid(const vector<dbd_sensor_info> & sensor_list,
    			  const string sensor_name) throw (dbd_error)
{
  // scan all the sensors looking for a match by name
  for (int s=0 ; s < sensors_per_cycle ; s++)
    {
      // Look thru the list of names for a match
      if (sensor_list[s].name == sensor_name )
        {
          // We found the sensor, make a reference to it
          const dbd_sensor_value & elem =  (*this)[s] ;

          // Test for validity
          return elem.is_valid() ;
        }
    }

  // If we got here, we didn't find the sensor
  ostringstream emsg ;
  emsg << "is_valid(): Unknown sensor: "
       << sensor_name ;
  throw (dbd_error(emsg)) ;    // die
}
