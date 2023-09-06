import requests
import secret
import time
import pandas as pd
import urllib3
from datetime import datetime

secretVersion = input('To edit production server, enter name of secret file: ')
if secretVersion != '':
    try:
        secret = __import__(secretVersion)
        print('Using Production')
    except ImportError:
        print('Using Stage')
else:
    print('Using Stage')

#  login info kept in secret.py file
baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

handle = '1774.2/32585'
endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies).json()
communityID = community['uuid']
print(communityID)

endpoint = baseURL+'/rest/communities/'+communityID+'/collections'
collections = requests.get(endpoint, headers=header, cookies=cookies).json()
itemList = []
for collection in collections:
    collectionID = collection['uuid']
    print('collection: '+collectionID)
    offset = 0
    items = ''
    while items != []:
        endpoint = baseURL+'/rest/collections/'+collectionID+'/items?limit=200&offset='+str(offset)
        items = requests.get(endpoint, headers=header, cookies=cookies)
        while items.status_code != 200:
            time.sleep(2)
            endpoint = baseURL+'/rest/collections/'+collectionID+'/items?limit=200&offset='+str(offset)
            items = requests.get(endpoint, headers=header, cookies=cookies)
        items = items.json()
        print(len(items))
        for item in items:
            itemID = item['uuid']
            itemHandle = item['handle']
            print(itemHandle)
            itemList.append({'itemID': itemID, 'itemHandle': itemHandle})
        offset = offset + 200
        print(offset)

print('Item links and handles collected for '+handle)

df = pd.DataFrame.from_dict(itemList)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
handle = handle.replace('/', '-')
newFile = 'listOfRecordsInCommunity'+handle+'_'+dt+'.csv'
df.to_csv(newFile, header='column_names', index=False)


logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))