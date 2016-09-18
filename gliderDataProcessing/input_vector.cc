// Copyright(c) 2003-2004, Webb Research Corporation, ALL RIGHTS RESERVED
/* input_vector.cc

31-Dec-03 trout.r@comcast.net Initial
21-Dec-09 tc@DinkumSoftware.com filter_mask(): find() wouldn't compile on linux.
                                Rewrote without iterators

*/

#include <fstream>

#include "input_vector.h"

InputVector::InputVector(void)
{
}

InputVector::~InputVector(void)
{
}

/* push_back_file

Purpose: Insert whitespace delimited strings from a file into the
         end of the vector.
Preconditions: Parameter filename should represent an existing file.
Postconditions: This vector contains the strings from the file as
                elements.

*/
  
void InputVector::push_back_file(const string& filename)
{
  ifstream item_file(filename.c_str(), ios::in);
  string item;
  
  if(!item_file)
  {
    throw dinkum_binary_data::dbd_error("Could not open item file");
  }
  while (!item_file.eof())
  {
  	item_file >> item >> ws;
    push_back(item);
  }
}

/* write_items

Purpose: Write the vector's elements to the passed output stream.
Preconditions: None.
Postconditions: None.

*/

void InputVector::write_items(ostream& output)
{
  vector<string>::const_iterator item_index;
  for(item_index = begin(); item_index != end(); item_index++)
  {
    output << *item_index << endl;
  }
}
  
/* filter_mask

Purpose: Returns a boolean vector representing the intersection of the passed sensor_list
  names and the string elements of this vector.  The returned vector's size is equal to
  the passed vector's size.  Each true element of the returned vector corresponds to an
  element of the passed vector that is a member of the intersection set.
Preconditions: None.
Postconditions: None.

?? Initial 
21-Dec-09 tc@DinkumSoftware.com find() wouldn't compile on linux.
                                Rewrote without iterators
*/

vector<bool> InputVector::filter_mask(const vector<dinkum_binary_data::dbd_sensor_info>& sensor_list)
{
  vector<bool> mask;
  vector<dinkum_binary_data::dbd_sensor_info>::const_iterator sensor_iter;
  //vector<string>::const_iterator pass_through_iter;

  // Iterate through sensor_list creating filter mask
  for(sensor_iter = sensor_list.begin();
      sensor_iter != sensor_list.end(); sensor_iter++)
  {
    /* This used to work, but quit compiling on linux.
       So I rewrote without iterators
          pass_through_iter = find (this->begin(),
                                    this->end(),
                                    (*sensor_iter).name);
    if(pass_through_iter == this->end())
    */
    bool value_to_push_back = false ; // assume find() fails
    for ( int s=0 ; s < this->size() ; s++)
      {
        if ( (*sensor_iter).name == (*this)[s] )
          {
            // found it
            value_to_push_back = true ;
            break ;
          }

      }

      // Set mask to include/exclude corresponding sensor
      mask.push_back(value_to_push_back);
  }
  return mask;
}

