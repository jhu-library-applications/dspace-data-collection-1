import requests
from datetime import datetime
import secrets
import time
import os
import argparse
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    fileName = args.file
else:
    fileName = input('Enter the file: ')


secretsVersion = input('To edit production server, enter secrets file name: ')
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

df_1 = pd.read_csv(fileName)
handleList = df_1.handle.to_list()

allItems = []
for handle in handleList:
    print(handle)
    endpoint = baseURL+'/rest/handle/'+handle
    item = requests.get(endpoint, headers=header, cookies=cookies).json()
    link = item['link']
    title = item['name']
    bitsLink = baseURL+link+'/bitstreams?expand=all&limit=1000'
    bitstreams = requests.get(bitsLink, headers=header, cookies=cookies).json()
    print(len(bitstreams))
    for bitstream in bitstreams:
        itemDict = {}
        bit_uuid = bitstream['uuid']
        fileName = bitstream['name']
        size = bitstream['sizeBytes']
        itemDict['item_link'] = link
        itemDict['item_handle'] = handle
        itemDict['title'] = title
        itemDict['bit_uuid'] = bit_uuid
        itemDict['file_name'] = fileName
        itemDict['size'] = size
        allItems.append(itemDict)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

df = pd.DataFrame.from_dict(allItems)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv('bitstreamsByItemHandle_'+dt+'.csv', index=False)


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
