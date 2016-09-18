// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_asc_header.cc

31-Dec-03 trout.r@comcast.net Added filter_sensors(const vector<bool>&)
21-Jan-04 trout.r@comcast.net Added Optional header Keys capability and segment
                              filenames.
23-Mar-04 trout.r@comcast.net Added output of header keys in glider_data.exe format
03-Jan-05 fnj@DinkumSoftware.com Fixed bug in numeric_merge_string which was
                                 causing random crashes.
// 21-Dec-09 tc@DinkumSoftware.com include syntax change
*/
    
#include "dbd_asc_header.h"
#include <iomanip>
    
using namespace dinkum_binary_data ;
    
/// constructor, Creates an ascii header from binary header
/**
   
/param hdr  Binary header to extract the information from
    
*/
    
    
dbd_asc_header::dbd_asc_header( const dbd_header & hdr )
{
    
  // Combine the full filename,8.3 filename, and extension to make a label
  // zippy-2001-104-21-0-dbd(00280000)
  filename_label = hdr.full_filename                +
                   '-' + hdr.filename_extension     +
                   '(' + hdr.the8x3_filename + ')'  ;
                       
        
  // Copy the other stuff we need directly
  all_sensors        = hdr.all_sensors ;
  filename           = hdr.full_filename ;
  the8x3_filename    = hdr.the8x3_filename ;
  filename_extension = hdr.filename_extension ;
  mission_name       = hdr.mission_name ;
  fileopen_time      = hdr.fileopen_time ;
  sensors_per_cycle  = hdr.sensors_per_cycle ;
    
  // And the sensor info
  sensor_list = hdr.infile_sensor_list ;
      
  // Start the optional keys for segment filenames
  optional_keys.insert(header_key_map_type::value_type(num_segments_key(), num_segments_key_initial_value())) ;
  optional_keys.insert(header_key_map_type::value_type(make_segment_filename_key(), hdr.full_filename)) ;
  increment_key(num_segments_key()) ;
  num_ascii_tags = num_ascii_required_tags_value() + 2 ;
   
  // Initialize segment filenames header key
  segment_filenames.push_back(hdr.full_filename) ;
  
  // Initially output optional keys when writing an ascii header
  output_optional_keys = true ;
}
    
    
/// constructor, Reads and parses an ascii header
/**  an example ASCII header we read
    
\param ins  Stream to read the header from
   
\verbatim
    
dbd_label: DBD_ASC(dinkum_binary_data_ascii)file
encoding_ver: 0
num_ascii_tags: 16
all_sensors: 1
filename: zippy-2001-119-2-0
the8x3_filename: 00440000
filename_extension: dbd
filename_label: zippy-2001-119-2-0-dbd(00440000)
mission_name: SASHBOX.MI
fileopen_time: Mon_Apr_30_17:28:25_2001
sensors_per_cycle: 216
num_label_lines: 3
num_segments: 3
segment_filename_0: zippy-2001-119-2-0
segment_filename_1: zippy-2001-119-2-1
segment_filename_2: zippy-2001-119-2-2
f_max_working_depth u_cycle_time m_present_time m_present_secs_into_mission ....
m s s s s nodim nodim nodim nodim nodim enum X enum X enum X enum enum enum ....
4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 ....
    
\endverbatim
*/
    
    
    
