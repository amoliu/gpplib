// Copyright(c) 2001-2008, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_header.h

21-Apr-01 tc@DinkumSoftware.com Initial
18-Jul-01 tc@DinkumSoftware.com Added a copy constructor
                                and operator <
21-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
26-Sep-01 tc@DinkumSoftware.com Support for 8 byte doubles
26-Jul-03  fnj@DinkumSoftware.com  Added handling factored sensor lists.
                                   Added a param to ctor to tell whether
                                   to parse the entire header or just the
                                   ASCII key:value lines.
27-Jul-03 tc@DinkumSoftware.com removed full arg, always read full reader
                                Changed sensor_list_crc from long to unsigned long
28-Jul-03 tc@DinkumSoftware.com Put ctor: parm back: read_abbrv_hdr
25-Aug-08 fnj@webbresearch.com  Replaced "field time_t fileopen_time_t" in class dbd_header
                                with "struct tm fileopen_time_struct".
                                Replaced "time_t set_fileopen_time_t()" in class dbd_header
                                with "struct tm set_fileopen_time_struct()".
*/


#ifndef DBD_HEADER_H
#define DBD_HEADER_H

#include <iostream>
#include <vector>
//#include <time.h>

#include "dbd_reqd_header.h" // class we derive from
#include "dbd_error.h"       // class we throw() on error

#include "dbdfrmat.h" // FIRST_VERSION_WITH_DOUBLES

#include "dbd_sensor_info.h"
#include "dbd_swab.h"


namespace dinkum_binary_data
{

void start_adding_to_cache() ;

void stop_adding_to_cache() ;

bool get_adding_to_cache() ;

void init_cache_path() ;

void set_cache_path(const string& s) ;

string get_cache_path() ;

bool create_entire_path(const string& path) ;

  /// Parses and holds all the information in header of DBD file
  /**
     Holds all the information contained in the header of a DBD file.
     Can be created by opening and parsing a DBD file or by copying
     another header.

   */
class dbd_header : public  dbd_reqd_header
  {
  public:
    // construct by reading from file
    dbd_header(istream & ins, const char * filename,
               bool read_abbrv_hdr = false ) throw (dbd_error) ;

    // copy constructor
    dbd_header(const dbd_header & them) throw (dbd_error) ;

    // Header contents of file parsed and set here
    // Available to user of the class
  public:

    /// T -> all sensors present in the file
    bool all_sensors ;

    /// Original filename, e.g. 00230042
    string the8x3_filename ;

    /// translated name, e.g. zippy-2001-222-04-05
    string full_filename ;

    /// the extension on the filename, e.g. dbd or sbd
    string filename_extension ;

    /// filename of the mission that was run
    string mission_name ;

    /// When the file was originally created
    string fileopen_time ;
        /// When the file was originally created
        struct tm fileopen_time_struct ; // computed in constructor

    /// Total number of variables in full data set
    int total_num_sensors ;

    /// The number of variables written each cycle
    int sensors_per_cycle ;

    /// How many bytes of data used to encode variable state
    int state_bytes_per_cycle ;

    // CRC32 of the sensor list.
    unsigned long sensor_list_crc ;

    // Is the sensor list factored out?
    bool sensor_list_factored ;


    /// Where we keep info about all the sensors (variables)
    vector<dbd_sensor_info> full_sensor_list ;

    /// Where we keep info about all the sensors in the file
    vector<dbd_sensor_info> infile_sensor_list ;

    /// Tells if filling, e.g. replacing NaN
    bool are_filling() const { return false ; }

    /// Contains information on byte order of data
    dbd_swab swab_info ; // how to swap bytes stored here

    // A comparision operator used for sorting headers
    bool operator< ( const dbd_header & them ) const ;

 private:

    /// translates fileopen_time string to struct tm fileopen_time_struct
    struct tm set_fileopen_time_struct() throw(dbd_error) ;


// ascii line parsing functions
  void read_and_parse_header()  throw (dbd_error) ;


// Sensor information

  // funcs to read sensor info
  void read_and_parse_sensor_info() throw (dbd_error) ;


  // Binary reader stuff
  void read_known_data_line() throw (dbd_error) ;


  /// Tells (based on encoding version) if 8 bytes doubles present in file
  bool are_doubles_in_file() const
    {
      // Simply test the encoding version
      return encoding_ver >= FIRST_VERSION_WITH_DOUBLES ;
    }

  }; // class dbd_header


} // namespace dinkum_binary_data


#endif // DBD_HEADER_H
