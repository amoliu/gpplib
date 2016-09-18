from gpplib.gppExceptions import *


class DateRange(object):
    ''' Produces a list of tuples (yyyy,mm,dd) called DateList, for use in other stuff
    '''
    def __init__(self,yy_start,mm_start,dd_start,yy_end,mm_end,dd_end):
        self.DateList = []
        startDay = yy_start+mm_start/100.+dd_start/10000.;
        endDay = yy_end+mm_end/100.+dd_end/10000.;
        if startDay > endDay:
            raise(DateRangeError('%04d-%02d-%02d comes after %04d-%02d-%02d'% \
                                (yy_start,mm_start,dd_start,yy_end,mm_end,dd_end))) 
        daysInMonths = [31,28,31,30,31,30,31,31,30,31,30,31]

        ''' Test for error conditions '''
        if yy_start != int(yy_start) or mm_start != int(mm_start) or dd_start != int(dd_start) \
           or yy_end != int(yy_end) or mm_end != int(mm_end) or dd_end != int(dd_end):
                raise(DateRangeError('Floats are not allowed!'))
        if dd_start<=0 or dd_end<=0 or mm_start<=0 or mm_end<=0 or yy_start<=0 or yy_end<=0:
            raise(DateRangeError('Negative numbers are not allowed'))
        if mm_start>12 or mm_end>12:
            raise(DateRangeError('Number of months in year on planet earth are bounded by 12'))
        if yy_start%4 == 0:
                daysInMonths[1] = 29
        if dd_start>daysInMonths[mm_start-1]:
            raise(DateRangeError('Number of days for start exceeded days in month'))
        if yy_end%4 == 0:
                daysInMonths[1] = 29
        if dd_end>daysInMonths[mm_end-1]:
            raise(DateRangeError('Number of days for end exceeded days in month. %d has %d days'%(mm_end,daysInMonths[mm_end-1])))
        
        ''' Safe to proceed now '''
        for yy in range(yy_start,yy_end+1):
            if yy==yy_start:
                mm_first = mm_start
            else:
                mm_first = 1
            # Check for leap year    
            if yy%4 == 0:
                daysInMonths[1] = 29
            else:
                daysInMonths[1] = 28
            # Check for end of the year
            if yy==yy_end:
                mm_last = mm_end+1 # Go only until the month specified
            else:
                mm_last = 12 + 1 # There are 12 months in a year.
            for mm in range(mm_first,mm_last):
                if mm==mm_start and yy==yy_start:
                    dd_first = dd_start
                else:
                    dd_first = 1
                for dd in range(dd_first,daysInMonths[mm-1]+1):
                    #print '%04d-%02d-%02d'%(yy,mm,dd)
                    self.DateList.append((yy,mm,dd))
                    if yy==yy_end and mm==mm_end and dd==dd_end:
                        break

class GppConfig(object):
    ''' We are going to try to load a few global variables. Normally, I wouldn't want to do this, 
    but in this case it is a little convenient. Remember, that to be able to populate this configuration
    data, we need to run gppConf which is at the root of gpplib.
    '''
    
    def __init__(self,configShelf = '../config.shelf'):
        ''' Load configuration parameters from the file created by gppConf.py which is at the root
        level of this distribution. Those files are normally stored to a file called config.shelf
        
        The keys that should be in this file are:
        myDataDir -> Location where the data is stored.
        romsDataDir -> Location where the roms data is stored.
        noisyGliderModelsDir -> Glider models which contain some noise in them.
        noiseLessGliderModelDir -> Glider models without noise in them.
        riskMapDir -> directory in which the RiskMap.shelf (created by GetRiskObsMaps.py is stored).
        riskPgmMapDir -> diretory in which the raw bathymetric and/or risk maps are stored.
        '''
        import shelve
        gppConf = shelve.open(configShelf,writeback=False)
        self.myDataDir = gppConf['myDataDir']
        self.romsDataDir = gppConf['romsDataDir'] 
        self.noisyGliderModelsDir = gppConf['noisyGliderModelsDir']
        self.noiseLessGliderModelDir = gppConf['noiseLessGliderModelDir']
        self.riskMapDir = gppConf['riskMapDir']
        self.riskPgmMapDir = gppConf['riskPgmMapDir']
        self.romsGpDataDir = gppConf['romsGpDataDir']
        gppConf.close()

