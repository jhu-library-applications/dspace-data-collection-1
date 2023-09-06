import requests
import secret
import csv
import time
import os.path
from collections import Counter
from datetime import datetime


secretVersion = input('To edit production server, enter the name of the secret file: ')
if secretVersion != '':
    try:
        secret = __import__(secretVersion)
        print('Using Production')
    except ImportError:
        print('Using Stage')
else:
    print('Using Stage')

baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections

handle = input('Enter community handle: ')

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

itemList = []
endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies).json()
communityName = community['name'].replace(' ', '')
communityID = community['uuid']

filePathComplete = filePath+'completeValueLists'+communityName+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'/'
filePathUnique = filePath+'uniqueValueLists'+communityName+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'/'

collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
for j in range(0, len(collections)):
    collectionID = collections[j]['uuid']
    if collectionID not in skippedCollections:
        offset = 0
        items = ''
        while items != []:
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=100&offset='+str(offset), headers=header, cookies=cookies)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=100&offset='+str(offset), headers=header, cookies=cookies)
            items = items.json()
            for k in range(0, len(items)):
                itemID = items[k]['uuid']
                itemList.append(itemID)
            offset = offset + 100
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: '+'%d:%02d:%02d' % (h, m, s))

os.mkdir(filePathComplete)
os.mkdir(filePathUnique)
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies).json()
    for l in range(0, len(metadata)):
        if metadata[l]['key'] != 'dc.description.provenance':
            key = metadata[l]['key']
            try:
                value = metadata[l]['value']
            except:
                value = ''
            if os.path.isfile(filePathComplete+key+'ValuesComplete.csv') is False:
                f = csv.writer(open(filePathComplete+key+'ValuesComplete.csv', 'w'))
                f.writerow(['itemID']+['value'])
                f.writerow([itemID]+[value])
            else:
                f = csv.writer(open(filePathComplete+key+'ValuesComplete.csv', 'a'))
                f.writerow([itemID]+[value])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Complete value list creation time: ', '%d:%02d:%02d' % (h, m, s))

for fileName in os.listdir(filePathComplete):
    reader = csv.DictReader(open(filePathComplete+fileName))
    fileName = fileName.replace('Complete', 'Unique')
    valueList = []
    for row in reader:
        valueList.append(row['value'])
    valueListCount = Counter(valueList)
    f = csv.writer(open(filePathUnique+fileName, 'w'))
    f.writerow(['value']+['count'])
    for key, value in valueListCount.items():
        f.writerow([key]+[str(value).zfill(6)])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))