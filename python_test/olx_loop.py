import requests

baseurl = 'https://m.olx.ro/api/v1/offers/?limit=10&category_id=948&city_id=30823&sort_by=created_at%3Adesc'

headers =  {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

#r = requests.get(baseurl + '&offset=1000')
#print(r.content)

offset = 0
print(baseurl + '&offset=' + str(offset))
r = requests.get(baseurl + '&offset=' + str(offset))
while (r.ok):
    print(r.status_code)
    offset += 10
    print(baseurl + '&offset=' + str(offset))
    r = requests.get(baseurl + '&offset=' + str(offset))
print(r.status_code)


#print(baseurl + '&offset=' + str(offset))