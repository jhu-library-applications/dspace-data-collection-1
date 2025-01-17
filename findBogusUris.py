
import requests
import secret
import csv
import time

secretVersion = input('To edit production server, enter the name of the secret file: ')
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
handlePrefix = secret.handlePrefix
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

f = csv.writer(open(filePath+'bogusUris.csv', 'w'))
f.writerow(['itemID']+['uri'])
offset = 0
recordsEdited = 0
items = ''
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]=dc.identifier.uri&query_op[]=doesnt_contain&query_val[]='+handlePrefix+'&limit=200&offset='+str(offset)
    print(endpoint)
    response = requests.get(endpoint, headers=header, cookies=cookies).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies).json()
        for l in range(0, len(metadata)):
            if metadata[l]['key'] == 'dc.identifier.uri':
                uri = str(metadata[l]['value'])
                if uri.startswith(handlePrefix) is False:
                    f.writerow([itemLink]+[uri])
    offset = offset + 200
    print(offset)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))