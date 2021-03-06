#!/usr/bin/env python3

import simplejson as json
import argparse
import os
import requests
import sys
import time
import urllib3
import subprocess
from pyfiglet import Figlet

dest_dir = "/tmp/iWe/client-conf"
error_file = "/tmp/iWe/activation_error"
uuid_file = "/tmp/iWe/server_uuid"

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
    key = installation_key['installation-key']
    headers = {'installation-key': key, 'Content-Type': 'application/json'}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(facter))
    except (urllib3.exceptions.NewConnectionError, requests.exceptions.ConnectionError):
        print ('Connection error!')
        return None
    if r.status_code == 200:
        return r.json()
    else:
        return None

def try_download_client_conf(activation_pin_json, installation_key_json):
    headers = {'installation-key': installation_key_json['installation-key']}
    try:
        r = requests.get(activation_pin_json['download_keys_url'], headers=headers)
    except (urllib3.exceptions.NewConnectionError, requests.exceptions.ConnectionError):
        print ('Connection error! Check the connection to the Internet')
        return None

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
        installation_key_json = json.load(json_file)

    with open(args.facter, 'r') as json_file:
        facter = json.load(json_file)

    activation_pin_json = None
    sleep_secs = 15
    while not activation_pin_json:
        print('.', end='', flush=True)
        activation_pin_json = request_activation_pin(installation_key_json, facter)
        if not activation_pin_json:
            print ('Error getting the activation pin. Check if the installation key is valid and if the server is connected to the Internet.')
            time.sleep(sleep_secs)
    print('')

    if 'error' in activation_pin_json:
        print (activation_pin_json['error'])
        with open(error_file, 'w+') as err:
            err.write(activation_pin_json['error'])
        sys.exit()

    client_conf_json = None
    f = Figlet('big')
    print('Waiting your authorization for pin {}'.format(
        str(activation_pin_json['activation_pin'])))
    print(f.renderText('Pin {}'.format(activation_pin_json['activation_pin'])))
    print('You can activate it at {}'.format(
        activation_pin_json['activate_pin_url']))

    while not client_conf_json:
        print('.', end='', flush=True)
        client_conf_json = try_download_client_conf(activation_pin_json, installation_key_json)
        if not client_conf_json:
            time.sleep(sleep_secs)
    print('')
    if 'error' in client_conf_json:
        print (client_conf_json['error'])
        with open(error_file, 'w+') as err:
            err.write(activation_pin_json['error'])
        sys.exit()

    uuid = client_conf_json['server_uuid']

    with open (uuid_file, 'w+') as uuid_fd:
        uuid_fd.write(uuid)

    with open('{}/{}.key'.format(dest_dir, uuid), 'w+') as pvt_key:
        pvt_key.write(client_conf_json['vpn_client_pvt_key'])

    with open('{}/{}.crt'.format(dest_dir, uuid), 'w+') as client_crt:
        client_crt.write(client_conf_json['vpn_client_crt'])

    with open('{}/ca.crt'.format(dest_dir), 'w+') as ca_crt:
        ca_crt.write(client_conf_json['vpn_ca_crt'])

    with open('{}/ta.key'.format(dest_dir), 'w+') as ta_key:
        ta_key.write(client_conf_json['vpn_ta_key'])

    with open('{}/iwe-beta.conf'.format(dest_dir), 'w+') as client_conf:
        client_conf.write(client_conf_json['vpn_client_conf'])

    with open('{}/id_rsa.pub'.format(dest_dir), 'w+') as ssh_pub:
        ssh_pub.write(client_conf_json['ssh_pub'])

    # create links so we can use client.key and client.crt inside
    # openvpn config file
    os.chdir(dest_dir)
    os.symlink('{}.key'.format(uuid), 'client.key')
    os.symlink('{}.crt'.format(uuid), 'client.crt')

if __name__ == "__main__":
    main()
