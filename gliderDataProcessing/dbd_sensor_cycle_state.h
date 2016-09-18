// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_cycle_state.h

24-Sep-01 tc@DinkumSoftware.com Documented with Doxygen

 */

#ifndef DBD_SENSOR_CYCLE_STATE_H
#define DBD_SENSOR_CYCLE_STATE_H

#include <iostream>
#include "dbd_header.h"

namespace dinkum_binary_data
{

  /// Holds the state of each sensor in a cycle
  /**
     A sensor(variable) can have one of three states:
     \li Updated this cycle with new value
     \li Updated this cycle with prior (same) value
     \li Not updated this cycle
   */

class dbd_sensor_cycle_state
  {
  public:
    dbd_sensor_cycle_state(const dbd_header & hdr) ;

    /// Reads the state bytes from a stream
    friend istream & operator>> ( istream & ins, dbd_sensor_cycle_state & state)
      {
        state.read_state( ins ) ; return ins ;
      }
    void read_state( istream & ins) ;

    /// Tells if updated with new value
    bool in_data_stream         (int i) const
      {    return _updated_with_new_value[i] ;
      }

    /// Tells if updated with prior(same) value
    bool updated_with_same_value(int i) const
      {    return _updated_with_same_value[i] ;
      }

    /// Tells if not updated this cycle
    bool not_updated            (int i) const
      {    return 
             !in_data_stream(i)         &&
             !updated_with_same_value(i) ;
      }


  private:
    vector<bool> _updated_with_same_value ;
    vector<bool> _updated_with_new_value ;

    int _sensors_per_cycle ;
    int _state_bytes_per_cycle ;

  } ; // class dbd_sensor_cycle_state

} // namespace dinkum_binary_data

#endif // DBD_SENSOR_cycle_state_H
