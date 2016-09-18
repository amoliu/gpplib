// stat_iface.h
//
// Handles system differences in the implementation of stat and mkdir.
//
// 26-Jul-03  fnj@DinkumSoftware.com  Initial.

#ifndef STAT_IFACE_H
#define STAT_IFACE_H

#ifdef __MWERKS__
// Metrowerks screwed up version: no include/sys dir, and _mkdir, not mkdir.

#include <stat.h>

#undef mkdir
#define mkdir(path, mode) _mkdir(path)

#else
// "Standard" version.

#include <sys/stat.h>

#endif

#endif // #ifndef STAT_IFACE_H
