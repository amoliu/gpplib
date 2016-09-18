# makefile-linux-dbd
#
# A makefile for linux hosted executables as part of
# of the Webb Research glider project.
#
#
# 15-Apr-01 tc@DinkumSoftware.com Initial, dbd2asc
# 16-Apr-01 tc@DinkumSoftware.com First, real
# 21-Apr-01 tc@DinkumSoftware.com Added dbd_header.cc/h
# 25-Apr-01 tc@DinkumSoftware.com Added clean entry
# 26-Apr-01 tc@DinkumSoftware.com Added dba2-orig-matlab
# 10-May-01 tc@DinkumSoftware.com Added rename_dbd_files and options
# 17-Jul-01 tc@DinkumSoftware.com dbd2asc reads multiple files
# 18-Sep-01 tc@DinkumSoftware.com Added doco entry
#  1-Dec-01 tc@DinkumSoftware.com Added dba_time_filter
#  2-Jan-02 tc@DinkumSoftware.com renamed Makefile->makefile-linux-glider
#                                 to avoid case collision under Windoze
# 30-Sep-02 tc@DinkumSoftware.com Support for location of html files moving
# 25-Jul-03 tc@DinkumSoftware.com Bug fix.  gcc3 requires using namespace std;
#                                 Added -include using_std.h
#                                 gcc (GCC) 3.2.2 20030222 (Red Hat Linux 3.2.2-5)
#                                 Note: also get deprecated header warning on:
#                                      options.cc dbd_reader.cc NOT FIXED
#                                 Suppressed the printout with -Wno-deprecated
# 26-Jul-03 tc@DinkumSoftware.com Went to -static links so would run on linux 7.x
# 21-Jan-04 tc@DinkumSoftware.com Added dba_sensor_filter and dba2_glider_data
#                                 new src: input_vector.h/cc
#  2-Feb-04 tc@DinkumSoftware.com Added mlg_file.cc
# 07-Jul-04 fnj@DinkumSoftware.com Changed -pedantic-errors to -pedantic to avoid fatal errors
#                                  due to "use of C99 hexadecimal floating constant" warnings.
# 16-Nov-05 tc@DinkumSoftware.com Built dba2_glider_view
# 2009.09.22 tc@DinkumSoftware.com Added dba_merge + dbd_asc_merged_header
# 2012.05.15 arvind.pereira@gmail.com Modified makefile-linux-dbd s.t. it works across all platforms.


# EXES = dbd2asc dba2_orig_matlab rename_dbd_files  \

EXES = dbd2asc dba2_orig_matlab \
       dba_time_filter dba_sensor_filter dba_merge \
       dba2_glider_data dba2_glider_view


default: $(EXES)

all: $(EXES) tags documentation

SRCS = dbd_reader.cc dbd_reqd_header.cc dbd_header.cc dbd_asc_header.cc \
       dbd_asc_merged_header.cc dbd_sensor_info.cc dbd_sensor_value_collection.cc \
	   dbd_sensor_value.cc dbd_sensor_cycle_state.cc dbd_support.cc \
	   options.cc dbd_header_collection.cc mas_time.cc mas_string.cc \
       input_vector.cc mlg_file.cc


include $(SRCS:.cc=.d)   # for generating automatic dependencies
OBJS =  $(SRCS:.cc=.o)


LOADLIBES = -lstdc++
#LDFLAGS   = -static
# CPPFLAGS
CXXFLAGS  = -ggdb -Wswitch -pedantic -Wunused -Wno-deprecated -include using_std.h

dbd2asc:           $(OBJS)
dba2_orig_matlab:  $(OBJS)
rename_dbd_files:  $(OBJS)
dba_time_filter:   $(OBJS)
dba_sensor_filter: $(OBJS)
dba_merge:         $(OBJS)
dba2_glider_data:  $(OBJS)
dba2_glider_view:  $(OBJS)

clean:
	rm -f $(OBJS)
	rm -f $(EXES)
	rm -rf docs/

superclean:
	rm -f *.d
	rm -rf *.dSYM/
	make clean

# Generate the documentation
documentation:
	doxygen Doxyfile

# Install the programs into /usr/local/bin/
install:
	for executable in $(EXE) ; do \
		cp $$executable /usr/local/bin/ ; \
	done


# Generate a specific tags file
INCLUDES = $(SRCS:.cc=.h) 
tags:
	chmod +w DBDTAGS
	etags $(SRCS) $(INCLUDES) -o DBDTAGS

# Rule to generate dependencies automatically
# This might ought to migrate into an include file somewhere
# Taken verbatium from GNU Make manual, sec 4.12
%.d: %.cc
	@echo Scanning for include dependencies: $<
	@set -e; $(CC) -M $(CPPFLAGS) $< \
    | sed 's/\($*\)\.o[ :]*/\1.o $@ : /g' > $@; \
    [ -s $@ ] || rm -f $@


