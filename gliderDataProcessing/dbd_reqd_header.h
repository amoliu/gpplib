// Copyright(c) 2001-2009, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_reqd_header.h

18-Jul-03  fnj@DinkumSoftware.com  Added do_a_header_line for a long.
27-Jul-03 tc@DinkumSoftware.com Changed do_a_header_line_hex( long ->unsigned long)
                                Added do_a_header_line(unsigned long)
24-Sep-09 tc@DinkumSoftware.com Made _ins public so dbd_asc_merged_header could get to it
 */

#ifndef DBD_REQD_HEADER_H
#define DBD_REQD_HEADER_H

#include <fstream>
#include "dbd_support.h"     // class we derive from
#include "dbd_error.h"


namespace dinkum_binary_data
{

  /// Parses the first few lines of DBD header that will never change
  /**
     Functionality typically achieved by deriving from this class.
     As the DBD format evolves over time, it is expected that the content
     of the header will change, i.e. various key/value pairs will be added.

     The first three lines of the file are expected to NEVER change.  An
     example is shown below:

         dbd_label:    DBD(dinkum_binary_data)file\n
         encoding_ver:    1\n
         num_ascii_tags:    12\n

    The encoding_ver will change and should be examined to created backward
    compatible code.  num_ascii_tags is the number of key/value pairs that
    will follow.

  */
class dbd_reqd_header : protected dbd_support

  {
  public:
    /// constructor if reading from a stream
    /**
       \param ins stream to read from
       \param filename_as_opened name of file associated with stream,
                                 used for error messages

       Reads and parse the required header lines from ins
     */
    dbd_reqd_header(istream & ins, const char * filename_as_opened)
      :
      _ins(ins),
      _filename_as_opened(filename_as_opened)
      {
        reset() ;
      }


    /// constructor for people who don't want to read from stream input
    dbd_reqd_header()
      :
      _ins(_null_input)
      {
        reset() ;
      }

    /// copy constructor
    dbd_reqd_header(const dbd_reqd_header & them)
      :
      _ins(               them._ins               ),
      _filename_as_opened(them._filename_as_opened),
      encoding_ver(       them.encoding_ver       ),
      num_ascii_tags(     them.num_ascii_tags     )
      {
      }

    /// returns name of the file which actually contains the header
    const char * filename_as_opened() const
      {
        return _filename_as_opened.c_str() ;
      }



    /// The input stream
    istream   & _ins ;

  protected:
    /// parsed data from the header
    int encoding_ver ;
    /// parsed data from the header, number of key/value tags to follow
    int num_ascii_tags ;

    /// Initializes all internal data
    void reset()
      {
        encoding_ver = -69 ;
        num_ascii_tags = 0 ;
      }

    /// name of file associated with input stream
    string    _filename_as_opened ;

    int do_reqd_header_lines(string reqd_label_value) throw (dbd_error) ;

    /// parses a key/value pair from input stream.  Exception if key doesn't match
    void do_a_header_line(const string key, string & value ) throw (dbd_error)
    {    parse_header_line(_ins, key, value) ; }
    /// parses a key/value pair from input stream.  Exception if key doesn't match
    void do_a_header_line(const string key, int & value) throw (dbd_error)
    {    parse_header_line(_ins, key, value) ; }
    /// parses a key/value pair from input stream.  Exception if key doesn't match
    void do_a_header_line(const string key, long & value) throw (dbd_error)
    {    parse_header_line(_ins, key, value) ; }
    void do_a_header_line(const string key, unsigned long & value) throw (dbd_error)
    {    parse_header_line(_ins, key, value) ; }
    /// parses a key/value pair from input stream.  Exception if key doesn't match
    void do_a_header_line_hex(const string key, unsigned long & value) throw (dbd_error)
    {    parse_header_line_hex(_ins, key, value) ; }
    /// parses a key/value pair from input stream.  Exception if key doesn't match
    void do_a_header_line(const string key, bool & value) throw (dbd_error)
    {    parse_header_line(_ins, key, value) ; }

    /// silently consumes a header line from input stream
    void eat_a_header_line() throw (dbd_error)
    {    dbd_support::eat_a_header_line(_ins) ;
    }


  private:
  // ###################################################################
                            // Bug alert.  Used to be istream instead
                            //   of ifstream, but Metrowerks Release 5 crashes
  // ###################################################################
  ifstream _null_input ;    // for use when caller doesn't
                            // want to read input


  } ; // class dbd_reqd_header

} // namespace dinkum_binary_data

#endif // DBD_REQD_header_H
