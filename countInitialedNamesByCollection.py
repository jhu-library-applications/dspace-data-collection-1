import requests
import secret
import csv
import re
import time

secretVersion = input('To edit production server, enter secret file name: ')
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
for community in communities:
    communityID = community['uuid']
    collectLink = baseURL+'/rest/communities/'+str(communityID)+'/collections'
    collections = requests.get(collectLink, headers=header, cookies=cookies).json()
    for collection in collections:
        collectionID = collection['uuid']
        if collectionID not in skippedCollections:
            collectionIds.append(collectionID)

names = []
keys = ['dc.contributor.advisor', 'dc.contributor.author', 'dc.contributor.committeeMember', 'dc.contributor.editor', 'dc.contributor.illustrator', 'dc.contributor.other', 'dc.creator']

f = csv.writer(open('initialCountInCollection.csv', 'w'))
f.writerow(['collectionName']+['handle']+['initialCount'])

for number, collectionID in enumerate(collectionIds):
    initialCount = 0
    collectionsRemaining = len(collectionIds) - number
    print(collectionID, 'Collections remaining: ', collectionsRemaining)
    collection = requests.get(baseURL+'/rest/collections/'+str(collectionID), headers=header, cookies=cookies).json()
    collectionName = collection['name']
    collectionHandle = collection['handle']
    collSels = '&collSel[]=' + collectionID
    offset = 0
    recordsEdited = 0
    items = ''
    while items != []:
        for key in keys:
            endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=exists&query_val[]='+collSels+'&limit=100&offset='+str(offset)
            print(endpoint)
            response = requests.get(endpoint, headers=header, cookies=cookies).json()
            items = response['items']
            for item in items:
                itemLink = item['link']
                metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies).json()
                for metadata_element in metadata:
                    if metadata_element['key'] == key:
                        individual_name = metadata_element['value']
                        for metadata_element in metadata:
                            if metadata_element['key'] == 'dc.identifier.uri':
                                uri = metadata_element['value']
                                contains_initials = re.search(r'(\s|,|[A-Z]|([A-Z]\.))[A-Z](\s|$|\.|,)', individual_name)
                                contains_middleinitial = re.search(r'((\w{2,},\s)|(\w{2,},))\w[a-z]+', individual_name)
                                contains_parentheses = re.search(r'\(|\)', individual_name)
                                if contains_middleinitial:
                                    continue
                                elif contains_parentheses:
                                    continue
                                elif contains_initials:
                                    initialCount += 1
                                else:
                                    continue
        offset = offset + 200
        print(offset)
    if initialCount > 0:
        f.writerow([collectionName]+[baseURL+'/'+collectionHandle]+[str(initialCount).zfill(6)])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))