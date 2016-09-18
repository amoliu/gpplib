// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* mas_string.cc

Collection of class-less standalone functions that manipulate
strings.

18-Jul-01 tc@DinkumSoftware.com Initial
20-Sep-01 tc@DinkumSoftware.com Documented with doxygen
 4-Dec-01 tc@DinkumSoftware.com Added to_double
 6-Dec-01 tc@DinkumSoftware.com doxygen fixes
*/

#include <cmath>     // HUGE_VAL
#include <ctype.h>   // tolower()
#include <stdio.h>   // sscanf()
#include "mas_string.h"

using namespace mas_string ;

/// Converts "s" to lower case and returns it
/**
   \param s string to convert
   \return a reference to the converted string
*/
string & mas_string::to_lower(string & s)
{

  // Examine each character and convert it to lower case
  string::size_type i ;
  for ( i = 0 ; i < s.length() ; i++)
    {
      s.replace( i, 1, 1, tolower (s[i] ) ) ;
    }

  // Give um back the argument
  return s ;
}


/// Converts "s" to a double
/**
   \param s string to convert
   \param value The output (HUGE_VAL on error)
   \return Normally returns false, returns true on error
*/

bool mas_string::to_double( const string & s, double & value )
{

  // The %lf converts the double
  // The %c will be set to the first unused character
  // It's an error if we don't consume the whole string
  char trail_c ;
  int num_fields_converted = sscanf ( s.c_str(), " %lf %c", &value, &trail_c) ;


  // Did we convert exactly one field?
  bool was_an_error = false ; // assume the best
  if ( num_fields_converted != 1 )
    {
      // No, We had an error
      value = HUGE_VAL ;
      was_an_error = true ;
    }

  // Tell um how it went
  return was_an_error ;

}
