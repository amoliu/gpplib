// Copyright(c) 2009 Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_asc_merged_header.cc

23-Sep-09 tc@DinkumSoftware.com Initial
30-Sep-09 tc@DinkumSoftware.com Added sci_m_present_time
06-Oct-09 tc@DinkumSoftware.com  bug fix, cout was hardwired instead of outs
06-Oct-09 dpingal@webbresearch.com fixed mantis 644 -- m_present_secs_into_mission
                                   not required to process
Table of contents
    dbd_asc_merged_header    constructor

    read_and_merge_asc       read a line
    write_asc                write a line

    merge_segment_filenames
    handle_duplicated_sensors
    pick_input_line_to_use
    sensor_copy_if_missing

*/

#include "dbd_asc_merged_header.h"


using namespace dinkum_binary_data ;


/* dbd_asc_merged_header

Constructor.

Initializes with a copy of the glider header and adjusts the the contents by
merging in the science_header.

23-Sep-09 tc@DinkumSoftware.com Initial
 1-Oct-09 tc@DinkumSoftware.com Adjusting the sensor renaming algorithm

*/


dbd_asc_merged_header::dbd_asc_merged_header( const dbd_asc_header & glider_header,
                                              const dbd_asc_header & science_header)
  : dbd_asc_header(glider_header, NULL),   // init us with copy of glider

    _glider_header(glider_header),         // and copy headers we are merging
    _science_header(science_header),

    _glider_data(_glider_header),          // input data
    _glider_has_data(false),

    _science_data(_science_header),
    _science_has_data(false),

    _merged_data_ptr(NULL)                // we allocate it in constructor body


{

// We are now a copy of the glider

// Add in any unique additional segment filenames that appear in the
// science segment list that aren't in the glider list
  merge_segment_filenames() ;


// Adjust the sensor list by adding on the science sensors.
  // Total count
  sensors_per_cycle =
    _glider_header.sensors_per_cycle  +
    _science_header.sensors_per_cycle ;

  // Iterate over science sensors
  for (int ss = 0 ; ss <  _science_header.sensor_list.size() ; ss++)
    // tack it on to end of our list
    sensor_list.push_back( _science_header.sensor_list[ss] ) ;


// Create output data line
  _merged_data_ptr = new dbd_sensor_value_collection(*this) ;

  /* handle sensors that exist in both science and glider
     this "renames" the one of the copys of the duplicated sensor.
        sci_XXX  ==> gld_dup_sci_XXX    [in glider copy]
        YYY      ==> sci_dup_YYY        [in science copy]

  */
  handle_duplicated_sensors() ;

}



/* read_and_merge_asc

Normally returns true.  Returns false when no more data (EOF on
both headers we are reading)

Throws dbd_error exeception on error.

Algorithm:
    1. We read data from either header that is empty, ignoring eof
    2. Return false if both input lines are empty
    3. Select an input line that occurred earliest in time
    4. Construct an output line from the selected input line with Nan
       for data from the other line, insuring that
    5. empty the input line we selected

24-Sep-09 tc@DinkumSoftware.com Initial
12-Apr-10 dpingal@webbresearch.com  Put try block around merge of
                                    m_present_secs_into_mission, will
                                    now successfully merge files without it
*/

