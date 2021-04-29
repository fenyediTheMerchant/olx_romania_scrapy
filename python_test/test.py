#!/usr/bin/python

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
print('The given Category_ID is:', category_id ,'\n')
print('The given City_ID is:', city_id ,'\n')

print(oplist,args)