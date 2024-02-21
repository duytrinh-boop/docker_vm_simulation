#!/usr/bin/python

import time
import commands
import random
import os

def write_log(line,file):
    output_file = open(file, 'a')
    output_file.write(line)
    output_file.close()

def get_user(seed):
	elements = ""
	id = ""
	acc = 0
	val = 0
	for i in range(1,9):
		val = ((seed*i*i+i-seed/i+seed/4+seed/67)*157/seed) % 36
		for i in range(1,val):
			acc = (acc + (seed+i)*i+(seed*i/val)) % 9
		id = id + str(acc)		
		if val > 9:
			val = chr(val+87)
		else:
			val = str(val)
		elements = elements+val
	id = id[0:4]+'-4'+id[5:9]
	return (elements, id)

def get_log(user_seed, currtime, logFile, transId):
	timestamp = time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime))
	log = time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime)) + " Sent to checkout TransactionID=" + str(transId) + "\n"
	log = log + time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime)) + " checkout response for TransactionID=" + str(transId) + " CustomerID=" + user[0] + "\n"
	if random.randint(1,25) == 25:
		log = log + time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime+random.randint(0,1))) + " ecomm engine response TransactionID=" + str(transId) + " CustomerID=" + user[0] + " error\n"
		log = log + time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime+random.randint(1,2))) + " ErrorCode=" + str(random.choice(errorCodes)) + "\n"
	else:
		log = log + time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime+random.randint(0,1))) + " ecomm engine response TransactionID=" + str(transId) + " CustomerID=" + user[0] + " accepted\n"
		log = log + time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime+random.randint(1,2))) +	" TransactionID=" + str(transId) + " AcctCode=" + user[1] + "\n"
		log = log + time.strftime("%a %b %d %Y %H:%M:%S", time.gmtime(currtime+random.randint(2,3))) +	" Sent to Accounting System " + str(random.choice(accSys)) + "\n"
	write_log(log, logFile)
	return transId + 1

file = "/opt/log/ecommsv1/sales_entries.log"
transId = 103447
accSys = [100303, 101809, 102795]
errorCodes = [103, 205, 224, 301, 356]
currtime = time.time() - 86400*30

dirname = os.path.dirname(file) 
if os.path.exists(dirname):   
	if os.path.exists(file):
        	print "Writing to " + file
        else:
                print "Creating " + file  #it will get created when data is written later
else:
        print "Creating " + dirname
        os.makedirs(dirname)

while True:
	if currtime < time.time():
		user = get_user(random.randint(1,101))
		transId = get_log(user, currtime+random.randint(0,59), file, transId)
		currtime = time.time() + 60 
