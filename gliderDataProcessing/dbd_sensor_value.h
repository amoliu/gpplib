// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_sensor_value.h
 */

#ifndef DBD_SENSOR_VALUE_H
#define DBD_SENSOR_VALUE_H

#include "dbd_sensor_info.h"
#include "dbd_swab.h" 
#include "dbd_support.h"

namespace dinkum_binary_data
{

  /// Tells what kind of data is being held
  enum dbd_sensor_value_type {has_not_been_set, isa_int, isa_float, isa_double} ;

  /// Holds the value of a single sensor (variable)
  /*
    The value is typically read from a DBD file and can be
    an integer or floating point number.
   */
class dbd_sensor_value : private dbd_support
  {
  public:
    /// constructor, makes empty, non-valid
    dbd_sensor_value()
      {    reset() ;
           _data_type = has_not_been_set ;
      }

    /// Tells if a value has been set
    bool is_valid() const { return __is_valid ; }

    /// Tells if value is an integer type
    bool is_int()   const { return _data_type == isa_int   ; }
    int  get_int()  const throw (dbd_error) ;

    /// tells if value is a floating point type
    bool is_float() const { return _data_type == isa_float ; }
    float get_float() const throw (dbd_error) ;


    /// Tells if value is double
    bool is_double() const { return _data_type == isa_double ; }
    double get_double() const throw (dbd_error) ;

    /// Marks value invalid, e.g. empty
    void reset()
      {  __is_valid = false ;
      }

    // Marks the valud valid and specifies type
    void validate(enum dbd_sensor_value_type svt)
      {
        _data_type = svt ;
        validate() ;
      }

    /// Marks the value valid
    void validate()
      {    __is_valid = true ;
      }


    bool read_sensor_value( istream & ins, const dbd_sensor_info & info,
                            const dbd_swab & swab_info)
      throw (dbd_error) ;

    // Read a floating point value from an ASCII stream or string
    double read_asc_double(istream & ins)  ;
    double read_asc_double(string  & str)  ;

  private:
    bool __is_valid ;

    /// What kind of value it is
    enum dbd_sensor_value_type _data_type ;

    /// Holds the value
    union 
    {
        /// as integer 
        int ivalue ;
       /// as float
        float fvalue ;
       /// as double
        double dvalue ;

    } _data ;


    int   read_binary_int( istream & ins, int bytes_to_read)
      throw (dbd_error) ;
    float  read_binary_float( istream & ins, int bytes_to_read) ;
    double read_binary_double( istream & ins, int bytes_to_read) throw (dbd_error) ;


  public:
    /// Reads a value equal to known from ins and sets info
    void figure_swab(istream & ins, unsigned char known, dbd_swab & info) throw (dbd_error) ;
    /// Reads a value equal to known from ins and sets info
    void figure_swab(istream & ins, int           known, dbd_swab & info) throw (dbd_error) ;
    /// Reads a value equal to known from ins and sets info
    void figure_swab(istream & ins, float         known, dbd_swab & info) throw (dbd_error) ;
    /// Reads a value equal to known from ins and sets info
    void figure_swab(istream & ins, double        known, dbd_swab & info) throw (dbd_error) ;

  private:

    void swab_int   (const dbd_swab & info) ;
    void swab_float (const dbd_swab & info) ;
    void swab_double(const dbd_swab & info) ;

  } ; // class dbd_sensor_value

} // namespace dinkum_binary_data

#endif // DBD_SENSOR_value_H
