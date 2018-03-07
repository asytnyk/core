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
    INSERT INTO ssh_key(pub, priv) VALUES (?,?)
"""

def main():
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
    c.execute(ADD_SSH_KEY_QUERY, (public_key, private_key))

    ssh_key_id = c.lastrowid
    db.commit()
    print "ssh_key_id: " + str(ssh_key_id)
    db.close()

#    try:
#        activated = c.fetchone()[0]
#    except TypeError:
#        print activation_uuid + " is not valid"
#        sys.exit()

    #print private_key + "\n"
    #print public_key

#    username = raw_input("Username: ")
#    hashed_pass = hashlib.sha256(getpass()).hexdigest()

#    if not check_login(username, hashed_pass):
#        print "Login failed"
#        db.close()
#        sys.exit()

#    print "Logged in"

#    activation_uuid = raw_input("Activation id: ")

#    time_in_secs = int(time.time())

#    c = db.cursor()
#    c.execute(CHECK_ACTIVATION_QUERY, (activation_uuid,))
#    try:
#        activated = c.fetchone()[0]
#    except TypeError:
#        print activation_uuid + " is not valid"
#        sys.exit()

#    if activated:
#        print activation_uuid + " is already active."
#        sys.exit()

#    c.execute(UPDATE_ACTIVATION_QUERY, (time_in_secs, activation_uuid))


    #print myuuid

if __name__ == "__main__":
    main()