dbd_asc_header::dbd_asc_header( istream & ins )
  :
  dbd_reqd_header(ins, "")
{
    
    // Initially output optional headers when writing an ascii header
    output_optional_keys = true ;
    
    // Read the required lines of ascii header
    // Basically identifiers dbd file, encoding version,
    // and total number of ascii header lines
    int n = do_reqd_header_lines(dba_label_value() ) ;
        
    // Read the remainder of the headers we know about
    // Count in "n" the number we read
    do_a_header_line(all_sensors_key(),       all_sensors       ) ; n++ ;
    do_a_header_line(filename_key(),          filename          ) ; n++ ;
    do_a_header_line(the8x3_filename_key(),   the8x3_filename   ) ; n++ ;
    do_a_header_line(filename_extension_key(),filename_extension) ; n++ ;
    do_a_header_line(filename_label_key(),    filename_label    ) ; n++ ;
    do_a_header_line(mission_name_key(),      mission_name      ) ; n++ ;
    do_a_header_line(fileopen_time_key(),     fileopen_time     ) ; n++ ;
    do_a_header_line(sensors_per_cycle_key(), sensors_per_cycle ) ; n++ ;
    do_a_header_line(num_label_lines_key(),   num_label_lines   ) ; n++ ;
    	
    // Check that the number of labels is what we expect
    if ( num_label_lines != num_label_lines_value() )
      { // Just warn them and carry on
        cerr << "Warning: dbd_asc_header(): Wrong number of label lines"
             << expect_str() << num_label_lines_value()
             << got_str() << num_label_lines << endl ;
      }
    
    // Read the remainging ascii header keys as optional keys
    read_optional_keys(num_ascii_tags - n, ins) ;
 
    // now read the label lines and use them to initialize our sensor_list
    // We are expecting a line of: names, units, and original bytes
    sensor_list.resize(sensors_per_cycle) ;  // for efficiency
    for ( int s = 0 ; s < sensors_per_cycle ; s++)
      _ins >> sensor_list[s].name ;
    
    for ( int s = 0 ; s < sensors_per_cycle ; s++)
      _ins >> sensor_list[s].units ;
    
    for ( int s = 0 ; s < sensors_per_cycle ; s++)
      _ins >> sensor_list[s].orig_bytes_of_storage ;
    
    
    // Gobble up the rest of any line we didn't read
    _ins >> ws ;
    
}
    
    
/// copy constructor
/**
    
\param ahdr The header we copy
\param addto_filename This string is added to filename member, NULL to ignore
    
Used to make a copy of ahdr.
    
Assuming ahdr.filename is "zippy-2001-222-04-05",  dbd_asc_header(ahdr, "foo")
creates a header with a filename "zippy-2001-222-04-05-foo"
    
    
*/
dbd_asc_header::dbd_asc_header(const dbd_asc_header & ahdr,
                               const char * addto_filename_str)
    
  :
  dbd_reqd_header( ahdr )    // copy in the base class
    
    
{
    
  // Copy the other stuff we need directly
  all_sensors        = ahdr.all_sensors ;
  filename           = ahdr.filename ;
  the8x3_filename    = ahdr.the8x3_filename ;
  filename_extension = ahdr.filename_extension ;
  filename_label     = ahdr.filename_label ;
  mission_name       = ahdr.mission_name ;
  fileopen_time      = ahdr.fileopen_time ;
  sensors_per_cycle  = ahdr.sensors_per_cycle ;
  
  // Copy optional keys output status
  output_optional_keys = ahdr.output_optional_keys ;
  
  // And the optional keys
  optional_keys = ahdr.optional_keys ;
   
  // And the segment filenames
  segment_filenames = ahdr.segment_filenames ;
   
  // And the sensor info
  sensor_list        = ahdr.sensor_list ;
    
  // Modify our filename per their wishes
  addto_filename(addto_filename_str) ;
    
}
    
