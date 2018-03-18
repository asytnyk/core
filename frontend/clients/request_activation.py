#!/usr/bin/env python3

import simplejson as json
import argparse
import os.path
import requests

def check_file(parser, path):
    if not os.path.isfile(path):
        parser.error("The file %s does not exist!" % path)
    else:
        with open(path, 'r') as json_file:
            try:
                json.load(json_file)
            except:
                parser.error("The file %s does not seem to be a valid json file!" % path)

# Check https://stackoverflow.com/questions/14393339/convert-this-curl-cmd-to-python-3 for https
def request_activation_pin(installation_key, facter):
    url = installation_key['request_activation_url']
    key = installation_key['installation_key']
    headers = {'installation_key': key, 'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(facter))
    if r.status_code == 200:
        return r.json()
    else:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('installationkey', help='path to installation-key json file')
    parser.add_argument('facter', help='path to facter json file')

    args = parser.parse_args()

    check_file(parser, args.installationkey)
    check_file(parser, args.facter)

    with open(args.installationkey, 'r') as json_file:
        installation_key = json.load(json_file)

    with open(args.facter, 'r') as json_file:
        facter = json.load(json_file)

    print (request_activation_pin(installation_key, facter))

if __name__ == "__main__":
    main()
