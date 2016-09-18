// Copyright(c) 2001-2009, Teledyne Webb Research, ALL RIGHTS RESERVED
/* dba2_orig_matlab.cc

Reads dinkum binary ascii data from stdin (output of dbd2asc)
and writes two matlab files (your filenames will vary):

    zippy_2001_104_21_0_dbd.m
    zippy_2001_104_21_0_dbd.dat

The output format is identical to the initial matlab files produced
in the development of the Webb Research Glider.

To use the file, from matlab, execute:
    
    zippy_2001_104_21_0_dbd.m

It reads the *.dat file

At the end of this file is an example .m and .dat file


26-Apr-01 tc@DinkumSoftware.com Initial
30-Apr-01 tc@DinkumSoftware.com Changed - to _ in filenames
                                Added filename extension
14-May-01 tc@DinkumSoftware.com Made it echo name of *.m file
                                 to stdout
13-Aug-01 tc@DinkumSoftware.com Added "global data" to the m-file
31-Jul-03 kniewiad@DinkumSoftware.com Added structure creation in gen_the_m_file
21-Jan-04 trout.r@comcast.net Added code to write ascii header keys as globals
                              to .m matlab file.  This code was commented out to
                              preserve backward compatability, yet have it if needed
                              in the future.  See the member function gen_the_m_file.
30-Jan-04 trout.r@comcast.net Fixed m_present_time is NaN defect.  
2009-11-17 pfurey@webbresearch.com  Support for processing science data files.
22-Dec-09 tc@DinkumSoftware.com  Debugging prior change
                                 


Table of contents
    main
    base_matlab_filename Chooses * of *.m, *.dat
    gen_the_m_file       Makes the *.m file

*/

#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include "dbd_asc_header.h"
#include "dbd_sensor_value_collection.h"

using namespace dinkum_binary_data ;

static string base_matlab_filename(const dbd_asc_header & hdr) ;

static void gen_the_m_file(const dbd_asc_header & hdr,
                           double secs_since_eden ) throw (dbd_error) ;
                           
                           
#pragma warn_unusedarg off
int main(int argc, char* argv[] )
{
  // What we say when we get an error
  const string error_msg_leadin = "ERROR prog: dba2_orig_matlab: " ;

  try
    {
      // Read in the ascii header
      dbd_asc_header  hdr(cin) ;

      // We have to preread the first line of data, cause
      // we need a value of M_PRESENT_TIME
      // buffer the line
      // Transfer a line into "buffer"
      string buffer ;
      while ( !cin.eof() )
        {
          char c ;
          cin.get(c) ;
          buffer += c ;
          if ( c == '\n')
            break ;
          
        }
      
      // PROTECT against an input DBA file with no data
      // in it.  Without this, dba2_orig_matlab hangs
      // forever
      if ( cin.eof() )
        {
          // No data in the file
          ostringstream emsg ;
          emsg << "Input *.dba file has no data in it, you might try dbd2asc -o" ;
          throw ( dbd_error(emsg) ) ;
        }

      // and make a copy for later outputing
      string buffer_copy( buffer) ;

      //parse it into first_line_values
      dbd_sensor_value_collection first_line_values(hdr) ;
      first_line_values.read_asc(buffer) ;

      // get what we need
      double mission_start_secs_since_eden = -1.0 ;
    
      string x_present_time_sensor ;
      try
      {
        // Look for m_present_time from glider
        x_present_time_sensor = "m_present_time" ;
        first_line_values.is_valid(hdr.sensor_list, x_present_time_sensor);
      }

      catch (dbd_error e)
      {
        // couldn't find m_present_time from glider
        // hope it is a science only file
        // look for science equivalent
        x_present_time_sensor = "sci_m_present_time" ;
        first_line_values.is_valid(hdr.sensor_list, x_present_time_sensor);
      }

      mission_start_secs_since_eden =
        first_line_values.lookup_as_double(hdr.sensor_list, x_present_time_sensor);

      // Produce the *.m file
      gen_the_m_file(hdr, mission_start_secs_since_eden) ;


      // Pick the *.dat filename
      string dat_filename = base_matlab_filename(hdr) ;
      dat_filename += ".dat" ;

      // Open up the *.dat file
      // We just have to copy data lines
      ofstream dat(dat_filename.c_str()) ;
      if ( !dat )
        {
          ostringstream emsg ;
          emsg << "Couldn't open filename: " << dat_filename ;
          throw ( dbd_error(emsg) ) ;
        }

      // Output the first data line we preread
      // It's sitting in buffer
      dat << buffer_copy ;

      // Copy the rest of the lines
      while(true)
      {
        // Get a char and quit on EOF
        char c ;
        cin.get(c) ; // read next input char
        if (cin.eof() ) break ;

        dat << c ;  // output it
      }

      // all done
    }
  catch(dbd_error e)
    {
      cerr << error_msg_leadin << e.get_err_msg() << endl ; 
    }
  catch(...)
    {   cerr << error_msg_leadin << "Unknown Exception Caught" << endl ;
    }



  // Life is good
  return 0 ;
}
#pragma warn_unusedarg on


