// Copyright(c) 2001-2003, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_support.c

18-Sep-01 tc@DinkumSoftware.com Added Doxygen documentation
18-Jul-03  fnj@DinkumSoftware.com  Added parse_header_line_hex for a long.
27-Jul-03 tc@DinkumSoftware.com port to linux, workaround broken >> hex
                                iomanip in parse_header_line_hex()
03-Mar-10 dpingal@webbresearch.com EOF on end instead of END_CYCLE_TAG is OK
 */

#include <sstream>
#include <cctype>  // isxdigit()
#include "dbd_support.h"
#include "dbdfrmat.h"


using namespace std ;
using namespace dinkum_binary_data ;



/// Parses a key: value line from a DBD header
/**
  \param ins stream to read from
  \param expected_key key to parse
  \param value corresonding value output here

Throws an exception if key doesn't match
*/
void dbd_support::parse_header_line(istream & ins, const string expected_key,
                                    string & value)  throw (dbd_error)
{
  parse_key( ins, expected_key ) ;    // Consume and check the key
  ins >> value ;

}

/// Parses a key: value line from a DBD header
/**
  \param ins stream to read from
  \param expected_key key to parse
  \param value corresonding value output here

Throws an exception if key doesn't match
*/
void dbd_support::parse_header_line(istream & ins, const string expected_key,
                                 int & value) throw (dbd_error)
{
  parse_key( ins, expected_key ) ;    // Consume and check the key
  ins >> value ;
}

/// Parses a key: value line from a DBD header
/**
  \param ins stream to read from
  \param expected_key key to parse
  \param value corresonding value output here

Throws an exception if key doesn't match
*/
void dbd_support::parse_header_line(istream & ins, const string expected_key,
                                    long & value) throw (dbd_error)
{
  parse_key( ins, expected_key ) ;    // Consume and check the key
  ins >> value ;
}

/// Parses a key: value line from a DBD header
/**
  \param ins stream to read from
  \param expected_key key to parse
  \param value corresonding value output here

Throws an exception if key doesn't match
*/
void dbd_support::parse_header_line(istream & ins, const string expected_key,
                                    unsigned long & value) throw (dbd_error)
{
  parse_key( ins, expected_key ) ;    // Consume and check the key
  ins >> value ;
}

/// Parses a key: value line from a DBD header
/**
  \param ins stream to read from
  \param expected_key key to parse
  \param value corresonding value output here

Throws an exception if key doesn't match or the value
string doesn't appear to be a boolean value.
Acceptable values are T,t,1 for true and F,f,0 for false.

*/
void dbd_support::parse_header_line(istream & ins, const string expected_key,
                                    bool & value)   throw (dbd_error)
{
  parse_key( ins, expected_key ) ;    // Consume and check the key

  char c ;    // There is a T,F,t,f,0,or 1 in file
  ins >> c ;

  switch (c)
    {
    case 'T':
    case 't':
    case '1':
      value = true ; break ;

    case 'F':
    case 'f':
    case '0':
      value = false ; break ;

    default:
      {
        ostringstream emsg ;
        emsg << "Wrong value for boolean field"
             << expect_str() << "T t 1 F f 0"
             << got_str() << c  ;
        throw dbd_error(emsg) ;
      }
    }

}


/// Parses a key: value line from a DBD header
//  sensor_list_crc:    9C982D99
/**
  \param ins stream to read from
  \param expected_key key to parse
  \param value corresonding value output here

Throws an exception if key doesn't match
*/
void dbd_support::parse_header_line_hex(istream & ins, const string expected_key,
                                        unsigned long & value) throw (dbd_error)
{
  // 27-Jul-03 tc@DinkumSoftware.com linux bug fix
  // >> hex didn't work

  string crc_in_hex ; 
  parse_header_line(ins, expected_key, crc_in_hex) ;

  /* Convert our string to hex
     We are expecting something like:  9C982D99
     We got do it ourselves cause >> hex on
     linux didn't work
  */
  const int expected_length = 8 ;
  if ( crc_in_hex.length() != expected_length)
    {
      ostringstream emsg ;
      emsg << "Wrong number of digits in "
           << expected_key << " " << crc_in_hex
           << ", expecting " << expected_length ;
      throw dbd_error(emsg) ;
    }

  // Iterate backwards over the string (msb to lsb)
  // converting the ascii hex digit and accumulating
  // it in value
  int pos ;
  value = 0 ;
  for ( pos = 0 ; pos < expected_length ; pos++)
    {
      // Make space in where we are totalizing
      value <<= 4 ;

      // retrive the current char position
      char c = tolower(crc_in_hex.at(pos)) ;

      // legal hex digit?
      if ( !isxdigit(c) )
        {
          ostringstream emsg ;
          emsg << "Non hex digits in "
               << expected_key << " " << crc_in_hex
               << ", expecting " << expected_length ;
          throw dbd_error(emsg) ;
        }

      // convert the char to appropriate hex value
      int this_char_hex_value ;
      if ( (c >= 'a') && ( c <= 'f') )
        this_char_hex_value = c - 'a' + 10 ;
      else if ( (c >= '0') && ( c <= '9') )
        this_char_hex_value = c - '0' ;
      else
        {
          // we shouldn't be here we checked before
          ostringstream emsg ;
          emsg << "Software error in parse_header_line_hex() "
               << expected_key << " " << crc_in_hex ;
          throw dbd_error(emsg) ;
        }

      // totalize this character
      value += this_char_hex_value ;

    }


}


/// Reads key of a DBD header line
/**
   \param ins stream to read from
   \param expected_key key to look for

Reads, checks and throws away expected_key from ins.
Throws exception if key doesn't match.
 */
void dbd_support::parse_key( istream &ins,
                             const string expected_key)
                             throw (dbd_error)
{
  string key_from_file ;  // what we read from the file

  // Read the key
  ins >> key_from_file ;

  // We read the right key?
  if ( key_from_file != expected_key)
    {
      ostringstream emsg ;
      emsg << "Wrong ascii field"
           << expect_str() << expected_key
           << got_str() << key_from_file ;
      throw dbd_error(emsg) ;
    }



}

/// Expects to read the binary value that signals start of a data cycle
/**
   \param ins stream to read from
   \param expected_tag type of tag to read DATA_CYCLE_TAG or SAMPLE_CYCLE_TAG

Silently consumes the tag if it matches.  Throws an exception if it doesn't
match.

Normally returns false, but returns true on ENDFILE_CYCLE_TAG or EOF

 */
bool dbd_support::read_cycle_tag(istream & ins, const unsigned char expected_tag)
                      throw (dbd_error)
    {

      unsigned char tag_from_file = ins.get() ;

      // Check for EOF
      if ( tag_from_file == ENDFILE_CYCLE_TAG || ins.eof() )
        return true ;    // ran out of data

      // Check for getting what we expected
      else if ( tag_from_file != expected_tag )
        { // Unknown tag
          ostringstream emsg ;
          emsg << "bad binary cycle tag" << expect_str() << expected_tag
               << got_str() << hex << "0x" << (int) tag_from_file ;
          throw ( dbd_error( emsg) ) ;    // bye
        }

      // We got out tag, tell 'um we didn't hit EOF
      return false ;
    }
