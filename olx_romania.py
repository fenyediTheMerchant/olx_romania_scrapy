# Importing mandatory libraries
# Scrapy for scraping, json for processing JSON files
# CSV to safe files as CSV, 
# Requests to make and recieve Requests, and SYS and GETOPT 
# to parse arguments to the script
# Time for using the sleep function
import scrapy
from scrapy.crawler import CrawlerProcess
import json
import csv
import re
import requests
import sys, getopt
import time

# Getting all of the args from the command line
commandLineArgs = sys.argv[1:]

# Defining options for the script, to be used as modifiers
unixOptions = "ho:s:l:f:"
gnuOptions = ["help", "output=", "sleep=", "limit=", "offsetIncrement="]

if len(sys.argv) < 2:
    print('usage:   python3 olx_scraper.py -o <outputfile> "Category_Name" "City_Name"\n')
    print('mentions:\nCity names can be either UPPER or LOWER case, or the mix of it!\nGiving an output file name is mandatory!')
    sys.exit(2)
else:
    try:
        oplist, args = getopt.getopt(commandLineArgs,unixOptions, gnuOptions)    
    except getopt.GetoptError:
        print('usage:   python3 olx_scraper.py -o <outputfile> "Category_Name" "City_Name"')
        print('mentions:\nCity names can be either UPPER or LOWER case, or the mix of it!\nGiving an output file name is mandatory!')
        sys.exit(2)
    # Setting the values of the two base variables
    # These will be used when generating the accces URL
    category_id = args[0]
    city_id = args[1]

# Error handling, if not all required args are given


# Initializing option variables
outputfileName = 'defaultFileName'
sleep = 0
limit = 10
offsetIncrement = 10

# HUN COMMENT FOR MAIN DEVELOPER ONLY #
# Ez azert van igy, mivel az oplisten belul levo opcioknak is vannak argumentumai
# -o outputfile.csv itt az argumentum az outputfile
for opt, arg in oplist:
    if opt == '-h':
        print('usage:   python3 olx_scraper.py -o <outputfile> "Category_Name" "City_Name"')
        print('Options: -h, -o, -s, -l, -f (--help, --output<filename>, --sleep, --limit, --offsetIncrement')
        print('mentions:\nCity names can be either UPPER or LOWER case, or the mix of it!\nGiving an output file name is mandatory!')
        sys.exit()
    elif opt in ("-o", "--output"):
        outputfileName = arg
    elif opt in ("-s", "--sleep"):
        sleep = int(arg)
    elif opt in ("-l", "--limit"):
        limit = arg
    elif opt in ("-f", "--offsetIncrement"):
        offsetIncrement = arg


# DEBUG Printing out the parsed arguments
print(oplist,args)
print(outputfileName)

# Defining the JSON input files
# Cities input file
fileCities = open('data/cities.json')
citiesData = json.load(fileCities)
# Categories input file
fileCategories = open('data/categories.json')
categoriesData = json.load(fileCategories)

# Key values for the searched city/ category
keyValCities = city_id
keyvalCategories = category_id

# We search and filter in both instances, if a match is found, we save the list to the 
# corresponding variables
resultCities = list(filter(lambda x:x['name'].lower()==keyValCities.lower(),citiesData['data']))
resultCategories = list(filter(lambda x:x['name'].lower()==keyvalCategories.lower(),categoriesData['data']))

# Checking if there is any result for the search
# If none is found in either of the lists, then abort
if len(resultCities) <= 0 or len(resultCategories) <= 0: 
    # print("A megadott település/ kategória nem található! \nKérjük adjon meg egy létező települést/ kategóriát!.")
    print("The given city/category cannot be found!\nPlease choose an existing city/category, or check the spelling of the city/category!")
    sys.exit(2)
else:
    # Saving  the results to the corresponding variables
    city_result_id = resultCities[0]['id']
    city_name = resultCities[0]['name']
    # DEBUG Printing out the values
    print("Result id = ", city_result_id)
    print("Result name = ",city_name)

    categories_result_id = resultCategories[0]['id']
    categories_name = resultCategories[0]['name']
    # DEBUG Printing out the values
    print("Result id = ", categories_result_id)
    print("Result name = ",categories_name)