string base_matlab_filename(const dbd_asc_header & hdr)
{
  // We start with the same filename as the *.dbd file
  string m_filename = hdr.filename ;

  // Tack on the filename extension, so dbd and sbd files have
  // unique filenames
  m_filename += '-' ;
  m_filename += hdr.filename_extension ;

  // Change all the -'s to _'s cause matlab thinks
  // they mean subtraction
  const char frm_c = '-' ;
  const char to_c  = '_' ; 

  int indx = 0 ;    // Position of the - we want to replace
  while ( (indx = m_filename.find( frm_c, indx)) != string::npos )
    {
      // We found a char, replace it
      // The 1's are the number of chars to replace
      m_filename.replace ( indx, 1, 1, to_c) ;
    }

  // Give them answer
  return m_filename ;

}





/* ------------------ Examples --------------------------------
------------------ z0110203.m ---------------------------------
% column indices for Glider data
% binary vehicle file: z0110203.obd
% tabular ascii file:  z0110203.dat

global run_name
run_name = 'z0110203';

% OS-9 process start time: 2001/04/12 17:21:12 GMT     
% structure creation time: 12 Apr 2001 17:21:11 Z     

clear time0
start = 987096071.00;
     f_max_working_depth =   1;
            u_cycle_time =   2;
          m_present_time =   3;
m_present_secs_into_mission =   4;

        ....... etc .......

                 s_speed = 212;
                s_vx_lmc = 213;
                s_vy_lmc = 214;
                 s_x_lmc = 215;
                 s_y_lmc = 216;
load('z0110203.dat')
data = z0110203;
clear z0110203


*/

/* gen_the_m_file

Produces a file similar to above.

The filename is echoed to stdout.

*/

void gen_the_m_file(const dbd_asc_header & hdr,
                    double start_secs_since_eden) throw (dbd_error)
{

  // Pick the filename
  // We have to change all the - to _ cause matlab thinks its a subtraction
  // zippy_2001_104_21_0.m
  const string base_filename = base_matlab_filename(hdr) ;

  string m_filename = base_filename ;
  m_filename += ".m" ;
  
  // Open up the file
  ofstream mf(m_filename.c_str() ) ;
  if ( !mf )
    {
      ostringstream emsg ;
      emsg << "Couldn't open filename: " << m_filename ;
      throw ( dbd_error(emsg) ) ;
    }

  // Blow out the fixed stuff
  mf << "% column indices for Glider data"                    << endl ;
  mf << "% binary vehicle file: " << hdr.filename_label       << endl ;
  mf << "% tabular ascii file:  " << base_filename  << ".dat" << endl ;
  mf << "global run_name"                                     << endl ;
  mf << "global data"                                         << endl ;
  mf << "run_name = '" << hdr.filename_label << "';"          << endl ;
  mf << "% OS-9 process start time: " << hdr.fileopen_time    << endl ;
  mf << "% structure creation time: " << hdr.fileopen_time    << endl ;
  mf << "clear time0"                                         << endl ;
  mf << "start = " ;
  if (start_secs_since_eden < 0.0)
  {
    mf << "NaN" ;
  }
  else
  {
    mf << start_secs_since_eden ;
  }
  mf << " ;" << endl ;

  /* List all the sensors
     Note well:  We count starting at index 0,
                 matlab starts at 1 !!
     f_max_working_depth =   1;
            u_cycle_time =   2;
          m_present_time =   3;
        ....... etc .......
  */
  for ( int i = 0 ; i < hdr.sensors_per_cycle ; i++ )
    {
      mf << "global " << hdr.sensor_list[i].name << endl ;
      mf << hdr.sensor_list[i].name << " = " << i+1 << " ;" << endl ;
    }  

/* Decided NOT to include header keys in Matlab globals to maintain backward
   compatibility with regression tests.  Uncomment if needed in the future.

  // Write the asc header keys and values just in case they're needed
  // downstream someday.
  // Required keys to matlab m file
  hdr.required_keys_to_matlab_globals(mf) ;
  
  //Optional keys to matlab m file
  hdr.optional_keys_to_matlab_globals(mf) ;
    
*/

  // finish up
  mf << "load('"  << base_filename << ".dat')"                << endl ;
  mf << "data = " << base_filename << ";"                     << endl ;
  mf << "clear "  << base_filename                            << endl ;


  // Tell um the name
  cout << m_filename << endl ;

  // file gets closed as it is destructed

}


 /*
>------------------ z0110203.dat ---------------------------------
>  There is one line per cycle
>  all the sensor values (in order) separated by spaces.
>-----------------------------------------------------------------
30	2	9.8709606e+08	2.316	0.07	.......
NaN	NaN	9.8709606e+08	5.2750001	NaN	.......


*/
