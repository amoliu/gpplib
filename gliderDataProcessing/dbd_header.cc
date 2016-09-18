// Copyright(c) 2001-2005, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_header.cc

21-Apr-01 tc@DinkumSoftware.com Initial
18-Jul-01 tc@DinkumSoftware.com Added a copy constructor
                                and < operator for sorting
19-Jul-01 tc@DinkumSoftware.com bug fixes on porting to WinDoze
21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
26-Sep-01 tc@DinkumSoftware.com Support for 8 byte doubles
26-Jul-03  fnj@DinkumSoftware.com  Added handling factored sensor lists.
                                   Added a param to ctor to tell whether
                                   to parse the entire header or just the
                                   ASCII key:value lines.
28-Jul-03 tc@DinkumSoftware.com Put ctor: parm back: read_abbrv_hdr
29-Jul-03 tc@DinkumSoftware.com output all cache names in lower case
 6-Oct-05 tc@DinkumSoftware.com Bug fix: read_and_parse_sensor_info() 
                                If an error occured while running dbd2asc (this is done
                                automatically in GliderView) and a cache file was being
                                written..... the cache file could be corrupted.  This corrupt
                                file would make any subsequent processing of files without
                                headers (typically a subsequent *.sdb) to fail with a
                                mysterious error message.
                                This was repaired by removing any open cache files when
                                an error is encountered.
25-Aug-08 fnj@webbresearch.com  fileopen_time_t has been replaced by fileopen_time_struct;
                                modify copy constructor, operator <, and read_and_parse_header()
                                accordingly.  Replace member function set_fileopen_time_t()
                                with set_fileopen_time_struct().
// 21-Dec-09 tc@DinkumSoftware.com include syntax change
//                                 include stdlib.h for getenv()
*/

#include <stdlib.h>
#include <iomanip>
#include <iostream>
#include <sstream>

#include "stat_iface.h"
#include "dbd_header.h"
#include "dbd_sensor_value.h"
#include "dbdfrmat.h"    // specs keys and the like
#include "mas_time.h"    // asctime_to_time_t()

using namespace dinkum_binary_data ;

// This is only used for performance tuning, i.e.
// the initial size of containers.  It's ok if it's
// not big enuf
static const int expected_number_of_sensors = 300 ;

namespace dinkum_binary_data
{

// Will we add to the cache?
bool add_to_cache = false ;

// Path to sensor list cache directory.
string cache_path = "./cache" ;

void start_adding_to_cache()
{
    add_to_cache = true ;
}

void stop_adding_to_cache()
{
    add_to_cache = false ;
}

bool get_adding_to_cache()
{
    return add_to_cache ;
}

void init_cache_path()
{
    cache_path = "./cache" ;
    char* s = getenv("GLIDER_PARENT_DIR") ;
    if (s)
    {
        cache_path = s ;
        if (cache_path.substr(cache_path.length() - 1) != ":"
        &&  cache_path.substr(cache_path.length() - 1) != "/"
        &&  cache_path.substr(cache_path.length() - 1) != "\\")
        {
            cache_path += '/';
        }
        cache_path += "cache" ;
    }
}

void set_cache_path(const string& s)
{
    cache_path = s ;
}

string get_cache_path()
{
    return cache_path ;
}

bool create_entire_path(const string& path)
{
    bool result = true ;
    const char* separators = "/\\" ;

    // Look for existing object.
    struct stat stat_buf ;
    if (stat(path.c_str(), &stat_buf))
    {
        // Does not exist yet - create it.
        int pos = path.find_last_of(separators) ;
        if (pos > 0)
        {
            // Create parent dirs via recursion.
            result = result && create_entire_path(path.substr(0, pos)) ;
        }
        // Create node.
        result = result && (mkdir(path.c_str(), 0755) == 0) ;
    }
    else if (!(stat_buf.st_mode & S_IFDIR))
    {
        // Object already exists, but is not a dir.
        result = false ;
    }

    return result ;
}

} // namespace dinkum_binary_data


/// constructor, reads and parses the header from a DBD file
/**

Throws an exception on any kind of error.

An example header we read:

\verbatim
dbd_label:    DBD(dinkum_binary_data)file
encoding_ver:    1
num_ascii_tags:    11
all_sensors:    T
the8x3_filename:    00410000
full_filename:    zippy-2001-115-2-0
mission_name:    SASHBOX.MI
fileopen_time:    Thu_Apr_26_07:35:08_2001
total_num_sensors:    216
sensors_per_cycle:    216
state_bytes_per_cycle:    54

\endverbatim
 */

