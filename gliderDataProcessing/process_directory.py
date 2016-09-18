#!/usr/local/bin/python
'''
@author : Arvind A de Menezes Pereira
@summary: Simple script to process all the glider files in a given directory
@os support: OS-X, Linux and Unix
'''
import os, re
import sys


# Specify the executables: eg. dbd2asc='/Users/home/burtjones/GliderFiles/dbd2asc' and so on...
# Default: assume they are already installed in /usr/bin/
dbd2asc = 'dbd2asc'
dba_merge = 'dba_merge'
dba2_orig_matlab = 'dba2_orig_matlab'

# Specify the directory in which the dbd,ebd,sbd,tbd files are located. 
# Default: the current directory.
dbd_file_directory,ebd_file_directory,sbd_file_directory,tbd_file_directory='.','.','.','.'
#dbd_file_directory = '../HeHaPe_Flight/LOGS'
#ebd_file_directory = '../HeHaPe_Sci/LOGS'
#sbd_file_directory = '../HeHaPe_Flight/LOGS'
#tbd_file_directory = '../HeHaPe_Sci/LOGS'

# Specify the directory which should be used to store the output files
# Default: the current directory. 
asc_file_directory = '.'
mat_file_directory = '.'
#mat_file_directory = 'mat'

# Get the list of files we are trying to process
dbd_dir_list = os.listdir(dbd_file_directory)
ebd_dir_list = os.listdir(ebd_file_directory)

# Find all the dbd files and convert them to asc
for dir_entry in dbd_dir_list:
	m_dbd = re.match( '([\w]+).([dD][bB][dD])$', dir_entry )	
	if m_dbd:
		dbd2asc_cmd = dbd2asc+' '+dbd_file_directory+'/'+dir_entry+' > '+asc_file_directory+'/'+m_dbd.group(1)+'.ASCa'
		print dbd2asc_cmd
		retCode = os.system(dbd2asc_cmd)

# Find all the ebd files and convert them to asc
for dir_entry in ebd_dir_list:
	m_ebd = re.match( '([\w]+).([eE][bB][dD])$', dir_entry )
	if m_ebd:
		ebd2asc_cmd = dbd2asc+' '+ebd_file_directory+'/'+dir_entry+' > '+asc_file_directory+'/'+m_ebd.group(1)+'.ASCb'
		print ebd2asc_cmd
		retCode = os.system(ebd2asc_cmd)

# Now we tackle the sbd and tbd files
sbd_dir_list = os.listdir(sbd_file_directory)
tbd_dir_list = os.listdir(tbd_file_directory)

# Find all the sbd files and convert them to asc
for dir_entry in sbd_dir_list:
	m_sbd = re.match( '([\w]+).([sS][bB][dD])$', dir_entry )	
	if m_sbd:
		dbd2asc_cmd = dbd2asc+' '+sbd_file_directory+'/'+dir_entry+' > '+asc_file_directory+'/'+m_sbd.group(1)+'.ASCa'
		print dbd2asc_cmd
		retCode = os.system(dbd2asc_cmd)

# Find all the tbd files and convert them to asc
for dir_entry in tbd_dir_list:
	m_tbd = re.match( '([\w]+).([tT][bB][dD])$', dir_entry )
	if m_tbd:
		tbd2asc_cmd = dbd2asc+' '+tbd_file_directory+'/'+dir_entry+' > '+asc_file_directory+'/'+m_tbd.group(1)+'.ASCb'
		print ebd2asc_cmd
		retCode = os.system(ebd2asc_cmd)

# Now Merge the ASCa and ASCb files
asc_file_list = os.listdir(asc_file_directory)
for dir_entry in asc_file_list:
	m_asc = re.match('([\w]+).ASCa$', dir_entry )
	if m_asc:
		dba_merge_cmd = dba_merge+' '+asc_file_directory+'/'+dir_entry+' '+asc_file_directory+'/'+m_asc.group(1)+'.ASCb > '+asc_file_directory+'/'+m_asc.group(1)+'.ASC'
		print dba_merge_cmd
		retCode = os.system(dba_merge_cmd)

asc_file_list = os.listdir(asc_file_directory)
for dir_entry in asc_file_list:
	# Now convert the files to MAT
	m_asc = re.match('([\w]+).ASC$', dir_entry)
	if m_asc:
		dba2_matlab_cmd = 'cat '+asc_file_directory+'/'+m_asc.group(1)+'.ASC | dba2_orig_matlab'
		print dba2_matlab_cmd
		retCode = os.system(dba2_matlab_cmd)

# Move the converted .mat and .m files to the directory specified
move_m_cmd = 'mv *.m '+mat_file_directory+'/' 
move_mat_cmd = 'mv *.dat '+mat_file_directory+'/'
rm_asc_cmd = 'rm '+asc_file_directory+'/*.ASCa '+asc_file_directory+'/*.ASCb'
retCode = os.system(rm_asc_cmd)
retCode = os.system(move_m_cmd)
retCode = os.system(move_mat_cmd)

print 'Done Converting SBD, TBD, DBD and EBD files to ASC, .M and .DAT files'
print '.DAT and .M files have been stored in the '+mat_file_directory+'/ directory.'
