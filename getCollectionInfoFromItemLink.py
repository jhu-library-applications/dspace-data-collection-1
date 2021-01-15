import requests
import secrets
import time
import csv
from datetime import datetime
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
parser.add_argument('-f', '--fileName', help='the filename of metadata CSV')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the metadata CSV file (including \'.csv\'): ')


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


f = csv.writer(open(filePath+'collectionDataFromItemList'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))

with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        itemID = row['itemID']
        date = row['value']
        logInformation = [itemID]
        print(itemID)
        itemInfo = requests.get(baseURL+str(itemID)+'/?expand=parentCollection', headers=header, cookies=cookies).json()
        parentCollection = itemInfo.get('parentCollection')
        collectionName = parentCollection.get('name')
        f.writerow([collectionName]+[itemID]+[date])


logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)
