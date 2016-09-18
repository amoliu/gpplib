// Copyright(c) 2003-2004, Webb Research Corporation, ALL RIGHTS RESERVED
/* mlg_file.cc

26-Jan-04 trout.r@comcast.net   Initial
 2-Feb-04 tc@DinkumSoftware.com Added newline at end of file
*/

#include <fstream>
#include "mlg_file.h"

using namespace dinkum_binary_data ;

mlg_file::mlg_file(void) : num_required_keys(2)
{
	is_mlg = false ;
}

mlg_file::~mlg_file(void)
{
}

/* the8x3_filename

Purpose: getter for the8x3_filename key value
Preconditions: A mlg file has been successfully opened
Postconditions: None

*/
string mlg_file::the8x3_filename(void)
{
	return get_key_value(the8x3_filename_key()) ;
}

/* full_filename

Purpose: getter for the full_filename key value
Preconditions: A .mlg file has been successfully opened
Postconditions: None

*/
string mlg_file::full_filename(void)
{
	return get_key_value(full_filename_key()) ;
}

/* get_key_value

Purpose: generic getter for key values
Preconditions: A .mlg file has been successfully opened
Postconditions: None

*/
string mlg_file::get_key_value(const string& key)
{
 	header_key_map_type::const_iterator iter_key ;
 	
 	iter_key = required_keys.find(key) ;
 	if (iter_key == required_keys.end())
 	{
 		return string() ;
 	}
 	else
 	{
 		return iter_key->second ;
 	}
}

/* open

Purpose: Opens the passed .mlg filename and reads the required header.
Preconditions: None
Postconditions: The required_keys data member contains the required keys
                and their values as read from the opened file.

*/
bool mlg_file::open(const char * mlg_filename)
{

    // Open up the input file
	mlg_stream.open(mlg_filename, ios::in | ios::binary) ;
    if (!mlg_stream)
    {
   		return false ;
    }
    else
    {
    	read_required_header() ;
    	return true ;
    }
}

/* read_required_header

Purpose: Reads the required keys from the opened .mlg file
Preconditions: A .mlg file has been successfully opened
Postconditions: required_keys contains the key values read
                from the open .mlg file.

*/
void mlg_file::read_required_header()
{
	string key ;
	string value ;
 	
 	for(int required_key_count = 0; required_key_count < num_required_keys; required_key_count++)
	{
 		mlg_stream >> key >> value ;
 		required_keys.insert(header_key_map_type::value_type(key, value));
 	}
 	is_mlg = do_required_keys_verify() ;
}

/* is_mlg_file

Purpose: Is the open file a .mlg file?
Preconditions: An open file
Postconditions: None

*/

bool mlg_file::is_mlg_file()
{
	return is_mlg ;
}

/* do_required_keys_verify

Purpose: Returns true if the open file contains the required
         keys of a .mlg file.
Preconditions: A .mlg file has been read
Postconditions: None

*/
bool mlg_file::do_required_keys_verify()
{
 	header_key_map_type::const_iterator iter_key ;
 	
 	iter_key = required_keys.find(the8x3_filename_key()) ;
 	if (iter_key == required_keys.end())
 	{
 		return false ;
 	}
 	iter_key = required_keys.find(full_filename_key()) ;
 	if (iter_key == required_keys.end())
 	{
 		return false ;
 	}
 	return true ;
}