dbd_header::dbd_header(istream & ins, const char * filename,
                       bool read_abbrv_hdr ) throw (dbd_error)
  :
  dbd_reqd_header(ins, filename),  // our base class
  full_sensor_list(expected_number_of_sensors)

{

    // the ascii (key,value) lines
    // These set member variables
    read_and_parse_header() ;

    // If they want only an abbreviated header....
    if ( read_abbrv_hdr )
      return ; // we are all done


    // Accumulate a list of sensors if desired
    read_and_parse_sensor_info() ;

    // We've read all the ascii portions
    // Flush any remaining whitespace
    _ins >> ws ;

    // Read binary cycle with "known" values
    read_known_data_line() ;



}

/// Copy constructor
dbd_header::dbd_header(const dbd_header & them) throw (dbd_error)
  :
  dbd_reqd_header(them),
  full_sensor_list  (them.full_sensor_list),
  infile_sensor_list(them.infile_sensor_list),
  swab_info         (them.swab_info)
{

  all_sensors            = them.all_sensors ;
  the8x3_filename        = them.the8x3_filename ;
  full_filename          = them.full_filename ;
  filename_extension     = them.filename_extension ;
  mission_name           = them.mission_name ;
  fileopen_time          = them.fileopen_time ;
    fileopen_time_struct =  them.fileopen_time_struct ;
  total_num_sensors      = them.total_num_sensors ;
  sensors_per_cycle      = them.sensors_per_cycle ;
  state_bytes_per_cycle  = them.state_bytes_per_cycle ;
  sensor_list_crc        = them.sensor_list_crc ;
  sensor_list_factored   = them.sensor_list_factored ;


}


void dbd_header::read_and_parse_header() throw (dbd_error)
{

    // Read the required lines of ascii header
    // Basically identifiers dbd file, encoding version,
    // and total number of ascii header lines
    int n = do_reqd_header_lines(DBD_LABEL_VALUE) ;

    // Read the remainder of the headers we know about
    // Count in "n" the number we read
    do_a_header_line(ALL_SENSORS_KEY,           all_sensors       )    ; n++ ;
    do_a_header_line(THE8x3_FILENAME_KEY,       the8x3_filename   )    ; n++ ;
    do_a_header_line(FULL_FILENAME_KEY,         full_filename     )    ; n++ ;
    do_a_header_line(FILENAME_EXTENSION_KEY,    filename_extension)    ; n++ ;
    do_a_header_line(MISSION_NAME_KEY,          mission_name      )    ; n++ ;
    do_a_header_line(FILEOPEN_TIME_KEY,         fileopen_time     )    ; n++ ;
    do_a_header_line(TOTAL_NUM_SENSORS_KEY,     total_num_sensors )    ; n++ ;
    do_a_header_line(SENSORS_PER_CYCLE_KEY,     sensors_per_cycle )    ; n++ ;
    do_a_header_line(STATE_BYTES_PER_CYCLE_KEY, state_bytes_per_cycle) ; n++ ;
    if (num_ascii_tags > n + 1)
    {
        if (encoding_ver > 4)
        {
          do_a_header_line_hex(SENSOR_LIST_CRC, sensor_list_crc )    ; n++ ;
        }
        else
        {
            do_a_header_line(SENSOR_LIST_CRC,   sensor_list_crc   )    ; n++ ;
        }
        do_a_header_line(SENSOR_LIST_FACTORED,  sensor_list_factored)  ; n++ ;
    }

    /* In case somebody added some ....
       i.e. format of *.dbd file changed....
       Eat the remainder of the header lines, even though we
       don't know what they are
    */
    for (; n < num_ascii_tags ; n++)
        eat_a_header_line() ;

    // set other data elements that we compute from the header strings
    set_fileopen_time_struct() ;

}