import datetime
from datetime import timedelta

class RomsTimeConversion(object):
    ''' This class allows us to convert between the current time in UTC or even local time
        into the appropriate ROMS index. There are several ways to get the appropriate index.
        
    '''
    def __init__(self):
        pass
        
    def GetRomsIndexFromDateTime(self,yy,mm,dd,dt):
        ''' Find the ROMS index for the time specified in the datetime object being passed.
            You have to pass along the ROMS data file date, so that we have
            an offset to look into.
            
            Args:
                yy, mm, dd - (int): year, month, date of the ROMS data file
                dt (datetime): datetime object of the time you are looking to index for.
            Returns:
                roms_index (int) : index in the ROMS data file of the date specified, whose time
                                    most closely matches the passed in datetime dt.
            '''
        roms_dt = datetime.datetime(yy,mm,dd,0,0,0) - timedelta(hours=3)
        time_diff  = dt - roms_dt
        diff_in_hours = (time_diff.seconds/3600. + time_diff.days * 24.0)
        
        if (time_diff)>timedelta(hours=72.):
            raise(DateRangeError('You are probably using too old a ROMS data file.'))
        if (time_diff)<=timedelta(hours=-1.):
            raise(DateRangeError('Your roms data file is too futuristic for me!'))

        roms_index = int(diff_in_hours + 0.5)
                
        return roms_index
    
    
    def GetRomsIndexFromCurrentTime(self,yy,mm,dd):
        ''' Find the ROMS index for the time right now.
            You have to pass along the ROMS data file date, so that we have
            an offset to look into.
         '''
        return self.GetRomsIndexNhoursFromNow(yy,mm,dd,0)
                
    def GetRomsIndexNhoursFromNow(self,yy,mm,dd,nhrs):
        ''' Find the ROMS index for the time nhrs from now.
            You have to pass along the ROMS data file date, so that we have
            an offset to look into.
        '''
        dt = datetime.datetime.today() + timedelta(hours=nhrs)
        return self.GetRomsIndexFromDateTime(yy, mm, dd, dt)



    
import ftplib

class GliderFTP(object):
    ''' Transfer files to the dockserver for transmission to the glider.
    '''
    def __init__(self,dockServerDirectory='',dockserver_addr = '192.168.2.20',user='gpplibuser',passwd='gl1d3r'):
        self.f = ftplib.FTP(dockserver_addr)
        self.f.login(user,passwd)
        if dockServerDirectory!='':
            self.f.cwd('%s'%(dockServerDirectory))
        
    def deleteFile(self,filename=None):
        if filename != None:
            self.f.delete('%s'%(filename))

    def SaveFile(self,local_filename=None,remote_file_name=None):
        f2 = open(local_filename,'r')
        self.f.storbinary('STOR %s'%(remote_file_name), f2 )
        f2.close()
        
    def Close(self):
        self.f.quit()
        
    def GetSimpleDirList(self,dir_path='./'):
        dir_list = []
        try:
            dir_list.append(self.f.nlst(dir_path))
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":
                print 'Directory is empty.'
            else:
                raise
        return dir_list
        
    def DoesFileExist(self,remote_file_name = None):
        if self.f.size(remote_file_name)!=None:
            return True
        else:
            return False
        
    def ReadFile(self,local_filename=None,remote_filename=None):
        f2 = open(local_filename,'w')
        print 'Retrieving file using RETR %s and storing it as %s locally.'%(remote_filename,local_filename)
        self.f.retrbinary('RETR %s'%(remote_filename), f2.write , blocksize=8192 )
        f2.close()
        
        
