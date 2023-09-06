import requests
import secret
import time
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

baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections

# Add list of collection handles.
handleList = ['1774.2/46193', '1774.2/37331', '1774.2/37595']

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, params=data).cookies['JSESSIONID']
print(session)
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies).json()
userFullName = status['fullname']
print('authenticated')

for handle in handleList:
    endpoint = baseURL+'/rest/handle/'+handle
    collection = requests.get(endpoint, headers=header, cookies=cookies).json()
    collectionID = collection['uuid']
    collectionTitle = requests.get(endpoint, headers=header, cookies=cookies).json()
    itemIdentifiers = {}
    offset = 0
    items = ''
    while items != []:
        items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies)
        while items.status_code != 200:
            time.sleep(5)
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies)
        items = items.json()
        for item in items:
            itemLink = item['link']
            itemHandle = item['handle']
            itemIdentifiers[itemLink] = itemHandle
        offset = offset + 200
        print(offset)

    print('Item links and handles collected')

    all_items = []
    for itemLink, itemHandle in itemIdentifiers.items():
        itemDict = {}
        itemDict['itemLink'] = itemLink
        itemDict['handle'] = itemHandle
        metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies).json()
        keyList = ['dc.title', 'dc.date.issued', 'dc.description.abstract']
        for item in metadata:
            key = item['key']
            value = item['value']
            if key in keyList:
                if itemDict.get(key) is None:
                    itemDict[key] = value
                else:
                    oldValue = itemDict[key]
                    newValue = oldValue+'|'+value
                    itemDict[key] = newValue
        bitstreams = requests.get(baseURL+itemLink+'/bitstreams?expand=all&limit=1000', headers=header, cookies=cookies).json()
        print(len(bitstreams))
        for bitstream in bitstreams:
            itemDict = itemDict.copy()
            bitName = bitstream['name']
            itemDict['bitstream'] = bitName
            all_items.append(itemDict)

    df = pd.DataFrame.from_dict(all_items)
    print(df.head(15))
    dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    handle = handle.replace('/', '-')
    newFile = handle+'handlesAndBitstreams'+'_'+dt+'.csv'
    df.to_csv(path_or_buf=newFile, header='column_names', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))