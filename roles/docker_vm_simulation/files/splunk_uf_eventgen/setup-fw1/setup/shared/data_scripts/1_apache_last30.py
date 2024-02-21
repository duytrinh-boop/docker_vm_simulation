#!/usr/bin/python
import random
import datetime
import time
import os
import sys
import csv
from platform import system

# Makes a set of faux apache log files for the Splunk Search & Report training
# *** This script creates a set of access_combined logs in /opt/log
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
# v3.1 -- now writes to /opt/log instead of /opt/apache
#         and generates data over the past 7 days instead of in "real time"
#
# v4.0 -- Changes Made by chris@poallc.com
#       Created generate_events function
#       Moved file wrting utility to own function so you can call it outside of the generate loop
#       Added check so if action is purchase, make sure the product was viewed and added to cart first
#       Added random chance of 503 at purchase point. So view/add to cart are included
#       Added success and fail pages to purchase flow
#       Moved non-200 html staus to bad requests.  Allows better control of % and more realistic data
#       Added 500 status error
#       Added cart success and failure check
#       Created ip generation function
#
# v5.0 -- changes to improve distribution of events etc. - lguinn
#       Added time of day, day of week and month of year multipliers
#       Added more browsers
#       Added external lists of ip addresses, browsers instead of internal arrays
#
	
# v5.1 -- Changes to give every action=purchase a categroyId - sross
#	Created categroy and product id data structure
#	Coded any action=purcahse log to include categroyId
 
###  Settings  ###
#Rough percentage of the purchases to have 503 server errors
purchServerErrors = 10
#Rough percentage of the purchases to end in user error when server is working (not 503)
purchUserErrors = 20
#Rough percentage of bad apache status (400, 404, 406, etc)
htmlErrors = 20

### Data Definitions ###
clientipAddresses = []
#ProductIds, itemIds and catIds now correspond to each other
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
fourOhFours = ["/product.screen?productId=SF-BVS-G01&","/stuff/logo.ico?","/numa/numa.html?","/search.do?items=2112&","/rush/signals.zip?","/passwords.pdf?","/hidden/anna_nicole.html?","/productscreen.html?t=ou812&","show.do?productId=SF-BVS-01&"]
purchaseErrors = ["/cart/error.do?msg=CreditNotAccepted","/cart/error.do?msg=FormError","/cart/error.do?msg=NothingInCart","/cart/error.do?msg=CreditDoesNotMatch","/cart/error.do?msg=CanNotGetCart"]
# hourly pattern is a multiplier - there is one number for each hour of the day (0 to 24)
# a higher number indicates greater spacing between events during that hour (so fewer events)
hourly_factor = [ 1.25, 1.3, 1.3, 1.25, 1.2, 1.2, 1.2, 1.1, .9, .9, 1, 1, 1, 1, 1, 1, 1, .9, .8, .9, .7, 1, 1.1, 1.2 ]
server_TZ = 0    # offset from GMT
class_TZ = -7 # most classes in US time, so this will be Mountain or Central unless overridden in default
day_index=1
last_event=-1

#----------------------------------------------------------------------

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

def randIP():
    return random.choice(clientipAddresses)

# function to calculate "wait time" between events
def time_to_wait_between_events(eventTime, low, high, last_event, day_index):
    if last_event!=-1:
        if eventTime.day!=last_event.day:  #increase the rate slightly each day
            day_index=day_index + 1
    last_event=eventTime
    hourIndex=eventTime.hour+(server_TZ+class_TZ)
    if hourIndex > 23:
        hourIndex=hourIndex-24
    timeFactor = hourly_factor[hourIndex] * (1-(day_index*.02))
    if eventTime.month == 2 and eventTime.day < 15 and eventTime.day > 11: # Valentine's Day
        timeFactor = timeFactor * .8
    if eventTime.month == 5 or eventTime.month == 6:   # Mothers Day & Weddings
        timeFactor = timeFactor * .9
    if eventTime.weekday() == 4 or eventTime.weekday() == 5:    # Friday or Saturday
        timeFactor = timeFactor * .95
    return datetime.timedelta(seconds=(random.randint(low,high) * timeFactor))

products = import_csv(product_csv)

