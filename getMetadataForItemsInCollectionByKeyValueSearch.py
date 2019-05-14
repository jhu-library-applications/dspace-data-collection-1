import json
import requests
import secrets
import csv
import time
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
parser.add_argument('-c', '--collect', help='collectionHandle of the collection to retreive. optional - if not provided, the script will ask for input')
parser.add_argument('-v', '--value', help='valueSearch of the collection to retreive. optional - if not provided, the script will ask for input')
parser.add_argument( '-k', '--key', help='keySearch of the collection to retreive. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.collect:
    collectionHandle = args.collect
else:
    collectionHandle = input('Enter handle: ')

if args.value:
    valueSearch = args.value
else:
    valueSearch = input('what value are you looking for today? ')

if args.key:
    keySearch = args.key
else:
    keySearch = input('what key will this value be contained in?(Please format as dc.key) : ')

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def findValue(keyName, rowName):
    for l in range (0, len (metadata)):
        if metadata[l]['key'] == keyName:
            itemDict[rowName] = metadata[l]['value'].encode('utf-8')


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

f=csv.writer(open(filePath+'recordsWith.csv', 'w'))
f.writerow(['itemID']+['uri']+['title']+['formatExtent']+['type']+['descriptionAbstract'])
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    itemDict = {}
    for l in range (0, len (metadata)):
        if metadata[l]['key'] == keySearch and metadata[l]['value'] == valueSearch:
            findValue('dc.identifier.uri', 'uri')
            findValue('dc.title', 'title')
            findValue('dc.format.extent', 'formatExtent')
            findValue('dc.type', 'type')
            findValue('dc.description.abstract', 'descriptionAbstract')
            f.writerow([itemID]+[itemDict['uri']]+[itemDict['title']]+[itemDict['formatExtent']]+[itemDict['type']]+[itemDict['descriptionAbstract']])

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