/// writes an ascii header to a stream
/** 
   
\param outs The stream to write the header on
    
an example ASCII header we write
    
\verbatim
dbd_label: DBD_ASC(dinkum_binary_data_ascii)file
encoding_ver: 0
num_ascii_tags: 16
all_sensors: 1
filename: zippy-2001-119-2-0
the8x3_filename: 00440000
filename_extension: dbd
filename_label: zippy-2001-119-2-0-dbd(00440000)
mission_name: SASHBOX.MI
fileopen_time: Mon_Apr_30_17:28:25_2001
sensors_per_cycle: 216
num_label_lines: 3
num_segments: 3
segment_filename_0: zippy-2001-119-2-0
segment_filename_1: zippy-2001-119-2-1
segment_filename_2: zippy-2001-119-2-2
f_max_working_depth u_cycle_time m_present_time m_present_secs_into_mission ....
m s s s s nodim nodim nodim nodim nodim enum X enum X enum X enum enum enum ....
4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 ....
    
\endverbatim
    
*/
void dbd_asc_header::write_header(ostream & outs) const 
{
    
  // Write the (key,value) pairs
  // count how many we wrote, so we can check it
  int cnt = 0 ;
  write_key_value(dbd_label_key(),         dba_label_value(),      outs) ; cnt++ ;
  write_key_value(encoding_ver_key(),      encoding_ver_value(),   outs) ; cnt++ ;
  if (output_optional_keys)
  {
    write_key_value(num_ascii_tags_key(),  num_ascii_tags,         outs) ; cnt++ ;
  }
  else
  {
    write_key_value(num_ascii_tags_key(),  num_ascii_required_tags_value(), outs) ; cnt++ ;
  }
  write_key_value(all_sensors_key(),       all_sensors,            outs) ; cnt++ ;
  write_key_value(filename_key(),          filename,               outs) ; cnt++ ;
  write_key_value(the8x3_filename_key(),   the8x3_filename,        outs) ; cnt++ ;
  write_key_value(filename_extension_key(),filename_extension,     outs) ; cnt++ ;
  write_key_value(filename_label_key(),    filename_label,         outs) ; cnt++ ;
  write_key_value(mission_name_key(),      mission_name,           outs) ; cnt++ ;
  write_key_value(fileopen_time_key(),     fileopen_time,          outs) ; cnt++ ;
  write_key_value(sensors_per_cycle_key(), sensors_per_cycle,      outs) ; cnt++ ;
  write_key_value(num_label_lines_key(),   num_label_lines_value(),outs) ; cnt++ ;
    
  // Make sure we wrote what we said we would
  if ( cnt != num_ascii_required_tags_value() )
    {
      ostringstream emsg ;
      emsg << "dbd_asc_header.cc::write_header() software error: bad num_ascii_tags" 
        << expect_str() << num_ascii_required_tags_value() << got_str() << cnt ;
      throw (dbd_error(emsg)) ;
    }
    
  // Write out optional keys
  if (output_optional_keys)
  {
    header_key_map_type::const_iterator iter_keys ;
    for (iter_keys = optional_keys.begin(); iter_keys != optional_keys.end(); iter_keys++)
    {
      write_key_value(iter_keys->first, iter_keys->second, outs) ;
    }
  }
   
  // Write out all the sensor names, all on one line
  for ( int s = 0 ; s < sensors_per_cycle ; s++)
    {
      outs << sensor_list[s].name << fill_char() ;
    }
  outs << endl ;
    
    
  // and their units
  for ( int s = 0 ; s < sensors_per_cycle ; s++)
    {
      outs << sensor_list[s].units << fill_char() ;
    }
  outs << endl ;
    
  // and how many bytes they originally occupied
  for ( int s = 0 ; s < sensors_per_cycle ; s++)
    {
      outs << sensor_list[s].orig_bytes_of_storage << fill_char() ;
    }
  outs << endl ;
   
    
}
    
// merge_header
    
/// Combines the fields of "hdr" with ourselves.
    
/** 
    \param hdr  Binary style header to combine
    
Generally used when combining multiple dbd files into a single
ascii file.
    
The output filename is chosen by merging the filenames on
a character by character basis.
    
\verbatim
For example, these:
    cassidy-2001-193-23-1
    cassidy-2001-193-28-29
yield:
    cassidy-2001-193-2X-XX.dbd
    
\endverbatim
    
*/
//18-Jul-01 tc@DinkumSoftware.com Initial
    
    
bool dbd_asc_header::merge_header( const dbd_header & hdr)
{
    
  // If any input is partial, we are partial
  all_sensors &= hdr.all_sensors ;
    
  // Generally the string functions replace unlike chars with X
  // Not a perfect strategy ....

  merge_full_filename( hdr.full_filename ) ;

  merge_string  ( hdr.the8x3_filename,    the8x3_filename) ;
  merge_string  ( hdr.filename_extension, filename_extension ) ;
    
  filename_label = filename + "(" + the8x3_filename + ")" ;
    
  merge_string  ( hdr.mission_name,       mission_name) ;
  merge_string  ( hdr.fileopen_time,      fileopen_time) ;
    
  // maximum present
  sensors_per_cycle = (hdr.sensors_per_cycle > sensors_per_cycle) ?
                       hdr.sensors_per_cycle : sensors_per_cycle  ;
  // Add full_filename to optional header keys and segment_filenames key
  merge_segment_filename(hdr.full_filename) ;
  
  // say it went ok
  return false ;
    
}
    
/* filter_sensors
 
Purpose:  Removes sensors with corresponding false elements in
 		  pass_through_mask from header sensor list.
Preconditions: None.
Postconditions: sensor_list only retains the sensors with corresponding true
                elements in pass_through_mask.
                sensors_per_cycle is changed to reflect the new size of
                sensor_list.
 
31-Dec-03 trout.r@comcast.net Initial
 
*/
 