# function to generate a good apache event
def generate_good_apache(ipAddr, agent, referer, jsessionId, files, host, purchServerErrors, purchUserErrors, eventTime):
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
        "/product.screen?productId=" + productId,
        "/category.screen?categoryId=" + catId,
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

        bytesXferred = str(random.randint(200,4000))
        timeTaken =  str(random.randint(100,1000))
        event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
        write_logs(event,files,host)
        eventTime = eventTime + time_to_wait_between_events(eventTime,1,9, last_event, day_index)
        #add product to cart
        method = "POST"
        referralUri = baseUrl + nextrefer
        uri = "/cart.do?action=" + 'addtocart' + "&itemId=" + itemId + "&productId=" + productId + "&JSESSIONID=" + jsessionId

        nextrefer = "/cart.do?action=" + 'addtocart' + "&itemId=" + itemId + "&categoryId=" + catId + "&productId=" + productId

        now = datetime.datetime.today()
        bytesXferred = str(random.randint(200,4000))
        timeTaken =  str(random.randint(100,1000))
        event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
        write_logs(event,files,host)
        eventTime = eventTime + time_to_wait_between_events(eventTime,1,9, last_event, day_index)
        #Add random chance of 503 error at purchase -- about 5% of the time
        if random.randint(1,100) < purchServerErrors:
            uri = "/cart.do?action=" + action + "&itemId=" + itemId + "&JSESSIONID=" + jsessionId
            referralUri = baseUrl + nextrefer

            nextrefer = "/cart.do?action=" + action + "&itemId=" + itemId

            status = "503"
            bytesXferred = str(random.randint(200,4000))
            timeTaken =  str(random.randint(100,1000))
            event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
            write_logs(event,files,host)
            # Let the generator know the server is broken
            return True
        else:
            #Purchase product

            referralUri = baseUrl + nextrefer
            uri = "/cart.do?action=" + action + "&itemId=" + itemId + "&JSESSIONID=" + jsessionId
            nextrefer = "/cart.do?action=" + action + "&itemId=" + itemId

            bytesXferred = str(random.randint(200,4000))
            timeTaken =  str(random.randint(100,1000))
            event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
            write_logs(event,files,host)

            referralUri = baseUrl + nextrefer
            eventTime = eventTime + time_to_wait_between_events(eventTime,1,3, last_event, day_index)
            #Add random chance that user get success page, leaves cart or gets cart error
            if random.randint(1,100) < purchUserErrors:                #Add random chance of user abandoning cart - 15%
                if random.randint(1,100) < 15:
                    pass
                else:
                    uri = random.choice(purchaseErrors) + "&JSESSIONID=" + jsessionId                    
		    bytesXferred = str(random.randint(200,4000))
                    timeTaken =  str(random.randint(100,1000))
                    event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
                    write_logs(event,files,host)
            else:
                uri = '/cart/success.do' + "?JSESSIONID=" + jsessionId
                bytesXferred = str(random.randint(200,4000))
                timeTaken =  str(random.randint(100,1000))
                event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
                write_logs(event,files,host)
            # Let the generator know the server is not broken
            return False
    else:
        event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
        write_logs(event,files,host)
        # Let the generator know the server is not broken
        return False

#function to generate a bad apache event
def generate_bad_apache(ipAddr, agent, referer, jsessionId, files, host, eventTime):
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
        "/product.screen?productId=SF-BVS-G01",
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
    # build the event
    event = ipAddr + " - - [" + eventTime.strftime('%d/%b/%Y:%H:%M:%S') + "] \"" + method + " " + uri + " HTTP 1.1\" " + status + " " + bytesXferred + " \"" + referralUri + "\" \"" + agent + "\" " + timeTaken + "\n"
    # write event to log file
    write_logs(event,files,host)
    #If server is broken with 503, let the generator know
    if status == '503':
        return True
    else:
        return False

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

#Random base value for the jsessionid calculation
jsessionnum = 4949
#compute start and stop times for data generation
stopTime = datetime.datetime.today()
curTime = stopTime - datetime.timedelta(days=30) # set the "current" time to a month ago
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
#get ip addresses
inputTarget = open(sys.path[0] + sep + "data" + sep + "target.input", "r")
for ip in inputTarget:
    clientipAddresses = clientipAddresses + [ ip.strip() ]
#get agents (types of browsers)
inputAgent = open(sys.path[0] + sep + "data" + sep + "browser.input", "r")
for iAgent in inputAgent:
    useragents = useragents + [ iAgent.strip() ]

#-----------------------------------------------------------------------
# generate events
# pick a client, create ip, host and get session id
while curTime < stopTime:
    clientipAddress = randIP()
    useragent = random.choice(useragents)   # a client has a particular user agent during a session
    host = random.randint(0, len(files)-1) # which of the apache hosts will get these events
    #create a jession id for these transactions so that it is consistent
    jsessionnum = jsessionnum + random.randint(1,17)
    jsessionId = "SD" + str(random.randint(0, 10)) + "SL" + str(random.randint(1, 10)) + "FF" + str(random.randint(1, 10)) + "ADFF" + str(jsessionnum)
    # generate a random number of events from this client to this host
    numEventsThisClient = random.randint(1,12)

    for eventNum in range(numEventsThisClient):
        if curTime > stopTime:
            break
        # for the first event, choose a referer
        if eventNum == 0:
            refererURI = random.choice(refererURIs)
        else:
            refererURI = ""
        # decide if we need to toss in a html error
        if random.randint(1,100) < htmlErrors and eventNum !=0:
            l = generate_bad_apache(clientipAddress, useragent, refererURI, jsessionId, files, host, curTime)
            if l == True:
                broke_server = True
            else:
                broke_server = False
        else:
            l = generate_good_apache(clientipAddress, useragent, refererURI, jsessionId, files, host, purchServerErrors, purchUserErrors, curTime)
            if l == True:
                broke_server = True
            else:
                broke_server = False
        if broke_server:
            break   #if a server is broken (503) clear clients and go to the next client/host combination
            #wait a short time before generating next event for this client/host combination
        curTime = curTime + time_to_wait_between_events(curTime,1,8, last_event, day_index)
    curTime = curTime + time_to_wait_between_events(curTime,300,901, last_event, day_index)
