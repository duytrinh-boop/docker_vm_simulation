#!/usr/bin/python
from optparse import OptionParser
import random
import datetime
import time
import os
import sys
import csv
from platform import system

### Docs ###
# Makes a set of faux apache log files for the Splunk Search & Report training
# *** This script creates a set of access_combined logs in /opt/apache
#
# *** Questions? lguinn@splunk.com
#
# *** Copyright Splunk, Inc. 2010
#
# v1.0 -- originally developed by Simon Shelston for online store app
#
# v2.0 -- now generates events in a more definite pattern AND
#         runs for approximately 4.5 hours and then quits
#         generates 3 different log files, to simulate 3 different web servers
#
# v3.0 -- runs on Linux and Windows
#
# v3.1 -- updated with new locations and additional client ip addresses, etc.
#
# v4.0 -- Changes Made by chris@poallc.com
#       Run time limit moved to settings.  If time limit is turned on, script will run the number of hours in runTime var
#       Wait time moved to settings.  Time script should wait between users
#       Created generate_events class so that limited run time can be used.
#       Moved file wrting utility to own class so you can call it outside of the generate loop
#       Added check so if action is purchase, make sure the product was viewed and added to cart first
#       Added random chance of 503 at purchase point. So view/add to cart are included
#       Added success and fail pages to purchase flow
#       Moved non-200 html staus to bad requests.  Allows better control of % and more realistic data
#       Added 500 status error
#       Added cart success and failure check
#       Created ip generation function
#
# v4.1 -- Now takes a command line setting for how long to run, if it exists, and overrides the
#       runTime parameter
#       Now loads ip addresses from a file of ip addresses
#       Pause between events is now based on hour of the day

# v5.1 -- Changes to give every	action=purchase	a categroyId - sross
#	Created	categroy and product id	data structure
#	Coded any action=purcahse log to include categroyId



###  Settings  ###
#Run Time Settings
limtRunTime = False
runTime = 0 # how long to generate data in hours.  Not used if limtRunTime is false
#Rough percentage of the purchases to have 503 server errors
purchServerErrors = 8
#Rough percentage of the purchases to end in user error when server is working (not 503)
purchUserErrors = 25
#Rough percentage of bad apache status (400, 404, 406, etc)
htmlErrors =15

### Data Definitions ###
clientipAddresses = []
# Note ProductIds, itemIds and catIds now correspond to each other
product_csv = "/opt/setup/shared/data_scripts/sample/productId_weight.csv"
productDict = {'STRATEGY':["DB-SG-G01", "DC-SG-G02", "FS-SG-G03", "PZ-SG-G05"],
                'SHOOTER':["WC-SH-G04"],
                'TEE':["WC-SH-T02", "MB-AG-T01"],
                'SPORTS':["CU-PG-G06"],
                'ARCADE':["MB-AG-G07", "FI-AG-G08", "BS-AG-G09"],
                'SIMULATION':["SC-MG-G10"],
                'ACCESSORIES':["WC-SH-A01", "WC-SH-A02"]}
itemIds = ["EST-19","EST-18","EST-14", "EST-6","EST-26","EST-17","EST-16","EST-15","EST-27","EST-7",
           "EST-21","EST-11","EST-12","EST-13"]
catIds = ["STRATEGY","STRATEGY","STRATEGY","STRATEGY","SHOOTER","TEE","TEE","SPORTS","ARCADE","ARCADE",
          "ARCADE","SIMULATION","ACCESSORIES","ACCESSORIES"]
actions = ["purchase", "addtocart", "addtocart","remove", "view", "view", "view", "view", "changequantity"]
badstatuses = [["503", "400", "406", "404", "408", "500", "505"], ["503", "400", "406", "404", "408", "500", "403"], ["503", "400", "406", "404", "408", "500", "505"]]
methods = ["GET", "GET", "GET", "GET", "POST"]
Winfiles = [ "C:\\opt\\log\\www1\\access.log", "C:\\opt\\log\\www2\\access.log", "C:\\opt\\log\\www3\\access.log"]
files = [ "/opt/log/www1/access.log", "/opt/log/www2/access.log", "/opt/log/www3/access.log"]
baseUrl = "http://www.buttercupgames.com"
useragents = []
refererURIs = ["http://www.buttercupgames.com", "http://www.buttercupgames.com", "http://www.buttercupgames.com", "http://www.buttercupgames.com", "http://www.buttercupgames.com", "http://www.google.com", "http://www.google.com",
               "http://www.google.com", "http://www.google.com", "http://www.yahoo.com", "http://www.yahoo.com", "http://www.bing.com"]
