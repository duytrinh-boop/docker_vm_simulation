#!/usr/bin/python
from optparse import OptionParser
import commands
import os
import sys
from pwd import getpwnam
from platform import system

# Removes Splunk users named student1, student2, etc

#  dependencies
#  - must be run as the Splunk account (splunkt)
#  - if $SPLUNK_HOME is not defined, the script will use the splunk user's directory as follows $SPLUNK_HOME=~splunkt/splunk

# *** Questions? lguinn@splunk.com
#
# *** Copyright Splunk, Inc. 2010
#
# v2.0 - now runs on both Windows and *NIX
#
# v3.0 - no longer accepts -A or --auth parameters, as this displayed the Splunk admin password on the command line
#        causing a security problem

def os_exec(cmd, stop_on_error):
	print cmd
	(cmd_status, cmd_output) = commands.getstatusoutput(cmd)
	print cmd_output, "\n"
	if cmd_status != 0 and stop_on_error:
		print "Command failed: ", cmd
		print "Status: ", cmd_status
		sys.exit(str(cmd_status))
	return(cmd_output)

# determine platform
if system() == 'Windows':
	sep = '\\'
else:
	sep = '/'

usage = "usage: %prog [options]"
parser = OptionParser(usage)
parser.add_option("-S", "--students", dest="numStudents",
					action="store", type="int", default="16",
					help="number of student accounts to create")
parser.add_option("-P", "--password", dest="password",
					action="store", type="string", default="splunk",
					help="the base for creating the student passwords")
parser.add_option("-I", "--install", dest="account",
					action="store", type="string", default="splunkt",
					help="the Linux username used to install Splunk")

# read in the defaults for the arguments from the defaults file
defaultFile = os.path.dirname(os.path.abspath(sys.argv[0])) + sep + 'default'
if os.access(defaultFile,os.R_OK):
	dFile = open(defaultFile,'r')
	for inputLine in dFile:
		pos=inputLine.find('=')
		if pos > 0:
			optionName = inputLine[:pos].strip()
			optionValue = inputLine[pos+1:].strip()
			if optionName == 'account':
				parser.set_defaults(account=optionValue)
			if optionName == 'students':
				parser.set_defaults(numStudents=int(optionValue))
			if optionName == 'password':
				parser.set_defaults(password=optionValue)

(options, args) = parser.parse_args()

numStudents = int(options.numStudents)
if numStudents < 1 or numStudents > 50:
	print "Error: you must supply the --students parameter with an integer between 1 and 50"
	sys.exit("Exiting due to command line error.")

accountName = str(options.account)
passwordBase = str(options.password)

try:
	splunkHome=""
	splunkHome = os.environ["SPLUNK_HOME"]
except:
	if splunkHome == "":
		if system() == 'Windows':
			splunkHome = "C:\\Program Files\\splunk"
		else:
			splunkHome = "/opt/splunk"
		print "$SPLUNK_HOME is not defined. Using ", splunkHome

# delete the student accounts
for n in range(numStudents):
	student="student" + str(n+1)
	cmdLine = splunkHome + "/bin/splunk remove user -username " + student
	os_exec(cmdLine, False)
