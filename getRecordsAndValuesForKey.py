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
parser.add_argument('-k', '--key', help='the key to be searched. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.key:
    key = args.key
else:
    key = input('Enter the key: ')

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

f = csv.writer(open(filePath+'recordsWith'+key+'batchA.csv', 'w'))
f.writerow(['itemID']+['uri']+[key])
offset = 0
recordsEdited = 0
items = ''
itemLinks = []
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=exists&query_val[]=&collSel[]=0725999c-3531-4999-b747-215405322111&collSel[]=0220bfa8-8d07-4520-8459-52853859bcb2&collSel[]=b4d3b494-e886-4899-94eb-8da129daacd9&collSel[]=17b40f69-3b5b-4b4c-b49e-ea7ca1016716&collSel[]=bab30277-0b5f-4d11-a1e0-6cc669adc72a&collSel[]=5ea8e47e-3c38-4616-9f47-c6b46b37813c&collSel[]=97dade59-5454-45f6-874b-273ef2b3b9d9&collSel[]=93ec277c-0c14-4f6a-bc8c-09d4f375ce65&collSel[]=efcc112c-d122-43a2-be08-39fef325157e&collSel[]=461cb1f4-1dca-4c84-a84f-1aa28672ffc1&collSel[]=3271be2d-771e-49b7-b753-13198a428808&collSel[]=98a76704-25d8-40b8-8dbe-43c48d3ec0c4&collSel[]=66134136-3993-4019-9f88-17acf5f3b2e1&collSel[]=ee9ea0a6-e4ba-4ed3-a785-783288b14bfb&collSel[]=c18838d7-b4e3-44ba-8db8-30f95937fdff&collSel[]=2ed3272a-32dc-4beb-b818-81d40f5a9835&collSel[]=a60293c7-7afd-444c-b69c-d6197048d3ba&collSel[]=a1e31d19-5920-44d4-8f26-d8ab064ac189&collSel[]=1727d4e7-5952-49dc-b471-56f7a187e208&collSel[]=556bd82a-2d4d-4a33-94b4-1419d0473fac&collSel[]=718b69ac-0a0d-4e4c-b02b-41c518ea46f9&collSel[]=0be184ac-e9c8-40d4-91c4-7ca27c1fd7f9&collSel[]=e038cf6a-0cc1-4526-a1f7-bc29bc85d0cf&collSel[]=10e5df18-a5f6-40cd-aeea-fd562e318c19&collSel[]=c76282b1-897b-40a2-a699-41e596d84492&collSel[]=2f0e5cc8-20fa-443b-af4f-9efab23076c4&collSel[]=4fbd8214-81dc-4014-8ffb-a43bfd37e3c9&collSel[]=7e692697-d553-4887-8404-61a0821e42b8&collSel[]=4c0bf61d-a52e-478a-a85f-1b9fab18bdb9&collSel[]=dec32558-b1f0-4775-b126-8f31c4f2bb9a&collSel[]=35b42aa3-6da2-43a8-941b-2492da179232&collSel[]=1375a92e-f698-4796-b264-629cf74bc66b&collSel[]=80f5252c-a719-48a2-9d78-0d50e1dfc51d&collSel[]=ea9384b5-cebe-46d9-bfc3-c27ff56d0841&collSel[]=f552cb76-3721-4a18-b8b5-c7506eb64fe1&collSel[]=cd1d7922-d23d-42f2-9508-93171de759fc&collSel[]=8541ebee-c1d1-4fc1-9fc6-3e07f0ee1f48&collSel[]=c91a336e-94fd-4197-9900-516b0a25dc27&collSel[]=d62fbfd3-c44a-4036-bb62-7adf096f5926&collSel[]=68f039f2-d644-484e-9b09-882344bfa941&collSel[]=378642de-89b4-41d6-bfad-67a8c1369ffe&collSel[]=f4ee15f8-96c3-4525-a30e-85a9f9e0fe23&collSel[]=e6fd7b97-48e7-4e3f-bb95-a9cdcd7b158d&collSel[]=b7f1871d-19fb-4eb1-8d85-879dd45e3372&limit=200&offset='+str(offset)
    response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        itemLinks.append(itemLink)
    offset = offset + 200
    print(offset)
for itemLink in itemLinks:
    metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify).json()
    for l in range(0, len(metadata)):
        if metadata[l]['key'] == key:
            metadataValue = metadata[l]['value']
            for l in range(0, len(metadata)):
                if metadata[l]['key'] == 'dc.identifier.uri':
                    uri = metadata[l]['value']
            f.writerow([itemLink] + [uri] + [metadataValue])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
