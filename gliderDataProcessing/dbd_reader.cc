// Copyright(c) 2001-2008, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_reader.cc

See dbd_reader.h

Note: I tried to make this trap Standard Library
iostream errors via exceptions... but it didn't
appear to be implemented in library shipped with
RedHat 7.0 (gcc --version ==> 2.96).  They may
be supported by now.  Wasn't clear whether Metrowerks
supported them or not.

18-Apr-01 tc@DinkumSoftware.com Initial
21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
24-Sep-01 tc@DinkumSoftware.com Bug fix, allow caller to control whether first line
                                of data outputed
26-Jul-03  fnj@DinkumSoftware.com  dbd_header ctor: added parameter.
28-Jul-03 tc@DinkumSoftware.com    put ctor: parm back
12-Sep-08 dpingal@webbresearch.com dbd_reader ctor: does not output header 
                                   until it has read initial data     
*/


#include <strstream>
#include "dbd_reader.h"
#include "dbd_asc_header.h"
#include "dbd_sensor_value_collection.h"


using namespace dinkum_binary_data ;


// dbd_reader

/// constructor, reads DBD file and writes ASCII with
/// or without a header
/**

   \param input_filename Name of DBD input file to open
   \param outs Where to write ascii
   \param output_header controls whether to write a header
   \param output_initial_data_values controls whether initial data line is written

Opens "input_filename" and parses the dbd file.
A ascii file is output to "outs".

If "output_header" is true, An ascii is sent to "outs".

If "output_initial_data_values" is true, the first line
of data where all values are recorded is sent.

The remainder of the data is sent regardless.

Use operator() or is_ok() to test for success.

*//*
16-Apr-01 tc@DinkumSoftware.com Initial
18-Jul-01 tc@DinkumSoftware.com Added output_header arg
24-Sep-01 tc@DinkumSoftware.com Added output_initial_data_values
26-Jul-03  fnj@DinkumSoftware.com  dbd_header ctor: added parameter.
27-Jul-03 tc@DinkumSoftware.com    removed prior parameter
12-Sep-08 dpingal@webbresearch.com does not attempt to output header 
                                   until it has read initial data     
*/

dbd_reader::dbd_reader(const char * input_filename,
                       ostream    & outs,
                       bool output_header,
                       bool output_initial_data_values)
  :
  _is_ok(true),
  _hdr_ptr(NULL)

{

  ifstream ins ;    // where we read from

  try
  {
    // Open up the input file
    ins.open(input_filename, ios::in | ios::binary) ;
    if ( !ins )
      throw dbd_error ("Couldn't open file" ) ;


    // All the following code throw exceptions
    // when they encounter an error
    // Reads the incoming header info
    _hdr_ptr = new dbd_header(ins, input_filename) ;
    if ( _hdr_ptr == NULL)
      throw (dbd_error("could not new dbd_header")) ;

    // make the code a little easier to read
    dbd_header & hdr = *_hdr_ptr ;

    // We're ready to output
    // Create the header we are going to output
    dbd_asc_header asc_hdr(hdr) ;

    // Make up some place to hold all the values
    dbd_sensor_value_collection v(hdr) ;

    // read and maybe write reqd first line
    if ( !v.read_bin(hdr, ins, true) )
    {
      return ;
    }
    else if ( output_initial_data_values)
    {
      if ( output_header )
      {
        outs << asc_hdr ;
        output_header = false ;
      }
      v.write_asc(asc_hdr, outs) ;
    }


    // Read and generate lines until input is exhausted
    while ( v.read_bin(hdr, ins) )
      {
        if ( output_header )
        {
          outs << asc_hdr ;
          output_header = false ;
        }
        v.write_asc(asc_hdr, outs) ;
      }

    // We're done

  }
  catch(dbd_error e)
  {
    // Preface the error message with what file it is
    ostringstream emsg ;
    emsg << "file:" << input_filename << " " << e.get_err_msg() << endl
         << "At input character position: " << ins.tellg() ;

    // Set it to error message caller will see
    set_err(emsg.str() ) ;
  }
  catch(...)
  {    set_err("Unknown Exception Caught") ;
  }

}

/// constructor, Just read the header
/**

\param input_filename Name of DBD file to open
\param read-abbrv_hdr true->only read ascii part, no sensors

Opens, reads, and parses only the header of the DBD file.
No data is output.  If read_abbrv_hdr is true, quits reading
after initial ascii lines, doesn't try to process any cache
related data.

 */
dbd_reader::dbd_reader(const char * input_filename, bool read_abbrv_hdr)
  :
  _is_ok(true),
  _hdr_ptr(NULL)

{

  ifstream ins ;    // where we read from

  try
  {
    // Open up the input file
    ins.open(input_filename, ios::in | ios::binary) ;
    if ( !ins )
      throw dbd_error ("Couldn't open file" ) ;


    // All the following code throw exceptions
    // when they encounter an error
    // Reads the incoming header info
    _hdr_ptr = new dbd_header(ins, input_filename, read_abbrv_hdr) ;

    if ( _hdr_ptr == NULL)
      throw (dbd_error("could not new dbd_header")) ;

    // We're done
  }
  catch(dbd_error e)
  {
    // Preface the error message with what file it is
    ostringstream emsg ;
    emsg << "file:" << input_filename << " " << e.get_err_msg() << endl
         << "At input character position: " << ins.tellg() ;

    // Set it to error message caller will see
    set_err(emsg.str() ) ;
  }
  catch(...)
  {    set_err("Unknown Exception Caught") ;
  }


}



/// Returns a previously read header
/**
   /return Returns reference to the header.j

Throws an exception if a header hasn't been read.

 */
dbd_header & dbd_reader::hdr() throw (dbd_error)
{
  // Make sure we've read a header
  if ( _hdr_ptr == NULL)
    throw (dbd_error("hdr(): No header has been read")) ;

  // We have, give it to them
  return * _hdr_ptr ;

}
