#!/bin/bash

echo -e "Please enter the file name: "
read name
(head -n 1 ./rawResults/$name.csv && tail -n +2 ./rawResults/$name.csv | sort -u) > ./filteredResults/$name"FILTERED".csv