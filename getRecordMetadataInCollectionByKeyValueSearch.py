import json
import requests
import secret
from datetime import datetime
import time

import argparse
import pandas as pd

secretVersion = input('To edit production, enter the secret file name: ')
if secretVersion != '':
    try:
        secret = __import__(secretVersion)
        print('Using Production')
    except ImportError:
        print('Using Stage')
else:
    print('Using Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--handle')
parser.add_argument('-v', '--value')
parser.add_argument('-k', '--key')
args = parser.parse_args()

if args.handle:
    handle = args.handle
else:
    handle = input('Enter handle: ')
if args.value:
    valueSearch = args.value
else:
    valueSearch = input('what value are you looking for today? ')
if args.key:
    keySearch = args.key
else:
    keySearch = input('what key will this value be contained in?(Please format as dc.key) : ')

baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath

startTime = time.time()
data = json.dumps({'email': email, 'password': password})
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type': 'application/json', 'accept': 'application/json', 'rest-dspace-token': session}
print('authenticated')

all_items = []
itemList = []

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=headerAuth).json()
collectionID = collection['uuid']
print(collectionID)

offset = 0
items = ''
while items != []:
    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=headerAuth)
    while items.status_code != 200:
        time.sleep(5)
        items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=headerAuth)
    items = items.json()
    for k in range(0, len(items)):
        itemID = items[k]['uuid']
        itemList.append(itemID)
    offset = offset + 200
    print(offset)
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ', '%d:%02d:%02d' % (h, m, s))


for count, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - count
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL+'/rest/items/'+itemID+'/metadata', headers=headerAuth).json()
    itemDict = {}
    itemDict['itemID'] = itemID
    for item in metadata:
        key = item['key']
        value = item['value']
        value = str(value)
        if itemDict.get(key) is None:
            itemDict[key] = value
        else:
            oldValue = itemDict[key]
            newValue = oldValue+'|'+value
            itemDict[key] = newValue
        value = itemDict.get(keySearch)
        if value:
            value = value.split('|')
            for v in value:
                if v == valueSearch:
                    all_items.append(itemDict)
                    break
                else:
                    pass

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
collection = handle.replace('/', '_')
newFile = collection+'_'+keySearch+'_'+valueSearch+'_'+dt+'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))