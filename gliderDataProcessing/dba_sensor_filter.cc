// Copyright(c) 2003-2004, Webb Research Corporation, ALL RIGHTS RESERVED
/* dba_senor_filter

This program:
    Reads dinkum binary ascii format from stdin (output of dbd2asc)
    Excludes the data of sensors NOT listed on the command line or in
      the -f <sensors_filename>
    Writes the data of remaining sensors in dinkum binary ascii format to stdout 

Usage:
    dba_sensor_filter [-h] [-f <sensors_filename>] [sensor_name_0 ... sensor_name_N]

Accepts a .dba file from stdin.  The data corresponding to sensors
listed on the command line or in the -f <sensors_filename> are written
to stdout as a .dba file.  All other sensor data is discarded.  Sensor names
in -f <sensors_filename> should be line or space delimited.

A -sf is added to the filename of the output header, e.g.
    filename: zippy-2001-222-04-05  --> zippy-2001-222-04-05-sf

30-Dec-03 trout.r@comcast.net Initial
21-Dec-09 tc@DinkumSoftware.com Added #include <cstdio> <cstdlib>

Table of contents
    main

*/
#include <cstdio>
#include <cstdlib>
#include <iostream>

#include "options.h"
#include "dbd_error.h"
#include "dbd_asc_header.h"
#include "dbd_sensor_value_collection.h"
#include "input_vector.h"
                           
// New filename suffix: zippy-2001-222-04-05  --> zippy-2001-222-04-05-sf
const char * addto_filename_str = "sf"; 

// Specify the command line help
static const char * usage_str_tail =
"[sensor_name_0 ... sensor_name_N]\n"
"   -h                    Print this message\n"
"   -f <sensors_filename> Read sensor pass-through list from file\n"
"\n"
"Accepts a .dba file from stdin.  The data corresponding to sensors\n"
"listed on the command line or in the -f <sensors_filename> are written\n"
"to stdout as a .dba file.  All other sensor data is discarded.  Sensor names\n"
"in -f <sensors_filename> should be line or space delimited.\n";

static const char * const optv[] =
{
  "h|help",
  "f:pass-through-sensors-filename <sensors_filename>",
  NULL
};

int main(int argc, char* argv[])
{
  // Error prefix
  const string error_msg_leadin = "ERROR prog: dba_sensor_filter: ";
  try
  {
    // Process the command line arguments
    Options cmdline_options(*argv, optv);
    OptArgvIter cmdline_options_iter(--argc, ++argv);
  
    InputVector pass_through_sensor_vector;
  
    // Process the switches
    int option_char;
    const char * option_arg = NULL;
    while(option_char = cmdline_options(cmdline_options_iter, option_arg))
    {
      switch(option_char)
      {
        case 'h':
          cmdline_options.usage(cerr, usage_str_tail);
          return EXIT_SUCCESS;
        case 'f':
          pass_through_sensor_vector.push_back_file(option_arg);
          break ;
        case Options::BADCHAR:
        case Options::BADKWD:
        case Options::AMBIGUOUS:
        default:
          cerr << "Error! ";
          cmdline_options.usage(cerr, usage_str_tail);
          return EXIT_FAILURE;
      }
    }


    // Add the sensor names on the command line to the include sensor list
    for (int index = cmdline_options_iter.index(); index < argc; index++)
    {
      pass_through_sensor_vector.push_back(argv[index]);
    }
    
    // Read the ascii header
    dinkum_binary_data::dbd_asc_header  header_in(cin);
      
    // Create an output header and tack on the sensor filter label
    dinkum_binary_data::dbd_asc_header  header_out(header_in, addto_filename_str);

	// Make filter mask
	vector<bool> pass_through_mask_vector = pass_through_sensor_vector.filter_mask(header_in.sensor_list);
	
    // Remove all sensors from the output header that have a corresponding false element in
    // pass_through_mask_vector
    header_out.filter_sensors(pass_through_mask_vector);
    
    // Write the header
    header_out.write_header(cout);

	// Prepare to read sensor data
    dinkum_binary_data::dbd_sensor_value_collection data_line_in(header_in);
    // Prepare to write filtered sensor data
    dinkum_binary_data::dbd_sensor_value_collection data_line_out(header_out);

    while(data_line_in.read_asc(cin))
    {
      // Copy data_line_in sensor data corresponding to true elements in pass_through_mask_vector
      // to data_line_out.
      data_line_in.filter_data(data_line_out, pass_through_mask_vector);
      // Write filtered sensor data
      data_line_out.write_asc(header_out, cout);
    }
  }
  catch (dinkum_binary_data::dbd_error error)
  {
    cerr << error_msg_leadin << error.get_err_msg() << endl;
  }
  catch(...)
  {
    cerr << error_msg_leadin << "Unknown Exception Caught" << endl;
  }
  // I keep prayin'
  return EXIT_SUCCESS ;
}
