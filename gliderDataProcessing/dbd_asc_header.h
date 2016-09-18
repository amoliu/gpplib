// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_asc_header.h
    
30-Sep-02 tc@DinkumSoftware.com went to encoding version 1.0
31-Dec-03 trout.r@comcast.net Added filter_sensors(const vector<bool>&)
21-Jan-04 trout.r@comcast.net Added Optional header Keys capability and segment
                              filenames.
23-Sep-09 tc@DinkumSoftware.com Made some segment processing functions protected so
                                could be accessed by dbd_asc_merged_header class
 */
    
#ifndef DBD_ASC_HEADER_H
#define DBD_ASC_HEADER_H
    
#include "dbd_reqd_header.h" // class we derive from
#include "dbd_header.h"
#include <map>
#include <sstream>
    
    
namespace dinkum_binary_data
{
    
  /// Holds all the information required in Ascii formatted file
class dbd_asc_header : public dbd_reqd_header
  {
  public:
    dbd_asc_header(const dbd_header & hdr) ;
    dbd_asc_header(istream & ins ) ;
    dbd_asc_header(const dbd_asc_header & ahdr,
                   const char * addto_filename_str = NULL) ;
    
    friend ostream & operator<< ( ostream & outs, dbd_asc_header & hdr )
      {
        hdr.write_header(outs) ; return outs ;
      }
    void write_header(ostream & outs) const ;
    
    // Merge the fields of another binary header with ours
    bool merge_header( const dbd_header & hdr) ;
    
	// Output segment filenames as matlab struct members
    void segment_filenames_to_matlab_struct(ofstream & matlab_stream, bool close_struct) const ;
    
    // Output required keys as matlab globals
 	void required_keys_to_matlab_globals(ofstream & matlab_stream) const;

 	// Output optional keys as matlab globals
 	void optional_keys_to_matlab_globals(ofstream & matlab_stream) const;

    // Output required keys as PART of a matlab struct members
 	void required_keys_to_matlab_struct(ofstream & matlab_stream, bool close_struct) const;

 	// Output optional keys as PART of a matlab struct members
 	void optional_keys_to_matlab_struct(ofstream & matlab_stream, bool close_struct) const;

	// Output segment filenames in glider_data.exe format
	void segment_filenames_to_matlab_exe(ofstream & glider_stream) const;

	// Output required keys in glider_data.exe format
	void required_keys_to_matlab_exe(ofstream & glider_stream) const;

	// Output optional keys in glider_data.exe format
	void optional_keys_to_matlab_exe(ofstream & glider_stream) const;

    // Remove all sensor info NOT in pass_through_sensors
    void filter_sensors(const vector<bool>& pass_through_mask);
    
    // Set output status of optional keys for dba files (for use by dbd2asc)
    void put_output_optional_keys(bool flag) ;
    
    // Check for the existance of optional keys in the ascii header
    bool hasOptionalKeys() const ;
        
  private:
    // Keys we write on the output string
    const char * dbd_label_key()          const { return "dbd_label:"          ; }
    const char * encoding_ver_key()       const { return "encoding_ver:"       ; }
    const char * num_ascii_tags_key()     const { return "num_ascii_tags:"     ; }
    const char * all_sensors_key()        const { return "all_sensors:"        ; }
    const char * filename_key()           const { return "filename:"           ; }
    const char * the8x3_filename_key()    const { return "the8x3_filename:"    ; }
    const char * filename_extension_key() const { return "filename_extension:" ; }
    const char * filename_label_key()     const { return "filename_label:"     ; }
    const char * mission_name_key()       const { return "mission_name:"       ; }
    const char * fileopen_time_key()      const { return "fileopen_time:"      ; }
    const char * sensors_per_cycle_key()  const { return "sensors_per_cycle:"  ; }
    const char * num_label_lines_key()    const { return "num_label_lines:"    ; }
    const char * num_segments_key()    	  const { return "num_segments:"       ; }
    
    // and associated values
    // the functions() are a priori values we write
    const char * dba_label_value() const
      { return "DBD_ASC(dinkum_binary_data_ascii)file" ; 
      }
    const int    encoding_ver_value()    const { return  2 ; }
    const int    num_ascii_required_tags_value()  const { return 12 ; }
    
  public:
    
    /// T -> all sensors present in the file
    bool all_sensors ;
    
    /// translated name, e.g. zippy-2001-222-04-05
    string filename ;
    
    /// Original filename, e.g. 00280000
    string the8x3_filename ;
    
    /// the extension on the filename, e.g. dbd or sbd 
    string filename_extension ;
    
    /// for human consumption, e.g. zippy-2001-104-21-0(00280000)
    string filename_label ;
    
    /// filename of the mission that was run
    string mission_name   ;
    
    /// When the file was originally created
    string fileopen_time  ;
    
    /// Segment filenames (long version) merged into a DBA file
    vector<string> segment_filenames ;
 
    /// The number of variables written each cycle
    int sensors_per_cycle ;
    
    /// The number of lines written for each sensor in header
    int num_label_lines   ;
    
    /// name/units/bytes
    const int   num_label_lines_value() const { return 3 ; } 
          
    /// Where we keep all the info about sensors
    vector<dbd_sensor_info> sensor_list ;
    
    /// What we use to separate data in each cycle
    char fill_char() const { return ' ' ; }
    
    /// Adds -str to end of filename
    void addto_filename(const char * str)
      {
        // They want to do anything?
        if ( str == NULL ) return ;    // no
   
        // Tack it on
        filename += full_filename_field_separator() ; // -
        filename += str ;                             // our arg
      }
   
    
  private:
    // For creating merged ascii headers
    bool merge_full_filename( const string & their_full_filename ) ;
    bool numeric_merge_string( const string & in_str, string & merged_str ) ;
    bool merge_string  ( const string & in_str, string & merged_str ) ;
   
    // splits/combines fields of a filename
    // cassidy-2001-193-28-0
    bool split_full_filename( const string & filename,
                              string & name, string & yr, string & day,
                              string & mission, string & segment) ;
    bool combine_full_filename( const string & name, const string & yr,
                                const string & day,  const string & mission,
                                const string & segment,
                                    string & filename ) ;
    char full_filename_field_separator() const { return '-'; } 
    
    // associative map definition for maintaining optional header key / value pairs
    typedef map<string, string, less<string> > header_key_map_type ;
    // actual optional header key / value pair association map
    header_key_map_type optional_keys ;
    
    // controls output of optional keys
    bool output_optional_keys ;
     
    // Initial value of num_segments key
    const string num_segments_key_initial_value() const { return "0" ; }
     
    // Prefix for segment filename keys
    const string segment_filename_prefix() const { return "segment_filename_" ; }
     
    // Load optional header key / values pairs from input stream into association map
    void read_optional_keys(const int number_of_keys, istream& input_stream) ;
 
	// Return a segment filename key made from the current value of num_segments key
 	string make_segment_filename_key() ;
 	
 	// Increment an optional key value that is stored as a string but represents an integer
 	void increment_key(const string& key) ;
 
 	// Strip off ":" from end of key label
	string strip_key_formating(const string & key) const;

 
  protected:
 	// Add a DBD header's filename to the segment_filename list
 	void merge_segment_filename(const string& segment_filename) ;
 	



  } ; // class dbd_asc_header
    
} // namespace dinkum_binary_data
    
#endif // DBD_ASC_header_H
