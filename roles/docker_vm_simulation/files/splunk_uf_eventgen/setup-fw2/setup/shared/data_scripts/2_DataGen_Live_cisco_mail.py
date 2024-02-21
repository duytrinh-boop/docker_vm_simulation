#!/usr/bin/python
from optparse import OptionParser
import random
import datetime
import time
import os
import sys
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
# v3.0 -- runs on Windows and *NIX
#
# v3.1 -- now runs for 8 hours

# v4.0 -- Now takes a command line setting for how long to run, if it exists, and overrides the
#       runTime parameter
#       Pause between events is now based on hour of the day

# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 3, 3, 4, 3, 3, 2, 1.5, 1.3, 1.2, 1.1, 1.1, 1.1, 1.2, 1.4, 2, 3, 3, 3, 2, 3, 2, 1.6, 2, 4 ]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central

# function to sleep between events
def wait_time():
    hourIndex=datetime.datetime.today().hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    time.sleep(random.randint(90,132) * timeFactor)

def short_wait(low,high):
    time.sleep(random.randint(low,high))

def generate_data_from_file(outfile, stoptime):
    inputlog = open(sys.path[0] + sep + "data" + sep + "cisco_ironport_mail.input","r")
    lastTimeStamp=""
    curtime = time.time()
    for inputline in inputlog:
        if stoptime > 0 and curtime > stoptime:
         #we have generated enough data, quit
             break
        inputTimeStamp=inputline[0:22]
        if inputTimeStamp != lastTimeStamp:
            wait_time()
        else:
            short_wait(5,14)
        now = datetime.datetime.today()
        currentTime = now.strftime('%a %b %d %H:%M:%S %Y')
        new_line =  currentTime + inputline[24:].replace('-',' ')
        outputlog  = open(outfile,"a")
        outputlog.writelines(new_line)
        outputlog.close()
        lastTimeStamp=inputTimeStamp
        curtime = time.time()
    inputlog.close()
#-----------------------------------------------------------------------

#identify platform
if system () == 'Windows':
    sep = '\\'
    outputFileName = "C:\\opt\\log\\cisco_router1\\cisco_ironport_mail.log"
else:
    sep = '/'
    outputFileName = "/opt/log/cisco_router1/cisco_ironport_mail.log"

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

#compute how long to generate data in seconds
curtime = time.time()
if hoursToRun > 0:
    stoptime = curtime + ( hoursToRun * 60 * 60)
else:
    stoptime = 0            # stoptime = 0 means never stop

while (stoptime == 0 or curtime < stoptime):
    generate_data_from_file(outputFileName, stoptime)
    curtime = time.time()
