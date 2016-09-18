// Copyright(c) 2001-2002, Webb Research Corporation, ALL RIGHTS RESERVED
/* dbdfrmat.h

This file has symbolic definitons for the various
keys and fields for a *.dbd file, Dinkum Binary Format.

See dbd.h or doco/dbd_file_format.txt for documentation.

This file is intended to be processor/OS neutral.
I.E. It is expected to be included in programs which
run in a vehicle or a shore-side data processing computer.

14-Apr-01 tc@DinkumSoftware.com Initial
18-Apr-01 tc@DinkumSoftware.com Renamed DBD_LABEL-->DBD_LABEL_VALUE
22-Apr-01 tc@DinkumSoftware.com Minor reworks, no special initial line
25-Apr-01 tc@DinkumSoftware.com Format change, add a ENDFILE_CYCLE_TAG
30-Apr-01 tc@DinkumSoftware.com Added FILENAME_EXTENSION_KEY
26-Sep-01 tc@DinkumSoftware.com Encoding version 2, Added ability to send eight byte doubles
18-Jul-03 fnj@DinkumSoftware.com Encoding version 4, sensor list factoring:
                                 added keys SENSOR_LIST_CRC and SENSOR_LIST_FACTORED.
*/

#ifndef DBDFRMAT_H
#define DBDFRMAT_H

// What must appear as value on the first line
#define    DBD_LABEL_VALUE "DBD(dinkum_binary_data)file"

// Definitions for keys in ascii portion of file
// No whitespace allowed in keys
// Header stuff
#define    DBD_LABEL_KEY             "dbd_label:"
#define    ENCODING_VER_KEY          "encoding_ver:"
#define    NUM_ASCII_TAGS_KEY        "num_ascii_tags:"
#define    ALL_SENSORS_KEY           "all_sensors:"
#define    THE8x3_FILENAME_KEY       "the8x3_filename:"
#define    FULL_FILENAME_KEY         "full_filename:"
#define    FILENAME_EXTENSION_KEY    "filename_extension:"
#define    MISSION_NAME_KEY          "mission_name:"
#define    FILEOPEN_TIME_KEY         "fileopen_time:"
#define    TOTAL_NUM_SENSORS_KEY     "total_num_sensors:"
#define    SENSORS_PER_CYCLE_KEY     "sensors_per_cycle:"
#define    STATE_BYTES_PER_CYCLE_KEY "state_bytes_per_cycle:"
#define    SENSOR_LIST_CRC           "sensor_list_crc:"
#define    SENSOR_LIST_FACTORED      "sensor_list_factored:"

// Labels start of line listing all the sensors
#define    SENSOR_NAME_KEY_STR       "s:"

// Different kinds of data types we support
#define    DATA_TYPE_DOUBLE 8
#define    DATA_TYPE_FLOAT  4
#define    DATA_TYPE_INT    2
#define    DATA_TYPE_BYTE   1


// Cycle tags, a one byte value that tells what kind of
// binary data follows
#define    DATA_CYCLE_TAG          ( (unsigned char) 'd' )
#define    SAMPLE_CYCLE_TAG        ( (unsigned char) 's' )
#define    ENDFILE_CYCLE_TAG       ( (unsigned char) 'X' )

    // Sample data written
#define SAMPLE_BYTE            ( (unsigned char) 'a'     )
#define SAMPLE_2BYTE_INT       ( (int)           0x1234  )
#define SAMPLE_4BYTE_FLOAT     ( (float )        123.456 )

    // Early versions (1) only had 3 data types
    // encoding version 2 added 8 byte doubles
#define FIRST_VERSION_WITH_DOUBLES 2
#define SAMPLE_8BYTE_DOUBLE    ( (double) 123456789.12345)


// Field codes for each sensor in a state byte
#define    FIELD_NOT_UPDATED                  0x00
#define    FIELD_UPDATED_WITH_SAME_VALUE      0x01  // 0000.0001
#define    FIELD_UPDATED_WITH_NEW_VALUE       0x02  // 0000.0010


#endif // DBDFRMAT_H