bool dbd_asc_merged_header::read_and_merge_asc()
{

  // We read data from any data set that is empty
  if ( ! _glider_has_data )
    {
    _glider_has_data = _glider_data.read_asc( _glider_header._ins) ;

    }
  if ( ! _science_has_data )
    {
      _science_has_data = _science_data.read_asc( _science_header._ins) ;
    }

  // Return false if both input lines are empty
  // Select an input line that occurred earliest in time
  bool use_glider_data ; // T==>use it, F=>don't
  bool use_science_data ;
  if ( ! pick_input_line_to_use( use_glider_data, use_science_data) )
    // Neither line has data
    return false ;


  // Construct an output line from the selected input line with Nan
  //  for data from the other line
  // empty the input line we selected
  _merged_data_ptr->reset() ; // clean out any old data
  if ( use_glider_data )
    {
      // Copy in the glider data
      int in  = 0 ;// starting copy positions
      int out = 0 ;
      while (in < _glider_data.sensors_per_cycle )
        {
          (*_merged_data_ptr)[out++] = _glider_data[in++] ;
        }
      _glider_has_data = false ;
    }

  if ( use_science_data )
    {
      // Copy in the science data
      int in  = 0 ;// starting copy positions
      int out = _glider_data.sensors_per_cycle ;  // just past the glider data
      while (in < _science_data.sensors_per_cycle )
        {
          (*_merged_data_ptr)[out++] = _science_data[in++] ;
        }
      _science_has_data = false ;
    }

  /* Almost all the downstream processing requires a timestamp on every line,
     which for historical reason is one of the glider (as opposed to science)
     sensors. The lines with science data only don't have these sensors, but
     they have some equivalent.

     To avoid breaking old data processing chains, we copy the science equivalent
     to the glider timestamps if they are missing.
  */
  //                      science name                       glider name
  sensor_copy_if_missing( "sci_m_present_time",              "m_present_time" ) ;
  // If there is no m_present_secs_into_mission, that's OK
  try
  {
    sensor_copy_if_missing( "sci_m_present_secs_into_mission", "m_present_secs_into_mission" ) ;
  }
  catch (dinkum_binary_data::dbd_error error)
  {
  }

  // Tell them that there is more data
  return true ;

}

/* write_asc

Writes a line of merged data from internal storage to "outs"

Throws dbd_error exeception on error.

24-Sep-09 tc@DinkumSoftware.com Initial
06-Oct-09 tc@DinkumSoftware.com  bug fix, cout was hardwired instead of outs

*/

void dbd_asc_merged_header::write_asc(ostream & outs) const
{
  // sanity check
  if ( _merged_data_ptr == NULL)
    throw (dbd_error("dbd_asc_merged_header.cc::write_asc() software error: _merged_data_ptr is NULL")) ;

  // Just write our line
  _merged_data_ptr->write_asc(*this, outs) ;

}



/* merge_segment_filenames

Adds unique segment filenames from science to us.
Presumes we have been inited with a copy of the glider.

24-Sep-09 tc@DinkumSoftware.com Initial, refactored from inline

*/

void dbd_asc_merged_header::merge_segment_filenames()
{

  // Iterate over segment filenames in science
  for (int ss = 0 ; ss < _science_header.segment_filenames.size() ; ss++)
    {
      /* this science segment already included in our list?
             This used to work:
                 if ( find (segment_filenames.begin() , segment_filenames.end(),
                      _science_header.segment_filenames[ss])                 == segment_filenames.end())
             but was getting compile errors, so I rewrote
      */

      // Iterate over the segment names we already have
      int os ;
      for ( os = 0 ; os < segment_filenames.size() ; os++)
        {
          // We already have this one?
          if ( _science_header.segment_filenames[ss] == segment_filenames[os] )
            {
              // yes, quit looking
              break ;
            }
        }
      /* If we break out of loop [os < segment_filenames.size()]
         then _science_header.segment_filenames[ss] is already in
         our list and we have nothing to do... otherwise...
      */
      if ( os >= segment_filenames.size() )
        {
          // stick science segment on the end of our segment list
          merge_segment_filename ( _science_header.segment_filenames[ss] ) ;
        }

    }
}


/* handle_duplicated_sensors

Prevents duplicated sensors in the output, i.e. the same sensor in both glider and science.

Any duplicated sensor is renamed by prepending something to the original sensorname:
    sci_XXX  ==> gld_dup_sci_XXX    [in glider copy]
    YYY      ==> sci_dup_YYY        [in science copy]

The idea is that sci_XXX originates on science and the science copy should be preserved.
Otherwise, YYY originates on the glider and the glider copy should be preserved


25-Sep-09 tc@DinkumSoftware.com Initial
 1-Oct-09 tc@DinkumSoftware.com Adjusting the sensor renaming algorithm
*/

