#!/usr/bin/python
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
# v3.1 -- now writes to /opt/log/server4
#         generates data over last 7 days instead of "real time"
#
# v3.2 -- removed arbitrary limit on number of events
#
# v4.0 -- generates data in a time-based pattern
#         generates data over last 30 days

# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 3, 3, 4, 3, 3, 2, 1.5, 1.3, 1.2, 1.1, 1, 1.1, 1.2, 1.4, 2, 3, 3, 3, 2, 3, 2, 1.6, 2, 4 ]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central

# function to calculate "wait time" between events
def time_to_wait(eventTime):
    hourIndex=eventTime.hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    return datetime.timedelta(seconds=(random.randint(3000,6001) * timeFactor))

def short_wait():
    return datetime.timedelta(seconds=random.randint(10,23))

def generate_data_from_file(outfile, stoptime, curTime):
    inputlog = open(sys.path[0] + sep + "data" + sep + "cisco_ironport_mail.input","r")
    lastTimeStamp=""
    for inputline in inputlog:
        if inputline.strip() == "":      #skip blank lines
            continue
        if curTime > stoptime:
            #we have generated enough data, quit
            break
        inputTimeStamp=inputline[0:22]
        if inputTimeStamp != lastTimeStamp:
            curTime = curTime + time_to_wait(curTime)
            if curTime > stoptime:
                break
        else:
            curTime = curTime + short_wait()
        currentTime = curTime.strftime('%a %b %d %H:%M:%S %Y')
        new_line =  currentTime + inputline[24:].replace('-',' ')
        outputlog  = open(outfile,"a")
        outputlog.writelines(new_line)
        outputlog.flush()
        lastTimeStamp=inputTimeStamp
    inputlog.close()
    return curTime
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

#compute start and stop times for data generation
stopTime = datetime.datetime.today()
curTime = stopTime - datetime.timedelta(days=30) # set the "current" time to the start

while curTime < stopTime:
    curTime = generate_data_from_file(outputFileName, stopTime, curTime)