void dbd_asc_header::filter_sensors(const vector<bool>& pass_through_mask)
{
  vector<dbd_sensor_info> filtered_sensor_list;
  
  // Iterate through sensor_list retaining only those sensors in mask
  for ( int sensor_index = 0 ; sensor_index < sensors_per_cycle ; sensor_index++)
  {
    if(pass_through_mask[sensor_index])
    {
      // Add sensor to new sensor list for header
      filtered_sensor_list.push_back(sensor_list[sensor_index]);
    }
  }
  if(filtered_sensor_list.size() < sensor_list.size())
  {
    all_sensors = false;
  }
  // Make filtered list new header list
  sensor_list = filtered_sensor_list;
  // Make sensor count agree with new sensor list
  sensors_per_cycle = sensor_list.size();
}
   
/* merge_full_filename
    
"their_filename" should be the full_filename from a header.
    
It is merged into our "full_filename" on a char by char basis
for each field.
    
For example, these:
    cassidy-2001-193-23-1
    cassidy-2001-193-28-29
yield:
    cassidy-2001-193-2X-XX.dbd
    
    
18-Jul-01 tc@DinkumSoftware.com Initial
    
*/
    
bool dbd_asc_header::merge_full_filename( const string & their_filename )
{
    
  // Break both filenames into fields
  string our_name, our_yr, our_day, our_mission, our_segment ;
  split_full_filename( filename, our_name, our_yr, our_day,
                                 our_mission, our_segment) ;
    
  string their_name, their_yr, their_day, their_mission, their_segment ;
  split_full_filename( their_filename, their_name, their_yr, their_day,
                                       their_mission, their_segment) ;
    
    
  // Go thru and merge the strings
  merge_string(         their_name,    our_name ) ;
  numeric_merge_string( their_yr,      our_yr ) ;
  numeric_merge_string( their_day,     our_day ) ;
  numeric_merge_string( their_mission, our_mission ) ;
  numeric_merge_string( their_segment, our_segment ) ;
    
  // Put them back together
  combine_full_filename ( our_name, our_yr, our_day,
                          our_mission, our_segment,    filename) ;
  
  return false ; // say no error
    
}
    
/* merge_string
    
Merges "in_str" into "merged_str" on a char by char basis.
    
If chars differ, they are replaced by "X"
    
Examples
    in_str    merged_str        merged_str
    abc       abc               abc
    ab0       abc               abX
    abcd      abc               abcd
    abc       abcd              abcd
        
18-Jul-01 tc@DinkumSoftware.com Initial
*/
    
bool dbd_asc_header::merge_string  ( const string & in_str, string & merged_str )
{
  const char replacement_char = 'X';
    
  // We are going to scan all of in_str char by char
  // and examine the characters at the same positions in
  // in_str and merged_str.
  // If in_str is shorter, we won't touch the end chars of merged_str
  // We must however, handle the case of merged_str being shorter
  if ( merged_str.size() < in_str.size() )
    {
      // make merged_str and in_str the same size by
      // coping the tail of in_str to merged_strf
      const string::size_type insert_point = merged_str.size() ;
      const string::size_type num_chars_to_copy = in_str.size() - merged_str.size() ;
      merged_str.insert( insert_point,    // index where to insert
                         in_str,          // a substr of this
                         insert_point,    // starting here in in_str
                         num_chars_to_copy) ;
          
    }
    
  // We now are assured that merge_str is at least as long as in_str
  // Go thru and replace and chars that aren't the same
  string::size_type i ;
  for (i = 0 ; i < in_str.size() ; i++)
    {
      // Are chars the same?
      if ( in_str[i] != merged_str[i] )
        {
          // nope, replace it
          merged_str.replace( i, 1, 1, replacement_char) ;
        }
    }
    
  // say no errors
  return false ;
}
    
/* numeric_merge_string
    
Merges "in_str" into "merged_str", replacing different
chars with 'X".
    
The strings are padded with on the left with 0's to make
them the same length.
    
Normally returns false, returns true on error.
    
18-Jul-01 tc@DinkumSoftware.com  Initial.
03-Jan-05 fnj@DinkumSoftware.com Fixed bug in determining which string is shorter.
                                 This was causing an abort or segfault or unexpected
                                 exception due to the attempted insertion of
                                 string::npos number of characters into a string,
                                 depending on the order the files were specified.
*/

