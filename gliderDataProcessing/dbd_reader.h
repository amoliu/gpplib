// Copyright(c) 2001-2003, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_reader.h

This specifies a "dbd_reader" class for reading and parsing
*.dbd files (Dinkum Binary Data).

See doco/dbd_file_format.txt for a description.


The constructor takes a filename and output stream as arguments.
It opens up filename and parses the header, echoing all the lines
to the output stream.

21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
24-Sep-01 tc@DinkumSoftware.com Added output_initial_data_values constructor argument
28-Jul-03 tc@DinkumSoftware.com Made work with squished sbd files
*/

#ifndef DBD_READER_H
#define DBD_READER_H


#include <fstream>
#include <string>

#include "dbd_support.h" // class we derive from
#include "dbd_error.h"  // class we throw() on error
#include "dbd_header.h"

namespace dinkum_binary_data {

  /// Reads DBD file, parses, and writes ascii to a stream
  /**
     High level interface to DBD files.

     Opens, reads, and parses a DBD file.  The contents
     are translated to ASCII and emitted on an output stream.
   */
class dbd_reader : private dbd_support
{

 public:
  dbd_reader(const char * input_filename,
             ostream    & outs,
             bool output_header = true,
             bool output_initial_data_values = false ) ;
  dbd_reader(const char * input_filename, bool read_abbrv_hdr = false ) ;

  /// destructor
  ~dbd_reader()
    {
      delete _hdr_ptr ;
    }


// Error stuff

  /// Returns true if all is ok, false otherwise
  operator bool ()      const { return is_ok(); }
  /// Returns true if all is ok, false otherwise
           bool is_ok() const { return _is_ok ; }

  /// Retrieves the last err
  const string  get_err_msg () {return _err_msg ;}

  /// retrieves one line err desc
  const string  get_brief_err_msg() const
    {
      string emsg ;  // what we return
      emsg.append( _err_msg, 0, _err_msg.find('\n')) ; // copy first line of msg
      return emsg ;      
    }

  dbd_header & hdr() throw (dbd_error) ;

 private:
  // da error state data
  bool _is_ok ;     // T--> things are good
  string _err_msg ; // describes failure

  // Sets error to be delivered to class user
  void set_err ( const string msg)
  { _is_ok = false ; _err_msg = msg ;
  }

  // Where we read the header
  dbd_header * _hdr_ptr ;


};  // class dbd_reader


} // namespace dinkum_binary_data

#endif // DBD_READER_H
