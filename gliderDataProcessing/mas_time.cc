// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* mas_time.cc

18-Jul-01 tc@DinkumSoftware.com Initial
19-Jul-01 tc@DinkumSoftware.com bug fixes on porting to WinDoze
20-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
13-Feb-02 tc@DinkumSoftware.com Added gmt_time_as_str()
25-Aug-08 fnj@webbresearch.com  Replaced asctime_to_time_t with asctime_to_time_struct.
                                N.B.: WE GOT DEBUG TRACE CODE ENABLED (see "@@@@@").
15-Oct-08 fnj@webbresearch.com  Commented out debug code.
*/

#include <iostream> // @@@@@
#include <sstream>
#include <time.h>   // asctime(), gmtime() 
#include "mas_time.h"
#include "mas_string.h"

using namespace mas_time ;


// asctime_to_time_struct

/// Converts the output of asctime() to a struct tm value

/**
   \param  asctime_str  String to convert
   \param  t converted time output here

\return Normally returns false, returns true on error

asctime_str should be the output of asctime():

    Fri Jul 13 21:51:12 2001

*/
/*
18-Jul-01 tc@DinkumSoftware.com Initial
19-Jul-01 tc@DinkumSoftware.com args to replace wrong()
25-Aug-08 fnj@webbresearch.com  Changed name and modified mission.
*/

bool mas_time::asctime_to_time_struct(const string & asctime_str, struct tm & tm)
{

  // Copy our input argument so we can alter it
  // Fri Jul 13 21:51:12 2001
  string in_str(asctime_str) ;

  // Convert : to spaces
  const char char_to_replace  = ':' ;
  const char replacement_char = ' ' ;
  string::size_type indx = 0 ;
  while ( (indx = in_str.find( char_to_replace, indx)) != string::npos )
    in_str.replace(indx, 1, 1, replacement_char) ;

  // what we are going to parse to
  // Fri Jul 13 21 51 12 2001
  string wday_str ; // Fri
  string mon_str  ; // Jul     jan-dec
  int    mday     ; // 13      1-31
  int    hour     ; // 21      0-23
  int    min      ; // 51      0-59
  int    sec      ; // 12      0-59
  int    year     ; // 2001    > 1900

  // change to stringstream so we can use >> to parse it
  // Extract all the fields
  stringstream in(in_str) ;

  in >> wday_str >> mon_str >> mday >> hour >> min >> sec >> year ;

  // The struct we need to set
  struct tm  working_tm ;
  working_tm.tm_isdst = 0 ;    // NOT daylight savings
                              // tm_yday, tm_wday need not be set

  // Error check each element and set it into structure
  // we simply return true on any error
  if ( year < 1900 ) return true ;
  working_tm.tm_year = year - 1900 ;

  int mon = month_str_to_month_num(mon_str) ;
  if ( mon < 0 ) return true ;
  working_tm.tm_mon = mon ;

  if ( (mday < 1) || (mday > 31) ) return true ;
  working_tm.tm_mday = mday ;

  if ( (hour <0) || (hour > 23) ) return true ;
  working_tm.tm_hour = hour ;

  if ( (min < 0) || (min > 59)) return true ;
  working_tm.tm_min = min ;

  if ( (sec < 0) || (sec > 59)) return true ;
  working_tm.tm_sec = sec ;

  // std::cerr << "@@@@@ year  = " << working_tm.tm_year << '\n' ; // @@@@@
  // std::cerr << "@@@@@ month = " << working_tm.tm_mon  << '\n' ; // @@@@@
  // std::cerr << "@@@@@ day   = " << working_tm.tm_mday << '\n' ; // @@@@@
  // std::cerr << "@@@@@ hour  = " << working_tm.tm_hour << '\n' ; // @@@@@
  // std::cerr << "@@@@@ min   = " << working_tm.tm_min  << '\n' ; // @@@@@
  // std::cerr << "@@@@@ sec   = " << working_tm.tm_sec  << '\n' ; // @@@@@

  // All went ok
  // Say no error
  tm = working_tm ;

  return false ;
}


// month_str_to_month_num

///  converts month string to month number
/**

\param    mon_str   Month to convert
\return returns the month number 0 to 11, -1 on error

  "jan" --> 0

Conversion is case insensitive.

*/

/*
18-Jul-01 tc@DinkumSoftware.com Initial
*/


int mas_time::month_str_to_month_num(string mon_str)
{
  // what we return on error, i.e. no match
  const int error_indication = -1 ;

  // Data we are matching against
  const int num_months = 12 ;
  static const char * month_name_table[ num_months ] =
  { "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
  } ;

  // Make a copy of our input string and convert it to lower case
  string in_str(mon_str) ;
  mas_string::to_lower( in_str ) ;


  // Search the table looking for a match
  for ( int month_num = 0 ; month_num < num_months ; month_num++)
    {
      // Match?
      if ( in_str.compare( month_name_table[month_num])  == 0 )
        return month_num ;    // yes, we're done
    }

  // If we fall out of the loop, we didn't match
  // indicate an error
  return error_indication ;
}


// gmt_time_as_str

/// Returns current gmt time as human readable string
/**


   Example return:
    GMT: Wed Feb 13 11:28:49 EST 2002

   The memory used to store the string is overwritten on each call.

 */

const string & mas_time::gmt_time_as_str()
{

  // Where we build the answer
  static string returned_string ;
  returned_string = "GMT:" ;

  // Get the time in the epoch
  time_t time_output ;
  time_t * time_output_ptr = & time_output ;
  if (time( time_output_ptr) == -1)
    {
      // error
      returned_string += "time() not available" ;
      return returned_string ;
    }

  // Convert to GMT (UTC)
  struct tm * gmtime_output_ptr = gmtime( time_output_ptr) ;
  if (  gmtime_output_ptr == NULL)
    {
      // error
      returned_string += "gmtime() not available" ;
      return returned_string  ;
    }

  // Convert to human readable format
  returned_string += asctime( gmtime_output_ptr) ;

  // Strip all the trailing new-line's
  string::size_type indx ;
  while ( (indx = returned_string.rfind( '\n' )) != string::npos )
  {
    returned_string.erase(indx) ;
  }


  // give them the answer
  return returned_string ;

}