bool dbd_asc_header::numeric_merge_string( const string & in_str, string & merged_str )
{
  const string::size_type insert_position = 0 ;
  const char pad_char = '0' ;
    
  // Make a copy of the input string so we can pad it if reqd
  string working_in_str(in_str) ;
  
  // Now we have 2 writable strings and have to pad the shorter
  // to make it as long as the longer
  if ( merged_str.size() < working_in_str.size() )
  {
    // merged_str is shorter than working_in_str; pad leading chars to make same size
    merged_str.insert( insert_position, working_in_str.size() - merged_str.size(), pad_char) ;
  }
  else if ( working_in_str.size() < merged_str.size() )
  {
    // working_in_str is shorter than merged_str; pad leading chars to make same size
      working_in_str.insert( insert_position, merged_str.size() - working_in_str.size(), pad_char) ;
  }
  
  // Now they are the same size.  Do the merge itself.  Replace differing chars with X.
  return merge_string( working_in_str, merged_str ) ;
}
    
/* split_full_filename
    
Breaks "filename" into its fields.
    
Example full_filename:
    cassidy-2001-193-23-1.dbd
   
Normally returns false, returns true on error
    
18-Jul-01 tc@DinkumSoftware.com Initial
    
*/
    
bool dbd_asc_header::split_full_filename( const string & filename,
                                          string & name, string & yr, string & day,
                                              string & mission, string & segment) 
{
  // what separates the fields
  const char sep = full_filename_field_separator() ;
   
  string::size_type indx = 0 ;
  string::size_type nxt_indx ;
    
  nxt_indx = filename.find( sep, indx) ;
  name = filename.substr(indx, nxt_indx - indx) ;
  indx = nxt_indx + 1 ;  // skip the separator
    
  nxt_indx = filename.find( sep, indx) ;
  yr = filename.substr(indx, nxt_indx - indx ) ;
  indx = nxt_indx + 1 ;  // skip the separator
    
  nxt_indx = filename.find( sep, indx) ;
  day = filename.substr(indx, nxt_indx - indx ) ;
  indx = nxt_indx + 1 ;  // skip the separator
    
  nxt_indx = filename.find( sep, indx) ;
  mission = filename.substr(indx, nxt_indx - indx ) ;
  indx = nxt_indx + 1 ;  // skip the separator
    
  nxt_indx = filename.find( sep, indx) ;
  segment = filename.substr(indx, nxt_indx - indx ) ;
  indx = nxt_indx + 1 ;  // skip the separator
    
  // say no error
  return true ;
}
    
/* combine_full_filename
   
Puts all the fields together into "filename".
    
Complement of split_full_filename()
    
Normally returns false, returns true on error
    
18-Jul-01 tc@DinkumSoftware.com Initial
    
*/
    
bool dbd_asc_header::combine_full_filename( const string & name, const string & yr,
                                            const string & day,  const string & mission,
                                            const string & segment,
                                                string & filename )
{
  // what we paste the fields together with
  const char sep = full_filename_field_separator() ;
    
  // Just stick um together
  filename = name    + sep +
             yr      + sep +
             day     + sep +
             mission + sep +
             segment ;
    
  // say no error
  return false ;
}
    
