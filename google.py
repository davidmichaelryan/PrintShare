#Prints the title, link, and snippet of the first three google search results for a given query
# by loading the JSON results of a Google Custom Search through yaml

import urllib2
import json
import yaml
import pprint

def query(q):
    url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDLjjiXwmTfTKufnyhoKgCZhG6rmXz7lpM&cx=002838561577770740964:v1yhgyblaxo&q='
    
    q = q.replace(',', '').replace('.','').replace("''", '').replace('\n', ' ')
    q = q.split(' ')[:10]
    return q
    q = '%20'.join(q)
    newUrl = url+q
    data = urllib2.urlopen(newUrl)
    data = yaml.load(data)
    return newUrl
    if 'items' not in data:
        q = data['spelling']['correctedQuery'].replace(' ', '%20')
        newUrl = url + q
        data = urllib2.urlopen(newUrl)
        data = yaml.load(data)
        if 'items' not in data:
            return 'could not find queries'
    results = data['items'][0]['link']
    return results

# if __name__ == '__main__':
#     text = "Alien Worlds on Earth Astrobiologlst Chris McKay searches extreme landscapes for clues about life on other planets."
#     print query(text)    