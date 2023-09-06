import requests
import secret
import time
import argparse
from datetime import datetime
import pandas as pd

secretVersion = input('To edit production server, enter the name of the secret file: ')
if secretVersion != '':
    try:
        secret = __import__(secretVersion)
        print('Using Production')
    except ImportError:
        print('Using Stage')
else:
    print('Using Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-1', '--searchKey')
parser.add_argument('-2', '--searchKey2')
parser.add_argument('-i', '--handle')
args = parser.parse_args()

if args.searchKey:
    searchKey = args.searchKey
else:
    searchKey = input('Enter first searchKey: ')
if args.searchKey2:
    searchKey2 = args.searchKey2
else:
    searchKey2 = input('Enter second searchKey: ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter community handle: ')

baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies).json()
print('authenticated')

endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies).json()
communityID = community['uuid']

itemList = []
endpoint = baseURL+'/rest/communities'
collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
for j in range(0, len(collections)):
    collectionID = collections[j]['uuid']
    print(collectionID)
    if collectionID not in skippedCollections:
        offset = 0
        items = ''
        while items != []:
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies)
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


all_items = []
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies).json()
    itemDict = {}
    itemDict['itemID'] = itemID
    keyList = [searchKey, searchKey2, 'dc.identifier.uri']
    for item in metadata:
        key = item['key']
        value = item['value']
        if key in keyList:
            if itemDict.get(key) is None:
                itemDict[key] = value
            else:
                oldValue = itemDict[key]
                newValue = oldValue+'|'+value
                itemDict[key] = newValue
        else:
            pass
    all_items.append(itemDict)

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
collection = handle.replace('/', '_')
newFile = collection+'Comparing'+searchKey+'And'+searchKey2+'_'+dt+'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))