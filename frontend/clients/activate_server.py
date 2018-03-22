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

def try_download_keys():
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

    download_keys_json = request_activation_pin(installation_key, facter)
    download_keys_url = download_keys_json['download_keys_url']

    keys_downloaded = None
    sleep_secs = 15
    while not keys_downloaded:
        download_keys_json = try_download_keys(download_keys_url, installation_key)
        keys_downloaded = download_keys_json['keys_downloaded']
        time.sleep(sleep_secs)

if __name__ == "__main__":
    main()
