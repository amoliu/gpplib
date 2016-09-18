// Copyright(c) 2009 Webb Research Corporation,k ALL RIGHTS RESERVED
/* dba_merge

This program is intended to "merge":
    science data files (dbd2asc *.ebd/nbd/tbd) -and-
    glider data files  (dbd2asc *.dbd/mbd/sbd)
into a single data file.

This program operates only with asci data (output of dbd2asc).

This program was required when logging on science was introduced in 2009.

Usage:
    dba_merge glider_dba_filename science_dba_filename
Resulting asci data file is output to stdout
The input files from command line must be the output of dbd2asc.


See dba_merge_workhorse() for the algorithm.
    

22-Sep-09 tc@DinkumSoftware.com Initial

Table of contents
    main
    dba_merge_workhorse
*/

#include <iostream>
#include <fstream>
#include "options.h"
#include "dbd_asc_header.h"
#include "dbd_asc_merged_header.h"
#include "dbd_error.h"


using namespace dinkum_binary_data ;

// Specify the command line help
static const char * usage_str_tail =
" glider_dba_filename"
" science_dba_filename\n"
"\n"
"glider_dba_filename + science_dba_filename ==> STDOUT\n"
"\n"
" This program merges:\n"
"    glider_dba_filename  (dbd2asc *.dbd/mbd/sbd)\n"
"    science_dba_filename (dbd2asc *.ebd/nbd/tbd) -and-\n"
"into a single data file and delivers output to STDOUT.\n"
"\n"
"This program reads and writes only ASCII data (output of dbd2asc).\n"
"This program was required when logging on science was introduced in 2009.\n"
"\n"
"   -h                    Print this message\n"
;

static const char * const optv[] =
{
  "h|help",
  NULL
};


// Local functions
static void dba_merge_workhorse( const char * glider_dba_filename, const char * science_dba_filename) ;



int main(int argc, char* argv[])
{
  // Error prefix
  const string error_msg_leadin = "ERROR prog: dba_merge: ";
  try
  {
    // Process the command line arguments
    Options cmdline_options(*argv, optv);
    OptArgvIter cmdline_options_iter(--argc, ++argv);
  
    // Process the switches
    int option_char;
    const char * option_arg = NULL;
    while(option_char = cmdline_options(cmdline_options_iter, option_arg))
    {
      switch(option_char)
      {
        case 'h':
          cmdline_options.usage(cerr, usage_str_tail);
          return EXIT_SUCCESS;

        case Options::BADCHAR:
        case Options::BADKWD:
        case Options::AMBIGUOUS:
        default:
          cerr << "Error! ";
          cmdline_options.usage(cerr, usage_str_tail);
          return EXIT_FAILURE;
      }
    }

    // Make sure there are the correct number of required arguments
    // These are the dba filenames
    const int num_of_cmd_line_args = argc - cmdline_options_iter.index() ;
    if ( num_of_cmd_line_args != 2 )
      {
        cmdline_options.usage(cerr, usage_str_tail);

        cerr << "ERROR! Must specify glider_dba_filename and science_dba_filename\n" ;
        return EXIT_FAILURE;

      }

    // Pick off the filenames to merge
    const char * glider_dba_filename = argv [cmdline_options_iter.index()      ] ;
    const char * science_dba_filename = argv [cmdline_options_iter.index() + 1 ] ;


    // Do the real work in a function to make it easier to read
    dba_merge_workhorse( glider_dba_filename, science_dba_filename) ;


  }
  catch (dinkum_binary_data::dbd_error error)
  {
    cerr << error_msg_leadin << error.get_err_msg() << endl;
    return EXIT_FAILURE;
  }
  catch(...)
  {
    cerr << error_msg_leadin << "Unknown Exception Caught" << endl;
    return EXIT_FAILURE;
  }



  // I keep prayin'
  return EXIT_SUCCESS ;
}



/* dba_merge_workhorse

Merges ascii data from input arguments and writes to stdout.
See top of file for usage.

Throws dbd_error execption on any kind of error.

22-Sep-09 tc@DinkumSoftware.com Initial

*/


void dba_merge_workhorse( const char * glider_dba_filename, const char * science_dba_filename)
{

// Common error messages
  const char * emsg_file_and_func       = "dbd_merge.cc: dba_merge_workhorse(): " ;
  const char * emsg_file_open_error     = "File Open Error: " ;

  try
    {
      // Open the input files
      ifstream glider_dba_in(glider_dba_filename) ;
      if ( ! glider_dba_in )
        {
          ostringstream emsg ;
          emsg << emsg_file_and_func << emsg_file_open_error << "glider_dba_filename: " << glider_dba_filename ;
          throw (dbd_error(emsg)) ;
        }

      ifstream science_dba_in(science_dba_filename) ;
      if ( ! science_dba_in)
        {
          ostringstream emsg ;
          emsg << emsg_file_and_func << emsg_file_open_error << "science_dba_filename: " << science_dba_filename ;
          throw (dbd_error(emsg)) ;
        }
  

      // Read the headers of the input files
      dbd_asc_header glider_header_in (glider_dba_in) ;
      dbd_asc_header science_header_in(science_dba_in) ;
      

      // Create and write the output header
      // as a merge of the two input files
      dbd_asc_merged_header merged_dba_out( glider_header_in, science_header_in) ;

      // Write the header to stdout
      merged_dba_out.write_header(cout);

      // Read, merge, and write data
      while ( merged_dba_out.read_and_merge_asc() )
        merged_dba_out.write_asc(cout) ;

    }

  catch (dinkum_binary_data::dbd_error error)
    {
      // Tack on a better error message label and rethrow it
      error.prepend_to_err_msg ( emsg_file_and_func ) ;
      throw error ;
    }

  // Life is good
  return ;
}
