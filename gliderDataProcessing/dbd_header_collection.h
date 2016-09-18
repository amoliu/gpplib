// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_header_collection.h

21-Jan-04 trout.r@comcast.net Added the output_optional_keys parameter
                              to write_asc_header.  Supports the -k
                              flag of dbd2asc.
 */

#ifndef DBD_HEADER_COLLECTION_H
#define DBD_HEADER_COLLECTION_H

#include <list>
#include "dbd_header.h"

namespace dinkum_binary_data
{

  /// A list of binary headers
  /**
     Typically used to merge multiple DBD files (segments) into a single
     ascii file.
   */
  class dbd_header_collection : public list<dbd_header>
  {
  public:

    // constructors
    dbd_header_collection( list<string> filenames, ostream & err_stream) ;

    // Output the ascii header
    bool write_asc_header(ostream & out, bool output_optional_keys = true ) ;

    // Read/Write data from one of our headers
    bool write_asc_data(iterator & iter, ostream & out, bool output_initial_data_line = false) ;

  } ; // class dbd_header_collection

} // namespace dinkum_binary_data

#endif // DBD_HEADER_collection_H
