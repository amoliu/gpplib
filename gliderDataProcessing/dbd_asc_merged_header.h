// Copyright(c) 2009 Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_asc_meerged_header.h

This class represents the data after a merge of a glider and science
dba file.  It represents the "union" of the two data sets.

When header data can't be merged/combined.  Data from the glider file
is used directly.

23-Sep-09 tc@DinkumSoftware.com Initial
21-Dec-09 tc@DinkumSoftware.com Include <stdlib.h> for free()
*/

#ifndef _DBD_ASC_MERGED_HEADER_H
#define _DBD_ASC_MERGED_HEADER_H

#include <stdlib.h>                       // free()
#include "dbd_asc_header.h"               // class we derive from
#include "dbd_sensor_value_collection.h"  // holds data we read/write


namespace dinkum_binary_data
{
  /// Holds all the information required in Ascii formatted file
  class dbd_asc_merged_header : public dbd_asc_header
  {

    // our data
  private:
    // copies of headers we are merging
    dbd_asc_header _glider_header ;
    dbd_asc_header _science_header ;

    // _glider/_science data read here
    dbd_sensor_value_collection _glider_data ;
    bool _glider_has_data ;

    dbd_sensor_value_collection _science_data ;
    bool _science_has_data ;

    // output data assembled here
    //     It has to be dynamically allocated in constructor
    //     because don't know it's size until inside constructor
    dbd_sensor_value_collection * _merged_data_ptr  ;


  public:
    // constructor
    dbd_asc_merged_header( const dbd_asc_header & glider_header,
                           const dbd_asc_header & science_header) ;

    // destructor, free up any dynamic memory
    ~dbd_asc_merged_header()
      {
        free(_merged_data_ptr) ;
      }

    bool read_and_merge_asc() ;            // read a line of data
    void write_asc(ostream & outs) const ; // write a line of data

  private:
    // Adds any unique science filenames to our segment filename list
    void merge_segment_filenames() ;
    void handle_duplicated_sensors() ;

    bool pick_input_line_to_use( bool & use_glider_data,
                                 bool & use_science_data) const ;

    void sensor_copy_if_missing(const char * sci_sensorname, const char * gld_sensorname) ;

  } ; // class dbd_asc_merged_header
}

#endif // _DBD_ASC_MERGED_HEADER_H

