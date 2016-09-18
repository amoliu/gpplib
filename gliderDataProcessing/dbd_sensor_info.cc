// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_info

21-Apr-01 tc@DinkumSoftware.com Initial
21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen


*/

#include <iostream>
#include "dbd_sensor_info.h"
#include "dbdfrmat.h"

using namespace dinkum_binary_data ;


/// Reads and parses header line
/**
   Reads a line of the form  

    s: T    0    0 4 f_max_working_depth m

\param ins                 where to read from
\param all_sensors         input, Tells if all sensors are in this file
\param expected_sensor_num Runs 0 to (N-1), which sensor about to read

\returns true if sensor is in the input file

Throws an exception on any kind of error

*/ 

bool dbd_sensor_info::read_sensor_info_line(istream & ins,
                                            bool all_sensors,
                                            int expected_sensor_num)  throw (dbd_error)

{

  // Start fresh
  reset() ;


  // s: T    0    0 4 f_max_working_depth m
  // ^^^^
  parse_header_line( ins, SENSOR_NAME_KEY_STR, is_in_input_file ) ;

  // Get the number associated with this sensor and make sure
  // it's what we are expecting
  // s: T    0    0 4 f_max_working_depth m
  //         ^
  int sensor_num_in_file ;
  ins >> sensor_num_in_file ;


  // Sanity check, make sure the global number matches
  if ( sensor_num_in_file != expected_sensor_num ) 
    {
      ostringstream emsg ;
      emsg << "Sensor info line mismatch"
           << expect_str() << expected_sensor_num
           << got_str() << sensor_num_in_file ;
      throw dbd_error( emsg ) ;
    }


  // s: T    0    0 4 f_max_working_depth m
  //              ^
  int sensor_num_in_data_stream ;
  ins >> sensor_num_in_data_stream ;


  // s: T    0    0 4 f_max_working_depth m
  //                ^ ^                   ^
  ins >> orig_bytes_of_storage ;
  ins >> name ;
  ins >> units ;

  // Confirm sensor_num_in_data_stream makes sense with 'all_sensors'
  // If we're doing all sensors...
  if ( all_sensors ) 
    {
      // Then this sensor better be in the list
      if ( ! is_in_input_file )
        {
          ostringstream emsg ;
          emsg << "all_sensors, but " << name << " not in input file" ;
          throw ( dbd_error (emsg) ) ; // see ya
        }

      // and it's number in the list should match the global number
      if ( sensor_num_in_data_stream != sensor_num_in_file )
        {
          ostringstream emsg ;
          emsg << "all_sensors, but numb in file bad"
               << expect_str() << sensor_num_in_file 
               << got_str()    << sensor_num_in_data_stream ;
          throw ( dbd_error (emsg) ) ; // see ya
        }
    }

  // Tell if sensor is in the file
  return is_in_input_file ;

}
