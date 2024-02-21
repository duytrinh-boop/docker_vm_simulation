#!/usr/bin/python
from sharedFunctions import *
from optparse import OptionParser
import commands
import os
import sys
import time
from stat import *
from platform import system

# Runs the data-generating scripts to complete the class setup
# This script can be run at any time -- before during or after
# the other course setup scripts
# Performs the following steps
#  1. runs each script in the data_scripts subdirectory

#  dependencies
#  - must be run as root
#  - cannot run on Windows due to differences in process launch

# *** Questions? lguinn@splunk.com
#
# *** Copyright Splunk, Inc. 2010
#
# v2.0 Runs all the scripts in the local scripts directory
#      then all the scripts in the shared scripts directory

# read in the defaults files to get the shared directory name
defaults = process_defaults_file(os.path.dirname(os.path.abspath(sys.argv[0])))
if "shared" in defaults:
    sharedDir=defaults["shared"]

usage = "usage: %prog"
parser = OptionParser(usage)
(options, args) = parser.parse_args()

if len(args) > 0:
    hoursToRun = " " + args[0]
    print "Generating data for " + hoursToRun + " hours"
else:
    hoursToRun = ""
    print "Generating data forever"
    time.sleep(1)

# run the data generating scripts
scriptPath = os.path.dirname(os.path.abspath(sys.argv[0]))

scriptPathData = scriptPath + "/data_scripts"
print "scriptPathData: ", scriptPathData
scriptList = os.listdir(scriptPathData)
scriptList.sort()
print "scripts Found: ", scriptList
for script in scriptList:
    cmdLine=scriptPathData + "/" + script
    print os.access(cmdLine,os.X_OK)
    print S_ISDIR(os.stat(cmdLine)[ST_MODE])
    if os.access(cmdLine,os.X_OK) and not S_ISDIR(os.stat(cmdLine)[ST_MODE]):
        print "Executing: ", cmdLine
        p = os.spawnl(os.P_NOWAIT, cmdLine, script, hoursToRun)
        time.sleep(2)

time.sleep(2)

# run the SHARED data generating scripts
scriptPathData = sharedDir + "/" + "data_scripts"
scriptList = os.listdir(scriptPathData)
scriptList.sort()
for script in scriptList:
    cmdLine=scriptPathData + "/" + script
    if os.access(cmdLine,os.X_OK) and not S_ISDIR(os.stat(cmdLine)[ST_MODE]):
        print "Executing: ", cmdLine
        p = os.spawnl(os.P_NOWAIT, cmdLine, script, hoursToRun)
        time.sleep(5)

print "Data Generation Script complete"
if hoursToRun == "":
    print "Data generation will continue indefinitely"
else:
    print "Data generation will continue for " + hoursToRun + " hours"
