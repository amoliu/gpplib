// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* mas_time.h

A collection of standalone (class-less) functions that
supplement the standard C library time functions

20-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
13-Feb-02 tc@DinkumSoftware.com Added gmt_time_as_str()
25-Aug-08 fnj@webbresearch.com  Replaced asctime_to_time_t() with asctime_to_time_struct().
*/

#ifndef MAS_TIME_H
#define MAS_TIME_H

#include <string>
#include "time.h"

/// A collection of standalone time related functions 

namespace mas_time
{

  // Converts output of asctime() to time_t
  // normally returns false, returns true on error
  bool asctime_to_time_struct(const string & asctime_str, struct tm & tm) ;

  // converts month string to month number
  // e.g. "jan" --> 0   returns -1 on error
  int month_str_to_month_num(string mon_str) ;

  // returns current GMT time as string
  const string & gmt_time_as_str() ;


} // namespace mas_time

#endif // MAS_TIME_H
