#!/usr/bin/python

import math

cisco_vpn_file = "cisco_vpn.sample"
history_access_file = "history_access.sample"
windows_authentication_file = "windows.authentication.sample"

user_array = ["bashful", "doc", "sleepy", "sneezy", "dopey", "grumpy", "happy"]

def mod_sample_file(filename, user_array):
	
	file = open(filename, 'r')
	file_lines = file.readlines()
	file.close()
	new_lines = []
	i = 0
	for line in file_lines:
		if "User=" in line:
			num_users = len(user_array)
			user=user_array[i]
			i=i+1
			if i == num_users:
				i=0

			new_line = swap_str(line, "User= ", "\n", user)
			new_lines.append(new_line)
		
		elif "User Name:" in line:
			new_line = swap_str(line, "User Name:\t", "\n", user)
                        new_lines.append(new_line)	
		
		elif "Domain:" in line:
			new_line = swap_str(line, "Domain:\t\t", "\n", "MYFLOWERSHOP")
		        new_lines.append(new_line)

		else:
			new_lines.append(line)			
		
			
		

	file = open(filename+".old", 'w')
	file.writelines(file_lines)
	file.close()
	
	file = open(filename, 'w')
	file.writelines(new_lines)
	file.close()
	

def swap_str(string, start_contex, end_contex, para):
	str_len = len(string)
	start_contex_len = len(start_contex)
        start_index = string.rfind(start_contex)+start_contex_len
       	end_index = string.find(end_contex)
        new_string = string[0:start_index]+para+string[end_index:str_len]
	return new_string
       	
mod_sample_file(windows_authentication_file, user_array)