fourOhFours = ["/product.screen?productId=SF-BVS-01&","/stuff/logo.ico?","/numa/numa.html?","/search.do?items=2112&","/rush/signals.zip?","/passwords.pdf?","/hidden/anna_nicole.html?","/productscreen.html?t=ou812&","show.do?productId=SF-BVS-01&"]
purchaseErrors = ["/cart/error.do?msg=CreditNotAccepted","/cart/error.do?msg=FormError","/cart/error.do?msg=NothingInCart","/cart/error.do?msg=CreditDoesNotMatch","/cart/error.do?msg=CanNotGetCart"]
# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 1.25, 1.3, 1.3, 1.25, 1.2, 1.2, 1.2, 1.1, .9, .9, 1, 1, 1, 1, 1, 1, 1, .9, .8, .9, .7, 1, 1.1, 1.2 ]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central

#-----------------------------------------------------------------------

def import_csv(csv_file):
        list = []
        csv_lines = open(csv_file,'rU')
        csv_dict = csv.DictReader(csv_lines, dialect='excel', delimiter=',')
        for item in csv_dict:
                list.append(item)
        return list   

def product_picker(products):
        list = []
        for product in products:
                for i in range(int(float(product['TOTAL']))):
                        list.append(product['ID'])
        return random.choice(list)

def get_category(product, cats):  
        for key in cats.keys():
                if product in cats[key]:
                        return key

# returns a random ip address
def randIP():
    return random.choice(clientipAddresses)

# function to sleep a random time between events
def wait_time(low, high):
    hourIndex=datetime.datetime.today().hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    time.sleep(random.randint(low, high) * timeFactor)

# function to sleep between events
def time_to_wait_between_events(sleeptime):
    eventTime = datetime.datetime.today()
    hourIndex=eventTime.hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex]
    if eventTime.month == 2 and eventTime.day < 15 and eventTime.day > 11: # Valentine's Day
        timeFactor = timeFactor * .8
    if eventTime.month == 5 or eventTime.month == 6:   # Mothers Day & Weddings
        timeFactor = timeFactor * .9
    if eventTime.weekday() == 4 or eventTime.weekday() == 5:    # Friday or Saturday
        timeFactor = timeFactor * .95
    time.sleep(sleeptime * timeFactor)

products = import_csv(product_csv)

