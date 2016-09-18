#!/usr/bin/env python
''' This script looks for new glider data in the folder RawDataFiles, finds all the log-file directories
in it under each glider and then tries to process these. '''
import os, sys, re
from os.path import getsize, join
import datetime, time
import shelve
import gpplib
from gpplib.GliderAscFileReader import *

# Specify the executables: eg. dbd2asc='/Users/home/burtjones/GliderFiles/dbd2asc' and so on...
# Default: assume they are already installed in /usr/bin/
dbd2asc = 'dbd2asc'
dba_merge = 'dba_merge'
dba2_orig_matlab = 'dba2_orig_matlab'

baseDir = '/Volumes/MacintoshHD2/GliderData/'
#sys.stdout = open("%sout.log"%(baseDir),'a')
#sys.stderr = open("%serr.log"%(baseDir),'a')


class GliderFileIndexer(object):
    ''' We are going to create an index of the raw files here. '''
    def __init__(self,**kwargs):
        self.gafr = GliderAscFileReader()
        self.rawFileIndex = shelve.open('RawFileIndex.shelf')
        self.BdPat = re.compile('([0-9a-zA-Z\-\_]+).([deDEstSTmnMN]+[bB]+[dD]+)$') # Matches a sbd/tbd,mbd/nbd,ebd/dbd file
        self.MatPat = re.compile('([0-9a-zA-Z\-\_]+)_([deDEstSTmnMN]+[bB]+[dD]+).([mM]+[aA]+[tT]+)$')
        self.LgPat = re.compile('([0-9a-zA-Z\-\_]+).([mMnN]+[lL]+[gG]+)') # Matches mlg/nlg files 
        self.GdPat = re.compile('full_filename:[\s]+([a-zA-Z0-9\-\_]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9])')
        self.FfPat = re.compile('full_filename:[\s]+([a-zA-Z0-9\-\.\_\(\)]+)')
        self.MiPat = re.compile('mission_name:[\s]+([_a-zA-Z\.0-9]+)')
        self.FoPat = re.compile('fileopen_time:[\s]+([a-zA-Z0-9\_\:]+)')
        self.DatePat1 = re.compile('([A-Za-z]+)_([A-Za-z]+)__([0-9]+)([0-9\_\:]+)')
        self.DatePat2 = re.compile('([A-Za-z]+)_([A-Za-z]+)_([0-9]+)([0-9\_\:]+)')
        
        
    def GetGliderMissionTime(self,fileName):
	# gliderName, missionName, fileOpenTime, fullFileName = '', '', '', '' 
        f = open(fileName,'r')
	#print fileName
        for i in range(0,15):
            line = f.readline()
            m1 = self.FfPat.match(line)
            if m1:
                fullFileName = m1.group(1)
                m1b = self.GdPat.match(line)
		if m1b:
                   gliderName = m1b.group(1)
		else:
		   gliderName = 'Unknown'
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
                
        
    def GetLogFileDirectories(self,top):
        ''' Create a list of files and an index to it for each file type
        '''
        self.FileList, self.FileIndex = {}, {}
        self.FileList['dbd'],self.FileList['ebd'],self.FileList['sbd'], \
        self.FileList['tbd'],self.FileList['mbd'],self.FileList['nbd'] = \
            [], [], [], [], [], []
        self.FileIndex['dbd'],self.FileIndex['ebd'],self.FileIndex['sbd'], \
        self.FileIndex['tbd'],self.FileIndex['mbd'],self.FileIndex['nbd'] = \
            {}, {}, {}, {}, {}, {}
        
        for root, dirs, files in os.walk(top, topdown=False):
            for file in files:
                m = self.BdPat.match(file)
                if m:
                    sz = getsize(join(root, file))
                    if sz>0:
                        fileName, fileType = m.group(1), str.lower(m.group(2))
                        #print root, file, sz, m.group(1), m.group(2)
                        gliderName, missionName, fileOpenTime, fullFileName = self.GetGliderMissionTime(os.path.join(root,file))
                        self.rawFileIndex['%s_%s'%(fullFileName,fileType)] = (root,file,sz,fileName,fileType,gliderName,missionName,fileOpenTime,fullFileName) 
                        self.FileList[fileType].append((root,file,sz,fileName,fileType,gliderName,missionName,fileOpenTime,fullFileName))
                        self.FileIndex[fileType]['%s_%s'%(fullFileName,fileType)] = len(self.FileList[fileType])-1
 
    def GetProcessedMatFilesInDirectory(self,top):
        ''' Create a list of files and an index to it for each file type
        '''
        self.MatFileList, self.MatFileIndex = {}, {}
        self.MatFileList['dbd'],self.MatFileList['ebd'],self.MatFileList['sbd'] = \
            [], [], []
        self.MatFileIndex['dbd'],self.MatFileIndex['ebd'],self.MatFileIndex['sbd'] = \
            {}, {}, {}
        
        for root, dirs, files in os.walk(top, topdown=False):
            for file in files:
                m = self.MatPat.match(file)
                if m:
                    sz = getsize(join(root, file))
                    if sz>0:
                        fileName, fileType = m.group(1), str.lower(m.group(2)) # group(3) is always .mat
                        self.MatFileList[fileType].append((root,file,sz,fileName,fileType))
                        self.MatFileIndex[fileType]['%s'%(fileName)] = len(self.FileList[fileType])-1




