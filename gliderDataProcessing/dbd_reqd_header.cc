// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_reqd_header.cc
 */

#include "dbd_reqd_header.h"
#include "dbdfrmat.h"

using namespace dinkum_binary_data ;

// do_reqd_header_lines
/// Reads, parses, sets corresponding member variable for all required header lines

/**
\param reqd_label_value The required string value of the first dbd_label: key

Example input:
dbd_label:    DBD(dinkum_binary_format)file\n
encoding_ver:    1\n
num_ascii_tags:    11\n

Throws an exception on any error.
Returns the number of lines read

*/

/*
18-Apr-01 tc@DinkumSoftware.com Initial
18-Sep-01 tc@DinkumSoftware.com documented with Doxygen
*/

int dbd_reqd_header::do_reqd_header_lines(string reqd_label_value)
  throw (dbd_error)
{
  int num_lines_read = 0 ;  // what we return
    
  
  // dbd_label:    DBD(dinkum_binary_format)file
  string label_value ;
  do_a_header_line(DBD_LABEL_KEY, label_value) ;
  if (label_value != reqd_label_value)
    {
      ostringstream emsg ;
      emsg << "Not a DBD file:" << expect_str() << reqd_label_value
           << got_str() << label_value ;
      throw dbd_error (emsg) ;
    }
  num_lines_read++ ;

  //  encoding_ver:    1
  do_a_header_line(ENCODING_VER_KEY, encoding_ver) ;
  num_lines_read++ ;  

  // num_ascii_tags:    11
  do_a_header_line(NUM_ASCII_TAGS_KEY, num_ascii_tags) ;
  num_lines_read++ ;  

  // Tell um how many we read
  return num_lines_read ;

}
