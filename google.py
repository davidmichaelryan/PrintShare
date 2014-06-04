#Prints the title, link, and snippet of the first five google search results for a given query
# by loading the JSON results of a Google Custom Search through yaml

import urllib2
import json
import yaml
import pprint
import string 

def clean(x):
    if not x.isdigit():
        if any(i.isdigit() for i in x):
            return False
    return True

def query(q):
    url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDLjjiXwmTfTKufnyhoKgCZhG6rmXz7lpM&cx=002838561577770740964:v1yhgyblaxo&q='
    
    q = q.replace(',', '').replace('.','').replace("''", '').replace('\n', ' ').replace('-',' ')
    q = q.split(' ')

    q = [x for x in q if clean(x)]

    q = '%20'.join(q[:8])
    newUrl = url+q
    data = urllib2.urlopen(newUrl)
    data = yaml.load(data)
    if 'items' not in data:
        q = data['spelling']['correctedQuery'].replace(' ', '%20')
        newUrl = url + q
        data = urllib2.urlopen(newUrl)
        data = yaml.load(data)
        if 'items' not in data:
            return 'could not find queries'
    results = [[] for x in xrange(5)]
    for i in range(len(data['items'])):
        if i >= 5:
            break
        else:
            results[i].append(data['items'][i]['link'])
            results[i].append(data['items'][i]['title'])
    return results 