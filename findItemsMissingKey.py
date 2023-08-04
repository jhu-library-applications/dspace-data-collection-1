import requests
import secret
import time
from datetime import datetime
import argparse
import pandas as pd

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--searchKey', help='the key to be searched. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.searchKey:
    searchKey = args.searchKey
else:
    searchKey = input('Enter the key to be searched: ')

baseURL = secret.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
skippedCollections = secret.skippedCollections

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies).json()
userFullName = status['fullname']
print('authenticated')

collectionIds = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            collectionIds.append(collectionID)

print('Collection IDs gathered')

itemLinks = []
for collectionID in collectionIds:
    offset = 0
    items = ''
    while items != []:
        endpoint = baseURL+'/rest/filtered-items?query_field[]='+searchKey+'&query_op[]=doesnt_exist&query_val[]=&collSel[]='+collectionID+'&limit=200&offset='+str(offset)+'&expand=parentCollection'
        response = requests.get(endpoint, headers=header, cookies=cookies).json()
        items = response['items']
        for item in items:
            try:
                itemLink = item['link']
                itemLinks.append(itemLink)
                print(itemLink)
            except TypeError:
                pass
        offset = offset + 200
        print(offset)

print('Item links collected')

all_items = []
for itemLink in itemLinks:
    itemDict = {}
    itemDict['itemLink'] = itemLink
    itemInfo = requests.get(baseURL+itemLink+'?expand=parentCollection', headers=header, cookies=cookies).json()
    for item in itemInfo:
        parent = item['parentCollection']
        collectionName = parent['name']
        itemDict['collection'] = collectionName
    metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies).json()
    keyList = ['dc.title', 'dc.identifier.uri', 'dc.type']
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
    all_items.append(itemDict)

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
newFile = 'itemsMissing'+searchKey+'_'+dt+'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))