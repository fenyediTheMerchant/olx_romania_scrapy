import scrapy
from scrapy.crawler import CrawlerProcess
import json
import csv
import re
import requests

class Olx(scrapy.Spider):
    name = 'olxScraper'

    url = 'https://m.olx.ro/api/v1/offers/?limit=10&category_id=948&city_id=30823&sort_by=created_at%3Adesc'

    headers = {
        'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    }

    #ez csak akkor hivodik meg ha netrol scrapel
    def __init__(self):
        with open('results.csv', 'w') as csv_file:
            csv_file.write('id, title, last_refresh_time, created_time, highlighted, urgent, top_ad, price, currency, negotiable, previous_value, business, locationID, locationName, regionID, regionName, categoryID, categoryName, delivery, safeDeal, url\n')

    
    def start_requests(self):
        offset = 0
        r = requests.get(url=self.url + '&offset=' + str(offset))
        #print(url=self.url + '&offset=' + str(offset))
        while (r.ok):
            print(r.status_code)
            yield scrapy.Request(url=self.url + '&offset=' + str(offset), headers=self.headers, callback=self.parse)
            offset += 10
            #print(url=self.url + '&offset=' + str(offset))
            r = requests.get(url=self.url + '&offset=' + str(offset))
        print(r.status_code)

        #for offset in range(0, 2):
        #    yield scrapy.Request(url=self.url + '&offset=' + str(offset*10), headers=self.headers, callback=self.parse)
        #yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse)

    def parse(self, res):
        data = res.text

        #offline
        #data = ''
        #with open('res.json', 'r') as json_file:
            #json_file.write(res.text)
        #    for line in json_file.read():
        #       data += line


        data = json.loads(data)

        #print(json.dumps(data, indent=2))

        for offer in data['data']:
            #print(json.dumps(offer['title'], indent=2))
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

            #print(json.dumps(items, indent=2))
            #print(items.keys())
            print(json.dumps(items, indent=2))
            with open('results.csv', 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=items.keys())
                writer.writerow(items)

#Run Online
process = CrawlerProcess()
process.crawl(Olx)
process.start()

#Debug futtatas
#Olx.parse(Olx, '')