import requests
import secret
import csv
import time
import urllib3
import argparse

secretVersion = input('To edit production server, enter the name of the secret file: ')
if secretVersion != '':
    try:
        secret = __import__(secretVersion)
        print('Using Production')
    except ImportError:
        print('Using Stage')
else:
    print('Using Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--handle', help='community or sub-community handle')
args = parser.parse_args()

if args.handle:
    handle = args.handle
else:
    handle = input('Enter the handle: ')


baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath
skippedCollections = secret.skippedCollections

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies).json()
userFullName = status['fullname']
print('authenticated')

f = csv.writer(open('collectionDescriptions'+handle.replace('/', '-')+'.csv', 'w'))
f.writerow(['handle']+['name']+['intro'])

endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies).json()
communityID = community['uuid']

endpoint = baseURL+'/rest/communities/'+str(communityID)+'/collections'
output = requests.get(endpoint, headers=header, cookies=cookies).json()

for collection in output:
    for item in collection:
        if item == 'introductoryText':
            intro = collection['introductoryText']
            print(intro)
        elif item == 'name':
            name = collection['name']
            print(name)
        elif item == 'handle':
            handle = collection['handle']
            handle = 'http://jhir.library.jhu.edu/handle/'+handle
        else:
            pass

    f.writerow([handle]+[name]+[intro])