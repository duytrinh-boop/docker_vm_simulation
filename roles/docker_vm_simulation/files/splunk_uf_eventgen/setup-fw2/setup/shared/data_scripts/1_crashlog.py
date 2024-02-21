#!/usr/bin/python

import os
import time
import random
from SharedDataScripts import *
log_directory = path_set("/opt/log/crashlog/")
if not os.path.isdir(log_directory):
    os.makedirs(log_directory)

sample_directory = path_set("/opt/setup/shared/data_scripts/sample/crashlog/")
if os.listdir(sample_directory):
    crash_logs = os.listdir(sample_directory)
else:
    print "Missing sample directory \""+sample_directory+"\""

for sample_file in crash_logs:
    if "crash-" in sample_file:
        file_lines = open(sample_directory + sample_file, 'r').readlines()        
        new_file = open(log_directory + sample_file.replace("2013-08-21", time.strftime("%Y-%m-%d")), 'w')
        file_lines[0] = file_lines[0].replace("2013-08-21", time.strftime("%Y-%m-%d"))
        for line in file_lines:
            new_file.write(line)
        new_file.close() 

    else:
        file_lines = open(sample_directory + sample_file, 'r').readlines()
        new_file = open(log_directory + sample_file, 'w')
        for line in file_lines:
            if "<ActionDate>" in line:
                action_date = time.time() - random.randint(0,2592000)
                line = line[0:line.find("<ActionDate>") + 12] + time.strftime("%Y-%m-%d", time.gmtime(action_date)) + line[line.rfind("</ActionDate>"):-1] + "\n"
            new_file.write(line)
        new_file.close()
