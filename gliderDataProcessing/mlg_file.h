// Copyright(c) 2003-2004, Webb Research Corporation, ALL RIGHTS RESERVED
/* mlg_file.h

26-Jan-04 trout.r@comcast.net Initial
*/

#ifndef _mlg_file_h
#define _mlg_file_h

#include <fstream>
#include <string>
#include <map>

using namespace std ;


namespace dinkum_binary_data
{

	/* mlg_file

	This class represents a glider mission log file (.mlg).

	*/
	class mlg_file
	{
	public:
  		mlg_file(void) ;
  		~mlg_file(void) ;
  
  		// Associate a file with the class
  		bool open(const char * mlg_filename) ;
  		
  		// Check that associated file is an .mlg file
  		bool is_mlg_file() ;
  
  		// Getter for the 8.3 filename
  		string the8x3_filename(void) ;
  		
  		// Getter for the full filename
  		string full_filename(void) ;
  		  
  	private:
  		// Generic getter for a key's value
		string get_key_value(const string& key) ;

		// Test that opened file contains the required .mlg keys		
		bool do_required_keys_verify() ;
		
		// Read a .mlg file's required header keys
		void read_required_header() ;
	
    	string full_filename_key() const
    	{
    		return "full_filename:" ;
    	}
	    
	    string the8x3_filename_key() const
	    {
	    	return "the8x3_filename:" ;
	    }

		const int num_required_keys ;
  		// Does associated file exist and is it a mlg file?
  		bool is_mlg ;
  		
  		// file stream for mlg file
		ifstream mlg_stream ;
		
	    // associative map definition for maintaining mlg header key / value pairs
    	typedef map<string, string, less<string> > header_key_map_type ;
    	
	    // actual header key / value pair association map
    	header_key_map_type required_keys ;
	};
}

#endif /* _mlg_file_h */
