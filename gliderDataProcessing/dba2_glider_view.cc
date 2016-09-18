// Copyright(c) 2004, Webb Research Corporation, ALL RIGHTS RESERVED
/* dba2_glider_view.cc

Reads dinkum binary ascii data from stdin (output of dbd2asc)
and writes two matlab files (your filenames will vary):

    zippy_2001_104_21_0_dbd_glv.txt
    zippy_2001_104_21_0_dbd_glv.dat

This file are processed by glider_data.exe

23-Mar-04 trout.r@comcast.net Initial file copied from dba2_glider_data.cc
							  and modified to output .txt and .dat files
							  consumed by glider_data.exe
2006-03-13 fnj@DinkumSoftware.com    In gen_the_txt_file: changed max_length from 30 to 63.
                                     In Matlab 6.5.1, variable names may be of any length,
                                     and are significant up to 63 characters.  There are
                                     starting to be masterdata sensor names that are not
                                     disambiguated until after the 30th character.
                                     Note: not sure why we should truncate them at all here.

Table of contents
    main
    base_matlab_filename Chooses * of *.txt, *.dat
    gen_the_txt_file       Makes the *.txt file

*/

#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include "dbd_asc_header.h"
#include "dbd_sensor_value_collection.h"

using namespace dinkum_binary_data ;

static string base_matlab_filename(const dbd_asc_header & hdr) ;

static void gen_the_txt_file(const dbd_asc_header & hdr) throw (dbd_error) ;
                           
                           
#pragma warn_unusedarg off
int main(int argc, char* argv[] )
{
  // What we say when we get an error
  const string error_msg_leadin = "ERROR prog: dba2_glider_view: " ;

  try
    {
      // Read in the ascii header
      dbd_asc_header  hdr(cin) ;

      // Produce the *.m file
      gen_the_txt_file(hdr) ;


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

  // Tack on the filename extension, so dbd, sbd, and gld files have
  // unique filenames
  m_filename = m_filename + "-" + hdr.filename_extension + "-glv" ;

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
------------------ 0057000X.txt ---------------------------------
run_name = 'ru04-2003-196-7-X(0057000X)';
segment_filenames = ru04-2003-196-7-0, ru04-2003-196-7-1;
all_sensors = 1;
filename = ru04-2003-196-7-X;
the8x3_filename = 0057000X;
mission_name = HOLD.MI;
sensors_per_cycle = 520;
num_segments = 2;
c_acoustic_modem_target_id = 415 ;
c_air_pump = 300 ;
c_alt_time = 284 ;
c_argos_on = 347 ;
c_att_time = 256 ;
c_ballast_pumped = 197 ;
c_battpos = 212 ;
c_battroll = 224 ;
.
.
.
*/

/* gen_the_txt_file

Produces a file similar to above.

The filename is echoed to stdout.

2006-03-13 fnj@DinkumSoftware.com    Changed max_length from 30 to 63.
*/

void gen_the_txt_file(const dbd_asc_header & hdr) throw (dbd_error)
{

  // Pick the filename
  // We have to change all the - to _ cause matlab thinks its a subtraction
  // ru04-2003-196-7-X-dbd-glv.txt
  const string base_filename = base_matlab_filename(hdr) ;

  string m_filename = base_filename ;
  m_filename += ".txt" ;
  
  // Open up the file
  ofstream mf(m_filename.c_str() ) ;
  if ( !mf )
    {
      ostringstream emsg ;
      emsg << "Couldn't open filename: " << m_filename ;
      throw ( dbd_error(emsg) ) ;
    }

  // Blow out the fixed stuff
  mf << "run_name = '" << hdr.filename_label << "';" << endl ;
  
  // Output header information as assignment statements
  if (hdr.hasOptionalKeys())
  {
    // Write segment filenames for glider_data.exe
    hdr.segment_filenames_to_matlab_exe(mf) ;
    
    // Write required header keys and values for glider_data.exe
    hdr.required_keys_to_matlab_exe(mf) ;
    
    // Write optional header keys and values for glider_data.exe
    hdr.optional_keys_to_matlab_exe(mf) ;
  }

  // Create assignment like statements for reading by glider_data.exe  
  // @@@@@ 2006-03-13 fnj@DinkumSoftware.com    Was 30.
  const int max_length = 63 ;
  int i ;
  for (i = 0 ; i < hdr.sensors_per_cycle ; i++)
  {
    string name_copy(hdr.sensor_list[i].name) ;
    if (name_copy.length() > max_length)
    {
      name_copy.erase(max_length, name_copy.length() - max_length) ;
    }
    mf << name_copy << " = " << i+1 << " ;" << endl ;
  }

  // Tell um the name
  cout << m_filename << endl ;

  // file gets closed as it is destructed
}


 /*
>------------------ 0057000X.dat ---------------------------------
>  There is one line per cycle
>  all the sensor values (in order) separated by spaces.
>-----------------------------------------------------------------
30	2	9.8709606e+08	2.316	0.07	.......
NaN	NaN	9.8709606e+08	5.2750001	NaN	.......


*/
