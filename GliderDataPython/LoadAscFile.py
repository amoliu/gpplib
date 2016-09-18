'''
Created on Aug 29, 2011

@author: Arvind A de Menezes Pereira
@summary: This program loads an ASCII file and writes out a CSV file with the appropriate data
'''
import re, sys
import string
import numpy as np
import time

def GetUnixTimeFromString(str):
    #int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone
    return int(time.mktime(time.strptime( str, '%Y-%m-%d %H:%M:%S'))) - time.timezone

def GetTimeString(epoch):
    str = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(epoch))
    return str

def GetKMLTimeString(epoch):
    str = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch))
    return str


def LoadHeadersUnitsFields(fileName):
    fid = open(fileName,'r')
    headers = {}
    data_fields = []
    data_units = []
    data_num_bytes = []
    num_hdr_items = 0
    line_no = 0
    num_fields = 0
    done_with_hdrs = 0
    
    lines = fid.readlines(20)
    for line in lines:
        # Test for header data.
        line_no = line_no+1
        if done_with_hdrs == 0:
            m_hdr = re.match('([a-zA-Z0-9\_]+): ([\(\)\_\:\.\-0-9a-zA-Z]+)', line)
            if (m_hdr):
                headers[m_hdr.group(1)] = m_hdr.group(2)
                num_hdr_items = num_hdr_items+1
            else:
                if line_no == num_hdr_items+1:
                    data_fields = string.split(line, ' ' )
                    num_fields = len( data_fields )
                else:
                    if line_no == num_hdr_items+2:
                        data_units = string.split( line, ' ')
                        if len(data_units) != num_fields:
                            print 'Number of data units is not the same as the number of fields!'    
                            sys.exit(-1)
                    if line_no == num_hdr_items+3:
                        done_with_hdrs = 1
                        data_num_bytes = string.split( line, ' ')
                        if( len(data_num_bytes) != num_fields ):
                            print 'Number of byte-fields is not the same as the number of fields!'
                            sys.exit(-1)
    fid.close()
    return headers,data_fields,data_units,data_num_bytes,num_fields

def LoadSelectFieldsFromAscFile(fileName,fields):
    fid = open(fileName,'r')
    headers = {}
    data_fields = []
    select_data_fields = []
    data_units = []
    data_num_bytes = []
    num_hdr_items = 0
    line_no = 0
    num_fields = 0
    data_values = np.array
    done_with_hdrs = 0
    field_index = {}
    
    lines = fid.readlines()
    for line in lines:
        # Test for header data.
        line_no = line_no+1
        if done_with_hdrs == 0:
            m_hdr = re.match('([a-zA-Z0-9\_]+): ([\(\)\_\:\.\-0-9a-zA-Z]+)', line)
            if (m_hdr):
                headers[m_hdr.group(1)] = m_hdr.group(2)
                num_hdr_items = num_hdr_items+1
            else:
                if line_no == num_hdr_items+1:
                    data_fields = string.split(line, ' ' )
                    indx = 0
                    for data_field in data_fields:
                        for field in fields:
                            if re.match(field,data_field):
                                field_index[data_field]=indx
                                select_data_fields.append(data_field)
                        indx = indx+1
                                
                    num_fields = len( data_fields )
                else:
                    if line_no == num_hdr_items+2:
                        data_units = string.split( line, ' ')
                        if len(data_units) != num_fields:
                            print 'Number of data units is not the same as the number of fields!'    
                            sys.exit(-1)
                    if line_no == num_hdr_items+3:
                        done_with_hdrs = 1
                        data_num_bytes = string.split( line, ' ')
                        if( len(data_num_bytes) != num_fields ):
                            print 'Number of byte-fields is not the same as the number of fields!'
                            sys.exit(-1)
        else:
            data_value_line = string.split( line, ' ')
            if len(data_value_line) != num_fields:
                print 'Amount of data in this line is not the same as the number of fields:'
                print data_value_line
                # Parse the data values into their appropriate value
            x = np.zeros(len(field_index))
            i = 0
            for select_field in select_data_fields:
                #print field_index['%s'%(indx)]
                x[i] = string.atof(data_value_line[field_index[select_field]])
                i=i+1
            if line_no == num_hdr_items+4:
                data_values = x
            else:
                data_values = np.vstack([data_values,x])
            #print('\r%d/%d' %( line_no, len(lines)));
    fid.close()
    print ('\nLoaded data from : %s which had %d lines of data.'%(fileName,len(lines)))
    return headers, num_hdr_items, num_fields, select_data_fields, data_units, data_num_bytes, data_values    
    

