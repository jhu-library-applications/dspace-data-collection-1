import requests
import secrets
import time
import urllib.request


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

fileLocation = ''
itemHandle = ''
endpoint = baseURL+'/rest/handle/'+itemHandle
item = requests.get(endpoint, headers=header, cookies=cookies).json()
link = item['link']
bitstreams = requests.get(baseURL+link+'/bitstreams?expand=all&limit=1000', headers=header, cookies=cookies).json()
for bitstream in bitstreams:
    fileName = bitstream['name']
    retrieveLink = bitstream['retrieveLink']
    print(retrieveLink)
    retrieveLink = baseURL+retrieveLink
    print(retrieveLink)
    urllib.request.urlretrieve(retrieveLink, fileLocation+fileName)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
