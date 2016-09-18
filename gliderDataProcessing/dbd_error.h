// Copyright(c) 2001-2009, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbd_error.h

Defines class "dbd_error" which is thrown by
a whole bunch of dbd_xxxx classes.

Basically just holds an error message.

18-Apr-01 tc@DinkumSoftware.com Initial
22-Sep-09 tc@DinkumSoftware.com Added prepend_to_msg()

*/

#ifndef DBD_ERROR_H
#define DBD_ERROR_H

#include <sstream>
#include <string>


namespace dinkum_binary_data {

using namespace std ;

class dbd_error
{
 public:
  // Construct error msg, by catting together args
  dbd_error(const char * err_msg_0,
            const char * err_msg_1 = NULL,
            const char * err_msg_2 = NULL,
            const char * err_msg_3 = NULL,
            const char * err_msg_4 = NULL,
            const char * err_msg_5 = NULL,
            const char * err_msg_6 = NULL,
            const char * err_msg_7 = NULL
           )
  {    _err_msg = err_msg_0 ;
       if ( err_msg_1 != NULL) _err_msg += err_msg_1 ;
       if ( err_msg_2 != NULL) _err_msg += err_msg_2 ;
       if ( err_msg_3 != NULL) _err_msg += err_msg_3 ;
       if ( err_msg_4 != NULL) _err_msg += err_msg_4 ;
       if ( err_msg_5 != NULL) _err_msg += err_msg_5 ;
       if ( err_msg_6 != NULL) _err_msg += err_msg_6 ;
       if ( err_msg_7 != NULL) _err_msg += err_msg_7 ;
  }

  // Construct error message from ostr
    dbd_error(ostringstream & err_msg)
      : _err_msg(err_msg.str())
    {}

  // Edit the error message in-place
  void prepend_to_err_msg(const char * err_msg_0,
                            const char * err_msg_1 = NULL,
                            const char * err_msg_2 = NULL,
                            const char * err_msg_3 = NULL,
                            const char * err_msg_4 = NULL,
                            const char * err_msg_5 = NULL,
                            const char * err_msg_6 = NULL,
                            const char * err_msg_7 = NULL,
                            const char * err_msg_8 = NULL,
                            const char * err_msg_9 = NULL)
  {                        

    if ( err_msg_7 != NULL) _err_msg.insert(0, err_msg_9) ;
    if ( err_msg_7 != NULL) _err_msg.insert(0, err_msg_8) ;
    if ( err_msg_7 != NULL) _err_msg.insert(0, err_msg_7) ;
    if ( err_msg_6 != NULL) _err_msg.insert(0, err_msg_6) ;
    if ( err_msg_5 != NULL) _err_msg.insert(0, err_msg_5) ;
    if ( err_msg_4 != NULL) _err_msg.insert(0, err_msg_4) ;
    if ( err_msg_3 != NULL) _err_msg.insert(0, err_msg_3) ;
    if ( err_msg_2 != NULL) _err_msg.insert(0, err_msg_2) ;
    if ( err_msg_1 != NULL) _err_msg.insert(0, err_msg_1) ;
    if ( err_msg_0 != NULL) _err_msg.insert(0, err_msg_0) ;

  }


  string get_err_msg() const { return _err_msg ; }

 private:
  string _err_msg ;

} ; // class dbd_error


}   // namespace dinkum_binary_data




#endif // DBD_ERROR_H
