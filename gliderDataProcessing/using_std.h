/* using_std.h

Used to make code compile under gcc 3.x

Alter the makefile by adding -i using_std.h to get
this file automagically inserted at the beginning
of every c++ file.

25-Jul-03 tc@DinkumSoftware.com Initial

*/

#ifndef USING_STD_H
#define USING_STD_H

// Required by gcc 3.x on linux for compilation

using namespace std ;


#endif // USING_STD_H
