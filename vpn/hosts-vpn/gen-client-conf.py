#!/usr/bin/env python3

import argparse, subprocess, os, sys
import simplejson as json

EASY_RSA_PATH = '/easy-rsa'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('commonName', type=str, help='X509 common name. Usually server UUID')
    args = parser.parse_args()

    if not args.commonName:
        raise ValueError('Argument(s) missing', args.commonName)

    cmd = ['./easyrsa', 'build-client-full', args.commonName, 'nopass']
    pwd = os.path.dirname(os.path.realpath(__file__))
    cwd = pwd + EASY_RSA_PATH
    ret = subprocess.run(cmd, cwd=cwd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if ret.returncode:
        sys.exit(ret.returncode)

    private_key_path = '{}/pki/private/{}.key'.format(cwd, args.commonName)
    with open(private_key_path, 'r') as private_key_file:
        private_key = private_key_file.read()

    certificate_path = '{}/pki/issued/{}.crt'.format(cwd, args.commonName)
    with open(certificate_path, 'r') as certificate_file:
        certificate = certificate_file.read()

    print (json.dumps(
        {'private_key': private_key,
        'certificate': certificate},
        sort_keys=True, indent=4 * ' '))


if __name__ == "__main__":
    main()
