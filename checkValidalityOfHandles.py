import json
import requests
import secrets
from datetime import datetime
import time
import argparse
import pandas as pd

secretsVersion = input('To edit production, enter the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter file of handles (including \'.csv\'): ')


baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

startTime = time.time()
data = json.dumps({'email': email, 'password': password})
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type': 'application/json', 'accept': 'application/json', 'rest-dspace-token': session}
print('authenticated')

df_1 = pd.read_csv(fileName)
handleList = df_1.handle.to_list()
handleCount = len(handleList)
all_items = []
for count, handle in enumerate(handleList):
    print(handleCount-count)
    try:
        itemInfo = requests.get(baseURL+'/rest/handle/'+handle, headers=headerAuth, timeout=1)
    except requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
        itemInfo = 'timeout'
    print(itemInfo)
    tinyDict = {'handle': handle, 'response':itemInfo}
    all_items.append(tinyDict)

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv('recordMetadataFromHandles'+dt+'.csv', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