# function to generate a good apache event
def generate_good_apache(ipAddr, agent, referer, jsessionId, files, host, purchServerErrors, purchUserErrors):
    #randomly choose the products, items, etc. for this transaction
    indx = random.randint(0, len(catIds) - 1)
    itemId = itemIds[indx]
    productId = product_picker(products)
    catId = get_category(productId, productDict) 
    action = random.choice(actions)
    status = '200'
    method = random.choice(methods)
    bytesXferred = str(random.randint(200,4000))
    timeTaken =  str(random.randint(100,1000))
    uris = [
        "/cart.do?action=" + action + "&itemId=" + itemId + "&productId=" + productId,
        "/product.screen?productId="+productId,
        "/category.screen?categoryId="+catId,
        "/oldlink?itemId=" + itemId
        ]
    uri = random.choice(uris) + "&JSESSIONID=" + jsessionId
    if referer == "":
        referralUri = baseUrl + random.choice(uris)
    else:
        referralUri = referer
    # If an item is purchased, make sure it has been viewed and added to cart first
    if action == 'purchase':
        #create product view
        referralUri = baseUrl + "/category.screen?categoryId=" + catId
        uri = "/product.screen?productId=" + productId + "&JSESSIONID=" + jsessionId

        nextrefer = "/product.screen?productId=" + productId

        now = datetime.datetime.today()
        bytesXferred = str(random.randint(200,4000))
        timeTaken =  str(random.randint(100,1000))
        event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
        write_logs(event,files,host)
        wait_time(1,5)

        #add product to cart
        method = "POST"
        referralUri = baseUrl + nextrefer
        uri = "/cart.do?action=" + 'addtocart' + "&itemId=" + itemId + "&productId=" + productId + "&JSESSIONID=" + jsessionId

        nextrefer = "/cart.do?action=" + 'addtocart' + "&itemId=" + itemId + "&categoryId=" + catId + "&productId=" + productId

        now = datetime.datetime.today()
        bytesXferred = str(random.randint(200,4000))
        timeTaken =  str(random.randint(100,1000))
        event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
        write_logs(event,files,host)
        wait_time(1,5)
        #Add random chance of 503 error at purchase -- about 5% of the time
        if random.randint(1,100) < purchServerErrors:
            uri = "/cart.do?action=" + action + "&itemId=" + itemId + "&JSESSIONID=" + jsessionId
            referralUri = baseUrl + nextrefer

            nextrefer = "/cart.do?action=" + action + "&itemId=" + itemId

            status = "503"
            now = datetime.datetime.today()
            bytesXferred = str(random.randint(200,4000))
            timeTaken =  str(random.randint(100,1000))
            event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
            write_logs(event,files,host)
            # Let the generator know the server is broken
            return True
        else:
            #Purchase product

            referralUri = baseUrl + nextrefer
            uri = "/cart.do?action=" + action + "&itemId=" + itemId + "&JSESSIONID=" + jsessionId
            nextrefer = "/cart.do?action=" + action + "&itemId=" + itemId

            now = datetime.datetime.today()
            bytesXferred = str(random.randint(200,4000))
            timeTaken =  str(random.randint(100,1000))
            event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
            write_logs(event,files,host)

            referralUri = baseUrl + nextrefer

            #Add random chance that user get success page, leaves cart or gets cart error
            if random.randint(1,100) < purchUserErrors:
                #Add random chance of user abandoning cart - 15%
                if random.randint(1,100) < 15:
                    pass
                else:
                    uri = purchaseErrors[random.randint(0, len(purchaseErrors) - 1)] + "&JSESSIONID=" + jsessionId
                    now = datetime.datetime.today()
                    bytesXferred = str(random.randint(200,4000))
                    timeTaken =  str(random.randint(100,1000))
                    event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
                    write_logs(event,files,host)
            else:
                uri = '/cart/success.do' + "?JSESSIONID=" + jsessionId
                now = datetime.datetime.today()
                bytesXferred = str(random.randint(200,4000))
                timeTaken =  str(random.randint(100,1000))
                event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
                write_logs(event,files,host)
            # Let the generator know the server is not broken
            return False
    else:
        now = datetime.datetime.today()
        event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
        write_logs(event,files,host)
        # Let the generator know the server is not broken
        return False

#function to generate a bad apache event
def generate_bad_apache(ipAddr, agent, referer, jsessionId, files, host):
    #randomly choose the products, items, etc. for this transaction
    indx = random.randint(0, len(catIds) - 1)
    itemId = itemIds[indx]
    productId = product_picker(products)
    catId = get_category(productId, productDict)
    action = random.choice(actions)
    status = random.choice(badstatuses[host])
    method = random.choice(methods)
    bytesXferred = str(random.randint(200,4000))
    timeTaken =  str(random.randint(100,1000))
    uris = [
        "/cart.do?action=" + action + "&itemId=" + itemId,
        "/product.screen?productId=SF-BVS-01",
        "/category.screen?categoryId=NULL",
        "/oldlink?itemId=" + itemId
        ]
    if status == '404':
        uri = random.choice(fourOhFours) + "JSESSIONID=" + jsessionId
    else:
        uri = random.choice(uris) + "&JSESSIONID=" + jsessionId
    if referer == "":
        referralUri = baseUrl + random.choice(uris)
    else:
        referralUri = referer
    now = datetime.datetime.today()
    # build the event
    event = ipAddr + " - - [" + now.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
    # write event to log file
    write_logs(event,files,host)
    #If server is broken with 503, let the generator know
    if status == '503':
        return True
    else:
        return False