# Closing the input files
fileCities.close
fileCategories.close

# Crawling trough the Webiste
# Defining(overriding) the main Spider class
class Olx(scrapy.Spider):
    # Setting the name for the Spider
    name = 'olxScraper'

    # Setting the start URL
    url = f'https://m.olx.ro/api/v1/offers/?limit={limit}&category_id={categories_result_id}&city_id={city_result_id}&sort_by=created_at%3Adesc'
    
    # DEBUG Printing the URL
    print(url)
    
    # Defining extra headers for the Request
    # We are defining only the user agent, to "not be as noticeable" for the Server
    headers = {
        'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }

    # Defining the INIT for the self instance of the Spider
    # It creates the output file, with the file name given as a parameter
    # Also it creates the headers for the CSV file
    def __init__(self):
        with open('./rawResults/%s.csv' % outputfileName, 'w') as csv_file:
            csv_file.write('id, title, last_refresh_time, created_time, highlighted, urgent, top_ad, price, currency, negotiable, previous_value, business, locationID, locationName, regionID, regionName, categoryID, categoryName, delivery, safeDeal, url\n')

    # Defining the START_REQUESTS for the Spider
    # Setting the offset to the 0 start value (the scraping will begin from the first result set)
    # Saving the data given back by the Request to the variable R + adding the offset to it, to iterate over the result set
    # Starting the loop, to iterate trough the data set
    # The exit condition is that if the requests wasn't successful
    # TBD
    # Incrementing the offset by the given amount
    # Getting the next request
    def start_requests(self):
        offset = 0
        r = requests.get(url=self.url + '&offset=' + str(offset))
        while (r.ok):
            # DEBUG Printing the status code of the request
            print(r.status_code)
            # TBD
            time.sleep(sleep)
            yield scrapy.Request(url=self.url + '&offset=' + str(offset), headers=self.headers, callback=self.parse)
            # Offset can be static, and user given from the arguments
            # offset += 10
            offset += int(offsetIncrement)
            r = requests.get(url=self.url + '&offset=' + str(offset))

    # Defining the parse method of the Scraper
    def parse(self, res):
        # Storing the text of the Response to a variable
        data = res.text
        # Loading the data from the variable and parsing as JSON
        jsonDict = json.loads(data)

        # Iterating trough the jsonDict and saving the needed data
        for advert in jsonDict['data']:
            details = {
                'id' : advert['id'],
                'title' : advert['title'],
                'last_refresh_time' : advert['last_refresh_time'],
                'created_time' : advert['created_time'],
                #'description' : advert['description'].replace('\n', ' ').replace('<br />', ' '),
                'highlighted' : advert['promotion']['highlighted'],
                'urgent' : advert['promotion']['urgent'],
                'top_ad' : advert['promotion']['top_ad'],
                'price' : advert['params'][0]['value']['value'],
                'currency' : advert['params'][0]['value']['currency'],
                'negotiable' : advert['params'][0]['value']['negotiable'],
                'previous_value' : advert['params'][0]['value']['previous_value'],
                #'state' : offer['params'][-1]['value']['key'], #???????????
                'business' : advert['business'],
                'locationID' : advert['location']['city']['id'],
                'locationName' : advert['location']['city']['name'],
                'regionID' : advert['location']['region']['id'],
                'regionName' : advert['location']['region']['name'],
                'categoryID' : advert['category']['id'],
                'categoryName' : advert['category']['type'],
                'delivery' : advert['delivery']['rock']['active'],
                'safeDeal' : advert['safedeal']['status'],
                'url' : advert['url']
            }

            # DEBUG Printing the collected data in each iteration, with the indent of 2
            # print(json.dumps(details, indent=2))

            # Appending the newly collected details about the curent advert to the OUTPUT.CSV file
            with open('./rawResults/%s.csv' % outputfileName, 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=details.keys())
                writer.writerow(details)

# Creating, and running the Crawler
process = CrawlerProcess()
process.crawl(Olx)
process.start()
