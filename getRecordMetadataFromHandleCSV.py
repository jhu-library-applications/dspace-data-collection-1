from json import JSONDecodeError
import json
import requests
import secret
from datetime import datetime
import time
import argparse
import pandas as pd

secretVersion = input('To edit production, enter secret filename: ')
if secretVersion != '':
    try:
        secret = __import__(secretVersion)
        print('Using Production')
    except ImportError:
        print('Using Stage')
else:
    print('Using Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter file of handles (including \'.csv\'): ')


baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath

startTime = time.time()
data = json.dumps({'email': email, 'password': password})
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header,
                        data=data).content
headerAuth = {'content-type': 'application/json', 'accept':
              'application/json', 'rest-dspace-token': session}
print('authenticated')

df_1 = pd.read_csv(fileName)
itemList = df_1.itemID.to_list()

all_items = []

for count, itemLink in enumerate(itemList):
    itemsRemaining = len(itemList) - count
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemLink)
    try:
        metadata = requests.get(baseURL+itemLink+'/metadata',
                                headers=headerAuth).json()
        itemDict = {}
        itemDict['itemID'] = itemLink
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
        print(itemDict)
        all_items.append(itemDict)
    except JSONDecodeError:
        itemDict = {}
        itemDict['itemID'] = itemLink
        all_items.append(itemDict)

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv('recordMetadataFromHandles'+dt+'.csv', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))