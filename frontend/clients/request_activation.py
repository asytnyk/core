#!/usr/bin/env python3

import simplejson as json
import argparse
import os.path

def check_file(parser, path):
    if not os.path.isfile(path):
        parser.error("The file %s does not exist!" % path)
    else:
        with open(path, 'r') as json_file:
            try:
                json.load(json_file)
            except:
                parser.error("The file %s does not seem to be a valid json file!" % path)


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

    print(installation_key)
    print(facter)

if __name__ == "__main__":
    main()