class ProcessRawFile(GliderFileIndexer):
    ''' Processing workhorse. Goes through the index, creates a 
    '''
    def __init__(self,baseDir='./',rawFileDir='RawDataFiles/',processedAscDataDir='ProcessedAsc/',**kwargs):
        super(ProcessRawFile,self).__init__(**kwargs)
        self.GetLogFileDirectories(baseDir+rawFileDir)
        if kwargs.has_key('temp_asc_file_dir'):
            self.temp_asc_file_dir = kwargs['temp_asc_file_dir']
        else:
            self.temp_asc_file_dir = baseDir+'TempAscFileDir/'
        
        self.processedWebbMatlabDir = os.path.join(baseDir,'ProcessedWebbMatlabFormat/')
        self.processedAscDataDir = os.path.join(baseDir,processedAscDataDir)
        try:
            os.mkdir(self.processedWebbMatlabDir)
        except:
            pass
        try:
            os.mkdir(self.temp_asc_file_dir)    
        except:
            pass
        try:
            os.mkdir(self.processedAscDataDir)
            print 'Created directory %s to store processed .asc files.'%(self.processedAscDataDir)
        except:
            pass
        self.baseDir, self.rawFileDir = baseDir, rawFileDir
        self.dbd2asc, self.dba_merge, self.dba2_orig_matlab = 'dbd2asc', 'dba_merge', 'dba2_orig_matlab'
        # Index all the processed directories so that we can compare what we have already processed with
        # what needs processing.
        self.AscPat = re.compile('([0-9a-zA-Z\-\_]+).([aA]{1}[sS]{1}[cC]{1})')
        self.FiPat = re.compile('filename:[\s]+([a-zA-Z0-9\-\.\_\(\)]+)')
        self.FePat = re.compile('filename_extension:[\s]+([a-zA-Z]+)')
        self.GlPat = re.compile('filename:[\s]+([a-zA-Z0-9\-\_]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9])')
        self.IndexProcessedAscFiles(self.processedAscDataDir)

    def GetAscMissionTime(self,fileName):
        
        f = open(fileName,'r')
        for i in range(0,15):
            line = f.readline()
            m1 = self.FiPat.match(line)
            if m1:
                FileName = m1.group(1)
                m1b = self.GlPat.match(line)
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
        return gliderName,missionName,fileOpenTime,FileName
        
    def IndexProcessedAscFiles(self,top):
        ''' Create a list of processed files and an index to it for each processed file
        '''
        self.ProcFileList, self.ProcFileIndex = {}, {}
        self.ProcFileList['asc'], self.ProcFileList['mat'], self.ProcFileList['m'], self.ProcFileList['dat'] = \
                [], [], [], []
        self.ProcFileIndex['asc'], self.ProcFileIndex['mat'], self.ProcFileIndex['m'], self.ProcFileIndex['dat'] = \
                {}, {}, {}, {}
        for root, dirs, files in os.walk(top, topdown=False):
            for file in files:
                m = self.AscPat.match(file)
                if m:
                    sz = getsize(join(root, file))
                    if sz>0:
                        fileName, fileType = m.group(1), str.lower(m.group(2))
                        gliderName, missionName, fileOpenTime, fullFileName = self.GetAscMissionTime(os.path.join(root,file))
                        self.ProcFileList['asc'].append((root,file,sz,fileName,fileType,gliderName,missionName,fileOpenTime,fullFileName))
                        self.ProcFileIndex['asc']['%s'%(fileName)] = len(self.ProcFileList)-1
    
    def ProcessUnprocessedFiles(self):
            ''' Use a space-efficient file-by-file ASC file merge
            '''
            FlightPersistorFileTypes = ['dbd','mbd','sbd']
            SciencePersistorFileTypes = ['ebd','nbd','tbd']
            
            start_t = time.time()
            print 'Indexing Raw data files'
            self.GetLogFileDirectories(self.baseDir+self.rawFileDir)
            
            print 'Indexing Processed Files'
            self.IndexProcessedAscFiles(self.processedAscDataDir)
            
            filesProcessed = 0
            for idx,fpFileType in enumerate(FlightPersistorFileTypes):
                for fileTup in self.FileList[fpFileType]:
                    root,file,sz,fileName,fileType,gliderName,missionName,fileOpenTime,fullFileName = fileTup
                    spFileType = SciencePersistorFileTypes[idx]
                    mergeRequired = False
                    if self.FileIndex[spFileType].has_key('%s_%s'%(fullFileName,spFileType)):
                        fileIdx = self.FileIndex[spFileType]['%s_%s'%(fullFileName,spFileType)]
                        fileTup2 = self.FileList[spFileType][fileIdx]
                        rootSp,fileSp,szSp,fileNameSp,fileTypeSp,gliderNameSp,missionNameSp,fileOpenTimeSp,fullFileNameSp = fileTup2
                        mergeRequired = True
                        
                    if not self.ProcFileIndex['asc'].has_key('%s_%s'%(fullFileName,fileType)):
                            # At this point of time we supposedly have the file locations and names of all the files that need 
                            # conversion.
                            #try:
                            FlightAscFile=os.path.join(self.baseDir,self.temp_asc_file_dir,'%s_%s.asc'%(fullFileName,fileType))
                            convFpCmd = '%s %s > %s'%(self.dbd2asc,os.path.join(root,file),FlightAscFile)
                            print convFpCmd; os.system(convFpCmd)
                            
                            if mergeRequired:
                                ScienceAscFile=os.path.join(self.baseDir,self.temp_asc_file_dir,'%s_%s.asc'%(fullFileNameSp,fileTypeSp))
                                convSpCmd = '%s %s > %s'%(self.dbd2asc,os.path.join(rootSp,fileSp),ScienceAscFile)
                                print convSpCmd; os.system(convSpCmd)
                                
                                print '----- Merging the files -----'
                                MergedAscFile = os.path.join(self.baseDir,self.temp_asc_file_dir,'%s.asc'%(fullFileName))
                                mergeCmd = '%s %s %s > %s'%(self.dba_merge,FlightAscFile,ScienceAscFile,MergedAscFile); 
                                print mergeCmd; os.system(mergeCmd)
                            movedAscFile = os.path.join(self.processedAscDataDir,'%s_%s.asc'%(fullFileName,fileType))
                            print '----- Done converting ------. Deleting temporary files'
                            
                            if mergeRequired:
                                os.unlink(ScienceAscFile); os.unlink(FlightAscFile);
                                print '----- Done. Now moving ASC file to %s directory ------'%(self.processedWebbMatlabDir)
                                move_asc_cmd = 'mv %s %s'%(MergedAscFile,movedAscFile); os.system(move_asc_cmd)
                            else:
                                print '----- Done. Now moving ASC file to %s directory ------'%(self.processedWebbMatlabDir)
                                move_asc_cmd = 'mv %s %s'%(FlightAscFile,movedAscFile); os.system(move_asc_cmd)
                            
                            print '----- Converting file to Matlab using %s ------'%(self.dba2_orig_matlab)
                            Dba2MatlabCmd = 'cat %s | %s'%(movedAscFile,self.dba2_orig_matlab)
                            print Dba2MatlabCmd; os.system(Dba2MatlabCmd)
                            move_m_cmd = 'mv %s_%s.m %s'%(fullFileName.replace('-','_'),fpFileType,self.processedWebbMatlabDir)
                            move_dat_cmd = 'mv %s_%s.dat %s'%(fullFileName.replace('-','_'),fpFileType,self.processedWebbMatlabDir)
                            print move_m_cmd; os.system(move_m_cmd)
                            print move_dat_cmd; os.system(move_dat_cmd)
                            filesProcessed +=1
                            #except OSError:
                            #print 'Encountered an error on the last conversion but will try to continue...'
                            
                    else:
                        #print 'No need to process %s as it is already processed.'%(fullFileName)
                        pass
            stop_t = time.time()
            print 'Processing %d files took %.3f seconds.'%(filesProcessed,(stop_t-start_t))

        
    def ReProcessEverything(self):
        ''' Use a space-efficient file-by-file ASC file merge
        '''
        FlightPersistorFileTypes = ['dbd','mbd','sbd']
        SciencePersistorFileTypes = ['ebd','nbd','tbd']
        
        for idx,fpFileType in enumerate(FlightPersistorFileTypes):
            for fileTup in self.FileList[fpFileType]:
                root,file,sz,fileName,fileType,gliderName,missionName,fileOpenTime,fullFileName = fileTup
                spFileType = SciencePersistorFileTypes[idx]
                if self.FileIndex[spFileType].has_key('%s_%s'%(fullFileName,spFileType)):
                    fileIdx = self.FileIndex[spFileType]['%s_%s'%(fullFileName,spFileType)]
                    fileTup2 = self.FileList[spFileType][fileIdx]
                    rootSp,fileSp,szSp,fileNameSp,fileTypeSp,gliderNameSp,missionNameSp,fileOpenTimeSp,fullFileNameSp = fileTup2
                    
                    # At this point of time we supposedly have the file locations and names of all the files that need 
                    # conversion.
                    FlightAscFile=os.path.join(self.baseDir,self.temp_asc_file_dir,'%s_%s.asc'%(fullFileName,fileType))
                    ScienceAscFile=os.path.join(self.baseDir,self.temp_asc_file_dir,'%s_%s.asc'%(fullFileNameSp,fileTypeSp))
                    convFpCmd = '%s %s > %s'%(self.dbd2asc,os.path.join(root,file),FlightAscFile)
                    convSpCmd = '%s %s > %s'%(self.dbd2asc,os.path.join(rootSp,fileSp),ScienceAscFile)
                    print convFpCmd; os.system(convFpCmd)
                    print convSpCmd; os.system(convSpCmd)
                    
                    print '----- Merging the files -----'
                    MergedAscFile = os.path.join(self.baseDir,self.temp_asc_file_dir,'%s.asc'%(fullFileName))
                    mergeCmd = '%s %s %s > %s'%(self.dba_merge,FlightAscFile,ScienceAscFile,MergedAscFile); 
                    print mergeCmd; os.system(mergeCmd)
                    movedAscFile = os.path.join(self.processedAscDataDir,'%s_%s.asc'%(fullFileName,fileType))
                    print '----- Done converting ------. Deleting temporary files'
                    os.unlink(FlightAscFile); os.unlink(ScienceAscFile)
                    print '----- Done. Now moving ASC file to %s directory ------'%(self.processedWebbMatlabDir)
                    move_asc_cmd = 'mv %s %s'%(MergedAscFile,movedAscFile); 
                    print move_asc_cmd; os.system(move_asc_cmd)
                                        
                    print '----- Converting file to Matlab using %s ------'%(self.dba2_orig_matlab)
                    Dba2MatlabCmd = 'cat %s | %s'%(movedAscFile,self.dba2_orig_matlab)
                    print Dba2MatlabCmd; os.system(Dba2MatlabCmd)
                    move_m_cmd = 'mv %s_%s.m %s'%(fullFileName.replace('-','_'),fpFileType,self.processedWebbMatlabDir)
                    move_dat_cmd = 'mv %s_%s.dat %s'%(fullFileName.replace('-','_'),fpFileType,self.processedWebbMatlabDir)
                    print move_m_cmd; os.system(move_m_cmd)
                    print move_dat_cmd; os.system(move_dat_cmd)


def main(argv=None):
	if argv is None:
		argv = sys.argv
	while(1):
		print '---------------------------------------------------------------------'
		print '\n%s - Starting a regular data processing run...'%(time.ctime())
		print '\n%s - Creating an index of the raw-files.'%(time.ctime())
		rfi = ProcessRawFile(baseDir)
		print '\n%s - Processing Unprocessed files.'%(time.ctime())
		rfi.ProcessUnprocessedFiles()
		print '\n%s - Asta-la-Vista Baby! I\'ll be back!!!'%(time.ctime())
		rfi.rawFileIndex.close()
		#rfi.GetLogFileDirectories(baseDir+'RawDataFiles/')
		#rfi.rawFileIndex.close()
		time.sleep(60)

if __name__ == "__main__":
	sys.exit(main())

#rfi = ProcessRawFile(baseDir)
#print '\n%s - Processing Unprocessed files.'%(time.ctime())
#rfi.ProcessUnprocessedFiles()
#rfi.rawFileIndex.close()
