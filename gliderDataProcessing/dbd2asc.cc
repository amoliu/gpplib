// Copyright(c) 2001-2005, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd2asc.cc

Translates *.dbd (Dinkum Binary Data) files into
ascii only output.


Usage: dbd2asc [-h] [-s] [-o] [-r] [-c <cache-path>] <dbd_filename> [<dbd_filename> ...]

Reads the filenames of DBD files from the command line (or stdin
if -s is present), sorts them by time based, parses them and
writes human readable ascii output to stdout.

A single ascii header will be written and the data from all
the input dbd files will be written.

If -c is given, the path to the sensor list cache directory will be taken
from <cache-path>

If -k is given, dbd2asc functions as it did before the optional keys (e.g., segment_filename)
were added.  This flag is typically used for backward compatibility with pre-optional keys
regression tests.

Other doco:
    See doco/dbd_file_format.txt for a description of the
    DBD file format.

Output format:
    All the ASCII header information is merged and
    output.

    The binary cycle data is output as a whitespace
    delimited list of values in sensor order.  There
    is one (long) line per cycle.

    All other binary cycles are silently consumed.


16-Apr-01 tc@DinkumSoftware.com Initial
17-Jul-01 tc@DinkumSoftware.com Handle multiple files
24-Sep-01 tc@DinkumSoftware.com Bug fix, wasn't writing initial data line
30-Sep-02 tc@DinkumSoftware.com Bug fix: suppress lines of data with duplicate
                                  timestamps in the first two lines of non-initial
                                  data segments that were processed standalone.
                                glider now writes DBD encoding version ==> 3
                                We output DBA_ASC encoding version ==> 1
                                We now longer output the initial data line, we used
                                  to output it on only the first segment
                                Added --output-initial-values optional cmd line arg
                                  for backward compatibility
27-Jul-03 tc@DinkumSoftware.com Commented out cache output to cerr
28-Jul-03 tc@DinkumSoftware.com Went to version 2.1
29-Jul-03 tc@DinkumSoftware.com Went to version 2.2
19-Jan-04 trout.r@comcast.net Added -k flag to suppress output of ascii header
                              optional keys
 6-Oct-05 tc@DinkumSoftware.com version 2.3 bug fix, remove possible corrupt
                                files on error
*/

#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <list>
#include <string>
#ifdef OSX
#include <dirent.h>
#endif

#include "options.h"
#include "dbd_header_collection.h"

using namespace dinkum_binary_data ;

// Specify the command line options
static const char * usage_str_tail =
"<dbd_file> [<dbd_file> ...]\n"
"   -h               Print this message\n"
"   -s               Read filenames from stdin\n"
"   -o               Output initial data lines (makes it behave like version:none)\n"
"   -k               Suppress ascii header optional keys (use for backward compatibility testing)\n"
"   -c <cache-path>  Specify path for sensor list cache directory\n"
"\n"
"Reads the filenames of DBD files from the command line (or stdin\n"
"if -s is present), sorts them by time based, parses them and\n"
"writes human readable ascii output to stdout.\n"
"\n"
"This is version 2.3\n" ;

static const char * const optv[] =
{
  "h|help",
  "s|stdin",
  "o|output-initial-values",  /* Used to force backward compatibility
                                with ver="none" prior to 30-Sep-02
                                Introduced in version 1.0
                             */
  "k|suppress-optional-keys",
  "c:cache-path <cache-path>",
  NULL
} ;



int main(int argc, char * argv[] )
{

  // Make a list of filenames to process
  // These come from the command line and stdin as well
  list<string> input_filenames ;


  bool read_from_stdin = false ;    // T ->read from stdin as well
                                    //  well as command line
  bool output_initial_values = false ; // T-> output initial values of all sensors
                                       // to ascii output file. Introduced in ver 1.0
  bool optional_keys = true ;       // default to include optional keys in .dba files

  // Initialize the sensor list cache path.
  init_cache_path() ;

  Options opts(*argv, optv) ;
  OptArgvIter iter(--argc, ++argv) ;


  // Process all the command line switches
  // There has to be at least one
  if ( argc == 0 )
    {
      opts.usage(cout, usage_str_tail);
      return EXIT_FAILURE ;
    }

  // Process the switches
  int optchar ;
  const char * optarg = NULL ;
  while ( optchar = opts(iter, optarg))
    {
      switch(optchar)
        {
        case 'h': // --help
          opts.usage(cout, usage_str_tail);
          return EXIT_SUCCESS ;

        case 's': // --stdin
          read_from_stdin = true ;
          break ;

        case 'o': // --output-initial-values
          output_initial_values = true ;
          break ;

        case 'c': // --cache-path
          set_cache_path(optarg) ;
          break ;
          
        case 'k': // --backward-regression
          optional_keys = false ;
          break ;


      case Options::BADCHAR :  // bad option ("-%c", *optarg)
      case Options::BADKWD  :  // bad long-option ("--%s", optarg)
      case Options::AMBIGUOUS  :  // ambiguous long-option ("--%s", optarg)
      default :
        cout << "Error! " ;
        opts.usage(cout, usage_str_tail);
        return EXIT_FAILURE ;

        }
    }

  // Inform the user what cache path is active.
  // cerr << "Sensor list cache path is '" << get_cache_path() << "'\n" ;

  // Make sure all segments of the cache path exist.
  create_entire_path(get_cache_path()) ;

  start_adding_to_cache() ;
  //cerr << "Adding to cache is enabled\n" ;

  // Process the filenames on the command line
  // We simply build a list of all the filenames
  for ( int i = iter.index() ; i < argc ; i++)
    {
      // Add the filename to the list as a string
      const char * filename_to_add = argv[i] ;
      input_filenames.push_back( filename_to_add ) ;
    }


  // Process the filenames from stdin
  // We add to list of all the filenames
  if ( read_from_stdin)
    {
      OptIstreamIter in_iter(cin) ;
      const char * filename_to_add = NULL ;
      while ( (filename_to_add = in_iter()) != NULL)
        {
          // Add the filename to the list as a string
          input_filenames.push_back( filename_to_add ) ;
        }
    }

  // Turn the list of filenames into list of sorted
  // headers.  This verifies that files exist and are
  // actually dbd files. Bad filenames are announced to
  // cerr and then ignored.
  // This does NOT throw any dbd exceptions
  dbd_header_collection input_dbd_headers( input_filenames, cerr ) ;

  // If there is nothing to do, quit
  if ( input_dbd_headers.size() <= 0 )
    {
      cerr << "Nothing to process!" << endl ;
      return EXIT_FAILURE ;
    }

  // Write the ascii header
  if ( input_dbd_headers.write_asc_header(cout, optional_keys) )
    {
      cerr << "Error from write_asc_header()" << endl ;
      return EXIT_FAILURE ;
    }

  /* Read and Write all the data
     By default, we never output the initial values
     If user requests it, we will output the initial values
     on the very first segment
  */
  dbd_header_collection::iterator h_iter ;
  bool first_segment = true ;
  for ( h_iter  = input_dbd_headers.begin() ;
        h_iter != input_dbd_headers.end()  ;
        h_iter++)
    {
      // first_segment controls where we MIGHT write line of initial values
      if ( input_dbd_headers.write_asc_data(h_iter, cout,
                                            first_segment && output_initial_values) )
        {
          cerr << "Error from write_asc_data()" << endl ;
          return EXIT_FAILURE ;
        }

      // Only write initial values once
      first_segment = false ;
    }

  // All went well
  return EXIT_SUCCESS ;

}

