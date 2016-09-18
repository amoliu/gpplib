// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* mas_string.h

Some class-less standalone functions that manipulate strings

18-Jul-01 tc@DinkumSoftware.com Initial
20-Sep-01 tc@DinkumSoftware.com Documented with Doxygen
 4-Dec-01 tc@DinkumSoftware.com Added to_double()
07-Dec-01 tc@DinkumSoftware.com Added include of stdio.h, this
                                was req'd to get it to compile
                                under Metrowerks.  Haven't a clue
                                why!
 */

#ifndef MAS_STRING_H
#define MAS_STRING_H

#include <stdio.h> // Reqd to get it to compile under Metrowerks
#include <string>

/// collection of standalone string functions
namespace mas_string
{

  // Converts "s" to lower case and returns it
  string & to_lower(string & s) ;


  // Converts "s" to a double
  bool to_double( const string & s, double & value ) ;

} // namespace mas_string

#endif // MAS_STRING_H

