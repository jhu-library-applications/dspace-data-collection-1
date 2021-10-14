import requests
import secrets
import time
import argparse

secretsVersion = input('To edit production, enter the secrets file name: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='the key to be searched')
args = parser.parse_args()

if args.key:
    key = args.key
else:
    key = input('Enter the key: ')


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


collectionIds = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            collectionIds.append(collectionID)

print('Collection information collected')

itemLinks = []
for collectionID in collectionIds:
    offset = 0
    items = ''
    while items != []:
        endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=exists&query_val[]=&collSel[]='+collectionID+'&limit=200&offset='+str(offset)
        response = requests.get(endpoint, headers=header, cookies=cookies).json()
        items = response['items']
        for item in items:
            itemMetadataProcessed = []
            itemLink = item['link']
            itemLinks.append(itemLink)
        offset = offset + 200
        print(offset)

print('Item links collected')

for itemLink in itemLinks:
    metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies).json()
    for l in range(0, len(metadata)):
        if metadata[l]['key'] == key:
            metadataValue = metadata[l]['value']
            for l in range(0, len(metadata)):
                if metadata[l]['key'] == 'dc.identifier.uri':
                    uri = metadata[l]['value']
            f.writerow([itemLink] + [uri] + [metadataValue])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
