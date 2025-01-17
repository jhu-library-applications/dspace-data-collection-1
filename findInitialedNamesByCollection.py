import requests
import secret
import csv
import re
import time
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
parser.add_argument('-i', '--handle', help='handle of the collection to retreive')
args = parser.parse_args()

if args.handle:
    handle = args.handle
else:
    handle = input('Enter collection handle: ')

baseURL = secret.baseURL
email = secret.email
password = secret.password
filePath = secret.filePath

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

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=header, cookies=cookies).json()
collectionID = collection['uuid']
collSels = '&collSel[]=' + collectionID

names = []
keys = ['dc.contributor.advisor', 'dc.contributor.author', 'dc.contributor.committeeMember', 'dc.contributor.editor', 'dc.contributor.illustrator', 'dc.contributor.other', 'dc.creator']

offset = 0
recordsEdited = 0
items = ''
while items != []:
    for key in keys:
        endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=exists&query_val[]='+collSels+'&limit=100&offset='+str(offset)
        print(endpoint)
        response = requests.get(endpoint, headers=header, cookies=cookies).json()
        items = response['items']
        for item in items:
            itemLink = item['link']
            metadata = requests.get(baseURL+itemLink+'/metadata', headers=header, cookies=cookies).json()
            for metadata_element in metadata:
                if metadata_element['key'] == key:
                    individual_name = metadata_element['value']
                    for metadata_element in metadata:
                        if metadata_element['key'] == 'dc.identifier.uri':
                            uri = metadata_element['value']
                            contains_initials = re.search(r'(\s|,|[A-Z]|([A-Z]\.))[A-Z](\s|$|\.|,)', individual_name)
                            contains_middleinitial = re.search(r'((\w{2,},\s)|(\w{2,},))\w[a-z]+', individual_name)
                            contains_parentheses = re.search(r'\(|\)', individual_name)
                            if contains_middleinitial:
                                continue
                            elif contains_parentheses:
                                continue
                            elif contains_initials:
                                name = {'link': uri, 'name': individual_name, 'key': key}
                                names.append(name)
                            else:
                                continue
            name = {'link': '', 'name': '', 'key': ''}
            names.append(name)
    offset = offset + 200
    print(offset)

handle = handle.replace('/', '-')
keys = names[0].keys()

with open('namesInitialsInCollection'+handle+'.csv', 'w') as name_file:
    f = csv.DictWriter(name_file, keys)
    f.writeheader()
    f.writerows(names)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))