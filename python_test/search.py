#!/usr/bin/env python3

# Import json module
import json

# Define json data
f = open('categories.json')
customerData = json.load(f)

# Input the key value that you want to search
keyVal = input("Enter a key value: \n")
result = list(filter(lambda x:x['name'].lower()==keyVal.lower(),customerData['data']))

if len(result) <= 0: print("A megadott település nem található! \nKérjük adjon meg egy létező települést.")
else:
    print("A vizsgálandó település adatai:")
    print(result)
    result_id = result[0]['id']
    name = result[0]['name']
    print("Result id = ", result_id)
    print("Result name = ",name)
 
f.close