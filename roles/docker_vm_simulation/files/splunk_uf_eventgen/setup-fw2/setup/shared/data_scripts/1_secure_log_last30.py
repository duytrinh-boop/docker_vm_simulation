#!/usr/bin/python
import random
import datetime
import time
import os
import sys
from platform import system

# Makes a faux linux_secure file that is used for the Splunk Using 4.x training
# *** Script wants to create the logfile in the directory /opt/secure/www1 through www5
# *** Questions? lguinn@splunk.com or drew@splunk.com
#
# *** Copyright Splunk, Inc. 2009, 2010
#
# v2.0 -- now generates events in a more definite "attack" pattern AND
#         runs for approximately 4 hours (so it will still be generating
#         events during the real-time and alerts labs)
# v3.0 -- now runs on Windows and Linux
#         creates directories if they don't already exist
# v3.1 -- now writes to /opt/log instead of /opt/secure, with new server names
# v3.2 -- this script was cloned from the secure_log_gen script
#         THIS VERSION generates data over the last 7 days and then
#         terminates; the other version generates data appropriate for
#         real time searches
#
# v3.3 -- removed arbitrary event limit
#
# v3.4 -- inputs lists of ip addresses, known users and unknown users from files instead of hard coded
#
# v4.0 -- generates data in a time-based pattern
#         generates data over last 30 days
#
# v4.1 -- generates new pattern data
#	imports users and ips from secLogDatagen.input

host_ary = [ "cisco_router1" ]
Winfile_ary = [ "C:\\opt\\log\\cisco_router1\\secure.log", "C:\\opt\\log\\mailsv1\\secure.log"]
file_ary = [ "/opt/log/cisco_router1/secure.log", "/opt/log/mailsv1/secure.log"]
known_usr_ary = []
unknown_usr_ary = []
ip_ary = []
# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 2, 3, 3, 2, 2, 2, 2, 1.5, 2, 1, 1.1, 1, .96, 1.1, 1.3, 1.2, 1.1, 1, 2, 1.4, 1.5, 1.3, 1, 1]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central
###------------------------------------------------------------------$
###New securelog event patterns

users = [{'NAME':"myuan", 'IP':"10.1.10.172", 'WEIGHT':1}, 
	{'NAME':"nsharpe", 'IP':"10.2.10.163", 'WEIGHT':3},
	{'NAME':"djohnson", 'IP':"10.3.10.46", 'WEIGHT':6}]

def user_picker(users):
        list = []
        for user in users:
                for i in range(int(float(user['WEIGHT']))):
                        list.append(user)
        return random.choice(list)

def randomPicks():
        sshd = random.randint(1000,99999)
        port = random.randint(1000,9999)
        pfindex = random.randint(0,9)
        if pfindex < 9:
                pfindex = 'Accepted'
        else:
                pfindex = 'Failed'
        return (sshd, port, pfindex)

def pickPattern(host, user, currtime):
	timestamp = currtime.strftime("%a %b %d %Y %H:%M:%S")
        (sshd, port, pfindex) = randomPicks()
        pick = random.randint(0,99)
        if pick < 30:   ##### Pattern 1
                fline = "%s %s sshd[%s]: %s password for %s from %s port %s ssh2\n"
                return fline % (timestamp, host, str(sshd), pfindex, user['NAME'], user['IP'], str(port))

        if pick < 50:   ##### Pattern 2
                fline = "%s %s sshd[%s]: pam_unix(sshd:session): session opened for user %s by (uid=0)\n"
                return fline % (timestamp, host, str(sshd), user['NAME'])

        if pick < 65:   ##### Pattern 3
                fline = "%s %s sshd[%s]: pam_unix(sshd:session): session closed for user %s by (uid=0)\n"
                return fline % (timestamp, host, str(sshd), user['NAME'])

        if pick < 75:   ##### Pattern 4
                fline = "%s %s sshd[%s]: Server listening on :: port 22.\n"
                return fline % (timestamp, host, str(sshd))

        if pick < 83:   ##### Pattern 5
                fline = "%s %s sshd[%s]: Received disconnect from %s 11: disconnected by user\n"
                return fline % (timestamp, host, str(sshd), user['IP'])

        if pick < 89:   ##### Pattern 6
                fline = "%s %s su: pam_unix(su:session): session closed for user root\n"
                return fline % (timestamp, host)

	if pick < 94:   ##### Pattern 7
                fline = "%s %s su: pam_unix(su:session): session opened for user root by %s(uid=0)\n"
                return fline % (timestamp, host, user['NAME'])

        if pick < 99:   ##### Pattern 8
                fline = "%s %s sudo: %s ;  TTY=pts/0 ; PWD=/home/%s ; USER=root ; COMMAND=/bin/su\n"
                return fline % (timestamp, host, user['NAME'], user['NAME'])

