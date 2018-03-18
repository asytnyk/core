#!/usr/bin/env python3

import simplejson as json
import argparse
import os.path

def check_file(parser, path):
    if not os.path.isfile(path):
        parser.error("The file %s does not exist!" % path)
    else:
        return open(path, 'r')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('installationkey', help='path to installation-key json file',
            type=lambda x:check_file(parser, x))
    parser.add_argument('facter', help='path to facter json file',
            type=lambda x:check_file(parser, x))

    args = parser.parse_args()

if __name__ == "__main__":
    main()
