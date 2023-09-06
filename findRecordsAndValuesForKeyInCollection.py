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
parser.add_argument('-k', '--searchKey')
parser.add_argument('-i', '--handle')
args = parser.parse_args()

if args.searchKey:
    searchKey = args.searchKey
else:
    searchKey = input('Enter the searchKey: ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter collection handle: ')

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
userFullName = status['fullname']
print('authenticated')

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=header, cookies=cookies).json()
collectionID = collection['uuid']
collSels = '&collSel[]=' + collectionID


offset = 0
recordsEdited = 0
items = ''
itemLinks = []
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]='+searchKey+'&query_op[]=exists&query_val[]='+collSels+'&limit=200&offset='+str(offset)
    print(endpoint)
    response = requests.get(endpoint, headers=header, cookies=cookies).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        itemLinks.append(itemLink)
    offset = offset + 200
    print(offset)
print('Item links collected')

all_items = []
for itemLink in itemLinks:
    metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies).json()
    itemDict = {}
    itemDict['itemLink'] = itemLink
    for item in metadata:
        key = item['key']
        value = item['value']
        if key == searchKey:
            itemDict[key] = value
        elif key == 'dc.identifier.uri':
            itemDict[key] = value
        else:
            pass
    if itemDict.get(searchKey):
        all_items.append(itemDict)

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
handle = handle.replace('/', '-')
newFile = handle+'With'+searchKey+'_'+dt+'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))