// 6-Oct-05 tc@DinkumSoftware.com Bug fix: read_and_parse_sensor_info() 
//                                removed any cache files opened for writin
void dbd_header::read_and_parse_sensor_info() throw (dbd_error)
{
    bool read_existing_cache_file = (encoding_ver >= 4 && num_ascii_tags >= 14 && sensor_list_factored) ;
    // cerr << "@@@@@ read_existing_cache_file = " << read_existing_cache_file << '\n' ;
    bool write_new_cache_file = (encoding_ver >= 4 && num_ascii_tags >= 14 && !sensor_list_factored && add_to_cache ) ;
    // cerr << "@@@@@ write_new_cache_file = " << write_new_cache_file << '\n' ;

    ifstream existing_cache_file ;
    if (read_existing_cache_file)
    {
        ostringstream ss ;
        string path = cache_path ;
        if (path.substr(path.length() - 1) != ":"
        &&  path.substr(path.length() - 1) != "/"
        &&  path.substr(path.length() - 1) != "\\")
        {
            path += '/';
        }

        // Create the filename we want
        ostringstream base_filename ;
        base_filename << hex << setfill('0') << setw(8) << sensor_list_crc ;

        // Convert it to lowercase to insure linux/windoze compatibility
        string base_filename_str = base_filename.str() ;
        int i ;
        for (i=0 ; i < base_filename_str.length() ; i++)
          base_filename_str.at(i) = tolower(base_filename_str.at(i)) ;

        ss << path << base_filename_str << ".cac" ;

        existing_cache_file.open(ss.str().c_str()) ;
        if (!existing_cache_file.is_open())
        {
            ostringstream emsg ;
            emsg << "Can't open cache file " << ss.str() ;
            throw dbd_error(emsg) ;
        }
    }

    // the name/handle on any cache file open for writing
    ofstream new_cache_file ;         // only valid if write_new_cache_file==T
    string   new_cache_filename ;    // ditto 
    if (write_new_cache_file)
    {
        ostringstream ss ;
        string path = cache_path ;
        if (path.substr(path.length() - 1) != ":"
        &&  path.substr(path.length() - 1) != "/"
        &&  path.substr(path.length() - 1) != "\\")
        {
            path += '/';
        }

        // Create the filename we want
        ostringstream base_filename ;
        base_filename << hex << setfill('0') << setw(8) << sensor_list_crc ;

        // Convert it to lowercase to insure linux/windoze compatibility
        string base_filename_str = base_filename.str() ;
        int i ;
        for (i=0 ; i < base_filename_str.length() ; i++)
          base_filename_str.at(i) = tolower(base_filename_str.at(i)) ;

        ss << path << base_filename_str << ".cac" ;

        // Make a copy of the filename for use in later catch block
        new_cache_filename = ss.str() ;


        new_cache_file.open(new_cache_filename.c_str()) ;
        if (!new_cache_file.is_open())
        {
            ostringstream emsg ;
            emsg << "Can't create cache file " << new_cache_filename ;
            throw dbd_error(emsg) ;
        }
    }

    // This kludge is is needed because apparently the types
    // on either side of the ":" in the "? :" construct
    // have to be exactly the same type.
    istream& existing_cache_file_kludge_ref = existing_cache_file ;
    istream& ins = read_existing_cache_file ? existing_cache_file_kludge_ref : _ins ;

    /* The rest of this function is in a try block to catch (and rethrow) ANY exeception
       This is to allow us to close and delete any cache file that we are in the process
       of writing.  Otherwise, a partially written (and hence corrupt) cache file will
       be left around
    */
    try
      {
        // Read a line for every sensor defined
        for (int i = 0 ; i < total_num_sensors ; i++)
          {
            if (write_new_cache_file)
              {
                // Remember where the line starts.
                istream::pos_type start_of_line = ins.tellg() ;
                if (start_of_line == istream::pos_type(-1))
                  {
                    ostringstream emsg ;
                    emsg << "Can't obtain stream position in data file" ;
                    throw dbd_error(emsg) ;
                  }

                // Read the line.
                string s ;
                char c ;
                ins >> noskipws >> c >> skipws ;
                getline(ins, s) ;
                // ins >> s ;
                // mygetline(ins, s) ;
                if (ins.fail())
                  {
                    ostringstream emsg ;
                    emsg << "Failed to read sensor line from data file" ;
                    throw dbd_error(emsg) ;
                  }
                
                // Write the line to the cache file.
                new_cache_file << s << '\n' ;
                if (new_cache_file.fail())
                  {
                    ostringstream emsg ;
                    emsg << "Failed to write sensor line to cache file" ;
                    throw dbd_error(emsg) ;
                  }
                
                // Rewind to the start of the line so we can read it again.
                ins.seekg(start_of_line) ;
                if (ins.fail())
                  {
                    ostringstream emsg ;
                    emsg << "Can't restore stream position in data file" ;
                    throw dbd_error(emsg) ;
                  }
              }

            dbd_sensor_info next ;
            bool in_file = next.read_sensor_info_line(ins, all_sensors, i) ;

            // Put it on end of full list
            full_sensor_list.push_back(next) ;

            // Is it in the file?
            if ( in_file )
              {
                // Yep, put it on the list
                infile_sensor_list.push_back(next) ;
              }

          } // end of Read a line for every sensor
      } // end of try block

    catch(...)     // Catch ANY and ALL execeptions
      {
        // If we are writing a cache file....
        if (write_new_cache_file)
          {
            // the cache file is only partially written
            // hence it is corrupt
            // We need to close and DELETE it
            new_cache_file.close() ; // ignore errors
            remove(new_cache_filename.c_str()) ; // ignore errors
          }


        // rethrow the SAME exeception
        // so someone else really handles it
        throw ;
      }

    // Normally (i.e. no errors) returns from here....
}




