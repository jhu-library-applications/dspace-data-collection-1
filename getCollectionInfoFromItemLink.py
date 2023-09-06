import requests
import secret
import time
import csv
from datetime import datetime
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
parser.add_argument('-f', '--fileName', help='the filename of metadata CSV')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the metadata CSV file (including \'.csv\'): ')


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