import getpass, poplib, re, math, time # MySQLdb, string
import string, os, sys
from time import strftime,mktime,localtime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from calendar import timegm
import mimetypes


class GliderGMail(object):
    ''' We use this class to use a mail account to send/receive email.        
    '''
    def __init__(self,email_user,email_passwd,pop_server='pop.gmail.com',smtp_server='smtp.gmail.com'):
        self.POP_SERVER = pop_server
        self.SMTP_SERVER = smtp_server
        self.SMTP_PORT = 587
        self.EMAIL_USER = email_user
        self.EMAIL_PASS = email_passwd
    
    def mail(self,to, subject, text, attach=None ):
        msg = MIMEMultipart()
    
        msg['From'] = self.EMAIL_USER
        msg['To'] = to
        msg['Subject'] = subject
    
        msg.attach(MIMEText(text))
    
        if attach != None:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attach, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                   'attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)
    
        mailServer = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(self.EMAIL_USER, self.EMAIL_PASS)
        mailServer.sendmail(self.EMAIL_USER, to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        
    def getGpsDegree(self,webb_gps_str):
        p=webb_gps_str.find(".")
        d=float(webb_gps_str[0:p-2])
        return d+cmp(d,0)*float(webb_gps_str[p-2:len(webb_gps_str)])/60

    def checkMessages(self):
        M = poplib.POP3_SSL(self.POP_SERVER)
        M.user(self.EMAIL_USER)
        M.pass_(self.EMAIL_PASS)
        messagesInfo = M.list()[1]
        numMessages = len(messagesInfo)
    
        res = []
        leftovers = ""
    
        for i in range(numMessages):
            #print M.retr(i+1)
            g = {}
            for j in M.retr(i+1)[1]:
                j = str.replace(j,"=3D","=")
                j = leftovers+str.replace(j,"=A0"," ")
                if(len(j) > 0 and j[-1] == '='):
                    leftovers = j[0:-1]
                else:
                    #print j
                    leftovers = ""
                    m = re.match("[ ]*(GPS|DR)[ ]*(TooFar|Location|Invalid)[ :]+([0-9\\.\\-]*) N ([0-9\\.\\-]*) E.*",j)
                    if(m and m.group(1) == "GPS" and m.group(2) == "Location"):
                        #print m.groups()
                        g['lat'] = self.getGpsDegree(m.group(3))
                        g['lon'] = self.getGpsDegree(m.group(4))
                    m = re.match("[ ]*sensor:[ ]*([a-z_]+)(?:\\(([a-zA-Z]+)\\))*[ ]*=[ ]*([0-9\\.-]+)[ ]*(lat|lon|enum)*.*",j)
                    if(m):
                        #print m.groups()
                        if(m.group(1) == "m_battery"):
                            g['battery'] = float(m.group(3))
                        elif(m.group(1) == "m_vacuum"):
                            g['vacuum'] = float(m.group(3))
                    m = re.match("MissionName:([a-zA-Z0-9\\.\\-\\_]*) MissionNum:([a-zA-Z0-9\\.\\-\\_]*) \\(([0-9\\.]*)\\)",j)
                    if(m):
                        #print m.groups()
                        g['missionfile'] = m.group(1)
                        g['mission'] = m.group(2)
                        g['missionnum'] = m.group(3)
                    m = re.match("[ ]*Waypoint: \\(([0-9\\.\\-]*),([0-9\\.\\-]*)\\) Range: ([0-9\\.]*)([a-zA-Z]*), Bearing: ([0-9\\.\\-]*)deg, Age: (.*)",j)
                    if(m):
                        #print m.groups()
                        g['wp_lat'] = self.getGpsDegree(m.group(1))
                        g['wp_lon'] = self.getGpsDegree(m.group(2))
                        g['wp_range'] = float(m.group(3))
                        g['wp_bearing'] = float(m.group(5))
                        #x = datetime(*time.strptime(m.group(6),"%H:%Mh:m")[:6])
                        g['wp_time'] = 0 #x.hour*60+x.minute
                    m = re.match("[ ]*Because:([a-zA-Z0-9 ]*) \\[(.*)\\]",j)
                    if(m):
                        #print m.groups()
                        g['because'] = m.group(1)
                    m = re.match("Vehicle Name: ([a-zA-Z\\-]*)",j)
                    if(m):
                        #print m.groups()
                        g['name'] = m.group(1)
                    m = re.match("[ ]*Curr Time: (.*) MT:[ ]*([0-9\\.]*)",j)
                    if(m):
                        #print m.groups()
                        g['time'] = time.strptime(m.group(1),"%a %b %d %H:%M:%S %Y")
    
            #print g
            res.append(g)
            M.dele(i+1)
    
        M.quit()
        return res
    

#import MySQLdb
    
class GliderSQL():
    ''' Very basic class to retrieve information from the glider data-base.
    ''' 
    pass



''' Image saving routines .
  import pylab
    import matplotlib.pyplot as plt

    fig = plt.figure()
    fig.patch.set_alpha(0)
    ax = fig.add_axes((0,0,1,1),frameon=False,aspect='equal',xticks=[],yticks=[])
    ax.patch.set_alpha(0)

    ax.scatter(data[:,1],data[:,0],c=data[:,2],linewidth=0)
    sz = 8
    # b are the lat lon boundaries, calculated by me, it's probably
better to use something like a = ax.viewLim, and then aspect =
abs((a.xmax-a.xmin)/(a.ymax-a.ymin))
    aspect = (b[3]-b[2])/(b[1]-b[0])
    fig.set_size_inches(sz*aspect,sz)

    import tempfile
    tmpfile = tempfile.NamedTemporaryFile(suffix='.png')

    pylab.savefig(tmpfile.name,pad_inches=0)


'''
import pylab
import matplotlib.pyplot as plt

def SaveFigureAsImage(fileName,fig=None,**kwargs):
    ''' Save a Matplotlib figure as an image without borders or frames.
       Args:
            fileName (str): String that ends in .png etc.
    
            fig (Matplotlib figure instance): figure you want to save as the image
        Keyword Args:
            orig_size (tuple): width, height of the original image used to maintain 
            aspect ratio.
    '''
    fig.patch.set_alpha(0)
    if kwargs.has_key('orig_size'): # Aspect ratio scaling if required
        w,h = kwargs['orig_size']
        fig_size = fig.get_size_inches()
        w2,h2 = fig_size[0],fig_size[1]
        fig.set_size_inches([(w2/w)*w,(w2/w)*h])
        fig.set_dpi((w2/w)*fig.get_dpi())
    a=fig.gca()
    a.set_frame_on(False)
    a.set_xticks([]); a.set_yticks([])
    plt.axis('off')
    plt.xlim(0,h); plt.ylim(w,0)
    fig.savefig(fileName, transparent=True, bbox_inches='tight', \
        pad_inches=0)

'''
def SaveFigureAsImage(fileName,fig=None,**kwargs):
    import pylab
    import matplotlib.pyplot as plt
    
    fig.patch.set_alpha(0)
    w,h = None,None
    if kwargs.has_key('orig_size'):
        w,h = kwargs['orig_size']
    a=fig.gca()
    a.set_frame_on(False)
    a.set_xticks([]); a.set_yticks([])
    fig.patch.set_alpha(0)
    #from matplotlib import pyplot as plt
    plt.axis('off')
    plt.xlim(0,h); plt.ylim(w,0)
    if w!=None and h!=None:
        fig_size = fig.get_size_inches()
        w2,h2 = fig_size[0],fig_size[1]
        fig.set_size_inches([(w2/w)*w,(w2/w)*h])
        fig.set_dpi((w2/w)*fig.get_dpi())
    fig.savefig('%s'%(fileName), transparent=True, bbox_inches='tight', pad_inches=0)
    #fig.savefig(fileName,pad_inches=0)
'''
