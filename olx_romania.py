import scrapy
from scrapy.crawler import CrawlerProcess
import json
import csv
import re
import requests
import sys, getopt

commandLineArgs = sys.argv[1:]

unixOptions = "ho:s:l:f:"
gnuOptions = ["help", "output=", "sleep=", "limit=", "offsetIncrement="]

try:
    oplist, args = getopt.getopt(commandLineArgs,unixOptions, gnuOptions)
except getopt.GetoptError:
    print('usage:   python3 olx_scraper.py -o <outputfile> category_id city_id')
    sys.exit(2)

outputfile = ''
sleep = 0
limit = 10
offsetIncrement = 10
#ez azert van igy, mivel az oplisten belul levo opcioknak is vannak argumentumai
# -o outputfile.csv itt az argumentum az outputfile
for opt, arg in oplist:
    if opt == '-h':
        print('usage:   python3 olx_scraper.py category_id city_id -o <outputfile>')
        print('Options: -h, -o, -s, -l, -f (--help, --output<filename>, --sleep, --limit, --offsetIncrement')
        sys.exit()
    elif opt in ("-o", "--output"):
        outputfile = arg
    elif opt in ("-s", "--sleep"):
        sleep = arg
    elif opt in ("-l", "--limit"):
        limit = arg
    elif opt in ("-f", "--offsetIncrement"):
        offsetIncrement = arg
category_id = args[0]
city_id = args[1]
outputfileName = outputfile

# Argumentumok kiirasa DEBUG
print(oplist,args)
print(outputfileName)

# Json adat definialasa mindket allomanyra
# Varosok input file
fileCities = open('cities.json')
citiesData = json.load(fileCities)
# Kategoriak input file
fileCategories = open('categories.json')
categoriesData = json.load(fileCategories)

# A keresendo ertekek a szureskor
keyValCities = city_id
keyvalCategories = category_id

# Mindket esetben megkeressuk s vissza teritjuk a listat ha kaptunk valamit
resultCities = list(filter(lambda x:x['name'].lower()==keyValCities.lower(),citiesData['data']))
resultCategories = list(filter(lambda x:x['name'].lower()==keyvalCategories.lower(),categoriesData['data']))

# Ellenorizzuk hogy van e talalat
if len(resultCities) <= 0 or len(resultCategories) <= 0: print("A megadott település/ kategória nem található! \nKérjük adjon meg egy létező települést/ kategóriát!.")
else:
    # print("A vizsgálandó település adatai:")
    # print(resultCities)
    city_result_id = resultCities[0]['id']
    city_name = resultCities[0]['name']
    print("Result id = ", city_result_id)
    print("Result name = ",city_name)
    # print("A vizsgálandó kategoria adatai:")
    # print(resultCategories)
    categories_result_id = resultCategories[0]['id']
    categories_name = resultCategories[0]['name']
    print("Result id = ", categories_result_id)
    print("Result name = ",categories_name)

# Fileok lezarasa
fileCities.close
fileCategories.close

class Olx(scrapy.Spider):
    name = 'olxScraper'

    url = f'https://m.olx.ro/api/v1/offers/?limit=10&category_id={categories_result_id}&city_id={city_result_id}&sort_by=created_at%3Adesc'
    print(url)
    headers = {
        'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }

    #ez csak akkor hivodik meg ha netrol scrapel
    def __init__(self):
        with open('./results/%s.csv' % outputfileName, 'w') as csv_file:
            csv_file.write('id, title, last_refresh_time, created_time, highlighted, urgent, top_ad, price, currency, negotiable, previous_value, business, locationID, locationName, regionID, regionName, categoryID, categoryName, delivery, safeDeal, url\n')

    
    def start_requests(self):
        offset = 0
        r = requests.get(url=self.url + '&offset=' + str(offset))
        while (r.ok):
            print(r.status_code)
            yield scrapy.Request(url=self.url + '&offset=' + str(offset), headers=self.headers, callback=self.parse)
            offset += 10
            r = requests.get(url=self.url + '&offset=' + str(offset))


    def parse(self, res):
        data = res.text
        data = json.loads(data)

        for offer in data['data']:
            items = {
                'id' : offer['id'],
                'title' : offer['title'],
                'last_refresh_time' : offer['last_refresh_time'],
                'created_time' : offer['created_time'],
                #'description' : offer['description'].replace('\n', ' ').replace('<br />', ' '),
                'highlighted' : offer['promotion']['highlighted'],
                'urgent' : offer['promotion']['urgent'],
                'top_ad' : offer['promotion']['top_ad'],
                'price' : offer['params'][0]['value']['value'],
                'currency' : offer['params'][0]['value']['currency'],
                'negotiable' : offer['params'][0]['value']['negotiable'],
                'previous_value' : offer['params'][0]['value']['previous_value'],
                #'state' : offer['params'][-1]['value']['key'], #???????????
                'business' : offer['business'],
                'locationID' : offer['location']['city']['id'],
                'locationName' : offer['location']['city']['name'],
                'regionID' : offer['location']['region']['id'],
                'regionName' : offer['location']['region']['name'],
                'categoryID' : offer['category']['id'],
                'categoryName' : offer['category']['type'],
                'delivery' : offer['delivery']['rock']['active'],
                'safeDeal' : offer['safedeal']['status'],
                'url' : offer['url']

            }
            print(json.dumps(items, indent=2))
            with open('./results/%s.csv' % outputfileName, 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=items.keys())
                writer.writerow(items)

#Run Online
process = CrawlerProcess()
process.crawl(Olx)
process.start()
