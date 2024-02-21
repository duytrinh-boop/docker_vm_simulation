#!/usr/bin/python
import random
import datetime
import time
import csv
import os
import sys
import re
from platform import system

# Makes a set of faux cisco mail log files for the Splunk Search & Report training
# *** This script appends to a log file in /opt/cisco
#
# *** Questions? lguinn@splunk.com
#
# *** Copyright Splunk, Inc. 2010
#
# v1.0 -- originally developed by Simon Shelston for online store app
#
# v2.0 -- updated to work for classroom servers
#
# v3.0 -- now works on Windows and *NIX
#         and varies the email addresses with dwarves++
#
# v3.1 -- now writes to /opt/log/server4 to look more realistic
#         and fakes data over the past 7 days
#
# v3.2 -- removed arbitrary limit on number of events generated
#
# v4.0 -- generates data in a time-based pattern
#         generates data over last 30 days

def import_user_csv(user_csv):
        users = []
        csv_file = open(user_csv,'rU')
        csv_users = csv.DictReader(csv_file, dialect='excel', delimiter=',')
        for row in csv_users:
                users.append(row)
        return users

user_csv = "/opt/setup/shared/data_scripts/sample/ButtercupGames_Employees.csv"

users = import_user_csv(user_csv)

email_addr = []
for user in users:
	email_addr.append(user['EMAIL'])
	
# only change username when hostname changes, so track last hostname
last_hostname=""
last_email_addr=""
# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 2, 3, 3, 4, 4, 2, 2, 3, 1.7, 1.5, 1.3, 1.4, 1.2, 1.1, 1, 1, 1.05, 1, 1.2, 1.4, 1.5, 1.7, 2, 2]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central

# function to calculate "wait time" between events
def time_to_wait(eventTime):
    hourIndex=eventTime.hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    return datetime.timedelta(seconds=(random.randint(120,801) * timeFactor))

def generate_data_from_file(outfile, stoptime, curTime):
    last_hostname=""
    last_email_addr=email_addr[0]
    regexpr = re.compile('GET http://(?P<url>.*?)/')
    inputLog = open(sys.path[0] + sep + "data" + sep + "cisco_ironport_web.input","r")
    for inputline in inputLog:
        if inputline.strip() == "":      #skip blank lines
            continue
        curTime=curTime + time_to_wait(curTime)
        if curTime > stoptime:
            break
        ipAddr = random.choice(targetIP)
        # add the current time to the front of the line as an epoch time
        # skip the first thing on the inputline and then add the remainder
        # of the line, replacing the ip.address
        fix_line = str(int(time.mktime(curTime.timetuple()))) + inputline[inputline.find('.'):].replace('###C_IP###',ipAddr)

        hostname=regexpr.search(fix_line).group('url')
        if hostname!=last_hostname:
            last_email_addr=random.choice(email_addr)
            last_hostname = hostname
        new_line = fix_line.replace('###EMAIL###', last_email_addr)

        outputlog = open(outfile,"a")
        outputlog.writelines(new_line)
        outputlog.close()
    inputLog.close()
    return curTime
#-----------------------------------------------------------------------

#identify path separator for platform
if system() == 'Windows':
    sep = '\\'
    outputFileName = 'C:\\opt\\log\\cisco_router1\\cisco_ironport_web.log'
else:
    sep = '/'
    outputFileName = "/opt/log/cisco_router1/cisco_ironport_web.log"

# read in the defaults file
defaultFile = os.path.dirname(os.path.abspath(sys.argv[0])) + sep + 'default'
if os.access(defaultFile,os.R_OK):
    dFile = open(defaultFile,'r')
    for inputLine in dFile:
        pos=inputLine.find('=')
        if pos > 0:
            optionName = inputLine[:pos].strip()
            optionValue = inputLine[pos+1:].strip()
            if optionName == 'ClassTZoffset':
                class_TZ=int(optionValue)
            if optionName == 'ServerTZoffset':
                server_TZ=int(optionValue)

#create directories if they don't exist
dirname = os.path.dirname(outputFileName)
if os.path.exists(dirname):
    if os.path.exists(outputFileName):
        print "Writing to " + outputFileName
    else:
        print "Creating " +  outputFileName  #it will get created when data is written
else:
    print "Creating " + dirname
    os.makedirs(dirname)

inputTarget = open(sys.path[0] + sep + "data" + sep + "target.input", "r")
targetIP = []
# read all targets into an array
for ip in inputTarget:
    targetIP = targetIP + [ ip.strip() ]

#compute start and stop times for data generation
stopTime = datetime.datetime.today()
curTime = stopTime - datetime.timedelta(days=30) # set the "current" time to the start

while curTime < stopTime:
    curTime = generate_data_from_file(outputFileName, stopTime, curTime)
