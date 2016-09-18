// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_value.cc
 */

#include <cmath>
#include "dbd_sensor_value.h"
#include "dbdfrmat.h"
#include "mas_string.h"

using namespace dinkum_binary_data ;



/// reads and parse a sensors value from a stream
/**

\param ins    stream to read from
\param info   Describes the sensor (variable) we are about to read
\param swab_info Tells how to byte swap the binary data

\return Returns is_valid(), i.e. true if data was successfully read and
false if not, typically because reached End of File.

Throws an exception on any kind of error.

*/

bool dbd_sensor_value::read_sensor_value( istream & ins,
                                          const dbd_sensor_info & info,
                                          const dbd_swab & swab_info)
  throw (dbd_error)
{

  // assume it doesn't work
  reset() ;

  switch (info.orig_bytes_of_storage)
    {
    case DATA_TYPE_BYTE:
      _data.ivalue = read_binary_int( ins, info.orig_bytes_of_storage ) ;
      validate(isa_int) ;
      break ;
      
    case DATA_TYPE_INT:
      _data.ivalue = read_binary_int( ins, info.orig_bytes_of_storage ) ;
      validate(isa_int) ;
      swab_int(swab_info) ;
      break ;

    case DATA_TYPE_FLOAT:
      _data.fvalue = read_binary_float( ins, info.orig_bytes_of_storage ) ;
      validate(isa_float) ;
      swab_float(swab_info) ;
      break ;

    case DATA_TYPE_DOUBLE:
      _data.dvalue = read_binary_double( ins, info.orig_bytes_of_storage ) ;
      validate(isa_double) ;
      swab_double(swab_info) ;
      break ;
      
    default:
      ostringstream emsg ;
      emsg << "Sensor: " << info.name << ", unknown bytes of storage="
           << info.orig_bytes_of_storage ;
      throw (dbd_error(emsg)) ;
    }

  // See if we ran out of data
  if ( ins.eof() )
    reset() ;  // yes, mark invalid

  // tell um if we hit the end
  return is_valid() ;

}



/// Returns value as integer, exception if value not integer
int dbd_sensor_value::get_int() const throw (dbd_error)
{
  if ( is_int() )
  {
    return _data.ivalue ;
  }
  else
  {
    throw (dbd_error("dbd_sensor_value::get_int() Value is NOT integer")) ;
  }
  
  // we don't ever get here, but Metrowerks 5.3 can't seem to figure that out
  return -69 ;
}

/// Returns value as float, exception if value not float
float dbd_sensor_value::get_float() const throw (dbd_error)
{
  if ( is_float() )
  {
    return _data.fvalue ;
  }
  else
  {
    throw (dbd_error("dbd_sensor_value::get_float() Value is NOT float")) ;
  }

  // we don't ever get here, but Metrowerks 5.3 can't seem to figure that out
  return -69.0 ;

}


/// Returns value as double, exception if not double
double dbd_sensor_value::get_double() const throw (dbd_error)
{
  if ( is_double() )
  {
    return _data.dvalue ;
  }
  else
  {
    throw (dbd_error("dbd_sensor_value::get_double() Value is NOT double")) ;
  }

  // we don't ever get here, but Metrowerks 5.3 can't seem to figure that out
  return -69.0 ;

}




int dbd_sensor_value::read_binary_int( istream & ins, int bytes_to_read)
  throw (dbd_error )
{
  int ivalue = 0 ;
  
  // Read each byte and stuff it in lsb's
  const int bits_per_byte = 8 ;
  int counter = bytes_to_read ;
  while (counter-- > 0 )
    {
      unsigned char c = ins.get() ;
      ivalue <<= bits_per_byte ;
      ivalue |= (c & 0xFF) ;
    }

  // Sign extend negative numbers
  switch (bytes_to_read)
    {
    case 1:
      // Is it negative?
      if ( ivalue & 0x80 )
        {    // yes, make upper bits 1
             ivalue |= ~0xFF ;
        }
      break; 
    case 2:
      // If it's only a 2 byte int, nothing to do
      if ( sizeof(int) == 2) break ;

      // Is it negative?
      if ( ivalue & 0x80 )
        {    // yes, make upper bits 1
             ivalue |= ~0xFFFF ;
        }
      break ;

    default:
      ostringstream emsg ;
      emsg << "read_binary_int(), invalid # bytes_to_read: "
           << bytes_to_read ;
      throw (dbd_error(emsg)) ;
    }


  return ivalue ;
}


float dbd_sensor_value::read_binary_float( istream & ins, int bytes_to_read)
{

  union
  {
      unsigned long read_here ;
      float    return_this ;
  } datum ; 

  // Read each byte and stuff it in lsb's
  datum.read_here = 0 ;
  const int bits_per_byte = 8 ;
  while (bytes_to_read-- > 0 )
    {
      unsigned char c = ins.get() ;

      datum.read_here <<= bits_per_byte ;
      datum.read_here |= (c & 0xFF) ;
    }

  // Now give it back to them as a float
  return datum.return_this ;
}

