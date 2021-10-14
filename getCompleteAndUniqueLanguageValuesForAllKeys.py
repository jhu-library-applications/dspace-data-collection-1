import requests
import secrets
import time
from datetime import datetime
import pandas as pd

secretsVersion = input('To edit production, enter the secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
skippedCollections = secrets.skippedCollections

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
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies)
                items = items.json()
                for k in range(0, len(items)):
                    itemID = items[k]['uuid']
                    itemList.append(itemID)
                offset = offset + 200
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ', "%d:%02d:%02d" % (h, m, s))

valueList = []
for count, itemLink in enumerate(itemList):
    itemsRemaining = len(itemList) - count
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemLink)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata?=expand', headers=header).json()
    itemDict = {}
    itemDict['itemID'] = itemID
    for item in metadata:
        key = item['key']
        language = item['language']
        if itemDict.get(key) is None:
            itemDict[key] = language
        else:
            pass
    valueList.append(itemDict)


df = pd.DataFrame.from_dict(valueList)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf=filePath+'languageValuesForKeys_'+dt+'.csv', header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
