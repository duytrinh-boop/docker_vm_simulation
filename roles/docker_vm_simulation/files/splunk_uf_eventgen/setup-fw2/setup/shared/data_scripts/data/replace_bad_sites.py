#!/usr/bin/python

import csv

def import_csv(csv_file):
        list = []
        csv_lines = open(csv_file,'rU')
        csv_dict = csv.DictReader(csv_lines, dialect='excel', delimiter=',')
        for item in csv_dict:
                list.append(item)
        return list

bad_site_file = "bad_sites.csv"
cisco_file = "cisco_ironport_web.input"
bad_list = import_csv(bad_site_file)
file = open(cisco_file, 'r')
sample_file = file.readlines()

for i in range(len(sample_file)-1):
	line = sample_file[i].split(" ")
	new_line = ""
	for j in range(len(line)-1):
		for bad_thing in bad_list:
			if bad_thing['cs_url'] == line[j]:
				new_line = new_line + "http://www.pokerstars.net "
				print "Bad Site: " + bad_thing['cs_url'] + "replaced with http://www.pokerstars.net"
			else:
				new_line = new_line + line[j] + " "
	new_line = new_line + "\n"
	sample_file[i] = new_line

file = open(cisco_file, 'w')
file.writelines(sample_file)
file.close()
				 

