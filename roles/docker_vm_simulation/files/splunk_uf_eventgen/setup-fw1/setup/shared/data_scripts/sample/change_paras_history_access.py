#!/usr/bin/python

import math

cisco_vpn_file = "cisco_vpn.sample"
history_access_file = "history_access.sample"
windows_authentication_file = "windows.authenication.sample"

user_array = ["bashful", "doc", "sleepy", "sneezy", "dopey", "grumpy", "happy"]

def mod_cisco_vpn(cisco_sample, user_array):
	
	file = open(cisco_sample, 'r')
	file_lines = file.readlines()
	file.close()
	new_lines = []
	i = 0
	for line in file_lines:
		num_users = len(user_array)
		user=user_array[i]
		i=i+1
		if i == num_users:
			i=0

		new_line = swap_str(line, "Username = ", ", IP", user)
		new_line = swap_str(new_line, "acmetech-vpn.", ".com %ASA-", "myflowershop")
		new_line = swap_str(new_line, "Group = ", ", Username", "myflowershop")
		new_lines.append(new_line)
				
	
	file = open(cisco_sample+".old", 'w')
	file.writelines(file_lines)
	file.close()
	
	file = open(cisco_sample, 'w')
	file.writelines(new_lines)
	file.close()
	

def swap_str(string, start_contex, end_contex, para):
	str_len = len(string)
	start_contex_len = len(start_contex)
        start_index = string.rfind(start_contex)+start_contex_len
       	end_index = string.find(end_contex)
        new_string = string[0:start_index]+para+string[end_index:str_len]
	return new_string
       	
mod_cisco_vpn(cisco_vpn_file, user_array)
