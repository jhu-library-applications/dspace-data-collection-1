import requests
import secrets
import time
import urllib3
import argparse
import pandas as pd
from datetime import datetime

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

# Get list of item handles from CSV file.
df_1 = pd.read_csv(fileName)
handles = df_1.handle.to_list()

itemList = []
for handle in handles:
    endpoint = baseURL+'/rest/handle/'+handle
    item = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    itemID = item['uuid']
    itemList.append(itemID)

print('Item ids collected')

all_items = []
for itemID in itemList:
    itemDict = {}
    itemDict['itemID'] = itemID
    mURL = baseURL+'/rest/items/'+itemID+'/metadata'
    metadata = requests.get(mURL, headers=header, cookies=cookies, verify=verify).json()
    for item in metadata:
        key = item['key']
        value = item['value']
        if itemDict.get(key) is None:
            itemDict[key] = value
        else:
            oldValue = itemDict[key]
            newValue = oldValue+'|'+value
            itemDict[key] = newValue
    all_items.append(itemDict)

print('Metadata collected')

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
newFile = 'selectedRecordMetadata'+dt+'.csv'
df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