/*
 
Purpose: Read the ascii header's optional keys.  The parameter, number_of_keys, specifies how many
         key / value pairs to reaq from the passed input stream.
Preconditions: None.
Postconditions: Data member optional_keys contains all optional keys.  Data member segment_filenames
                contains the .dbd segment filenames.  These filenames are a subset of optional_keys.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::read_optional_keys(const int number_of_keys, istream& input_stream)
{
	string key ;
	string value ;
 	
 	for(int optional_key_count = 0; optional_key_count < number_of_keys; optional_key_count++)
	{
 		input_stream >> key >> value ;
 		optional_keys.insert(header_key_map_type::value_type(key, value));
 	    // Select out segment filenames
 	    if (key.substr(0, segment_filename_prefix().size()) == segment_filename_prefix())
 	    {
    		segment_filenames.push_back(value) ;
 	    }
 	}
}
 
 
/*
 
Purpose: Add the segment filename of a merged dbd header to the segment filename list and as
         an optional key.
Preconditions: optional_keys must have a num_segments: key
Postconditions: The merged dbd header's segment filename is added to optional_keys and segment_filenames.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::merge_segment_filename(const string& segment_filename)
{
 	// Add segment filename to optional keys
 	optional_keys.insert(header_key_map_type::value_type(make_segment_filename_key(), segment_filename)) ;
 	increment_key(num_segments_key()) ;
 	num_ascii_tags++ ;
 	
 	// Add new segment to segment_filenames
 	segment_filenames.push_back(segment_filename) ;
}
 
/*
 
Purpose: Support function to build a segment filename key.  This method increments the number suffix
         for the segment_filename_X key.
Preconditions: The passed key name exists in optional_keys whose string value represents an integer
Postconditions: None
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::increment_key(const string& key)
{
 	header_key_map_type::const_iterator iter_key ;
 	
 	iter_key = optional_keys.find(key) ;
 	if (iter_key == optional_keys.end())
 	{
       ostringstream error_message ;
       error_message << "dbd_asc_header.cc::increment_key() software error: Expected header key "
       	<< key << " NOT found." ;
       throw (dbd_error(error_message)) ;
 	}
  	string key_value = iter_key->second ;
 	istringstream in_key_value(key_value) ;
 	int value ;
 	in_key_value >> value ;
 	value++ ;
 	
 	ostringstream out_key_value ;
 	out_key_value << value ;
 	optional_keys[key] = out_key_value.str() ;
}
 
/*
 
Purpose: Makes a segment filename key by adding a number suffix to the base name 'segment_filename_'
         and returns it.
Preconditions: The key 'num_segments:' exists as an optional key whose value is the number suffix to add
Postconditions: None
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
string dbd_asc_header::make_segment_filename_key()
{
 	header_key_map_type::const_iterator iter_key ;
 	
 	iter_key = optional_keys.find(num_segments_key()) ;
 	if (iter_key == optional_keys.end())
 	{
       ostringstream error_message ;
       error_message << "dbd_asc_header.cc::make_segment_filename_key() software error: Expected header key "
       	<< num_segments_key() << " NOT found." ;
       throw (dbd_error(error_message)) ;
 	}
 	return segment_filename_prefix() + iter_key->second + ":" ;
}
 
/*
 
Purpose: This method writes the required ascii header keys to the passed stream as Matlab
         globals.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::required_keys_to_matlab_globals(ofstream & matlab_stream) const
{
	string key ;

 	matlab_stream << endl ;

 	key = strip_key_formating(dbd_label_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << dba_label_value() << "' ;" << endl ;
 
 	key = strip_key_formating(encoding_ver_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = " << encoding_ver_value() << " ;" << endl ;
 
 	key = strip_key_formating(num_ascii_tags_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = " << num_ascii_tags << " ;" << endl ;
 
 	key = strip_key_formating(all_sensors_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = " << all_sensors << " ;" << endl ;
 
 	key = strip_key_formating(filename_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << filename << "' ;" << endl ;
 
 	key = strip_key_formating(the8x3_filename_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << the8x3_filename << "' ;" << endl ;

 	key = strip_key_formating(filename_extension_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << filename_extension << "' ;" << endl ;
 
 	key = strip_key_formating(filename_label_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << filename_label << "' ;" << endl ;
 
 	key = strip_key_formating(mission_name_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << mission_name << "' ;" << endl ;
 
 	key = strip_key_formating(fileopen_time_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = '" << fileopen_time << "' ;" << endl ;
 
 	key = strip_key_formating(sensors_per_cycle_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = " << sensors_per_cycle << " ;" << endl ;
 
 	key = strip_key_formating(num_label_lines_key()) ;
    matlab_stream << "global " << key << endl ;
    matlab_stream << key << " = " << num_label_lines_value() << " ;" << endl ;
}
 
/*
 
Purpose: This method writes the ascii header optional keys to the passed stream as Matlab globals.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::optional_keys_to_matlab_globals(ofstream & matlab_stream) const
{
 	header_key_map_type::const_iterator iter_key ;
 	string key ;
 	
 	for(iter_key = optional_keys.begin(); iter_key != optional_keys.end(); iter_key++)
 	{
 	 	key = strip_key_formating(iter_key->first) ;
		matlab_stream << "global " << key << endl ;
     	matlab_stream << key << " = '" << iter_key->second << "' ;" << endl ;
    }
}

/*
 
Purpose: This method writes the .dbd segment filenames to the passed stream as a matlab struct element
         with identifier 'segment_filenames' and value a Matlab list of segment filenames.  If the parameter
         close_struct is true, a closing ');' is written to the stream.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::segment_filenames_to_matlab_struct(ofstream & matlab_stream, bool close_struct) const
{
	vector<string>::const_iterator iter_segments ;
	int longest_segment_filename_size = 0 ;
	
	// Need the size of the longest segment_filename for matlab structure formating
	for (iter_segments = segment_filenames.begin(); iter_segments != segment_filenames.end(); iter_segments++)
	{
		if(iter_segments->size() > longest_segment_filename_size)
		{
			longest_segment_filename_size = iter_segments->size() ;
		}
	}
	// Output segment filenames in matlab structure format
	iter_segments = segment_filenames.begin() ;
	if (iter_segments != segment_filenames.end())
	{
		matlab_stream << "'segment_filenames', ['" << setiosflags(ios::left) << setw(longest_segment_filename_size) << *iter_segments << "'";
		iter_segments++ ;
		while (iter_segments != segment_filenames.end())
		{
			matlab_stream << "; '" << setw(longest_segment_filename_size) << *iter_segments << "'";
			iter_segments++ ;
		}
		matlab_stream << resetiosflags(ios::left) << "]" ;
		if (close_struct)
		{
			matlab_stream << ");" << endl ;
		}
		else
		{
			matlab_stream << " ,..." << endl ;
		}
	}
}

/*
 
Purpose: This method writes the ascii header's required keys to the passed stream as elements of a
         matlab struct where the identifier is the key name and the value is the key's value.  If the
         parameter close_struct is true, a closing ');' is written to the stream.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::required_keys_to_matlab_struct(ofstream & matlab_stream, bool close_struct) const
{
    matlab_stream << "'" << strip_key_formating(dbd_label_key()) << "', '" << dba_label_value() << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(encoding_ver_key()) << "'," << encoding_ver_value() << " ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(num_ascii_tags_key()) << "'," << num_ascii_tags << " ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(all_sensors_key()) << "'," << all_sensors << " ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(filename_key()) << "', '" << filename << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(the8x3_filename_key()) << "', '" << the8x3_filename << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(filename_extension_key()) << "', '" << filename_extension << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(filename_label_key()) << "', '" << filename_label << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(mission_name_key()) << "', '" << mission_name << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(fileopen_time_key()) << "', '" << fileopen_time << "' ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(sensors_per_cycle_key()) << "'," << sensors_per_cycle << " ,..." << endl ;
 
    matlab_stream << "'" << strip_key_formating(num_label_lines_key()) << "'," << num_label_lines_value() ;
     
    if (close_struct)
    {
     	matlab_stream << ");" << endl ;
    }
    else
    {
     	matlab_stream << " ,..." << endl ;
    }
}
 
/*
 
Purpose: This method writes the ascii header's optional keys to the passed stream as elements of a
         matlab struct where the identifier is the key name and the value is the key's value.  If the
         parameter close_struct is true, a closing ');' is written to the stream.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::optional_keys_to_matlab_struct(ofstream & matlab_stream, bool close_struct) const
{
 	header_key_map_type::const_iterator iter_key ;
 	
 	iter_key = optional_keys.begin() ;
 	if (iter_key != optional_keys.end())
 	{
 		matlab_stream << "'" << strip_key_formating(iter_key->first) << "', '" << iter_key->second << "'";
 		iter_key++ ; 		
 		while (iter_key != optional_keys.end())
 		{
     		matlab_stream << " ,..." << endl << "'" << strip_key_formating(iter_key->first) << "', '" << iter_key->second << "'";
     		iter_key++ ;
 	    }
 	    if (close_struct)
 	    {
 	    	matlab_stream << ");" << endl ;
 	    }
 	    else
 	    {
 	    	matlab_stream << " ,..." << endl ;
 	    }
 	}
}

/*
Purpose: This method writes the .dbd segment filenames to the passed stream in glider_data.exe format.
		 That is, segment_filenames = [segment_filename0, ... ] segment_filenameN;
Preconditions: None.
Postconditions: None.
History:
23-Mar-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::segment_filenames_to_matlab_exe(ofstream & glider_stream) const
{
	vector<string>::const_iterator iter_segments ;

	// Output segment filenames in matlab structure format
	iter_segments = segment_filenames.begin() ;
	if (iter_segments != segment_filenames.end())
	{
		glider_stream << "segment_filenames = " << *iter_segments ;
		iter_segments++ ;
		while (iter_segments != segment_filenames.end())
		{
			glider_stream << ", " << *iter_segments ;
			iter_segments++ ;
		}
		glider_stream << ";" << endl ;
	}
}

/*
 
Purpose: This method writes the required ascii header keys to the passed stream in
		 glider_data.exe format.
Preconditions: None.
Postconditions: None.
History:
23-Mar-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::required_keys_to_matlab_exe(ofstream & glider_stream) const
{
	string key ;

 	key = strip_key_formating(dbd_label_key()) ;
    glider_stream << key << " = " << dba_label_value() << " ;" << endl ;
 
 	key = strip_key_formating(encoding_ver_key()) ;
    glider_stream << key << " = " << encoding_ver_value() << " ;" << endl ;
 
 	key = strip_key_formating(num_ascii_tags_key()) ;
    glider_stream << key << " = " << num_ascii_tags << " ;" << endl ;
 
 	key = strip_key_formating(all_sensors_key()) ;
    glider_stream << key << " = " << all_sensors << " ;" << endl ;
 
 	key = strip_key_formating(filename_key()) ;
    glider_stream << key << " = " << filename << " ;" << endl ;
 
 	key = strip_key_formating(the8x3_filename_key()) ;
    glider_stream << key << " = " << the8x3_filename << " ;" << endl ;

 	key = strip_key_formating(filename_extension_key()) ;
    glider_stream << key << " = " << filename_extension << " ;" << endl ;
 
 	key = strip_key_formating(filename_label_key()) ;
    glider_stream << key << " = " << filename_label << " ;" << endl ;
 
 	key = strip_key_formating(mission_name_key()) ;
    glider_stream << key << " = " << mission_name << " ;" << endl ;
 
 	key = strip_key_formating(fileopen_time_key()) ;
    glider_stream << key << " = " << fileopen_time << " ;" << endl ;
 
 	key = strip_key_formating(sensors_per_cycle_key()) ;
    glider_stream << key << " = " << sensors_per_cycle << " ;" << endl ;
 
 	key = strip_key_formating(num_label_lines_key()) ;
    glider_stream << key << " = " << num_label_lines_value() << " ;" << endl ;
}

/*
 
Purpose: This method writes the ascii header's optional keys to the passed stream in glider_data.exe format.
Preconditions: None.
Postconditions: None.
History:
23-Mar-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::optional_keys_to_matlab_exe(ofstream & glider_stream) const
{
 	header_key_map_type::const_iterator iter_key ;
 	
 	iter_key = optional_keys.begin() ;
 	while (iter_key != optional_keys.end())
 	{
    	glider_stream << strip_key_formating(iter_key->first) << " = " << iter_key->second << " ;" << endl;
    	iter_key++ ;
 	}
}

/*
 
Purpose: This method returns the passed ascii header key name with the ':' suffix removed.  Used to make
         the Matlab output of these names appear more natural as matlab struct elements.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
string dbd_asc_header::strip_key_formating(const string & key) const
{
	// strip off ending ":"
	return key.substr(0, key.size() - 1) ;
}

/*
 
Purpose: The setter for specifying if the ascii header's optional keys should be output to the .dba file stream.
         Used by the -k flag of dbd2asc.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
void dbd_asc_header::put_output_optional_keys(bool flag)
{
  output_optional_keys = flag ;
}

/*
 
Purpose: This method returns a boolean indicating if the ascii header has optional keys or not.
Preconditions: None.
Postconditions: None.
History:
21-Jan-04 trout.r@comcast.net Initial
 
*/
bool dbd_asc_header::hasOptionalKeys() const
{
  if (optional_keys.size() == 0)
  {
    return false ;
  }
  else
  {
    return true ;
  }
}