def pattern_9(source):
        (timeStamp, user, sshd, port, pfindex) = randomPicks()
        fline = "%s %s passwd: pam_unix(passwd:chauthtok): password changed for %s\n"
        return fline % (timestamp, source, user['name'])

###-------------------------------------------------------------------###


# function to calculate "wait time" between events
def time_to_wait(eventTime, low, high):
    hourIndex=eventTime.hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    return datetime.timedelta(seconds=(random.randint(low,high) * timeFactor))
#-----------------------------------------------------------------------
#determine plaform
if system == 'Windows':
    file_ary = Winfile_ary
    sep = '\\'
else:
    sep = '/'

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
for file in file_ary:
    dirname = os.path.dirname(file)
    if os.path.exists(dirname):
        if os.path.exists(file):
            print "Writing to " + file
        else:
            print "Creating " + file  #it will get created when data is written
    else:
        print "Creating " + dirname
        os.makedirs(dirname)

###Weighted list of users and ips for new patterns
#get weighted list of ip addresses
ip_ary = []
inputTarget = open(sys.path[0] + sep + "data" + sep + "target.input", "r")
for ip in inputTarget:
    ip_ary = ip_ary + [ ip.strip() ]
inputTarget.close()

#get weighted list of known users
inputUsers = open(sys.path[0] + sep + "data" + sep + "KnownUsers.input", "r")
known_usr_ary = []
for user in inputUsers:
    known_usr_ary = known_usr_ary + [ user.strip() ]
inputUsers.close()

#get weighted list of unknown user
inputUsers = open(sys.path[0] + sep + "data" + sep + "UnknownUsers.input", "r")
unknown_usr_ary = []
for user in inputUsers:
    unknown_usr_ary = unknown_usr_ary + [ user.strip() ]
inputUsers.close()

#compute start and stop times for data generation
stopTime = datetime.datetime.today()
curTime = stopTime - datetime.timedelta(days=30) # set the "current" time to the start

while curTime < stopTime:
    #pick an ip address to use for attack, a host to attack
    #and how many times it will attack
    hst_num = random.randint(0, len(host_ary)-1)
    ip_user=random.choice(ip_ary)
    nohits=random.randint(1,20)
    

    onceInAwhile = random.randint(0,99)
    if onceInAwhile < 10:
        #add a couple of hours and start again
        curTime = curTime + time_to_wait(curTime,5000,9000)
    if curTime > stopTime:
        break
    
    i = 0
    for hit in range(nohits):
###---------------------------------------------------------------------------------------###
###Run a new pattern for every 3 of the old
 	
        if random.randint(0,2)==2:
		user = user_picker(users)
                logline = pickPattern(host_ary[hst_num], user, curTime)
                if logline != None:
                        output_file = open(file_ary[hst_num], 'a')
                        output_file.write(logline)
                        output_file.close()
###---------------------------------------------------------------------------------------###

        #generate a single login attempt
        pid=random.randint(1000,6000)
        port=random.randint(1025,5000)
        timestamp = curTime.strftime("%a %b %d %Y %H:%M:%S")

        #choose a known user about 1/3 of the time
        cointoss=random.randint(0,10)
        if cointoss < 3:
            known_user=random.choice(known_usr_ary)
            fline="%s %s sshd[%s]: Failed password for %s from %s port %s ssh2\n"
            newline=fline % (timestamp, host_ary[hst_num], pid, known_user, ip_user, port)
        else:
            unknown_user=random.choice(unknown_usr_ary)
            fline="%s %s sshd[%s]: Failed password for invalid user %s from %s port %s ssh2\n"
            newline=fline % (timestamp, host_ary[hst_num], pid, unknown_user, ip_user, port)

        #write out the login attempt
        output_file = open(file_ary[hst_num], 'a')
        output_file.write(newline)
        output_file.close()
        #wait a short time before generating next attempt by same ip
        curTime = curTime + time_to_wait(curTime,3,26)
        if curTime > stopTime:
            break

    #update the current time and loop for next attack
    curTime = curTime + time_to_wait(curTime,600,901)
