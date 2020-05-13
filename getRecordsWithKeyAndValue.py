import requests
import secrets
import time
import urllib3
import argparse
from datetime import datetime
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
parser.add_argument('-k', '--searchKey', help='the searchKey to be searched. optional - if not provided, the script will ask for input')
parser.add_argument('-v', '--searchValue', help='the searchValue to be searched. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.searchKey:
    searchKey = args.searchKey
else:
    searchKey = input('Enter the searchKey: ')
if args.searchValue:
    searchValue = args.searchValue
else:
    searchValue = input('Enter the searchValue: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

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


offset = 0
recordsEdited = 0
items = ''
itemLinks = []
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]='+searchKey+'&query_op[]=equals&query_val[]='+searchValue+'&limit=200&offset='+str(offset)
    print(endpoint)
    response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        itemLinks.append(itemLink)
    offset = offset + 200
    print(offset)

all_items = []
for itemLink in itemLinks:
    metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies, verify=verify).json()
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
newFile = 'recordsWith'+searchKey+'And'+searchValue+'_'+dt'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))
