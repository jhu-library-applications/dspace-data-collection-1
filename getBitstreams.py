import requests
import time
import csv
import argparse
import os
import re
from six.moves import input


def main():
    # NOTE: this is the secrets file, not a module
    import secrets

    # Define defaults
    default_response_timeout = 1
    default_limit = 100

    # Define globals for requests, so too many args aren't passed to functions.
    global header
    global cookies

    # begin: argument parsing
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    parser.add_argument('-i', '--handle',
                        help='handle of the object to retreive.')

    # bitstream formats:
    # REM: set number of args
    # '+' == 1 or more.
    # '*' == 0 or more.
    # '?' == 0 or 1.
    # An int is an explicit number of arguments to accept.
    parser.add_argument('-f', '--formats', nargs='*',
                        help='optional list of bitstream formats.\
                        will return all formats if not provided')

    parser.add_argument('-b', '--bundles', nargs='*',
                        help='optional list of bundles (e.g. ORIGINAL or LICENSE).\
                        will return all bundles if not provided')

    parser.add_argument('-dl', '--download', action='store_true',
                        help='download bitstreams (rather than retreive\
                        their metadata). default: false')

    parser.add_argument('-rt', '--rtimeout', type=int,
                        help='response timeout: seconds to wait for a response.\
                        not a timeout for a download or for entire script.\
                        default: '+str(default_response_timeout))

    parser.add_argument('-l', '--limit', type=int,
                        help='limit to the number of objects to return in a\
                        given request. default: '+str(default_limit))

    parser.add_argument('-u', '--baseURL',
                        help='url of the dspace instance.\
                        can be read from the secrets file')

    parser.add_argument('-e', '--email',
                        help='email of an authorized dspace user.\
                        can be read from the secrets file')

    parser.add_argument('-p', '--password',
                        help='password of an authorized dspace user.\
                        can be read from the secrets file')

    parser.add_argument('-d', '--filePath',
                        help='directory where output files will be written.\
                        can be read from the secrets file')
    args = parser.parse_args()

    secretsVersion = input('To edit production, enter secrets filename: ')
    if secretsVersion != '':
        try:
            secrets = __import__(secretsVersion)
            print('Accessing Production')
        except ImportError:
            print('Accessing Stage')
    else:
        print('Accessing Stage')
    if not args.rtimeout:
        args.rtimeout = default_response_timeout
    if not args.limit:
        args.limit = default_limit
    if not args.baseURL:
        args.baseURL = secrets.baseURL
    if not args.email:
        args.email = secrets.email
    if not args.password:
        args.password = secrets.password
    if not args.filePath:
        args.filePath = secrets.filePath
    if args.handle:
        handle = args.handle
    else:
        handle = input('Enter handle: ')
    if args.verbose:
        print('verbosity turned on')
    if args.handle:
        print('retreiving object with handle {}'.format(args.handle))
    if args.formats:
        print('filtering results to the bitstream\
               formats: {}'.format(args.formats))
    else:
        print('returning bitstreams of any format')
    if args.bundles:
        print('filtering results to bundles: {}'.format(args.bundles))
    else:
        print('returning bitstreams from any bundle')
    if args.download:
        print('downloading bitstreams')
    if args.rtimeout:
        print('response_timeout set to {}'.format(args.rtimeout))

    # end: argument parsing

    startTime = time.time()
    data = {'email': args.email, 'password': args.password}
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    session = requests.post(args.baseURL+'/rest/login', headers=header,
                            params=data, timeout=args.rtimeout).cookies['JSESSIONID']
    cookies = {'JSESSIONID': session}
    print('authenticated')

    # NOTE: expanding items (of collections) + bitstreams (of items) for count.
    endpoint = args.baseURL+'/rest/handle/'+handle+'?expand=items,bitstreams'
    dsObject = requests.get(endpoint, headers=header,
                            cookies=cookies, timeout=args.rtimeout)
    dsObject.raise_for_status()  # ensure we notice bad responses
    dsObject = dsObject.json()
    if args.verbose:
        print(dsObject)
    dsObjectID = dsObject['uuid']
    # TODO: extend
    if dsObject['type'] == 'collection':
        if args.verbose:
            print(dsObject['type'])

        itemCount = len(dsObject['items'])
        print('{} items'.format(itemCount))
        for collItem in dsObject['items']:
            endpoint = args.baseURL + collItem['link'] + '?expand=bitstreams'
            item = requests.get(endpoint, headers=header,
                                cookies=cookies, timeout=args.rtimeout)
            item.raise_for_status()  # ensure we notice bad responses
            item = item.json()
            processItem(item, args)

    elif dsObject['type'] == 'item':
        processItem(dsObject, args)

    else:
        print('Object is of an invalid type for this script ({}).\
              Enter item or collection handle.'.format(dsObject['type']))

    logout = requests.post(args.baseURL+'/rest/logout', headers=header,
                           cookies=cookies, timeout=args.rtimeout)

    elapsedTime = time.time() - startTime
    m, s = divmod(elapsedTime, 60)
    h, m = divmod(m, 60)
    print('Total script run time: {:01.0f}:{:02.0f}:{:02.0f}'.format(h, m, s))


def processItem(dsObject, args):
    if args.verbose:
        print(dsObject['type'])
    itemHandle = dsObject['handle']
    handleID = re.sub(r'.*\/', '', itemHandle)
    itemPath = args.filePath + '/' + handleID + '/'
    if not os.path.exists(itemPath):
        os.makedirs(itemPath)

    f = csv.writer(open(itemPath + handleID + '_bitstreams.csv', 'w'))
    f.writerow(['sequenceId']+['name']+['format']+['bundleName'])

    itemID = dsObject['uuid']
    bitCount = len(dsObject['bitstreams'])
    dlBitstreams = []
    offset = 0
    limit = args.limit
    bitstreams = ''
    # while bitstreams != []:
    while bitCount > 0:
        # don't retreive more bitstreams than we have left
        if limit > bitCount:
            limit = bitCount
        print('bitCount: {0} offset: {1} limit: {2}'.format(bitCount, offset, limit))
        link = (args.baseURL+'/rest/items/'+str(itemID)+'/bitstreams?limit='
                + str(limit)+'&offset='+str(offset))
        bitstreams = requests.get(link, headers=header, cookies=cookies,
                                  timeout=args.rtimeout)
        bitstreams.raise_for_status()  # ensure we notice bad responses
        bitstreams = bitstreams.json()
        for bitstream in bitstreams:
            if ((args.formats and bitstream['format'] in args.formats or not args.formats)
                    and (args.bundles and bitstream['bundleName']
                         in args.bundles or not args.bundles)):
                if args.verbose:
                    print(bitstream)
                sequenceId = str(bitstream['sequenceId'])
                fileName = bitstream['name']
                fileFormat = bitstream['format']
                bundleName = bitstream['bundleName']
                f.writerow([sequenceId]+[fileName]+[fileFormat]+[bundleName])

                if args.download:
                    dlBitstreams.append(bitstream)
        offset += limit
        bitCount -= limit

    for dlBitstream in dlBitstreams:
        if not os.path.isfile(itemPath + dlBitstream['name']):
            link2 = str(dlBitstream['retrieveLink'])
            response = requests.get(args.baseURL+link2,
                                    headers=header, cookies=cookies,
                                    verify=args.verify, timeout=args.rtimeout)
            response.raise_for_status()  # ensure we notice bad responses
            file = open(itemPath + dlBitstream['name'], 'w')
            file.write(response.content)
            file.close()


if __name__ == "__main__":
    main()
