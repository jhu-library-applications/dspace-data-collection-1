import requests
import secret
import time
import csv

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

# login info kept in secret.py file
baseURL = secret.baseURL
email = secrets.email
password = secret.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections

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

endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies).json()

# create list of all item IDs
itemList = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        print(collectionID)
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
                print(offset)
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ', '%d:%02d:%02d' % (h, m, s))

# retrieve metadata from all items
keyList = []
for itemID in itemList:
    print(itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies).json()
    for i in range(0, len(metadata)):
        key = metadata[i]['key']
        if key not in keyList:
            keyList.append(key)

keyListHeader = ['collectionNameColumn']
keyList.sort()
keyListHeader = keyListHeader + keyList
f = csv.writer(open(filePath+'collectionsKeysMatrix.csv', 'w'))
f.writerow(keyListHeader)

for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    communityName = communities[i]['name']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            print('Collection skipped')
        else:
            collectionItemList = []
            collectionName = collections[j]['name']
            fullName = communityName+' - '+collectionName
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=header, cookies=cookies)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=header, cookies=cookies)
            items = items.json()
            for i in range(0, len(items)):
                itemID = items[i]['uuid']
                collectionItemList.append(itemID)

            collectionKeyCount = {}
            for key in keyList:
                collectionKeyCount[key] = 0
            for itemID in collectionItemList:
                print(itemID)
                metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies).json()
                for i in range(0, len(metadata)):
                    itemKey = metadata[i]['key']
                    for key in keyList:
                        if itemKey == key:
                            collectionKeyCount[key] = collectionKeyCount[key]+1

            collectionKeyCountList = []
            for k, v in collectionKeyCount.items():
                collectionKeyCountList.append(k+' '+str(v))
            collectionKeyCountList.sort()
            updatedCollectionKeyCountList = []
            for entry in collectionKeyCountList:
                count = entry[entry.index(' ')+1:]
                updatedCollectionKeyCountList.append(count)
            fullName = [fullName]
            updatedCollectionKeyCountList = fullName + updatedCollectionKeyCountList
            f.writerow(updatedCollectionKeyCountList)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)