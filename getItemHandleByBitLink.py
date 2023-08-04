import json
import requests
import secret
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


baseURL = secret.baseURL
email = secret.email
password = secrets.password
filePath = secret.filePath

startTime = time.time()
data = json.dumps({'email': email, 'password': password})
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type': 'application/json', 'accept': 'application/json', 'rest-dspace-token': session}
print('authenticated')

df_1 = pd.read_csv(fileName)
bitList = df_1.link.to_list()

all_items = []

for count, bitLink in enumerate(bitList):
    itemsRemaining = len(bitList) - count
    print('Items remaining: ', itemsRemaining, 'ItemID: ', bitLink)
    metadata = requests.get(baseURL+bitLink+'?expand=parent', headers=headerAuth).json()
    itemDict = {}
    itemDict['bitLink'] = bitLink
    itemDict['file'] = metadata.get('name')
    parent = metadata.get('parentObject')
    print(parent)
    itemDict['itemLink'] = parent.get('link')
    itemDict['handle'] = parent.get('handle')
    print(itemDict)
    all_items.append(itemDict)

df = pd.DataFrame.from_dict(all_items)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv('itemHandleFromBitLinks_'+dt+'.csv', index=False)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))