// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_value_collection.h

24-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
 6-Dec-01 tc@DinkumSoftware.com Added read_asc(string &)
31-Dec-03 trout.r@comcast.net Added filter_data(dbd_sensor_value_collection&,
    				                            const vector<bool>&)
30-Jan-04 trout.r@comcast.net Added is_valid(vector<dbd_sensor_info> &,
                                             const string)
24-Sep-09 tc@DinkumSoftware.com Made lookup_as_double const
25-Sep-09 tc@DinkumSoftware.com Added lookup()
*/

#ifndef DBD_SENSOR_VALUE_COLLECTION_H
#define DBD_SENSOR_VALUE_COLLECTION_H

#include <iostream>
#include <vector>
#include <string>
#include "dbd_sensor_value.h"
#include "dbd_header.h"
#include "dbd_asc_header.h"
#include "dbd_error.h"
#include "dbd_support.h"

namespace dinkum_binary_data
{


  /// An array of sensor(variable) data
  /**
     This class holds one cycle's worth of data.

     Methods exist to read binary values from a stream and to
     write ascii values to a stream.
   */

class dbd_sensor_value_collection : public vector<dbd_sensor_value>,
                                    private dbd_support
{
    public:
    dbd_sensor_value_collection(const dbd_header     & hdr) ;
    dbd_sensor_value_collection(const dbd_asc_header & hdr) ;

    /// Makes the collection empty
    void reset()
      {
        for ( int i=0 ; i < sensors_per_cycle ; i++)
          (*this)[i].reset() ;
      }


    bool read_bin ( const dbd_header & hdr, istream & ins,
                    bool all_sensors_must_be_present = false) throw (dbd_error) ;
    bool read_asc( istream & ins ) throw (dbd_error) ;
    bool read_asc( string  & str ) throw (dbd_error) ;

    void write_asc( const dbd_asc_header & ahdr, ostream & outs ) ;

    double lookup_as_double(const vector<dbd_sensor_info> & sensor_list,
                            const string sensor_name) const throw (dbd_error)  ;
      
    dbd_sensor_value & lookup(      vector<dbd_sensor_info> & sensor_list,
                              const string sensor_name) throw (dbd_error)  ;

    void filter_data(dbd_sensor_value_collection& filtered_data_collection,
    				 const vector<bool>& pass_through_mask);
    				 
    bool is_valid(const vector<dbd_sensor_info> & sensor_list,
    			  const string sensor_name) throw (dbd_error) ;
    
    /// The number of sensors (variables) in each cycle
    int sensors_per_cycle ;



} ; // class dbd_sensor_value_collection

} // namespace dinkum_binary_data

#endif // DBD_SENSOR_value_collection_H
