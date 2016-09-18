// Copyright(c) 2001-2003, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_header_collection.cc
 */

#include "dbd_header_collection.h"
#include "dbd_reader.h"
#include "dbd_asc_header.h"

using namespace dinkum_binary_data ;



// dbd_header_collection
/// constructor, merges headers from multiple dbd files

/**
   \param filenames List of filenames of the DBD files to merge
   \param err_stream Where errors are announced

"filenames" should be a list of dbd files.

A sorted list of dbd_headers is built from those filenames.

Any errors associated with a file are announced to "err_stream"
and the file is ignored, e.g. file doesn't exist, it isn't
a dbd file, etc.

17-Jul-01 tc@DinkumSoftware.com Initial
21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
21-Jan-04 trout.r@comcast.net Added the output_optional_keys parameter
                              to write_asc_header.  Supports the -k
                              flag of dbd2asc.
*/


dbd_header_collection::dbd_header_collection( list<string> filenames, ostream & err_stream)
{

  /* Iterate over the input filenames to build all the headers we need
     We have to do it twice.
         On the first pass we don't announce errors, but build
           a separate list of filenames that don't look like dbds
         On second pass, we process those that failed on first pass
           and do announce errors.
      This is to handle being give file0 with no header (and it's not
      in the cache) followed by file1 with a header required by file0
  */
  list<string> files_failing_on_first_pass ; // filenames

  // Pass one
  list<string>::iterator p1_iter ;
  for ( p1_iter = filenames.begin() ; p1_iter != filenames.end() ; p1_iter++)
    {
      const char * filename = p1_iter->c_str() ;

      // Try to form the header      
      dbd_reader r( filename ) ;
      if ( !r )
        {
          // Error, silently put it error list
          files_failing_on_first_pass.push_back( filename ) ;
          continue ;
        }

      // success, Put the header in our list (our base class)
      push_back( r.hdr() ) ;

    }

  // Pass 2
  list<string>::iterator p2_iter ;
  for ( p2_iter  = files_failing_on_first_pass.begin() ;
        p2_iter != files_failing_on_first_pass.end() ; p2_iter++)
    {
      const char * filename = p2_iter->c_str() ;

      // Try to form the header      
      dbd_reader r( filename ) ;
      if ( !r )
        {
          // Error, announce and ignore the file
          err_stream << "Error, ignoring: " << r.get_brief_err_msg() << endl ;
          continue ;
        }

      // success, Put the header in our list (our base class)
      push_back( r.hdr() ) ;

    }

  // Make sure we actually read some files
  if ( size() <= 0 )
    return ; // nothing else to do

  // Sort the list by time
  sort() ;

  // Check that the data sets are the same
  // and the data in the file is the same
  // Compare the first data set
  if ( size() > 1 )
    {
      list<dbd_header>::iterator i = begin() ;
      vector<dbd_sensor_info> & first_ds   = i->full_sensor_list ;
      vector<dbd_sensor_info> & first_ifds = i->infile_sensor_list ;

      // With all the rest
      i++ ;
      for ( ; i != end() ; i++)
        {
          // data set under test
          vector<dbd_sensor_info> & ds = i->full_sensor_list ;

          // Are they the same
          if ( ds != first_ds )
            {
              // Nope, announce it and remove this header
              err_stream << "Error, ignoring: mismatched data set:"
                         << i->filename_as_opened() << endl ;

              erase(i) ;    // remove it
              continue ;
            }

          // The ones in the files
          vector<dbd_sensor_info> & ifds = i->infile_sensor_list ;

          // Are they the same
          if ( ifds != first_ifds )
            {
              // Nope, announce it and remove this header
              err_stream << "Error, ignoring: mismatched data in file:"
                         << i->filename_as_opened() << endl ;

              erase(i) ;    // remove it
              continue ;
            }
        }
    }


}



// write_asc_header
/// writes and ascii header to a stream
/**

Outputs the ascii header to "out".

\param out where to write the ascii header


/return Normally returns false, returns true on error.

*/

// 18-Jul-01 tc@DinkumSoftware.com Initial



bool dbd_header_collection::write_asc_header(ostream & out, bool output_optional_keys)
{

  // Make sure we have some data
  if ( size() <= 0 )
    return true ; // nothing to output

  // Create an initial ascii header as a direct copy
  // of the first binary header
  iterator i = begin() ;
  dbd_asc_header h( *i ) ;
  h.put_output_optional_keys(output_optional_keys) ;

  // Merge in the rest
  i++ ; // skip the first one
  for ( ; i != end() ; i++)
    {
      if ( h.merge_header( *i ) )
        {
          // error merging
          return true ;
        }
    }

  // Write it out
  out << h ;

  // all went ok
  return false ;

}


// write_asc_data
/// reads binary data and writes ascii data

/**

Reads all the binary data and writes ascii data for the
header referenced by "iter".

It's assumed that the ascii header has been previously written.

\param iter  Should return a previously opened binary header
\param out   Where to write the ascii data
\param output_initial_data_line controls whether first line of all data values is written

/return Normally returns false, returns true on error.

*/

// 18-Jul-01 tc@DinkumSoftware.com Initial
// 24-Sep-01 tc@DinkumSoftware.com Added output_initial_data_line argument


bool dbd_header_collection::write_asc_data(iterator & iter, ostream & out,
                                           bool output_initial_data_line)
{

  // The header we need to write the data for
  dbd_header & our_header = *iter ;

  // The name of the file holding the data
  const char * filename = our_header.filename_as_opened() ;

  // Reopen the file this header came and
  // output the data. false means don't output the header
  dbd_reader dbr(filename, out, false, output_initial_data_line ) ;
  if ( !dbr )
    {
      // error
      cerr << dbr.get_err_msg() << endl ;
      return true ;
    }
  else
    return false ; // all went ok

}

