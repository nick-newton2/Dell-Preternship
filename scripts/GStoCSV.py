#!/usr/bin/env python3

import requests
import sys

#URL = str(sys.argv[1])  # get the URL from the 1st command line arg
# when we combine it with the csvtojson script and ultimately the shell script,
# we can have a variable to contain the URL
URL = r'https://yld.me/eMUD'
response = requests.get(URL)
assert response.status_code == 200, 'Wrong status code'

with open('data.csv', 'w') as f:
	f.write(response.text)
