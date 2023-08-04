import json
import requests
import secret
import time

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
email = secret.email
password = secrets.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections


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

handle = input('Enter handle: ')
endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=header, cookies=cookies).json()
collectionID = collection['uuid']
collectionTitle = requests.get(endpoint, headers=header, cookies=cookies).json()
endpoint = baseURL+'/rest/collections/'+str(collectionID)+'/items'
output = requests.get(endpoint, headers=header, cookies=cookies).json()

itemList = []
for i in range(0, len(output)):
    name = output[i]['name']
    itemID = output[i]['uuid']
    itemList.append(itemID)

f = open(filePath+handle.replace('/', '-')+'.json', 'w')
metadataGroup = []
for itemID in itemList:
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies).json()
    metadataGroup.append(metadata)
json.dump(metadataGroup, f)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))