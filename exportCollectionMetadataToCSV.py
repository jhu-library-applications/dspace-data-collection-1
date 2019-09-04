import json
import requests
import secrets
import time
import csv
from collections import Counter
import urllib3
import argparse

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

#login info kept in secrets.py file
baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

# parser = argparse.ArgumentParser()
# parser.add_argument('-i', '--handle', help='handle of the collection to retreive. optional - if not provided, the script will ask for input')
# args = parser.parse_args()
#
# if args.handle:
#     handle = args.handle
# else:
#     handle = input('Enter collection handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

handleList = ['1774.2/40426', '1774.2/38221', '1774.2/33509', '1774.2/38695', '1774.2/38219', '1774.2/38220', '1774.2/38696', '1774.2/44572', '1774.2/32581', '1774.2/32579', '1774.2/44451', '1774.2/44448', '1774.2/34787', '1774.2/34121', '1774.2/36252', '1774.2/33646', '1774.2/32829', '1774.2/40630', '1774.2/35703', '1774.2/33500', '1774.2/36506', '1774.2/40428', '1774.2/33059', '1774.2/882', '1774.2/33951', '1774.2/59439', '1774.2/33259', '1774.2/33431', '1774.2/35587', '1774.2/843', '1774.2/33512', '1774.2/33842', '1774.2/32768', '1774.2/33503', '1774.2/32822', '1774.2/61377', '1774.2/40421', '1774.2/40418', '1774.2/40419', '1774.2/40420', '1774.2/6', '1774.2/36431', '1774.2/36558', '1774.2/35483', '1774.2/36209', '1774.2/35927', '1774.2/35930', '1774.2/35931', '1774.2/35929', '1774.2/35928', '1774.2/58586', '1774.2/40905', '1774.2/35404', '1774.2/36054', '1774.2/59', '1774.2/32505', '1774.2/32749', '1774.2/35704', '1774.2/36422', '1774.2/32588', '1774.2/32750', '1774.2/33096', '1774.2/32646', '1774.2/59948', '1774.2/35406', '1774.2/32589', '1774.2/35407', '1774.2/32751', '1774.2/32586', '1774.2/32752', '1774.2/36250', '1774.2/33533', '1774.2/33785', '1774.2/33705', '1774.2/880', '1774.2/32807', '1774.2/841', '1774.2/34012', '1774.2/34147', '1774.2/35932', '1774.2/35933', '1774.2/33796', '1774.2/37744', '1774.2/61241', '1774.2/44563', '1774.2/44564', '1774.2/41445', '1774.2/44736', '1774.2/32721', '1774.2/36448', '1774.2/46193', '1774.2/37331', '1774.2/37595', '1774.2/37597', '1774.2/1023', '1774.2/3', '1774.2/2085', '1774.2/33495', '1774.2/40923', '1774.2/844', '1774.2/845', '1774.2/838', '1774.2/32570']

#authentication
startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')

for handle in handleList:
    endpoint = baseURL+'/rest/handle/'+handle
    collection = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    print(collection)
    collectionID = collection['uuid']
    collectionTitle = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    itemList = {}
    offset = 0
    items = ''
    while items != []:
        items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
        while items.status_code != 200:
            time.sleep(5)
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
        items = items.json()
        for k in range (0, len (items)):
            itemID = items[k]['uuid']
            print(itemID)
            itemHandle = items[k]['handle']
            itemList[itemID] = itemHandle
        offset = offset + 200
        print(offset)

    keyList = []
    for itemID in itemList:
        print(baseURL+'/rest/items/'+str(itemID)+'/metadata')
        metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
        for metadataElement in metadata:
            key = metadataElement['key']
            if key not in keyList and key != 'dc.description.provenance':
                keyList.append(key)
                print(itemID, key)

    keyListHeader = ['itemID']
    keyListHeader = keyListHeader + keyList
    print(keyListHeader)
    f=csv.writer(open(filePath+itemHandle.replace('/','-')+'Metadata.csv', 'w'))
    f.writerow(keyListHeader)

    itemRows = []
    for itemID in itemList:
        itemRow = dict.fromkeys(keyListHeader, '')
        itemRow['itemID'] = itemID
        print(itemID)
        metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
        for metadataElement in metadata:
            for key in keyListHeader:
                if metadataElement['key'] == key:
                    value = metadataElement['value']+'|'
                    try:
                        itemRow[key] = itemRow[key] + value
                    except:
                        itemRow[key] = value
        itemList = []
        for key in keyListHeader:
            itemList.append(itemRow[key][:len(itemRow[key])-1])
        f.writerow(itemList)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ','%d:%02d:%02d' % (h, m, s))
