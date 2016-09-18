// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_cycle_state.cc

24-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
 */

#include "dbd_sensor_cycle_state.h"
#include "dbdfrmat.h"

using namespace dinkum_binary_data ;

/// constructor, Extracts required information from hdr
dbd_sensor_cycle_state::dbd_sensor_cycle_state(const dbd_header & hdr)
{

  // Copy what we need out of header
  _sensors_per_cycle     = hdr.sensors_per_cycle ;
  _state_bytes_per_cycle = hdr.state_bytes_per_cycle ;

  
  // Set up the containter's size
  _updated_with_same_value.resize( _sensors_per_cycle ) ;
  _updated_with_new_value .resize( _sensors_per_cycle ) ;

}


/// reads the state information for one cycle from a stream
/**
   \param ins    stream to read from
 */

void dbd_sensor_cycle_state::read_state( istream & ins)
{

  int sensor_num = 0 ;
  for ( int byte_count = 0 ; byte_count < _state_bytes_per_cycle ; byte_count++)
    {
      // Read the next state byte
      unsigned char c = ins.get() ;

      const int bits_per_field = 2 ;
      const unsigned char field_mask = 0x03 ;    // 0000.0011 two lower bits
      const int field_shift_cnt_to_lsbs = 6 ;    //        xx 

      const int bits_per_byte = 8 ;
      const int fields_per_byte = bits_per_byte / bits_per_field ;
      for ( int field_num = 0 ; field_num < fields_per_byte ;
            field_num++, c <<= bits_per_field )
        {
          // Get the bits in question into LSB of field
          int field = (c >> field_shift_cnt_to_lsbs) & field_mask ;

          // Test and set
          _updated_with_same_value[sensor_num] = 
            ( field == FIELD_UPDATED_WITH_SAME_VALUE ) ;

          _updated_with_new_value[sensor_num] = 
            ( field == FIELD_UPDATED_WITH_NEW_VALUE ) ;
            

          // All done?
          if ( ++sensor_num >= _sensors_per_cycle )
            break ;    // yep
        }
    }
}


