// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dba_time_filter

This program:
    Reads dinkum binary ascii data from stdin (output of dbd2asc)
    Throws away some data based on time
    Writes the remainder ad dinkum binary ascii data to stdout 

Usage:
    dba_time_filter [-help] [-epoch] earliest_included_t latest_included_t

All records between earliest_included_t and latest_included_t
(inclusive) are output.  All others are discarded.  The time is
normally based on mission time (M_PRESENT_SECS_INTO_MISSION).  If
-epoch is present, time is based on seconds since 1970 (M_PRESENT_SECS)

A -tf is added to the filename of the output header, e.g.
    filename: zippy-2001-222-04-05  --> zippy-2001-222-04-05-tf

 1-Dec-01 tc@DinkumSoftware.com Initial
 5-Oct-05 tc@DinkumSoftware.com Bug fix, --epoch was completely broken
                                only delivered an error message
21-Dec-09 tc@DinkumSoftware.com Added #include <cstdio> <cstdlib>

Table of contents
    main

*/

#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include "options.h"
#include "dbd_asc_header.h"
#include "dbd_sensor_value_collection.h"

using namespace dinkum_binary_data ;

                           
                           
// What we add to the filename
// filename: zippy-2001-222-04-05  --> zippy-2001-222-04-05-tf
const char * addto_filename_str = "tf" ; 

// Specify the command line
static const char * usage_str_tail = "earliest_t latest_t" ;

static const char * const optv[] =
{
  "h|help",
  "e|epoch",
  NULL
} ;



int main(int argc, char* argv[] )
{

// **** Initialization

  // Process the command line arguments
  Options opts(*argv, optv) ;
  OptArgvIter iter(--argc, ++argv) ;
  
  // Process the switches
  bool are_using_epoch_time = false ; // default to mission time

  int optchar ;
  const char * optarg = NULL ;
  while ( optchar = opts(iter, optarg))
    {
      switch(optchar)
        {
        case 'h':
          opts.usage(cerr, usage_str_tail);
          return EXIT_SUCCESS ;

        case 'e':
          are_using_epoch_time = true ;
          break ;


      case Options::BADCHAR :  // bad option ("-%c", *optarg)
      case Options::BADKWD  :  // bad long-option ("--%s", optarg)
      case Options::AMBIGUOUS  :  // ambiguous long-option ("--%s", optarg)
      default :
        cerr << "Error! " ;
        opts.usage(cerr, usage_str_tail);
        return EXIT_FAILURE ;

        }
    }


  // We have two or three arguments left on the command line
  // [--epoch] earliest_included_t and lastest_included_t
  if ( argc != (are_using_epoch_time ? 3 : 2) )
    {
      opts.usage(cerr, usage_str_tail);
      return EXIT_FAILURE ;
    }

  // convert them
  const int first_arg_indx  = are_using_epoch_time ? 1 : 0 ;
  const int second_arg_indx = first_arg_indx + 1 ;

  const char * earliest_cptr = argv[first_arg_indx] ;
  double earliest_included_t ;
  istringstream es ( earliest_cptr ) ;
  es >> earliest_included_t ;

  if ( es.fail() )
    {
      opts.usage(cerr, usage_str_tail) ;
      cerr << "Error with earliest_time arg:" << earliest_cptr << endl ;
      return EXIT_FAILURE ;
    }
  
  const char * latest_cptr = argv[second_arg_indx] ;
  double latest_included_t  ; 
  istringstream ls ( latest_cptr ) ;
  ls >> latest_included_t ;
  if ( ls.fail() )
    {
      opts.usage(cerr, usage_str_tail) ;
      cerr << "Error with latest_time arg:" << latest_cptr << endl ;
      return EXIT_FAILURE ;
    }




// **** the main loop

  // What we say when we get an error
  const string error_msg_leadin = "ERROR prog: dba_time_filter: " ;

  try
    {
      // Read in the ascii header
      dbd_asc_header  hdr_in(cin) ;
      
      // Create an output header and tack on our label
      dbd_asc_header  hdr_out(hdr_in, addto_filename_str) ;

      // Write the header
      hdr_out.write_header(cout) ;

      // Read and write the data
      dbd_sensor_value_collection data_line(hdr_in) ;
      while ( data_line.read_asc(cin) )
        {

          // Pick off the time of this record
          double t = data_line.lookup_as_double( hdr_in.sensor_list,
                                                 are_using_epoch_time ?
                                                 "m_present_time"     :
                                                 "m_present_secs_into_mission" ) ;

          // if need be ... pass it along
          if ( (earliest_included_t <= t)                &&
               (t                   <= latest_included_t))
            {

              // This one qualifies, write it out
              data_line.write_asc(hdr_out, cout) ;
            }
        }

    }
  catch(dbd_error e)
    {
      cerr << error_msg_leadin << e.get_err_msg() << endl ; 
    }
  catch(...)
    {   cerr << error_msg_leadin << "Unknown Exception Caught" << endl ;
    }






  // Life is good
  return EXIT_SUCCESS ;
}
