// Copyright(c) 2003-2004, Webb Research Corporation, ALL RIGHTS RESERVED
/* input_vector.h

31-Dec-03 trout.r@comcast.net Initial
21-Jan-04 tc@DinkumSoftware.com Put newline at end of file
*/

#ifndef _input_vector_h
#define _input_vector_h

#include <string>
#include <vector>
#include "dbd_error.h"
#include "dbd_sensor_info.h"

using namespace std ;

/* InputVector

Behaves just like vector<string> with the added abilities to load strings
from a whitespace delimited file, write its string elements to a given
output stream, and build a vector mask indicating items in a passed sensor info
vector that are also members of this vector.

*/
class InputVector : public vector<string>
{
public:
  InputVector(void);
  ~InputVector(void);
  
  // Insert strings from a file to the back of the vector
  void push_back_file(const string& filename);
  
  // Write the string elements to the passed output stream
  void write_items(ostream& output);
  
  // Make filter mask from sensor info vector
  vector<bool> filter_mask(const vector<dinkum_binary_data::dbd_sensor_info>& sensor_list);
};

#endif /* _input_vector_h */
