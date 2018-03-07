#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import ConfigParser, sqlite3, time, uuid, hashlib, sys
from getpass import getpass

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

UPDATE_ACTIVATION_QUERY = """
    UPDATE activation SET activation_date = ?, active = 1 WHERE activation_uuid = ?
"""

CHECK_ACTIVATION_QUERY = """
    SELECT active FROM activation WHERE activation_uuid = ?
"""

def check_login(username, hashed_pass):
    GET_PASS_QUERY = """
    SELECT password FROM customer WHERE username=?
    """

    UPDATE_LAST_LOGIN_QUERY = """
    UPDATE customer SET "last-login" = ? WHERE username = ?
    """

    c = db.cursor()
    c.execute(GET_PASS_QUERY, (username,))
    pass_from_db = c.fetchone()[0]

    if not pass_from_db == hashed_pass:
        return 0

    time_in_secs = int(time.time())

    c = db.cursor()
    c.execute(UPDATE_LAST_LOGIN_QUERY, (time_in_secs, username))
    db.commit()

    return 1


def main():
    
    username = raw_input("Username: ")
    hashed_pass = hashlib.sha256(getpass()).hexdigest()

    if not check_login(username, hashed_pass):
        print "Login failed"
        db.close()
        sys.exit()

    print "Logged in"

    activation_uuid = raw_input("Activation id: ")

    time_in_secs = int(time.time())

    c = db.cursor()
    c.execute(CHECK_ACTIVATION_QUERY, (activation_uuid,))
    try:
        activated = c.fetchone()[0]
    except TypeError:
        print activation_uuid + " is not valid"
        sys.exit()

    if activated:
        print activation_uuid + " is already active."
        sys.exit()

    c.execute(UPDATE_ACTIVATION_QUERY, (time_in_secs, activation_uuid))

    db.commit()
    db.close()

    #print myuuid

if __name__ == "__main__":
    main()
