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
parser.add_argument('-h', '--handle', help='the community or sub-community to be searched. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.handle:
    handle = args.handle
else:
    handle = input('Enter the handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')

f=csv.writer(open('collectionDescriptions'+handle.replace('/','-')+'.csv', 'w'))
f.writerow(['handle']+['name']+['intro'])

endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
communityID = community['uuid']

endpoint = baseURL+'/rest/communities/'+str(communityID)+'/collections'
output = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()

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
