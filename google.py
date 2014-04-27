#Prints the title, link, and snippet of the first three google search results for a given query
# by loading the JSON results of a Google Custom Search through yaml

import urllib2
import json
import yaml
import pprint

#denote multi-word search by leading with '%22' and replacing spaces with '%20'
query = '%22astrobiologist%20chris%20mckay%20searches%20extreme%20landscapes'
url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDLjjiXwmTfTKufnyhoKgCZhG6rmXz7lpM&cx=002838561577770740964:v1yhgyblaxo&q='
url = url+query
data = urllib2.urlopen(url)
data = yaml.load(data)

results = [ [data['items'][0]['title'], data['items'][0]['link'], data['items'][0]['snippet']],
			[data['items'][1]['title'], data['items'][1]['link'], data['items'][1]['snippet']],
			[data['items'][2]['title'], data['items'][2]['link'], data['items'][2]['snippet']]  ]

print('----------------------------------------\n')
for x in xrange(0,3):
	for y in xrange(0,3):
		print(results[x][y])
	print('\n----------------\n')
