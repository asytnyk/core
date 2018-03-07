#!/usr/bin/env python

""" Generates an uuid, saves to DB, and prints it """

import ConfigParser, sqlite3, time, sys, hashlib, uuid
from getpass import getpass

config = ConfigParser.ConfigParser()
config.read("backend.conf")
db_file = config.get("db", "file")

db = sqlite3.connect(db_file)

USER_ADD_QUERY = """
    INSERT INTO customer(customer_uuid,username, password, registration_date) values (?,?, ?, ?)
"""

def main():
    customer_uuid = str(uuid.uuid4())

    # No need of more than one second of precision
    time_in_secs = int(time.time())

    username = raw_input("Username: ")

    hashed_pass = hashlib.sha256(getpass()).hexdigest()

    c = db.cursor()
    c.execute("PRAGMA foreign_keys=ON");
    c.execute(USER_ADD_QUERY, (customer_uuid, username, hashed_pass, time_in_secs))

    db.commit()
    db.close()

    print "customer_uuid: " + customer_uuid


if __name__ == "__main__":
    main()
