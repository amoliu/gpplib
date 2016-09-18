// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_support.h

21-Apr-01 tc@DinkumSoftware.com Initial
18-Sep-01 tc@DinkumSoftware.com Documented via Doxygen
27-Sep-01 tc@DinkumSoftware.com Added definition of DBL_DIG for linux
 3-Dec-01 tc@DinkumSoftware.com Moved invalid_sensor_str() here
 6-Dec-01 tc@DinkumSoftware.com Doxygen doco fixes
18-Jul-03  fnj@DinkumSoftware.com  Added parse_header_line_hex for a long.
27-Jul-03 tc@DinkumSoftware.com   Changed parse_header_line_hex(value) from
                                  long to unsigned long
                                  Added parse_header_line(unsigned long)
21-Jan-04 trout.r@comcast.net Added write_key_value(const string&,
                              const string&, ostream&) const.  Supports
                              writing ascii header optional keys.
*/

#ifndef DBD_SUPPORT_H
#define DBD_SUPPORT_H

#include "dbd_error.h"

/// Collection of classes for encoding time varing binary data
/**

Initially developed for the Webb Research Glider.

This is a collection of C++ classes that run on a host computer
to decode the *.dbd and *.sbd files generated in a glider.  The
code in the glider that generates the files is written in C and
is not documented here.

See .../doco/dbd_file_format.txt for the specification of the
format.


 */
namespace dinkum_binary_data {

using namespace std ;

// The number of digits to output for a double
// On Windows/Metrowerks this symbol is defined.
// It isn't on Linux
#ifndef DBL_DIG
#define DBL_DIG    15
#endif



/// Class of common support functions for Dinkum Binary Data
/**
Functionality is typically gained by deriving from this class.
It has functions to parse key/value pairs from the header of
a dbd file.
 */

class dbd_support
  {

  protected:
    void parse_header_line(istream & ins, const string key, string & value)  throw (dbd_error) ;
    void parse_header_line(istream & ins, const string key, int    & value)  throw (dbd_error) ;
    void parse_header_line(istream & ins, const string key, long   & value)  throw (dbd_error) ;
    void parse_header_line(istream & ins, const string key, bool   & value)  throw (dbd_error) ;
    void parse_header_line(istream & ins, const string key, unsigned long   & value)  throw (dbd_error) ;


    void parse_header_line_hex(istream & ins, const string key, unsigned long   & value)  throw (dbd_error) ;

    /// silently consumes a DBD header line from ins
    /**
       \param ins stream to consume the line from
     */
    void eat_a_header_line(istream & ins) throw (dbd_error)
      {    string ignored ;
           ins >> ignored >> ignored ;
      }


    void parse_key( istream & ins, const string expected_key) throw (dbd_error) ;


    // Read a check a binary label, returns TRUE of EOF or running out of data
    bool read_cycle_tag(istream & ins,
                        const unsigned char expected_tag)  throw (dbd_error) ;


    // Some functions to make error message text consistent
    /// Used to generate consistent text in error messages
    /** blah blah,  exp=onething, got=another
     */
    const char * expect_str() const { return ", exp=" ; }

    /// Used to generate consistent text in error messages
    /** blah blah,  exp=onething, got=another
     */
    const char * got_str()    const { return ", got=" ; }


    // Output functions
    /// Writes key: value to outs
    void write_key_value( const char * key, const char * value, ostream & outs) const
      {
        outs << key << " " << value << endl ;
      }
    /// Writes key: value to outs
    void write_key_value( const char * key, const string value, ostream & outs) const
      {
        outs << key << " " << value << endl ;
      }
    /// Writes key: value to outs
    void write_key_value( const char * key, int value, ostream & outs) const
      {
        outs << key << " " << value << endl ;
      }
    /// Writes key: value to outs
    void write_key_value(const string& key, const string& value, ostream& outs) const
      {
        outs << key << " " << value << endl ;
      }


    /// ASCII representation of Not A Number
    const char * invalid_sensor_str() const { return "NaN" ; }


  } ; // class dbd_support

} // namespace dinkum_binary_data

#endif // DBD_SUPPORT_H
