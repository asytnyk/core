#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import ConfigParser, sqlite3, time, uuid, hashlib, sys, random, string, os
from getpass import getpass
from subprocess import call

CWD = os.getcwd()
EASYRSA_PATH = CWD + "/../vpn/hosts-vpn/easy-rsa"

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

# white_listed logs if the key was added to the vpn_server white list
ADD_VPN_KEY_QUERY = """
    INSERT INTO vpn_key(vpn_key_uuid, crt, key, white_listed) VALUES (?,?,?,0)
"""

def main():
    vpn_key_uuid = str(uuid.uuid4())

    # using vpn_key_uuid as the commonName
    call([EASYRSA_PATH + "/easyrsa", "build-client-full", vpn_key_uuid, "nopass"],
            stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), cwd=EASYRSA_PATH)

    path_to_key = EASYRSA_PATH + "/pki/private/" + vpn_key_uuid + ".key"
    with open(path_to_key, 'r') as myfile:
        vpn_key = myfile.read()

    path_to_crt = EASYRSA_PATH + "/pki/issued/" + vpn_key_uuid + ".crt"
    with open(path_to_crt, 'r') as myfile:
        vpn_crt = myfile.read()

    c = db.cursor()
    c.execute(ADD_VPN_KEY_QUERY, (vpn_key_uuid, vpn_crt, vpn_key))
    db.commit()
    db.close()

    print "vpn_key_uuid: " + str(vpn_key_uuid)

if __name__ == "__main__":
    main()
