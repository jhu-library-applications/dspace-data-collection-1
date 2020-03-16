import requests
from datetime import datetime
import secrets
import time
import csv
import urllib3
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')

args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter the file: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
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

bit_dict = []
with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        itemHandle = row['handle']
        bitstreams_names = row['pres_bits']
        endpoint = baseURL+'/rest/handle/'+itemHandle
        item = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
        link = item['link']
        bitstreams = requests.get(baseURL+link+'/bitstreams?expand=all&limit=1000', headers=header, cookies=cookies, verify=verify).json()
        for bitstream in bitstreams:
            bit_uuid = bitstream['uuid']
            fileName = bitstream['name']
            size = bitstream['sizeBytes']
            if fileName in bitstreams_names:
                bit_dict.append({'handle': itemHandle, 'bit_uuid': bit_uuid, 'bit_name': fileName, 'size': size})

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

df = pd.DataFrame.from_dict(bit_dict)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='bitstreamsSizes_'+dt+'.csv', header='column_names', index=False)


elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
