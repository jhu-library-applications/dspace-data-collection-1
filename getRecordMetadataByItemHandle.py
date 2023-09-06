import json
import requests
import secret
from datetime import datetime
import time
import argparse
import pandas as pd

secretVersion = input('To edit production, enter the secret file: ')
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
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies).json()
userFullName = status['fullname']
print('authenticated')

# df_1 = pd.read_csv(fileName)
# handleList = df_1.handle.to_list()
handleList = ['1774.2/62107']
all_items = []
itemList = []

for count, handle in enumerate(handleList):
    itemInfo = requests.get(baseURL+'/rest/handle/'+handle, headers=header).json()
    itemLink = itemInfo['link']
    itemList.append(itemLink)

for count, itemLink in enumerate(itemList):
    itemsRemaining = len(itemList) - count
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemLink)
    metadata = requests.get(baseURL+itemLink+'/metadata', headers=header).json()
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

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='recordMetadataFromHandles'+dt+'.csv', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))