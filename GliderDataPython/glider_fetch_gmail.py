import getpass, poplib, re, math, time, MySQLdb, string
from datetime import datetime
from time import strftime,mktime,localtime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from calendar import timegm

POP_SERVER = 'pop.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'usc.cinaps@gmail.com'
EMAIL_PASS = 'r0b0t.icx'

class GliderSurfacing:
	pass

def mail(to, subject, text, attach=None):
	msg = MIMEMultipart()

	msg['From'] = EMAIL_USER
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

	mailServer = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(EMAIL_USER, EMAIL_PASS)
	mailServer.sendmail(EMAIL_USER, to, msg.as_string())
	# Should be mailServer.quit(), but that crashes...
	mailServer.close()


def gpsBla(bla):
	p=bla.find(".")
	d=float(bla[0:p-2])
	return d+cmp(d,0)*float(bla[p-2:len(bla)])/60

def checkMessages():
	M = poplib.POP3_SSL(POP_SERVER)
	M.user(EMAIL_USER)
	M.pass_(EMAIL_PASS)
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
					g['lat'] = gpsBla(m.group(3))
					g['lon'] = gpsBla(m.group(4))
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
					g['wp_lat'] = gpsBla(m.group(1))
					g['wp_lon'] = gpsBla(m.group(2))
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

msg = checkMessages()
#
# CREATE TABLE `glider`.`surfacings2` (
#`glider_id` INT NOT NULL ,
#`mission_run_id` INT NOT NULL ,
#`mission_surface_id` INT NOT NULL ,
#`time` DATETIME NOT NULL ,
#`time_latest` DATETIME NOT NULL ,
#`lat` DOUBLE NOT NULL ,
#`lon` DOUBLE NOT NULL ,
#`gumstix_run_id` INT NOT NULL ,
#`bs_id` INT NOT NULL ,
#`because` CHAR( 32 ) NOT NULL ,
#`battery` DOUBLE NOT NULL ,
#`vacuum` DOUBLE NOT NULL ,
#`leakdetect` DOUBLE NOT NULL ,
#`mission_name` CHAR( 16 ) NOT NULL ,
#`mission_str` CHAR( 32 ) NOT NULL ,
#`wp_lat` DOUBLE NOT NULL ,
#`wp_lon` DOUBLE NOT NULL ,
#`wp_range` DOUBLE NOT NULL ,
#`wp_bearing` FLOAT NOT NULL ,
#`wp_time` INT NOT NULL ,
#PRIMARY KEY ( `glider_id` , `mission_run_id` , `mission_surface_id` )
#) ENGINE = MYISAM 


if len(msg) > 0:
	conn = MySQLdb.connect(host="localhost",user="glider",passwd="gl1d3r",db="glider")
	c=conn.cursor()
	for m in msg:
		print m
		if not m.has_key('missionnum'):
			continue
		mission = string.split(m['missionnum'],'.')
		try:
			sss = ",".join(['USC-'+m['name'],str(timegm(m['time'])),str(m['lon']),str(m['lat'])])
			mail('glidertrack@mbari.org',sss,sss)
			mail('jnaneshwar.das@gmail.com',sss,sss)
		except Exception, e:
			print "Error mailing report"

		try:
			c.execute(
			"""INSERT INTO surfacings2 (glider_id,mission_run_id,mission_surface_id,time,time_latest,lat,lon,because,battery,vacuum,mission_name,mission_str,wp_lat,wp_lon,wp_range,wp_bearing,wp_time)  VALUES ((select glider_id from gliders where lower(name)=lower(%s)),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(m['name'],int(mission[0]),int(mission[1]),
			strftime("%Y-%m-%d %H:%M:%S",m['time']),strftime("%Y-%m-%d %H:%M:%S",m['time']),m['lat'],m['lon'],m['because'],m['battery'],m['vacuum'],m['missionfile'],m['mission'],
			m.get('wp_lat',0),m.get('wp_lon',0),m.get('wp_range',0),m.get('wp_bearing',0),m.get('wp_time',0)))
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			print m
else:
	print 'No new messages'
