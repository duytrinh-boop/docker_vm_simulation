#!/usr/bin/python
from optparse import OptionParser
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
# v3.1 -- now generates data for 8 hours

# v4.0 -- Now takes a command line setting for how long to run, if it exists, and overrides the
#       runTime parameter
#       Pause between events is now based on hour of the day

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

#email_addr = [ "grumpy@demo.com", "grumpy@demo.com", "grumpy@demo.com", "happy@demo.com", "sleepy@demo.com", "bashful@demo.com",
#              "sneezy@demo.com", "dopey@demo.com", "doc@demo.com", "queasy@demo.com", "surly@demo.com", "edgy@demo.com",
#              "dizzy@demo.com", "peevish@demo.com", "remorseful@demo.com", "grumpy@demo.com", "grumpy@demo.com", "grumpy@demo.com",
#              "happy@demo.com", "sleepy@demo.com", "bashful@demo.com", "sneezy@demo.com", "dopey@demo.com", "doc@demo.com",
#              "queasy@demo.com", "surly@demo.com", "edgy@demo.com", "dizzy@demo.com", "peevish@demo.com", "remorseful@demo.com",
#              "tipsy@demo.com", "hammer@splunk.com", "madonna@splunk.com", "prince@splunk.com", "britany@splunk.com",
#              "cher@splunk.com", "beyonce@splunk.com", "hammer@splunk.com", "bieber@splunk.com"]
# only change username when hostname changes, so track last hostname
last_hostname=""
last_email_addr=""
# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 2, 3, 3, 4, 4, 2, 2, 3, 1.7, 1.5, 1.3, 1.4, 1.2, 1.1, 1, 1, 1.05, 1, 1.2, 1.4, 1.5, 1.7, 2, 2]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central

# function to sleep between events
def wait_time():
    hourIndex=datetime.datetime.today().hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    time.sleep(random.randint(13,80) * timeFactor)

def generate_data_from_input(outfile, stoptime):
    regexpr = re.compile('GET http://(?P<url>.*?)/')
    last_hostname=""
    last_email_addr=email_addr[0]
    inputLog = open(sys.path[0] + sep + "data" + sep + "cisco_ironport_web.input","r")
    curtime = time.time()
    for inputline in inputLog:
        if stoptime > 0 and curtime > stoptime:
            #we have generated enough data, quit
            break
        wait_time()
        curtime = time.time()
        ipAddr = random.choice(targetIP)
        # add the current time to the front of the line
        # skip the first thing on the inputline and then add the remainder
        # of the line, replacing the ip.address
        fix_line = str(int(curtime)) + inputline[inputline.find('.'):].replace('###C_IP###',ipAddr)

        hostname=regexpr.search(fix_line).group('url')
        if hostname!=last_hostname:
            last_email_addr=random.choice(email_addr)
            last_hostname = hostname
        new_line = fix_line.replace('###EMAIL###', last_email_addr)

        outputlog  = open(outfile,"a")
        outputlog.writelines(new_line)
        outputlog.close()
    inputLog.close()
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

# Get argument (hours to run) if supplied
usage = "usage: %prog"
parser = OptionParser(usage)
(options, args) = parser.parse_args()

if len(args) > 0:
    if len(args[0]) > 0 and args[0].isdigit:
        hoursToRun = int(args[0])
    else:
        hoursToRun = 0
else:
    hoursToRun = 0

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

#compute how long to generate data in seconds
curtime = time.time()
if hoursToRun > 0:
    stoptime = curtime + ( hoursToRun * 60 * 60)
else:
    stoptime = 0            # stoptime = 0 means never stop

while (stoptime == 0 or curtime < stoptime):
    generate_data_from_input(outputFileName, stoptime)
    curtime = time.time()