/*

  We're expecting:
    <swap_cycle_tag>    one byte cycle identifier
    <sample_byte>               'a'
    <sample_2byte_int>          0x1234
    <sample_4byte_float>       123.456

For encoding version 2 and higher
    <sample_8byte_double>      123456789.12345

*/

void dbd_header::read_known_data_line() throw (dbd_error)
{

  // SAMPLE_CYCLE_TAG
  read_cycle_tag( _ins, SAMPLE_CYCLE_TAG ) ;

  dbd_sensor_value test ;

  // get the next char from the stream
  // 'a'
  const unsigned char known_c = SAMPLE_BYTE ;
  test.figure_swab( _ins, known_c, swab_info ) ;

  // Get the next 2 byte int from the file
  // We will test to see if we have to swap them
  // to get the expected 0x1234.  We remember this!
  const int known_int = SAMPLE_2BYTE_INT ;
  test.figure_swab (_ins, known_int, swab_info) ;

  // And similiarly for a 4 byte float
  const float known_float = SAMPLE_4BYTE_FLOAT ;
  test.figure_swab (_ins, known_float, swab_info) ;

  // If this is a new data set...
  if ( are_doubles_in_file() )
    {
      const double known_double = SAMPLE_8BYTE_DOUBLE ;
      test.figure_swab (_ins, known_double, swab_info) ;
    }

}


// operator <

/// Used for sorting headers.

/**
We base the sort on the "fileopen_time-t"
*/

// 18-Jul-01 tc@DinkumSoftware.com Initial
// 25-Aug-08 fnj@webbresearch.com  Recoded to use struct tm rather than time_t.


bool dbd_header::operator< ( const dbd_header & them ) const
{

  if (fileopen_time_struct.tm_year != them.fileopen_time_struct.tm_year) return fileopen_time_struct.tm_year < them.fileopen_time_struct.tm_year ;
  if (fileopen_time_struct.tm_mon  != them.fileopen_time_struct.tm_mon ) return fileopen_time_struct.tm_mon  < them.fileopen_time_struct.tm_mon  ;
  if (fileopen_time_struct.tm_mday != them.fileopen_time_struct.tm_mday) return fileopen_time_struct.tm_mday < them.fileopen_time_struct.tm_mday ;
  if (fileopen_time_struct.tm_hour != them.fileopen_time_struct.tm_hour) return fileopen_time_struct.tm_hour < them.fileopen_time_struct.tm_hour ;
  if (fileopen_time_struct.tm_min  != them.fileopen_time_struct.tm_min ) return fileopen_time_struct.tm_min  < them.fileopen_time_struct.tm_min  ;
  return fileopen_time_struct.tm_sec  < them.fileopen_time_struct.tm_sec  ;
}


/* set_fileopen_time_struct

Computes and sets fileopen_time_struct from fileopen_time.

e.g.
    fileopen_time:        Fri_Jul_13_21:51:12_2001
    fileopen_time_struct: set to corresponding components

Throws an exception on error.

18-Jul-01 tc@DinkumSoftware.com Initial
19-Jul-01 tc@DinkumSoftware.com bug fixes, arg to replace wrong
25-Aug-08 fnj@webbresearch.com  Changed name and modified mission to
                                fill in struct tm rather than set time_t.
*/

struct tm dbd_header::set_fileopen_time_struct() throw(dbd_error)
{

  // Make a copy of fileopen_time
  string asctime_str(fileopen_time) ;

  // change underscores to spaces
  // this gets us back to original output of asctime()
  const char char_to_replace  = '_' ;
  const char replacement_char = ' ' ;
  string::size_type indx = 0 ;
  while ( (indx = asctime_str.find( char_to_replace, indx)) != string::npos )
    asctime_str.replace(indx, 1, 1, replacement_char) ;

  // Convert to structure
  if ( mas_time::asctime_to_time_struct( asctime_str, fileopen_time_struct ) )
  {
    // Error converting the string
    ostringstream emsg ;
    emsg << "Bad fileopen_time " << fileopen_time ;
    throw ( dbd_error( emsg) ) ;    // bye
  }

  // All went ok
  return fileopen_time_struct ;
}
