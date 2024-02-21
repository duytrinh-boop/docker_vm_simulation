#!/usr/bin/python

# IMPORTANT - ONLY RUN THIS WHEN YOU ARE CREATING A NEW SETUP!
# a script that copies all the config files into their respective
# directories; for the Using and Searching + Reporting classes

#  dependencies

#  - runs only on Linux platforms
#  - must be run as root
#  - assumes that files are in the config directory rooted under etc
#     and that the destination is the etc directory of the splunk instance

# *** Questions? lguinn@splunk.com
#
# *** Copyright Splunk, Inc. 2010
#
# v2.0  Now deals with both shared and unique config files
#
#################################################################
#  The following variables MUST be set correctly for this script
#  to work!!

username="splunkt"           #username where splunk is installed
groupname="splunkt"          #groupname where splunk is installed

#where to find the conf files to copy to the installation
confFiles = [ "$SHARED$/conf_files", "./conf_files" ]

################################################################
from sharedFunctions import *
import os
import commands
import string

# read in the defaults for the arguments from the defaults file
defaults = process_defaults_file(os.path.dirname(os.path.abspath(sys.argv[0])))
if "shared" in defaults:
    sharedDir = defaults["shared"]
else:
    print "Error: Missing shared entry in default file "
    sys.exit("...Exiting.")

if "license" in defaults:
    licenseFile = defaults["license"]
else:
    print "Error: Missing license entry in default file "
    sys.exit("...Exiting.")

dest = "/home/" + username + "/splunk/"

for confDir in confFiles:
    confDir = confDir.replace("$SHARED$",sharedDir,1)
    copy_files(confDir, dest)

# copy in the license
os_exec("cp " + licenseFile + " ~" + username + "/splunk/etc/licenses/enterprise/", False)

# try to chown the files
os_exec("chown -R " + username + ":" + groupname + " ~" + username, False)
