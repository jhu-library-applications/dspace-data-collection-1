import requests
import secrets
import time
import csv
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

# login info kept in secrets.py file
baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName', help='the CSV file of record handles')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the CSV file of record handles (including \'.csv\'): ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# authentication
startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')


handles = []
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        handles.append(row['handle'])


itemList = []
for handle in handles:
    endpoint = baseURL+'/rest/handle/'+handle
    item = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    itemID = item['uuid']
    itemList.append(itemID)

print(itemList)

keyList = []
for itemID in itemList:
    mURL = baseURL+'/rest/items/'+itemID+'/metadata'
    metadata = requests.get(mURL, headers=header, cookies=cookies, verify=verify).json()
    for metadataElement in metadata:
        key = metadataElement['key']
        if key not in keyList and key != 'dc.description.provenance':
            keyList.append(key)
            print(itemID, key)

keyListHeader = ['itemID']
keyListHeader = keyListHeader + keyList
print(keyListHeader)
keyListHeader = sorted(keyListHeader)
f = csv.writer(open(filePath+'selectedRecordMetadata.csv', 'w'))
f.writerow(keyListHeader)

itemRows = []
for itemID in itemList:
    itemRow = dict.fromkeys(keyListHeader, '')
    itemRow['itemID'] = itemID
    print(itemID)
    mURL = baseURL+'/rest/items/'+itemID+'/metadata'
    metadata = requests.get(mURL, headers=header, cookies=cookies, verify=verify).json()
    for metadataElement in metadata:
        for key in keyListHeader:
            if metadataElement['key'] == key:
                value = metadataElement['value']+'|'
                try:
                    itemRow[key] = itemRow[key] + value
                except:
                    itemRow[key] = value
    print(itemRow)
    itemRows.append(itemRow)

for item in itemRows:
    item = dict(sorted(item.items()))
    print(item)
    values = list(item.values())
    for index, x in enumerate(values):
        try:
            last = x[-1]
            if last == "|":
                x = x[:-1]
                values[index] = x
        except IndexError:
            pass
    f.writerows([values])
