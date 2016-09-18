// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_info.h

21-Apr-01 tc@DinkumSoftware.com 
18-Jul-01 tc@DinkumSoftware.com Added operator==
21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
*/


#ifndef DBD_SENSOR_INFO_H
#define DBD_SENSOR_INFO_H

#include <iostream>
#include <string>

#include "dbd_support.h"
#include "dbd_error.h"    // what we throw

namespace dinkum_binary_data
{

  /// Holds knowledge of a single sensor (variable)
  /**
     This information is typically extracted from a file header.
     It tells the name and size of the sensor.
   */
  class dbd_sensor_info : private dbd_support
    {    
    public:
      /// True means sensor is included in this data set
      bool is_in_input_file ;

      /// The name of the sensor
      string name ;

      /// Units of the sensor, e.g. meters
      string units ;

      /// How many bytes of storage a sensor occupies in the file
      int orig_bytes_of_storage ;

      // Functions
      /// constructor, makes empty object
      dbd_sensor_info() { reset() ; }

      /// Copy constructor
      dbd_sensor_info(const dbd_sensor_info & them)
        {
          is_in_input_file      = them.is_in_input_file ;
          name                  = them.name ;
          units                 = them.units ;
          orig_bytes_of_storage = them.orig_bytes_of_storage ;
        }

      /// destructor
      ~dbd_sensor_info() {}


      /// Makes empty object
      void reset()
        {
          is_in_input_file      = false ;
          orig_bytes_of_storage = 0     ; 
          name = "" ;
          units = "" ;
        }


      // Reads/parse a line from a file
      bool read_sensor_info_line(istream & ins,
                                 bool all_sensors,
                                 int expected_sensor_num) throw (dbd_error) ;



      /// Tests for equality
      /* only looks at name/units/size
         it is a don't care whether it is in file or not
      */
      bool operator==(const dbd_sensor_info & them) const
      {
        return
          (name                  == them.name )                &&
          (units                 == them.units)                &&
          (orig_bytes_of_storage == them.orig_bytes_of_storage) ;
      }

    } ; // class dbd_sensor_info


} // namespace dinkum_binary_data

#endif //  DBD_SENSOR_INFO_H
