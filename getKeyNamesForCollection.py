import json
import requests
import secrets
import csv
import time
import urllib3

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
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

collectionHandle = input('enter collection handle please:' )


startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print('authenticated')


itemList = []
endpoint = baseURL+'/rest/handle/'+collectionHandle
collection = requests.get(endpoint, headers=headerAuth, verify=verify).json()
collectionID = collection['uuid']
print(collectionID)
offset = 0
items = ''
while items != []:
    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=headerAuth, verify=verify)
    while items.status_code != 200:
        time.sleep(5)
        items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=headerAuth, verify=verify)
    items = items.json()
    for k in range (0, len (items)):
        itemID = items[k]['uuid']
        itemList.append(itemID)
    offset = offset + 200
    print(offset)
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ','%d:%02d:%02d' % (h, m, s))

dcElements = []
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    for l in range (0, len(metadata)):
        keys = metadata[l]['key']
        keys = str(keys)
        if keys in dcElements:
            pass
        if keys not in dcElements:
            dcElements.append(keys)
print(len(dcElements))
print("\'] + [\'".join(dcElements))