void dbd_asc_merged_header::handle_duplicated_sensors()
{
  // How we tell whether science or glider originates
  // we rename the non-originating copy
  const string sci_originates_leading_str("sci_") ;

  const string glider_rename_prepend( "gld_dup_") ;
  const string science_rename_prepend("sci_dup_") ;

  // Iterate over the science sensor names
  for ( int sci = 0 ; sci < _science_header.sensors_per_cycle ; sci++)
    {
      // Pick off the sensor we are testing
      dbd_sensor_info sci_sensor = _science_header.sensor_list[sci] ;

      // Iterate over glider sensors, checking for duplicates
      for ( int gld = 0 ; gld < _glider_header.sensors_per_cycle ; gld++)
        {
          // Pick off the sensor we are testing
          dbd_sensor_info gld_sensor = _glider_header.sensor_list[gld] ;

          // Is it a duplicate?
          if ( sci_sensor.name == gld_sensor.name )
            {
              // Orignate on science?
              if ( sci_sensor.name.find(sci_originates_leading_str) == 0 )
                {
                  // originates on science, rename the glider copy
                  // NOTE: we count on the index being the same, i.e. the
                  //       glider sensors come before the science sensors
                  sensor_list[gld].name = glider_rename_prepend + gld_sensor.name ;
                }
              else
                {
                  // originates on glider, rename the science copy
                  // NOTE: we count glider sensors come before the science sensors
                  sensor_list[_glider_header.sensors_per_cycle + sci].name = science_rename_prepend + sci_sensor.name ;
                }

              // and quit looking
              break ;
            }
        }
    }
}


/* pick_input_line_to_use

Selects which line(s) of input data (glider/science) to use and
sets "use_glider/science_data" appropriately.

Normally returns true, returns false if no more input data.

24-Sep-09 tc@DinkumSoftware.com Initial

 */


bool dbd_asc_merged_header::pick_input_line_to_use( bool & use_glider_data,
                                                    bool & use_science_data) const
{
  // If there is data, assume we use it
  use_glider_data  = _glider_has_data ;
  use_science_data = _science_has_data ;

  // If neither has data (i.e. both at EOF).....
  if ( !use_glider_data && !use_science_data)
    return false ; // no more input data

  // Do both have data ?
  if ( ! (use_glider_data && use_science_data))
    // no, use the one (preset) we have
    return true ; // say more data to come

  // There is data for both glider and science
  // Figure out when the data happened
  const double glider_timestamp  = _glider_data.lookup_as_double(_glider_header.sensor_list,
                                                                 "m_present_time") ;
  const double science_timestamp = _science_data.lookup_as_double(_science_header.sensor_list,
                                                                  "sci_m_present_time") ;


  // Only use the early of the two data lines
  // Use both if time is identical (neither if triggers)
  if ( glider_timestamp < science_timestamp)
    use_science_data = false ;
  else if ( science_timestamp < glider_timestamp)
    use_glider_data = false ;

  // Tell um we have more data
  return true ;

}



/* sensor_copy_if_missing

If "gld_sensorname" isn't set in our output data, set's it value to "sci_sensorname".

Why?....

     Almost all the downstream processing requires a timestamp on every line,
     which for historical reason is one of the glider (as opposed to science)
     sensors. The lines with science data don't have these sensors, but
     they have some equivalent.

     To avoid breaking old data processing chains, we copy the science equivalent
     to the glider timestamps if the glider copy isn't set

25-Sep-09 tc@DinkumSoftware.com Initial
*/


void dbd_asc_merged_header::sensor_copy_if_missing(const char * sci_sensorname, const char * gld_sensorname)
{
  // sanity check
  if ( _merged_data_ptr == NULL)
    throw (dbd_error("dbd_asc_merged_header.cc::sensor_copy_if_missing() software error: _merged_data_ptr is NULL")) ;

  // Get the glider copy
  dbd_sensor_value & gld_sensor_value = _merged_data_ptr->lookup(sensor_list, gld_sensorname) ;

  // Is it set?
  if ( gld_sensor_value.is_valid() )
    // yes, we are all done
    return ;

  // glider copy is NOT set
  // copy in science equivalent
  dbd_sensor_value & sci_sensor_value = _merged_data_ptr->lookup(sensor_list, sci_sensorname) ;
  gld_sensor_value = sci_sensor_value ;

}
