import json
import requests
import secrets
import time
import csv
from datetime import datetime
import urllib3
import argparse

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='the key to be searched. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.key:
    key = args.key
else:
    key = input('Enter the key to be searched: ')


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')


def findValue(keyName, rowName):
    for l in range(0, len(metadata)):
        if metadata[l]['key'] == keyName:
            itemDict[rowName] = metadata[l]['value']


f = csv.writer(open(filePath+'recordsMissing'+key+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['itemID']+['uri']+['collectionName']+['title'])


collectionIds = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            collectionIds.append(collectionID)

itemLinks = []
for collectionID in collectionIds:
    offset = 0
    items = ''
    while items != []:
        endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=doesnt_exist&query_val[]=&collSel[]='+collectionID+'&limit=200&offset='+str(offset)+'&expand=parentCollection'
        response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
        items = response['items']
        for item in items:
            try:
                itemLink = item['link']
                itemLinks.append(itemLink)
                print(itemLink)
            except TypeError:
                pass
        offset = offset + 200
        print(offset)

for itemLink in itemLinks:
    itemInfo = requests.get(baseURL+itemLink+'?expand=parentCollection', headers=header, cookies=cookies, verify=verify).json()
    for l in range(0, len(itemInfo)):
        collectionName = itemInfo['parentCollection']['name']
    metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    itemDict = {}
    for l in range(0, len(metadata)):
        findValue('dc.identifier.uri', 'uri')
        findValue('dc.title', 'title')
        findValue('dc.type', 'type')
    print(itemDict)
    try:
        f.writerow([itemLink]+[itemDict['uri']]+[collectionName]+[itemDict['title']]+[itemDict['type']])
    except KeyError:
        f.writerow([itemLink]+[itemDict['uri']]+[collectionName]+[itemDict['title']])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
