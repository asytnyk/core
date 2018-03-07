#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import ConfigParser, sqlite3, time, uuid, hashlib, sys, random, string, os
from getpass import getpass
from subprocess import call

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

ADD_SSH_KEY_QUERY = """
    INSERT INTO ssh_key(ssh_key_uuid, pub, priv) VALUES (?,?,?)
"""

def gen_keys():
    ssh_key_uuid = str(uuid.uuid4())

    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits;
    filename = ''.join(random.SystemRandom().choice(chars) for _ in range(8))

    #ssh-keygen -t rsa -b 4096 -N '' -f /tmp/test    
    call(["ssh-keygen", "-t", "rsa", "-b", "4096", "-N", "", "-f", filename], stdout=open(os.devnull, 'wb'))

    with open(filename, 'r') as myfile:
        private_key = myfile.read()#
    os.remove(filename)

    with open(filename + '.pub', 'r') as myfile:
        public_key = myfile.read()
    os.remove(filename + '.pub')

    c = db.cursor()
    c.execute(ADD_SSH_KEY_QUERY, (ssh_key_uuid, public_key, private_key))
    db.commit()
    db.close()

    return ssh_key_uuid

def main():
    print "ssh_key_uuid: " + gen_keys()

if __name__ == "__main__":
    main()
