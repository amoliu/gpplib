#!/usr/bin/env python
''' 
@author: Arvind A de Menezes Pereira
@summary: This program contains the base class that allows glider ASC file manipulation
'''
import re, sys
import string
import numpy as np
import time

class GliderAscFileReader(object):
    ''' Base class for glider Ascii file manipulation
    '''
    def __init__(self,**kwargs):
        self.BdPat = re.compile('([0-9a-zA-Z\-\_]+).([deDEstSTmnMN]+[bB]+[dD]+)') # Matches a sbd/tbd,mbd/nbd,ebd/dbd file
        self.LgPat = re.compile('([0-9a-zA-Z\-\_]+).([mMnN]+[lL]+[gG]+)') # Matches mlg/nlg files 
        self.GdPat = re.compile('filename:[\s]+([a-zA-Z0-9\-]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9])')
        self.FfPat = re.compile('filename:[\s]+([a-zA-Z0-9\-\.\_\(\)]+)')
        self.MiPat = re.compile('mission_name:[\s]+([_a-zA-Z\.0-9]+)')
        self.FoPat = re.compile('fileopen_time:[\s]+([a-zA-Z0-9\_\:]+)')
        self.DatePat1 = re.compile('([A-Za-z]+)_([A-Za-z]+)__([0-9]+)([0-9\_\:]+)')
        self.DatePat2 = re.compile('([A-Za-z]+)_([A-Za-z]+)_([0-9]+)([0-9\_\:]+)')
        self.FePat = re.compile('filename_extension:[\s]+([a-zA-Z]+)')
        self.GlPat = re.compile('filename:[\s]+([a-zA-Z0-9\-]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9])')
    
    def LoadHeadersUnitsFields(self,fileName):
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
        print lines
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
        lines = fid.readlines(20)
        data_units = string.split( lines[0], ' ')
        if len(data_units) != num_fields:
            print 'Number of data units is not the same as the number of fields!'    
        done_with_hdrs = 1
        data_num_bytes = string.split( lines[1], ' ')
        if( len(data_num_bytes) != num_fields ):
            print 'Number of byte-fields is not the same as the number of fields!'
        fid.close()
        #import pdb; pdb.set_trace()
        
        return headers,data_fields,data_units,data_num_bytes,num_fields
    
    
    def LoadSelectFieldsFromAscFile(self,fileName,fields):
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
                                break #sys.exit(-1)
                        if line_no == num_hdr_items+3:
                            done_with_hdrs = 1
                            data_num_bytes = string.split( line, ' ')
                            if( len(data_num_bytes) != num_fields ):
                                print 'Number of byte-fields is not the same as the number of fields!'
                                break #sys.exit(-1)
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

    def GetDataForField(self,data_field,data_fields,data_values):
        return data_values[:,data_fields.index(data_field)]
    
    def GetDataForEachType(self,data_fields,data_values):
        sci_indices = []; cmd_indices = []; meas_indices = []; gld_indices = []
        x_indices = []; xs_indices = []; cc_indices = []; usr_indices= []; f_indices=[]
        
        sci_fields = []; cmd_fields = []; meas_fields = []; gld_fields = []
        x_fields = [];   xs_fields = []; cc_fields = []; usr_fields = []; f_fields = []
        
        sci_data, meas_data, cmd_data = {}, {}, {}
        
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
                sci_data[data_field] = self.GetDataForField(data_field,data_fields,data_values)
            if m_cmd:
                cmd_indices.append(data_fields.index(data_field))
                cmd_fields.append(data_field)
                cmd_data[data_field] = self.GetDataForField(data_field, data_fields, data_values)
            if m_meas:
                meas_indices.append(data_fields.index(data_field))
                meas_fields.append(data_field)
                meas_data[data_field] = self.GetDataForField(data_field,data_fields,data_values)
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
                
            return meas_data,sci_data,cmd_data
        
    def GetGliderMissionTime(self,fileName):
        f = open(fileName,'r')
        for i in range(0,15):
            line = f.readline()
            m1 = self.FfPat.match(line)
            if m1:
                fullFileName = m1.group(1)
                m1b = self.GdPat.match(line)
                gliderName = m1b.group(1)
            else:
                m2 = self.MiPat.match(line)
                if m2:
                    missionName = m2.group(1)
                else:
                    m3 = self.FoPat.match(line)
                    if m3:
                        if self.DatePat1.match(m3.group(1)):       
                            fileOpenTime = time.strptime(m3.group(1), '%a_%b__%d_%H:%M:%S_%Y')
                        elif self.DatePat2.match(m3.group(1)):
                            fileOpenTime = time.strptime(m3.group(1),'%a_%b_%d_%H:%M:%S_%Y')
        f.close()
        return gliderName,missionName,fileOpenTime,fullFileName
