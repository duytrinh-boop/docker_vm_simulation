import sys

file = open(sys.argv[1], 'r')

wordlist = ["pussy", "sex", "girl", "porn", "busty", "adult", "teen", "blowjob"]

newfile = open(sys.argv[1]+".filtered", 'w')

for line in file:
    triggerd = False
    for word in wordlist:
        if word in line:
            triggerd = True
    if not triggerd:
        newfile.write(line)