double dbd_sensor_value::read_binary_double( istream & ins, int bytes_to_read) throw (dbd_error)
{

  // sanity check, give um bad value if sizes don't match
  const int sizeof_double = sizeof(double) ;
  if ( bytes_to_read > sizeof_double )
    {
      ostringstream emsg ;
      emsg << "Sample Double has too many bytes"
           << expect_str() << sizeof_double
           << got_str() << bytes_to_read ;
      throw (dbd_error(emsg)) ;
    }


  union
  {
      unsigned char read_here[sizeof_double] ;
      double   return_this ;
  } datum ; 

  // Read each byte and stuff it in lsb's
  for ( int i = 0 ; i < bytes_to_read ; i++)
    {
      // Stuff from lsb to msb
      const int indx = sizeof_double-i-1 ;  // i goes 0->7, indx goes 7->0
      datum.read_here[indx] = ins.get() ;
    }

  // Now give it back to them as a double
  return datum.return_this ;
}



/* NOTE: In the initial implementation, we didn't need to swap any bytes ...
   So these merely test the rest and throw an error if it doesn't match.
   At some point in the future, they can swap bytes around and record
   what they did in "info"
*/
#pragma warn_unusedarg off   // info
void dbd_sensor_value::figure_swab(istream & ins, unsigned char known, dbd_swab & info)
  throw (dbd_error) 

{
  // Read the byte from the file
  unsigned char read_c = read_binary_int(ins, 1) ;

  // Make sure it's whatwe expect
  if ( read_c != known)
    {
      ostringstream emsg ;
      emsg << "Sample Byte does not match"
           << expect_str() << known
           << got_str() << read_c ;
      throw (dbd_error(emsg)) ;
    }
}
void dbd_sensor_value::figure_swab(istream & ins, int   known, dbd_swab & info)
  throw (dbd_error) 
{
  // Read the bytes from the file
  int read_int = read_binary_int(ins, 2) ;

  // Make sure it's what we expect
  if ( read_int != known)
    {
      ostringstream emsg ;
      emsg << "Sample int does not match"
           << expect_str() << known
           << got_str() << read_int ;
      throw (dbd_error(emsg)) ;
    }

}

void dbd_sensor_value::figure_swab(istream & ins, float known, dbd_swab & info)
  throw (dbd_error) 
{
  // Read the bytes from the file
  float read_float = read_binary_float(ins, 4) ;

  // Make sure it's what we expect
  if ( read_float != known)
    {
      ostringstream emsg ;
      emsg << "Sample float does not match"
           << expect_str() << known
           << got_str() << read_float ;
      throw (dbd_error(emsg)) ;
    }

}
void dbd_sensor_value::figure_swab(istream & ins, double known, dbd_swab & info)
  throw (dbd_error) 
{
  // Read the bytes from the file
  double read_double = read_binary_double(ins, 8) ;

  // Make sure it's what we expect
  if ( read_double != known)
    {
      ostringstream emsg ;
      emsg << "Sample double does not match"
           << expect_str() << known
           << got_str() << read_double ;
      throw (dbd_error(emsg)) ;
    }

}


void dbd_sensor_value::swab_int(const dbd_swab & info)
   {}
void dbd_sensor_value::swab_float(const dbd_swab & info)
 {}
void dbd_sensor_value::swab_double(const dbd_swab & info)
 {}
 
 
#pragma warn_unusedarg on


/// Reads and stores a floating point value from an ASCII stream
/**

\param ins  stream to read from

*/

double dbd_sensor_value::read_asc_double(istream & ins)

{

  // Create a string of what we want to convert
  string token ;
  ins >> ws >> token ;


  // Let someone else the work
  read_asc_double( token ) ;


  // Tell um how it went
  return is_valid() ? _data.dvalue : HUGE_VAL ;


}

/// Reads and stores a floating point value from a string
/**

Check is_valid() to see if it succeeded.

\param str  string to read from

\return Returns the value converted

*/

double dbd_sensor_value::read_asc_double(string  & str)
{
  const double ret_value_on_err = HUGE_VAL ; // gotta return something

  // Mark the data as invalid
  reset() ;
  
  // Check for NaN
  if ( str == invalid_sensor_str() )
    {
      return ret_value_on_err ;
    }

  else
    {
      // Try to convert it
      if ( ! mas_string::to_double( str, _data.dvalue ) )
        {
          // Success
          validate( isa_double) ;
          return _data.dvalue ;
        }
    }
  
  // Conversion failed
  return ret_value_on_err ;
}

