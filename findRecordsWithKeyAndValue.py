import requests
import secret
import time
import argparse
from datetime import datetime
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
parser.add_argument('-k', '--searchKey', help='the key to be searched')
parser.add_argument('-v', '--searchValue', help='the value to be searched')
args = parser.parse_args()

if args.searchKey:
    searchKey = args.searchKey
else:
    searchKey = input('Enter the searchKey: ')
if args.searchValue:
    searchValue = args.searchValue
else:
    searchValue = input('Enter the searchValue: ')

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


offset = 0
recordsEdited = 0
items = ''
itemLinks = []
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]='+searchKey+'&query_op[]=equals&query_val[]='+searchValue+'&limit=200&offset='+str(offset)
    print(endpoint)
    response = requests.get(endpoint, headers=header, cookies=cookies).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        itemLinks.append(itemLink)
    offset = offset + 200
    print(offset)

all_items = []
for itemLink in itemLinks:
    metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies).json()
    itemDict = {}
    itemDict['itemLink'] = itemLink
    for item in metadata:
        key = item['key']
        value = item['value']
        if key == searchKey and value == searchValue:
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
newFile = 'recordsWith'+searchKey+'And'+searchValue+'_'+dt+'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))