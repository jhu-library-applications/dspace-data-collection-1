import requests
import secret
import time
import pandas as pd
import urllib3
from datetime import datetime

secretsVersion = input('To edit production server, enter name of secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

#  login info kept in secret.py file
baseURL = secret.baseURL
email = secret.email
password = secret.password

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# fileName = 'collections.csv'

# Add list of collection handles.
handleList = ['1774.2/2085']
# with open(fileName) as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         handle = row['Handle']
#         handleList.append(handle)

# authentication
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

for handle in handleList:
    endpoint = baseURL+'/rest/handle/'+handle
    collection = requests.get(endpoint, headers=header, cookies=cookies).json()
    collectionID = collection['uuid']
    itemIdentifiers = {}
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
            print(itemID)
            itemHandle = items[k]['handle']
            itemIdentifiers[itemID] = itemHandle
        offset = offset + 200
        print(offset)

    print('Item links and handles collected for '+handle)

    all_items = []
    for itemID, itemHandle in itemIdentifiers.items():
        itemDict = {}
        itemDict['itemID'] = itemID
        itemDict['itemHandle'] = itemHandle
        metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies).json()
        for item in metadata:
            key = item['key']
            value = item['value']
            if itemDict.get(key) is None:
                itemDict[key] = value
            else:
                oldValue = itemDict[key]
                newValue = oldValue+'|'+value
                itemDict[key] = newValue
        print(itemDict)
        all_items.append(itemDict)

    print('Metadata collected for '+handle)

    df = pd.DataFrame.from_dict(all_items)
    print(df.head(15))
    dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    handle = handle.replace('/', '-')
    newFile = handle+'collectionMetadata'+'_'+dt+'.csv'
    df.to_csv(path_or_buf=newFile, header='column_names', index=False)
    print('Spreadsheet made for '+handle)
    print('')

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))