def generate_events(jsessionnum, files, sleeptime, purchServerErrors, purchUserErrors, htmlErrors):
    time_to_wait_between_events(sleeptime)
    # pick a client, create ip, host and get session id
    clientipAddress = randIP()
    useragent = random.choice(useragents)   # a client has a particular user agent during a session
    host = random.randint(0, len(files)-1) # which of the apache hosts will get these events
    #create a jession id for these transactions so that it is consistent
    jsessionnum = jsessionnum + random.randint(1,17)
    jsessionId = "SD" + str(random.randint(0, 10)) + "SL" + str(random.randint(1, 10)) + "FF" + str(random.randint(1, 10)) + "ADFF" + str(jsessionnum)
    # generate a random number of events from this client to this host
    numEventsThisClient = random.randint(1,12)
    for eventNum in range(numEventsThisClient):
        # for the first event, choose a referer
        if eventNum == 0:
            refererURI = refererURIs[random.randint(0, len(refererURIs) - 1)]
        else:
            refererURI = ""
        # decide if we need to toss in a html error
        if random.randint(1,100) < htmlErrors:
            l = generate_bad_apache(clientipAddress, useragent, refererURI, jsessionId, files, host)
            if l == True:
                broke_server = True
            else:
                broke_server = False
        else:
            l = generate_good_apache(clientipAddress, useragent, refererURI, jsessionId, files, host, purchServerErrors, purchUserErrors)
            if l == True:
                broke_server = True
            else:
                broke_server = False
        if broke_server:
            break   #if a server is broken (503) clear clients and go to the next client/host combination
        #wait a short time before generating next event for this client/host combination
        wait_time(4,19)

def write_logs(line,files,host):
        #write out the event, open and close the file each time for proper tailing
        output_file = open(files[host], 'a')
        output_file.write(line)
        output_file.close()

#-----------------------------------------------------------------------
## Make Ready ##

#File Location settings
if system() == 'Windows':
    files = Winfiles
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

# Get argument (hours to run) if supplied on command line
# Overrides hard coded settings
usage = "usage: %prog n \n      where n is an optional number of hours to run"
parser = OptionParser(usage)
(options, args) = parser.parse_args()
if len(args) > 0:
    if len(args[0]) > 0 and args[0].isdigit:
        runTime = int(args[0])
        limtRunTime = True
#Compute how long to generate data if limtRunTime is 'True'
if limtRunTime:
    stoptime = time.time() + (runTime * 60 * 60)

#Random base value for the jsessionid calculation
jsessionnum = 4949
#create directories if they don't exist
for file in files:
    dirname = os.path.dirname(file)
    if os.path.exists(dirname):
        if os.path.exists(file):
            print "Writing to " + file
        else:
            print "Creating " + file  #it will get created when data is written later
    else:
        print "Creating " + dirname
        os.makedirs(dirname)
#get addtional ip addresses
inputTarget = open(sys.path[0] + sep + "data" + sep + "target.input", "r")
for ip in inputTarget:
    clientipAddresses = clientipAddresses + [ ip.strip() ]
#get agents (types of browsers)
inputAgent = open(sys.path[0] + sep + "data" + sep + "browser.input", "r")
for iAgent in inputAgent:
    useragents = useragents + [ iAgent.strip() ]
#-----------------------------------------------------------------------
# Generate Events
if limtRunTime:
    curtime = time.time()
    while curtime < stoptime:
        sleeptime = random.randint(50,413)
        generate_events(jsessionnum, files, sleeptime, purchServerErrors, purchUserErrors, htmlErrors)
        curtime = time.time()
else:
    while('freerun'):
        sleeptime =random.randint(50,413)
        generate_events(jsessionnum, files, sleeptime, purchServerErrors, purchUserErrors, htmlErrors)