def LoadAscFile(fileName):
    fid = open(fileName,'r')

    headers = {}
    data_fields = []
    data_units = []
    data_num_bytes = []
    num_hdr_items = 0
    line_no = 0
    num_fields = 0
    data_values = np.array
    lines = fid.readlines()
    for line in lines:
        # Test for header data.
        line_no = line_no+1
        m_hdr = re.match('([a-zA-Z0-9\_]+): ([\(\)\_\:\.\-0-9a-zA-Z]+)', line)
        if (m_hdr):
            headers[m_hdr.group(1)] = m_hdr.group(2)
            num_hdr_items = num_hdr_items+1
        else:
            if line_no == num_hdr_items+1:
                data_fields = string.split(line, ' ' )
                num_fields = len( data_fields )
            else:
                if line_no == num_hdr_items+2:
                    data_units = string.split( line, ' ')
                    if len(data_units) != num_fields:
                        print 'Number of data units is not the same as the number of fields!'
                        sys.exit(-1)
                if line_no == num_hdr_items+3:
                    data_num_bytes = string.split( line, ' ')
                    if( len(data_num_bytes) != num_fields ):
                        print 'Number of byte-fields is not the same as the number of fields!'
                        sys.exit(-1)
                else:
                    data_value_line = string.split( line, ' ')
                    if len(data_value_line) != num_fields:
                        print 'Number of data units in this line is not the same as the number of fields:'
                        print data_value_line
                    else:
                        if line_no >= num_hdr_items+4:
                            # Parse the data values into their appropriate value
                            x = np.zeros(num_fields-1)
                            for i in range(0,num_fields-1):
                                x[i] = string.atof(data_value_line[i])
                            if line_no == num_hdr_items+4:
                                data_values = x
                            else:
                                data_values = np.vstack([data_values,x])
    fid.close()
    return headers, num_hdr_items, num_fields, data_fields, data_units, data_num_bytes, data_values
 
 
def GetDataForField(data_field,data_fields,data_values):
    return data_values[:,data_fields.index(data_field)]
    
'''    
    Get all the science data
''' 
def GetDataForEachType(data_fields,data_values):
    sci_indices = []
    cmd_indices = []
    meas_indices = []
    gld_indices = []
    x_indices = []
    xs_indices = []
    cc_indices = []
    usr_indices= []
    f_indices=[]
    
    sci_fields = []
    cmd_fields = []
    meas_fields = []
    gld_fields = []
    x_fields = []
    xs_fields = []
    cc_fields = []
    usr_fields = []
    f_fields = []
    
    sci_data = {}
    meas_data = {}
    
    for data_field in data_fields:
        m_sci = re.match( '(sci_[a-zA-Z\_0-9]+)', data_field )
        m_cmd = re.match('(c_[a-zA-Z\_0-9]+)', data_field )         
        m_meas = re.match('(m_[a-zA-Z\_0-9]+)', data_field )
        m_gld = re.match('(gld_[a-zA-Z\_0-9]+)', data_field )
        m_x = re.match('(x_[a-zA-Z\_0-9]+)', data_field )
        m_xs =re.match('(xs_[a-zA-Z\_0-9]+)', data_field ) 
        m_cc = re.match('(cc_[a-zA-Z\_0-9]+)', data_field )
        m_usr = re.match('(usr_[a-zA-Z\_0-9]+)', data_field )
        m_f = re.match('(f_[a-zA-Z\_0-9]+)', data_field )
        
        if m_sci:
            sci_indices.append(data_fields.index(data_field))
            sci_fields.append(data_field)
            sci_data[data_field] = GetDataForField(data_field,data_fields,data_values)
        if m_cmd:
            cmd_indices.append(data_fields.index(data_field))
            cmd_fields.append(data_field)
        if m_meas:
            meas_indices.append(data_fields.index(data_field))
            meas_fields.append(data_field)
            meas_data[data_field] = GetDataForField(data_field,data_fields,data_values)
        if m_gld:
            gld_indices.append(data_fields.index(data_field))
            gld_fields.append(data_field)
        if m_x:
            x_indices.append(data_fields.index(data_field))
            x_fields.append(data_field)
        if m_xs:
            xs_indices.append(data_fields.index(data_field))
            xs_fields.append(data_field)
        if m_cc:
            cc_indices.append(data_fields.index(data_field))
            cc_fields.append(data_field)
        if m_usr:
            usr_indices.append(data_fields.index(data_field))
            usr_fields.append(data_field)
        if m_f:
            f_indices.append(data_fields.index(data_field))
            f_fields.append(data_field)
  
    '''print sci_fields 
    print meas_fields 
    print cmd_fields
    print cc_fields
    print x_fields
    print xs_fields
    print gld_fields'''
    return meas_data,sci_data
    
            
'''       
if len(sys.argv)>1:
    print sys.argv
    hdrs,num_hdr_items,num_fields,data_fields,data_units, data_num_bytes, data_values = LoadAscFile(sys.argv[1])

    print hdrs
    print num_hdr_items
    
    meas_data,sci_data = GetDataForEachType(data_fields,data_values)
'''